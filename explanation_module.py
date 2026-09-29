import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

try:
    from transformers import pipeline
except Exception:  # pragma: no cover
    pipeline = None

LOCAL_MODEL = os.getenv("LOCAL_EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M").strip()


@lru_cache(maxsize=1)
def _local_pipeline():
    if pipeline is None:
        raise RuntimeError("transformers is not installed. Run: pip install -r requirements.txt")
    return pipeline("text2text-generation", model=LOCAL_MODEL, tokenizer=LOCAL_MODEL)


def explain_concept(text: str) -> str:
    prompt = (
        "Explain the following educational concept in simple language for a beginner. "
        "Use a short definition, key points, and one simple example. Keep it concise.\n\n"
        f"Concept: {text}"
    )
    try:
        result = _local_pipeline()(prompt, max_new_tokens=220, do_sample=False)
        generated = result[0].get("generated_text", "").strip()
        if not generated:
            raise RuntimeError("The local explanation model returned an empty response.")
        return generated
    except Exception as exc:
        return (
            "The local explanation model is currently unavailable. "
            "Please make sure the required Hugging Face/PyTorch dependencies are installed "
            f"and the model can be downloaded. Technical detail: {exc}"
        )
