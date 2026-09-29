# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational assistant specified around five learning tasks: Q&A, simplified concept explanation, quiz generation, summarization, and personalized learning recommendations.

## Specification alignment

The project follows the attached EduGenie specification. The original document names Gemini 1.5 Pro for Q&A, summarization, quizzes, and learning paths, and LaMini-Flan-T5-783M locally for concept explanation. Gemini 1.5 Pro is no longer a current supported Gemini API model, so this implementation uses the current configurable `GEMINI_MODEL` default (`gemini-3.8-flash`) while preserving the requested Gemini-powered workflow. Change the value in `.env` if your Google AI account exposes another supported model.

## Project structure

```text
EduGenie/
├── main.py
├── ai_client.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_app.py
```

## Requirements

- Python 3.10+
- Google Gemini API key
- Internet access for Gemini API and first-time Hugging Face model download
- CPU/GPU compatible PyTorch installation

## Local setup

### Windows PowerShell

```powershell
cd EduGenie
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder `GEMINI_API_KEY` with your own key.

### macOS/Linux

```bash
cd EduGenie
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`.

## Run

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

## API routes

- `GET /` — web application
- `GET /health` — health check
- `POST /qa` — question answering; body `{ "question": "..." }`
- `POST /explain` — local concept explanation; body `{ "text": "..." }`
- `POST /quiz` — three-MCQ generation; body `{ "text": "..." }`
- `POST /summarize` — summarization; body `{ "text": "..." }`
- `POST /learn/recommendations` — learning path; body `{ "text": "..." }`
- `POST /task` — frontend unified task endpoint; body `{ "task": "qa|explain|quiz|summarize|recommend", "text": "..." }`

## Testing

Run the automated API/UI integration tests:

```bash
pytest -q
```

The test suite verifies application startup, frontend loading, health status, route validation, and each major backend endpoint using mocked AI functions. This prevents tests from requiring a real API key or downloading the local model.

For end-to-end testing with real AI services, configure `.env`, start the server, and manually test:

1. Ask a factual question using QnA.
2. Request a beginner-friendly explanation.
3. Paste an educational passage and generate exactly three MCQs.
4. Summarize a long paragraph.
5. Request a beginner-to-advanced learning path.
6. Use Download on each result.
7. Try empty input and unsupported tasks to verify validation/error handling.

## Deployment preparation

Use a production ASGI server setup appropriate to your host. Set environment variables through the hosting platform's secret/environment-variable system rather than committing `.env`. For the local model, ensure the deployment environment has enough memory for the LaMini-Flan-T5-783M weights or adapt the model configuration to a compatible hosted/local inference option.

## Security notes

- Never commit `.env` or real API keys.
- The browser never receives the Gemini key; AI requests are made by the FastAPI backend.
- User input is length-limited with Pydantic validation.
- Quiz responses use structured JSON output plus Pydantic validation.

## Gemini temporary 503/429 handling

EduGenie retries temporary Gemini service/capacity errors and can automatically try configured fallback models. If all configured models are temporarily unavailable, the API returns a JSON error with HTTP 503 instead of the generic plain-text `Internal Server Error` response. The browser UI displays that message directly.

If Gemini is unavailable for an extended period, wait a short time and try again. Verify that `.env` contains a valid `GEMINI_API_KEY` and a supported `GEMINI_MODEL`.
