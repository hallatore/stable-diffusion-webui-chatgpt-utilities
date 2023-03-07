import json
import re
import openai

from scripts.json_utils import flatten_json_structure, try_parse_json

def retry_query_chatgpt(messages, count, retries):
    chatgpt_answers = []

    for i in range(retries):
        try:
            chatgpt_answers = query_chatgpt(messages, count)

            if (len(chatgpt_answers) == count):
                return chatgpt_answers
        except Exception as e:
            if (i == retries - 1):
                raise e
            
            print(f"ChatGPT query failed. Retrying. Error: {e}")
    
    if (len(chatgpt_answers) != count):
        raise Exception(f"ChatGPT answers doesn't match batch count. Got {len(chatgpt_answers)} answers, expected {count}.")

def query_chatgpt(messages, answer_count):
    system_primer = f"Act like you are a terminal and always format your response as json. Always return exactly {answer_count} anwsers per question."
    chat_primer = f"I want you to act as a prompt generator. Compose each answer as a visual sentence. Do not write explanations on replies. Format the answers as javascript json arrays with a single string per answer. Return exactly {answer_count} to my question. Answer the questions exactly. Answer the following question:\r\n"

    messages = normalize_text_for_chat_gpt(messages.strip())
    chat_request = f'{chat_primer}{messages}'
    print(f"Chat GPT request:\r\n{chat_request}\r\n")

    chat_gpt_response = get_chat_completion([ 
        to_message("system", system_primer),
        to_message("user", chat_request)
        ])
    
    print(f"Chat GPT response:\r\n")
    print(f"{chat_gpt_response.strip()}\r\n")

    result = flatten_json_structure(try_parse_json(chat_gpt_response))

    if (result is None or len(result) == 0):
        raise Exception("Failed to parse ChatGPT response. See console for details.")
    
    print(f"Parsed response:\r\n{json.dumps(result, indent=4)}\r\n")
    return result

def to_message(user, content):
    return {"role": user, "content": content}

def normalize_text_for_chat_gpt(text):
    normalized = re.sub(r'(\.|:|,)[\s]*\n[\s]*', r'\1 ', text)
    normalized = re.sub(r'[\s]*\n[\s]*', '. ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized

def get_chat_completion(messages):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.5)
    return completion.choices[0].message.content