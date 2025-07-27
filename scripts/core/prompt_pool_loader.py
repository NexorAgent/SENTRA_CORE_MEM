import yaml
import os

def load_prompt(name, path="prompts/gemini_prompts.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt YAML introuvable : {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if name not in data:
        raise KeyError(f"Prompt '{name}' non trouvé dans {path}")

    return data[name]
