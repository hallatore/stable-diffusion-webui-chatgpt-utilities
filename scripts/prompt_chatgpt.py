import copy
import os 
import openai

import modules.scripts as scripts
import gradio as gr
from modules import images, shared, script_callbacks
from modules.processing import Processed, process_images
from modules.shared import state
import modules.sd_samplers
from scripts.chatgpt_utils import query_chatgpt
from scripts.template_utils import get_templates

script_dir = scripts.basedir()

def on_ui_settings():
    section = ('chatgpt_utilities', "ChatGPT Utilities")
    shared.opts.add_option("chatgpt_utilities_api_key", shared.OptionInfo("", "OpenAI API Key", section=section))

script_callbacks.on_ui_settings(on_ui_settings)

class Script(scripts.Script):
    def title(self):
        return "ChatGPT"

    def ui(self, is_img2img):
        templates = get_templates(os.path.join(script_dir, "templates"))

        with gr.Row().style(equal_height=False, variant='compact'):
            templates_dropdown = gr.Dropdown(
                label="Templates", 
                choices=[t[0] for t in templates],
                type="index", 
                elem_id="chatgpt_template_dropdown")
            #templates_load_button = gr.Button('🔄', elem_id="chatgpt_template_button4").style(full_width=False)
            gr.HTML('<a href="https://github.com/hallatore/stable-diffusion-webui-chatgpt-utilities" target="_blank" style="text-decoration: underline;">Help & More Examples</a>')

        chatgpt_prompt = gr.Textbox(label="", lines=3)
        chatgpt_append_to_prompt = gr.Checkbox(label="Append to original prompt instead of replacing it", default=False)
        chatgpt_batch_count = gr.Number(value=4, label="Response count")
        chatgpt_prepend_prompt = gr.Textbox(label="Prepend generated prompt with", lines=1)
        chatgpt_append_prompt = gr.Textbox(label="Append generated prompt with", lines=1)
        chatgpt_no_iterate_seed = gr.Checkbox(label="Don't increment seed per permutation", default=False)
        chatgpt_generate_original_prompt = gr.Checkbox(label="Also generate original prompt", default=False)

        def apply_template(dropdown_value, prompt, append_to_prompt):
            if not (isinstance(dropdown_value, int)):
                return prompt, append_to_prompt

            file_path = templates[dropdown_value][1]
            dir_name = os.path.basename(os.path.dirname(file_path))
            
            with open(templates[dropdown_value][1], 'r') as file:
                template_text = file.read()

            return template_text, dir_name.lower() == "append"

        templates_dropdown.change(
            apply_template, 
            inputs=[templates_dropdown, chatgpt_prompt, chatgpt_append_to_prompt], 
            outputs=[chatgpt_prompt, chatgpt_append_to_prompt]
        )
        
        return [
            chatgpt_prompt, 
            chatgpt_append_to_prompt, 
            chatgpt_batch_count, 
            chatgpt_prepend_prompt, 
            chatgpt_append_prompt, 
            chatgpt_no_iterate_seed, 
            chatgpt_generate_original_prompt
        ]

    def run(
            self, 
            p, 
            chatgpt_prompt, 
            chatgpt_append_to_prompt, 
            chatgpt_batch_count, 
            chatgpt_prepend_prompt, 
            chatgpt_append_prompt,
            chatgpt_no_iterate_seed, 
            chatgpt_generate_original_prompt
        ):
        modules.processing.fix_seed(p)

        openai.api_key = shared.opts.data.get("chatgpt_utilities_api_key", "")

        if openai.api_key == "":
            raise Exception("OpenAI API Key is not set. Please set it in the settings menu.")
        
        if (chatgpt_prompt == ""):
            raise Exception("ChatGPT prompt is empty.")
        
        if (chatgpt_batch_count < 1):
            raise Exception("ChatGPT batch count needs to be 1 or higher.")

        original_prompt = p.prompt[0] if type(p.prompt) == list else p.prompt
        chatgpt_prompt = chatgpt_prompt.replace("{prompt}", f'"{original_prompt}"')

        for i in range(3):
            chatgpt_answers = query_chatgpt(chatgpt_prompt, int(chatgpt_batch_count))

            if (len(chatgpt_answers) == int(chatgpt_batch_count)):
                break
        
        if (len(chatgpt_answers) != int(chatgpt_batch_count)):
            raise Exception(f"ChatGPT answers doesn't match batch count. Got {len(chatgpt_answers)} answers, expected {int(chatgpt_batch_count)}.")

        prompts = []
        chatgpt_prefix = ""

        if len(original_prompt) > 0:
            if chatgpt_generate_original_prompt:
                prompts.append(["", original_prompt])

            if chatgpt_append_to_prompt:
                chatgpt_prefix = f"{original_prompt}, "

        for answer in chatgpt_answers:
            prompts.append([answer, f"{chatgpt_prefix}{chatgpt_prepend_prompt}{answer}{chatgpt_append_prompt}"])
                           
        p.do_not_save_grid = True
        state.job_count = 0
        permutations = 0
        
        state.job_count += len(prompts) * p.n_iter
        permutations += len(prompts)
            
        print(f"Creating {permutations} image permutations")
        image_results = []
        all_prompts = []
        infotexts = []
        current_seed = p.seed

        for prompt in prompts:
            copy_p = copy.copy(p)
            copy_p.prompt = prompt[1]
            copy_p.seed = current_seed

            if not chatgpt_no_iterate_seed:
                current_seed += 1

            proc = process_images(copy_p)
            temp_grid = images.image_grid(proc.images, p.batch_size)
            image_results.append(temp_grid)

            all_prompts += proc.all_prompts
            infotexts += proc.infotexts

        if (len(prompts) > 1):
            grid = images.image_grid(image_results, p.batch_size)
            infotexts.insert(0, infotexts[0])
            image_results.insert(0, grid)
            images.save_image(grid, p.outpath_grids, "grid", grid=True, p=p)

        return Processed(p, image_results, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)
