from typing import List
from pydantic import BaseModel, Field, field_validator

from ai_client import generate_structured


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str

    @field_validator("correct_answer")
    @classmethod
    def answer_must_be_an_option(cls, value: str, info):
        options = info.data.get("options", [])
        if options and value not in options:
            raise ValueError("correct_answer must match one of the options")
        return value


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(min_length=3, max_length=3)


def clean_json_block(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def generate_quiz(passage: str) -> dict:
    prompt = (
        "Create exactly three multiple-choice questions from the passage below. "
        "Each question must have exactly four plausible options. The correct_answer must be "
        "the exact text of one option. Focus only on information supported by the passage. "
        "Return JSON matching the requested schema.\n\n"
        f"Passage:\n{passage}"
    )
    raw = generate_structured(prompt, QuizResponse.model_json_schema(), temperature=0.2, max_output_tokens=1800)
    cleaned = clean_json_block(raw)
    try:
        quiz = QuizResponse.model_validate_json(cleaned)
    except Exception as exc:
        raise RuntimeError(f"Quiz response could not be parsed or validated: {exc}") from exc
    return quiz.model_dump()
