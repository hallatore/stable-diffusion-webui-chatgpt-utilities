# stable-diffusion-webui-chatgpt-utilities
This an extension for [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) that enables you to use ChatGPT for prompt variations, inspiration and pretty much anything you can think of.

[![name](images/ui.jpg)](images/ui.jpg?raw=true)

## Installation & Setup

- Go to the directory \<stable-diffusion-webui project path\>/extensions and run command  to install: `git clone https://github.com/hallatore/stable-diffusion-webui-chatgpt-utilities` and restart your stable-diffusion-webui.
[See here for more install details](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Extensions)

- Add your OpenAI API Key in Settings/ChatGPT Utilities within the web ui. You need a paying account at  [OpenAI](https://platform.openai.com/account/billing/overview).

- Enable ChatGPT under scripts in txt2img/img2img

## Tips

ChatGPT can be a bit hit & miss when it comes to generating good responses.

If you want to emulate the script on [the ChatGPT website](https://chat.openai.com/chat) you can use the following prompt:

    I want you to act as a prompt generator. Compose each answer as a visual sentence. Do not write explanations on replies. Format the answers as javascript json arrays with a single string per answer. Return exactly 6 anwsers to my question. Answer my questions exactly. My first question is:
    <Make a prompt describing an cyberpunk movie scene of a character standing. And the rest of your prompt here>

* Set the number of answers you want.
* Don't use newlines in your part of the prompt. (The script strips any newlines before it sends it to ChatGPT, so you can have stuff on new lines in the UI.)

## Usage

ChatGPT is quite fluid/dynamic/analog in it's responses. So play around with what questions works best. ChatGPT response is printed in the console, so you can check what it generated there and interupt SD if it's too off.

**Input textbox**

Add your ChatGPT question here. It should be something that asks for variations. 
PS: {prompt} is a special key and will insert the original prompt in your ChatGPT request.

See examples further down.

**Replace prompt checkbox**

This checkbox replaces the prompt instead of appending to it. Turn this ON if you want chatGPT to return prompt variations to try out.
- OFF: "ORIGINAL_PROMPT, CHATGPT_RESPONSE"
- ON: "CHATGPT_RESPONSE"

## Examples

### Make new unique prompts based on a starting prompt

![image](images/example_4.png)

> prompt: warlock karl urban rasputin, full shot, neutral background, highly detailed, digital painting, artstation, concept art, sharp focus, illustration

> chatgpt: Describe an epic d&d scene using this prompt {prompt} as inspiration. 
Describe the person, clothing/armor and atmosphere.
Don't use any names or artist names from the original prompt. 
Give me 8 example with unique characteristics. 
Return only a short description.

Parsed response:

    [
        "A warlock in flowing, obsidian robes stands at the ready, a staff of twisted oak clasped firmly in their left hand.",
        "A heavily armored figure glares menacingly at the viewer, their plate mail shining in the pale moonlight.",
        "A dark and mysterious figure, garbed in tattered robes, emerges from the shadows with a sinister grin.",
        "A robed mage, brimming with arcane power, conjures a mighty bolt of lightning that crackles in the air around them.",
        "A brooding figure draped in a cloak of black feathers surveys the bleak and desolate landscape, an air of quiet menace surrounding them.",
        "A daunting presence, adorned in spiked leather and wielding a wicked maul, dominates the space around them with an aura of deadly force.",
        "A fierce warrior, clad in gleaming silver armor and wielding twin blades, charges headlong into the fray with wild abandon.",
        "A powerful sorcerer, wreathed in arcane energies, stands amidst the smoldering ruins of a once-great city and casts a spell of immense destruction."
    ]

---

### Reduce prompt complexity and change sentences to keywords.

![image](images/example_3.jpg)

> prompt: ToreLervik-v1 as an assassin, Thin, supple black leather armor with an attached hood to conceal ToreLervik-v1's face, and forearm-length gloves equipped with hidden daggers. His boots are fitted with grappling hooks which allow him to scale walls with ease., The night is moonless and the only sound is the distant chirping of crickets. In the shadows, ToreLervik-v1 moves like a wraith, silent and deadly, stalking his prey through the abandoned city streets.

> chatgpt: Do not change the word ToreLervik-v1. Take the following prompt {prompt} and make 5 variations only containing 10 keywords each containing the most important parts of the prompt.

parsed response:

    [
        "ToreLervik-v1 as assassin, black leather armor, attached hood, forearm-length gloves, hidden daggers, grappling hooks, moonless night, chirping crickets, silent, deadly",
        "ToreLervik-v1, thin black leather armor, hooded face, forearm gloves, hidden daggers, grappling hook boots, abandoned city streets, wraith-like movement, stalking prey, silent killer",
        "Assassin ToreLervik-v1, supple leather armor, concealed face, hidden daggers, grappling hook boots, moonless night, chirping crickets, deadly movements, abandoned streets, skilled hunter",
        "ToreLervik-v1, stealthy assassin, black leather armor, hooded face, hidden daggers, grappling hooks, moonless night, chirping crickets, silent stalker, abandoned city",
        "Assassin ToreLervik-v1, thin armor, hooded face, hidden daggers, grappling hooks, abandoned streets, moonless night, chirping crickets, wraith-like movement, deadly predator"
    ]

---

### Give me x variations

![image](images/example_1.png)

> prompt: a forest path with trees

> chatgpt: Describe 5 unique fantasy settings given the prompt {prompt} with 4 keywords per item