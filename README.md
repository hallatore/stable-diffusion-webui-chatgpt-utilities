# stable-diffusion-webui-chatgpt-utilities
This an extension for [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

This is a set of utilities for the stable-diffusion-webui.

## Installation & Setup

- Go to the directory \<stable-diffusion-webui project path\>/extensions and run command  to install: `git clone https://github.com/hallatore/stable-diffusion-webui-chatgpt-utilities` and restart your stable-diffusion-webui.
[See here for more install details](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Extensions)

- Add your OpenAI API Key in Settings/ChatGPT Utilities within the web ui. You need a paying account at  [OpenAI](https://platform.openai.com/account/billing/overview).

- Enable ChatGPT under scripts in txt2img/img2img

## Usage

### Input
Add your ChatGPT question here. It should be something that asks for variations. 
PS: {prompt} is a special key and will insert the original prompt in your ChatGPT request.

See examples further down.

### Replace prompt
This checkbox replaces the prompt instead of appending to it. Turn this ON if you want chatGPT to return prompt variations to try out.
- OFF: "ORIGINAL_PROMPT, CHATGPT_RESPONSE"
- ON: "CHATGPT_RESPONSE"

## Examples

![image](images/example_1.png)

    prompt: a forest path with trees
    chatgpt: Describe 5 unique fantasy settings given the prompt "{prompt}" with 4 keywords per item

---

![image](images/example_2.png)

    prompt: a photo of a bird
    chatgpt: Give me 5 colorful tropical birds. Their names and 4 keywords




