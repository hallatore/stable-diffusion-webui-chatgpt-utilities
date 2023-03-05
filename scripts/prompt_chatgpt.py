import copy 
import openai

import modules.scripts as scripts
import gradio as gr
from modules import images, shared, script_callbacks
from modules.processing import Processed, process_images
from modules.shared import state
import modules.sd_samplers
from scripts.chatgpt_utils import query_chatgpt

def on_ui_settings():
    section = ('chatgpt_utilities', "ChatGPT Utilities")
    shared.opts.add_option("chatgpt_utilities_api_key", shared.OptionInfo("", "OpenAI API Key", section=section))

script_callbacks.on_ui_settings(on_ui_settings)

class Script(scripts.Script):
    def title(self):
        return "ChatGPT"

    def ui(self, is_img2img):

        with gr.Row().style(equal_height=True, variant='compact'):
            template_button2 = gr.Button(value="Generate prompts", elem_id="chatgpt_template_button2")
            template_button1 = gr.Button(value="Add keywords", elem_id="chatgpt_template_button1")
            template_button3 = gr.Button(value="Prompt variations", elem_id="chatgpt_template_button3")
            gr.HTML('<a href="https://github.com/hallatore/stable-diffusion-webui-chatgpt-utilities" target="_blank" style="text-decoration: underline;">Help & More Examples</a>')

        chatgpt_prompt = gr.Textbox(label="", lines=3)
        chatgpt_batch_count = gr.Number(value=4, label="Response count")
        chatgpt_append_to_prompt = gr.Checkbox(label="Append to original prompt instead of replacing it", default=False)
        chatgpt_no_iterate_seed = gr.Checkbox(label="Don't increment seed per permutation", default=False)
        chatgpt_prepend_prompt = gr.Textbox(label="Prepend generated prompt with", lines=1)
        chatgpt_append_prompt = gr.Textbox(label="Append generated prompt with", lines=1)
        chatgpt_generate_original_prompt = gr.Checkbox(label="Also generate original prompt", default=False)

        def apply_template1():
            return """
Find 3 keywords per answer related to the prompt {prompt} that are not found in the prompt. 
The keywords should be related to each other. 
Each keyword is a single word.
            """.strip(), True, True

        template_button1.click(apply_template1, inputs=[], outputs=[chatgpt_prompt, chatgpt_append_to_prompt, chatgpt_no_iterate_seed])

        def apply_template2():
            return """
Make a prompt describing a movie scene with a a character in a movie.
Themes can be Cyperpunk, Steampunk, Western, Alien or something similar.
Pick a theme and use it when describing the movie. 
Pick a gender, either male or female, and use it when describing the person. 
Focus on the person, what he/she is wearing, theme and the art style
            """.strip(), False, False

        template_button2.click(apply_template2, inputs=[], outputs=[chatgpt_prompt, chatgpt_append_to_prompt, chatgpt_no_iterate_seed])

        def apply_template3():
            return """
Take the prompt {prompt} and change 3 words somewhere in the prompt.
            """.strip(), False, True

        template_button3.click(apply_template3, inputs=[], outputs=[chatgpt_prompt, chatgpt_append_to_prompt, chatgpt_no_iterate_seed])
        
        return [
            chatgpt_prompt, 
            chatgpt_batch_count, 
            chatgpt_append_to_prompt, 
            chatgpt_no_iterate_seed, 
            chatgpt_prepend_prompt, 
            chatgpt_append_prompt, 
            chatgpt_generate_original_prompt
        ]

    def run(
            self, 
            p, 
            chatgpt_prompt, 
            chatgpt_batch_count, 
            chatgpt_append_to_prompt, 
            chatgpt_no_iterate_seed, 
            chatgpt_prepend_prompt, 
            chatgpt_append_prompt,
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
        chatgpt_answers = query_chatgpt(chatgpt_prompt, int(chatgpt_batch_count))

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
