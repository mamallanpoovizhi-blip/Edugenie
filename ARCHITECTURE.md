# EduGenie Architecture

```text
Browser (HTML/CSS/JS)
        |
        | POST /task or module endpoint
        v
FastAPI (main.py)
        |
        +--> qna.py --------------------+
        +--> summary_module.py ---------+--> ai_client.py --> Google Gemini API
        +--> quiz_module.py ------------+
        +--> learning_path.py ----------+
        |
        +--> explanation_module.py --> LaMini-Flan-T5-783M (local)
```

The frontend is intentionally lightweight and uses server-rendered Jinja HTML plus static CSS/JavaScript. The backend keeps AI integration outside route functions. Structured output is used for quizzes, and the generated quiz is validated with Pydantic before being returned.
