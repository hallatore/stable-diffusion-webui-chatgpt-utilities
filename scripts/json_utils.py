import re
import json5

# Takes a string and attempts to parse it as JSON. Returns a JSON object.
# Handles many edge cases caused by the way ChatGPT returns responses.
def try_parse_json(input_text):
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
        json_string = input_text[start_index:end_index+1]
        json_string = re.sub(r'\}[\s]*\{', '}, {', json_string)
        json_string = re.sub(r'\][\s]*\[', '], [', json_string)
        json_string = re.sub(r'\"[\s]*\"', '", "', json_string)

        try:
            json_object = json5.loads(json_string)
        except ValueError:
            json_object = json5.loads(f"[{json_string}]")

        return json_object
    
    raise Exception("No JSON object found in input text.")

# Takes a JSON object and flattens it into an array of strings.
def flatten_json_structure(json_array):
    if (isinstance(json_array, list) and len(json_array) == 1 and not isinstance(json_array[0], str)):
        return flatten_json_structure(json_array[0])    
    
    if (isinstance(json_array, dict) and len(json_array.values()) == 1 and not isinstance(list(json_array.values())[0], str)):
        return flatten_json_structure(list(json_array.values())[0])

    flattened_json_array = []

    if (isinstance(json_array, dict)):
        json_array = json_array.values()

    for json_object in json_array:
        flattened_dict = flatten_json_object(json_object)
        flattened_values = ", ".join(str(v) for v in flattened_dict.values())
        flattened_json_array.append(flattened_values)
    
    return flattened_json_array

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