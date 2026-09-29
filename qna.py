from ai_client import generate_text


def answer_question(question: str) -> str:
    prompt = (
        "You are EduGenie, an educational assistant. Answer the student's question accurately "
        "and concisely. Explain important terms when useful. If the question is ambiguous, state "
        "the assumption you made. Do not invent sources or facts.\n\n"
        f"Question: {question}"
    )
    return generate_text(prompt, temperature=0.2, max_output_tokens=1200)
