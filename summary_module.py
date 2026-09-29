from ai_client import generate_text


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the educational passage below in concise, easy-to-understand language. "
        "Preserve the main facts and important terms. Avoid adding information not present in the text. "
        "Use short paragraphs or bullet points when helpful.\n\n"
        f"Passage:\n{text}"
    )
    return generate_text(prompt, temperature=0.2, max_output_tokens=1200)
