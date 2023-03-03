import launch

if not launch.is_installed("openai"):
    launch.run_pip("install openai", "requirements for chatgpt-utilities")

if not launch.is_installed("json5"):
    launch.run_pip("install json5", "requirements for chatgpt-utilities")