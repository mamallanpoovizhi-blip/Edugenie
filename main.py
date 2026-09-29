from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_concept
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie",
    version="1.0.0",
    description="Google Gemini powered learning assistant",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000)


class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1, max_length=20000)


TASK_NAMES = {"qa", "explain", "quiz", "summarize", "recommend"}


def _run_task(task_name: str, text: str):
    handlers = {
        "qa": lambda: answer_question(text),
        "explain": lambda: explain_concept(text),
        "quiz": lambda: generate_quiz(text),
        "summarize": lambda: summarize_text(text),
        "recommend": lambda: get_learning_recommendations(text),
    }

    if task_name not in handlers:
        raise ValueError(f"Unsupported task: {task_name}")

    return handlers[task_name]()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request. Please provide the required text/question.",
            "errors": exc.errors(),
        },
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "EduGenie"}


@app.post("/qa")
async def qa(payload: QARequest):
    try:
        return {"result": answer_question(payload.question)}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to answer the question right now."},
        )


@app.post("/explain")
async def explain(payload: TextRequest):
    try:
        return {"result": explain_concept(payload.text)}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to explain the concept right now."},
        )


@app.post("/quiz")
async def quiz(payload: TextRequest):
    try:
        return {"result": generate_quiz(payload.text)}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to generate the quiz right now."},
        )


@app.post("/summarize")
async def summarize(payload: TextRequest):
    try:
        return {"result": summarize_text(payload.text)}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to summarize the passage right now."},
        )


@app.post("/learn/recommendations")
async def learn(payload: TextRequest):
    try:
        return {"result": get_learning_recommendations(payload.text)}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"detail": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Unable to create the learning path right now."},
        )


@app.post("/task")
async def task(payload: TaskRequest):
    """Unified endpoint used by the browser UI.

    Every expected failure is returned as JSON so the frontend never attempts to
    parse a plain-text 'Internal Server Error' as JSON.
    """
    if payload.task not in TASK_NAMES:
        return JSONResponse(
            status_code=400,
            content={
                "task": payload.task,
                "detail": "Unsupported task. Choose qa, explain, quiz, summarize, or recommend.",
            },
        )

    try:
        result = _run_task(payload.task, payload.text)
        return {"task": payload.task, "result": result}
    except RuntimeError as exc:
        print(f"EduGenie service error [{payload.task}]: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "task": payload.task,
                "detail": str(exc),
            },
        )
    except Exception as exc:
        print(f"EduGenie unexpected error [{payload.task}]: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "task": payload.task,
                "detail": "An unexpected server error occurred. Please try again.",
            },
        )
