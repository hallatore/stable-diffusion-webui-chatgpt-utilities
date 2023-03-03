import json
import json5
import re
import openai

def find_json(input_text):
    input_text.index
    start_index = input_text.find('[')
    end_index = input_text.rfind(']')
    json_object = None

    if start_index >= 0 and end_index > 0:
        json_object = json5.loads(input_text[start_index:end_index+1])
        return json_object
    else:
        start_index = input_text.find('{')
        end_index = input_text.rfind('}')
        if start_index >= 0 and end_index > 0:
            json_object = json5.loads(input_text[start_index:end_index+1])
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
    flattened_json_array = []

    if (isinstance(json_array, dict)):
        json_array = json_array.values()

    for json_object in json_array:
        flattened_dict = flatten_json_object(json_object)
        flattened_values = ", ".join(str(v) for v in flattened_dict.values())
        flattened_json_array.append(flattened_values)

    if (len(flattened_json_array) == 1):
        return ensure_flat_json(flattened_json_array[0])
    
    return flattened_json_array

def to_message(user, content):
    return {"role": user, "content": content}

def get_chat_completion(messages):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return completion.choices[0].message.content

def get_chat_json_completion(messages):
    jsonChatMessage = 'Only respond with a valid json array. Example response: [{name: "First response" }, {name: "Second response" }]'

    chat_gpt_response = get_chat_completion([ 
        to_message("system", f'Act like you are a terminal and only respond with json. {jsonChatMessage}'),
        to_message("user", f'{messages}\r\nreturn everything as a json object.\r\n{jsonChatMessage}')
        ])
    
    print("Chat GPT response")
    print(chat_gpt_response.strip())

    json_object = find_json(chat_gpt_response)
    parsed_response = ensure_flat_json(json_object)
    
    print("Parsed response")
    print(json.dumps(parsed_response, indent=4))
    return parsed_response