# Human-in-the-Loop Payment System
A banking payment workflow built with LangGraph that pauses high-risk transactions for human approval.

## Prerequisites
- Python 3.12+
- Docker
- uv (package manager)

## Setup

### 1. Install dependencies
uv sync
## Install uv (if not installed)
pip install uv

### 2. Start Postgres with Docker
docker run --name langgraph-pg -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=langgraph -p 5432:5432 -d postgres:15

## How to Run

### Step 1 — Submit a payment
uv run python submit_payment.py
(Enter amount when asked. If amount > 1,00,000 it will pause for human review)

### Step 2 — Check status of all transactions
uv run python check_status.py

### Step 3 — Approve or reject pending transactions
uv run python approve_payment.py
(Shows pending transactions, ask you to pick one and enter decision)

## Flow
- Amount <= 1,00,000 → Auto approved, no human needed
- Amount > 1,00,000 → Paused, saved to Postgres, waits for human decision
- Human decision can be made hours or days later, state is preserved in database




to check database in TABLE FORM
docker exec -it langgraph-pg psql -U postgres -d langgraph -c "SELECT thread_id, checkpoint->'channel_values'->>'amount' AS amount, checkpoint->'channel_values'->>'risk_score' AS risk_score, checkpoint->'channel_values'->>'status' AS status, checkpoint->'channel_values'->>'human_decision' AS decision FROM checkpoints WHERE checkpoint->'channel_values'->>'status' IN ('completed','declined') ORDER BY thread_id;"cls