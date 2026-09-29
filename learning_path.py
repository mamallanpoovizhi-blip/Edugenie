from ai_client import generate_text


def get_learning_recommendations(topic: str) -> str:
    prompt = (
        "Create a personalized learning path for the topic below. Organize it from beginner to "
        "advanced level. For each stage, include concepts to learn, a suggested timeline, practice "
        "activities, and useful resource types such as videos, articles, or books. Keep the plan "
        "practical and adaptable to a learner's starting level.\n\n"
        f"Topic: {topic}"
    )
    return generate_text(prompt, temperature=0.4, max_output_tokens=2200)
