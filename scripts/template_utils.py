import glob
import os

def get_name(path):
    type = x = "A" if os.path.basename(os.path.dirname(path)).lower() == "append" else "R"
    name = os.path.splitext(os.path.basename(path))[0]
    return f"{type} - {name}"

def get_templates(path):
    txt_files = glob.glob(os.path.join(path, "**/*.txt"), recursive=True)
    templates = [[get_name(f), f] for f in txt_files]
    templates = sorted(templates, key=lambda p: p[0])
    return templates