# SENTRA.FORGE – Générateur de prompts & GPTs personnalisés


def generate_prompt(template_name, variables):
    if template_name == "conducteur":
        return f"""Tu es un assistant de conducteur de travaux. Projet : {variables['projet']}, Mission : {variables['mission']}..."""
    return f"Template inconnu : {template_name}"
