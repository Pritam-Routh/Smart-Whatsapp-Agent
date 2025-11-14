# Smart-Whatsapp-Agent

A lightweight chatbot interface that uses Google's GenAI (Gemini) via LangChain adapters to analyze incoming WhatsApp-style customer messages, identify intent (stock queries, dispatch, payment updates, complaints), consult local warehouse records for stock lookups, and generate suggested replies.

**Key features**
- Streamlit-based chat UI (`streamlit_app.py`) for live messaging.
- Single-message analysis function (`agent.agent_v0.analyze_message`) that returns intent, identified item, and a suggested reply.
- Warehouse-aware stock lookup using `inputs/warehouse_records.json`.
- Auto-save of conversations to `streamlit_output.json` (and manual save to `output.json`).
- API key loading from `.env` or environment variables with a fallback to a hardcoded key (see `agent/agent_v0.py`).

**Files of interest**
- `streamlit_app.py` — Streamlit chat UI (run with `streamlit run streamlit_app.py`).
- `agent/agent_v0.py` — Core logic: LLM integration, `analyze_message`, `process_messages`, and warehouse helpers.
- `app.py` — Batch processing entrypoint that runs `process_messages` against `inputs/messages.json` and writes `output.json`.
- `inputs/warehouse_records.json` — Warehouse data used for stock lookups.
- `streamlit_output.json` — Auto-saved conversation output (created by the Streamlit UI).
- `requirements.txt` — Python dependencies for the workspace.

Libraries used
- `streamlit` — Web UI.
- `langchain` and LangChain Google GenAI adapters — LLM client integration.
- `google-genai` / `google-ai-generativelanguage` — Google GenAI SDK (used in some helper modules).
- `python-dotenv` — Optional `.env` loader for API keys.
- `pydantic` — Schema validation for structured LLM output.

Setup
1. Create a virtual environment and install dependencies (recommended):

```bash
# create venv
python3 -m venv core
# activate (bash)
source core/bin/activate
# install requirements
pip install --upgrade pip
pip install -r requirements.txt
```


```bash
/workspaces/Smart-Whatsapp-Agent/core/bin/python -m pip install -r requirements.txt
```

2. Provide your Google GenAI API key via one of the following methods:
- Create a `.env` file in the project root with:

```text
GOOGLE_API_KEY=your_real_api_key_here
```

- Or export it in your shell before running the app:

```bash
export GOOGLE_API_KEY="your_real_api_key_here"
```

3. Run the Streamlit UI (development):

```bash
streamlit run streamlit_app.py
```

Batch processing (run `app.py`)
- `app.py` is a lightweight entrypoint that calls `agent.agent_v0.process_messages`. It reads messages from `inputs/messages.json` and writes analysis results to `output.json`.

Example:

```bash
# using the active venv
python app.py

# or using the workspace core python
/workspaces/Smart-Whatsapp-Agent/core/bin/python app.py
```

Usage
- Streamlit UI: Open the local URL printed by Streamlit (usually `http://localhost:8501`). Enter a `Sender name` and a message in the chat form. The agent replies with a suggested reply and (for stock queries) appends warehouse stock information.
- Batch: Place messages in `inputs/messages.json` (array of objects with `sender` and `text` fields), then run `python app.py`. Results are saved to `output.json`.

Auto-save
- Streamlit UI auto-saves exchanges to `streamlit_output.json` in the repo root. The manual "Save conversation" button writes to `output.json`.



Improvements & Next Features

- Use a database for warehouse and user data: move `inputs/warehouse_records.json` into a managed database (PostgreSQL, MySQL, or a cloud DB). This enables real-time updates, indexing, and joins with product metadata.
- MCP / API server: add a small MCP (Model Context Protocol) or API server to serve warehouse data and user-specific data (product purchase history, credit limits, preferences). The Streamlit UI or any client can query the MCP for fresh stock counts before calling the LLM.
- User profile & product history: store each customer's purchase history and preferences, so replies can be personalized (e.g., suggest frequently-ordered variants or preferred warehouses).
- Tooling for actions (orders/payments): create secure server-side tools/endpoints the assistant can call for non-LLM actions:
	- `place_order(customer_id, product_id, qty, warehouse_id)` — returns order id / confirmation.
	- `check_payment_status(invoice_id)` — returns payment/ledger status.
	- `raise_support_ticket(order_id, issue)` — creates a ticket and returns tracking id.
	These tools should be implemented as authenticated endpoints and invoked by the backend (not directly by the LLM) to avoid exposing credentials.
- Event logging & observability: log all model inputs/outputs (with PII redaction) and tool calls for auditing and troubleshooting.
- Granular permissions and auditing: require service credentials for any order/payment tool and keep detailed audit trails.
- Caching and rate-limiting: cache frequent stock queries and apply rate-limits to avoid DB/API overload when serving many concurrent users.

Security & architecture notes
- Use signed, time-limited tokens for any assistant-to-tool calls and validate on the server side.
- Sanitize and validate all user inputs before passing them to tools or the database.

Questions or changes? Tell me which additional features you'd like and I can implement them next.
