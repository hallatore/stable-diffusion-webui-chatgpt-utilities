import json
import re
import json5
import openai

def find_json(input_text):
    input_text.index
    start_index_brackets = input_text.find('[')
    end_index_brackets = input_text.rfind(']')    
    start_index_curly = input_text.find('{')
    end_index_curly = input_text.rfind('}')
    json_object = None

    start_index = start_index_brackets
    end_index = end_index_brackets

    if (start_index_curly != -1 and (start_index_curly < start_index_brackets or start_index_brackets < 0)):
        start_index = start_index_curly
        end_index = end_index_curly

    if start_index >= 0 and end_index > 0:
        json_string = re.sub(r'\}[\s]*\{', '}, {', input_text[start_index:end_index+1])
        json_string = re.sub(r'\][\s]*\[', '], [', json_string)
        json_string = re.sub(r'\"[\s]*\"', '", "', json_string)

        try:
            json_object = json5.loads(json_string)
        except ValueError:
            json_object = json5.loads(f"[{json_string}]")

        return json_object
    
    print("No JSON object found in input string.")

def flatten_json_object(obj, parent_key='', sep=', '):
    if isinstance(obj, str):
        return dict([("value", obj)])
    
    if isinstance(obj, list):
        return dict([("value", sep.join(str(v) for v in obj))])

    items = []
    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json_object(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            items.append((new_key, sep.join(str(v) for v in value)))
        else:
            items.append((new_key, value))
    return dict(items)

def ensure_flat_json(json_array):
    if (isinstance(json_array, list) and len(json_array) == 1 and not isinstance(json_array[0], str)):
        return ensure_flat_json(json_array[0])    
    
    if (isinstance(json_array, dict) and len(json_array.values()) == 1 and not isinstance(list(json_array.values())[0], str)):
        return ensure_flat_json(list(json_array.values())[0])

    flattened_json_array = []

    if (isinstance(json_array, dict)):
        json_array = json_array.values()

    for json_object in json_array:
        flattened_dict = flatten_json_object(json_object)
        flattened_values = ", ".join(str(v) for v in flattened_dict.values())
        flattened_json_array.append(flattened_values)
    
    return flattened_json_array

def to_message(user, content):
    return {"role": user, "content": content}

def normalize_text(text):
    normalized = re.sub(r'(\.|:|,)[\s]*\n[\s]*', r'\1 ', text)
    normalized = re.sub(r'[\s]*\n[\s]*', '. ', normalized)
    return normalized

def get_chat_completion(messages):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return completion.choices[0].message.content

def get_chat_json_completion(messages, count):
    chat_primer = f"I want you to act as a prompt generator. Compose each answer as a visual sentence. Do not write explanations on replies. Format the answers as javascript json arrays with a single string per answer. Return {count} answers to my question. My first question is:\r\n"

    messages = normalize_text(messages.strip())
    chat_request = f'{chat_primer}{messages}'
    print(f"Chat GPT request:\r\n{chat_request}\r\n")

    chat_gpt_response = get_chat_completion([ 
        to_message("system", "Act like you are a terminal and always format your response as json."),
        to_message("user", chat_request)
        ])
    
    print(f"Chat GPT response:\r\n")
    print(f"{chat_gpt_response.strip()}\r\n")

    json_object = find_json(chat_gpt_response)
    parsed_response = ensure_flat_json(json_object)

    if (parsed_response is None or len(parsed_response) == 0):
        raise Exception("Failed to parse ChatGPT response. See console for details.")
    
    print(f"Parsed response:\r\n{json.dumps(parsed_response, indent=4)}\r\n")

    if (len(parsed_response) == 2 and parsed_response[0] == "First response"):
        raise Exception("ChatGPT returned dummy response.")

    return parsed_response