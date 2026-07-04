# AI-Powered Personal Finance Assistant — Standalone Chatbot (Phase 1)

This version has **no dependency on Claude, OpenAI, or any external AI API**.
It runs entirely on your own machine/server, with no API key and no internet
connection required at runtime.

## How the "AI" works here

The NLP is handled by **rule-based intent classification** in `nlp_engine.py`:
1. The user's message is scored against keyword sets for each intent
   (spending questions, budget questions, savings questions, etc.).
2. The highest-scoring intent wins; category names (e.g. "groceries") are
   detected by direct matching against your known categories.
3. The matched intent calls the relevant function in `finance_data.py` and
   fills a natural-language template with the real numbers.

This is a legitimate, widely-used pattern for a bounded domain like personal
finance, where the space of things a user can ask is well-defined — it's how
many production banking chatbots work before (or instead of) reaching for a
large language model. It's deterministic, free to run, instant (no network
round trip), and fully auditable.

**Trade-off vs. an LLM-based chatbot:** it only understands questions that
match its known intents/keywords — it won't handle totally novel phrasing or
open-ended reasoning. If you outgrow it later, you can swap `classify_intent()`
in `nlp_engine.py` for a trained scikit-learn/spaCy classifier without
changing `main.py` at all.

## Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

No API key, no environment variables needed. Then open `frontend/index.html`
directly in your browser.

Sanity check: visit `http://localhost:8000/health` — should show `{"status":"ok"}`.

## Try asking

- "How much have I spent on groceries?"
- "Am I over budget anywhere?"
- "What's my net savings this month?"
- "Where do I spend the most?"
- "What can you do?"

## Project layout

```
finance-assistant-standalone/
  backend/
    main.py            # FastAPI app + /chat endpoint (no external API calls)
    nlp_engine.py        # Rule-based intent classification + response generation
    finance_data.py     # Mock transactions/budgets — replace with real DB in Phase 2
    requirements.txt
  frontend/
    index.html          # Minimal chat UI (vanilla JS, no framework needed)
```

## Deploying to get a shareable public link

The backend now serves the frontend directly (visiting `/` returns the chat
page), so deploying this gives you **one URL** that works on any PC, without
your own computer needing to stay on.

### Deploy on Render (free tier, no credit card)

1. Push this folder to a GitHub repo (Render deploys from GitHub).
   ```bash
   git init
   git add .
   git commit -m "Finance assistant standalone"
   ```
   Create a new repo on github.com, then follow its "push an existing
   repository" instructions to push this code there.
2. Go to **render.com** → sign up (free) → **New +** → **Web Service**.
3. Connect your GitHub repo.
4. Set:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Click **Create Web Service**. After a couple of minutes you'll get a URL
   like `https://finance-assistant-xxxx.onrender.com` — that's your
   shareable link. Open it on any PC; the chat page loads directly.

**Free-tier note:** Render's free web services "sleep" after 15 minutes of
inactivity and take ~30–50 seconds to wake up on the next request — that's
normal, not a bug. Fine for demos and sharing with others to try.

### Alternative: Railway
Same idea — railway.app → New Project → Deploy from GitHub repo → set
Root Directory to `backend` and Start Command to
`uvicorn main:app --host 0.0.0.0 --port $PORT`.

## Extending the intents

To add a new kind of question, open `nlp_engine.py` and:
1. Add a new intent name + its keyword list to `INTENT_KEYWORDS`.
2. Add a matching `elif intent == "your_new_intent":` branch in `handle_message()`
   that calls a function from `finance_data.py` and builds the reply text.

## Roadmap — next phases (same as the full plan)

- **Phase 2** — Real database (PostgreSQL) replacing the mock data, manual
  transaction entry, auto budget generation.
- **Phase 3** — Bank account integration (e.g. Plaid) to replace mock data
  with real transactions.
- **Phase 4** — Savings recommendations + "what-if" projections (add a new
  intent + calculation function).
- **Phase 5** — Weekly/monthly PDF and Excel report generation.
- **Phase 6** — Auth/MFA, encryption at rest, RBAC, and scaling for
  production traffic.
