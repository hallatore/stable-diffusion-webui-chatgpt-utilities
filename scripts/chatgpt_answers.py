from functools import reduce
import operator
import re
from scripts.chatgpt_utils import retry_query_chatgpt


def get_chatgpt_answers(chatgpt_prompt, batch_count, temperature, original_prompt):
    prompt_split = chatgpt_prompt.split("::")
    prompts = []
    explode_prompts = False

    for index, prompt in enumerate(prompt_split):
        prompt = re.sub(r"^[\d]+", "", prompt)
        prompt_count = batch_count

        if (index != len(prompt_split) - 1):
            possible_batch_count = re.search(r"^[\d]+", prompt_split[index + 1])

            if (possible_batch_count is not None):
                explode_prompts = True
                prompt_count = int(possible_batch_count.group(0))

        if (prompt.strip() != ""):
            prompts.append([prompt_count, prompt.strip()])

    results = []

    for prompt_count, prompt in prompts:
        prompt = prompt.replace("{prompt}", f'"{original_prompt}"')
        chatgpt_answers = retry_query_chatgpt(prompt, prompt_count, temperature, 4)

        if (len(results) == 0):
            results = chatgpt_answers
            continue

        if (explode_prompts):
            temp_results = []
            for result in results:
                for answer in chatgpt_answers:
                    seperator = " " if result.endswith(",") or result.endswith(".") else ", "
                    temp_results.append(f"{result}{seperator}{answer}")

            results = temp_results
        else:
            for i, answer in enumerate(chatgpt_answers):
                seperator = " " if results[i].endswith(",") or results[i].endswith(".") else ", "
                results[i] += f"{seperator}{answer}"

    return results