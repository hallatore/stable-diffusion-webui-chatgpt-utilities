import copy 
import re
import openai

import modules.scripts as scripts
import gradio as gr

from PIL import ImageFont, ImageDraw
from fonts.ttf import Roboto
from modules import images, shared, script_callbacks
from modules.processing import Processed, process_images
from modules.shared import state, opts
import modules.sd_samplers
from scripts.chatgpt_utils import get_chat_json_completion, to_message

def trimPrompt(prompt):
    prompt = prompt.replace(", :", ":")
    prompt = re.sub(r"[, ]*\(:[\d.]+\)", "", prompt)
    prompt = re.sub(r"[, ]*[\(]+[\)]+", "", prompt)
    prompt = re.sub(r"^[, ]*", "", prompt)
    prompt = re.sub(r"[, ]*$", "", prompt)
    return prompt

def splitPrompt(prompt, skip=0, include_base=True):
    pattern = re.compile(r'[ ]*([\w ]+)([,]*)[ ]*')
    prompts = []

    if include_base:
        prompts.append(["", prompt])

    matches = list(re.finditer(pattern, prompt))

    for i in range(len(matches)):
        if i < skip:
            continue

        m = matches[i]
        if (len(m.group(1).strip()) > 1):
            prompts.append([m.group(1), trimPrompt(prompt.replace(m.group(0), ''))])
    
    return prompts

# This is a modified version of code from https://github.com/Extraltodeus/test_my_prompt/blob/main/test_my_prompt_custom_script.py
def write_on_image(img, msg):
    ix,iy = img.size
    draw = ImageDraw.Draw(img)
    margin=2
    fontsize=16
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(Roboto, fontsize)
    text_height=iy-40
    tx = draw.textbbox((0,0),msg,font)
    draw.text((int((ix-tx[2])/2),text_height+margin),msg,(0,0,0),font=font)
    draw.text((int((ix-tx[2])/2),text_height-margin),msg,(0,0,0),font=font)
    draw.text((int((ix-tx[2])/2+margin),text_height),msg,(0,0,0),font=font)
    draw.text((int((ix-tx[2])/2-margin),text_height),msg,(0,0,0),font=font)
    draw.text((int((ix-tx[2])/2),text_height), msg,(255,255,255),font=font)
    return img

def on_ui_settings():
    section = ('chatgpt_utilities', "ChatGPT Utilities")
    shared.opts.add_option("chatgpt_utilities_api_key", shared.OptionInfo("", "OpenAI API Key", section=section))

script_callbacks.on_ui_settings(on_ui_settings)

class Script(scripts.Script):
    def title(self):
        return "ChatGPT"

    def ui(self, is_img2img):
        chatgpt_prompt = gr.Textbox(label="", lines=3)
        return [chatgpt_prompt]

    def run(self, p, chatgpt_prompt):
        modules.processing.fix_seed(p)


        original_prompt = p.prompt[0] if type(p.prompt) == list else p.prompt
        chatgpt_prompt = chatgpt_prompt.replace("{prompt}", original_prompt)
        openai.api_key = shared.opts.data.get("chatgpt_utilities_api_key", "")
        chatgpt_json_response = get_chat_json_completion(chatgpt_prompt)

        prompts = []
        chatgpt_prefix = ""

        if len(original_prompt) > 0:
            prompts.append(["", original_prompt])
            chatgpt_prefix = f"{original_prompt}, "

        for resp in chatgpt_json_response:
            prompts.append([resp, f"{chatgpt_prefix}{resp}"])
                           
        p.do_not_save_grid = True
        state.job_count = 0
        permutations = 0
        
        state.job_count += len(prompts) * p.n_iter
        permutations += len(prompts)
            
        print(f"Creating {permutations} image permutations")
        image_results = []
        all_prompts = []
        infotexts = []
        for prompt in prompts:
            copy_p = copy.copy(p)
            copy_p.prompt = prompt[1]

            proc = process_images(copy_p)
            temp_grid = images.image_grid(proc.images, p.batch_size)
            temp_grid = write_on_image(temp_grid, "" if prompt[0] == "" else prompt[0])
            image_results.append(temp_grid)

            all_prompts += proc.all_prompts
            infotexts += proc.infotexts

        grid = images.image_grid(image_results, p.batch_size)
        infotexts.insert(0, infotexts[0])
        image_results.insert(0, grid)
        images.save_image(grid, p.outpath_grids, "grid", grid=True, p=p)

        return Processed(p, image_results, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)
