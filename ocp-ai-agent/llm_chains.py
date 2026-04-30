import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from rag import initialize_rag, find_similar_incidents

# ─────────────────────────────────────────────
# Initialize RAG once at startup
# ─────────────────────────────────────────────
print("Initializing RAG pipeline...")
rag_query_engine = initialize_rag()

# ─────────────────────────────────────────────
# Initialize Groq LLM
# ─────────────────────────────────────────────
llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.llm_model,
    temperature=0,
    max_tokens=2048,
)

# ─────────────────────────────────────────────
# Chain 1: Analysis Chain
# Raw cluster data → failures list + summary
# ─────────────────────────────────────────────
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior OpenShift SRE expert.
You will receive a snapshot of a live OpenShift cluster.
Analyze it and return ONLY a JSON object with this exact structure:

{{
  "failures": [
    {{
      "id": "unique-id",
      "component": "component name",
      "severity": "CRITICAL or WARNING or INFO",
      "message": "clear description of the issue"
    }}
  ],
  "summary": "one paragraph summary of overall cluster health"
}}

Rules:
- If everything is healthy return {{"failures": [], "summary": "All systems healthy."}}
- severity CRITICAL = immediate action needed
- severity WARNING = needs attention soon
- severity INFO = informational only
- Return ONLY the JSON, no extra text, no markdown
"""),
    ("user", "Analyze this cluster snapshot:\n{snapshot}")
])

analysis_chain = analysis_prompt | llm


# ─────────────────────────────────────────────
# Analysis Function
# ─────────────────────────────────────────────
def run_analysis(state: dict) -> tuple:
    """Run LLM analysis enriched with RAG past incidents."""
    print("\n  [LLM] Analyzing cluster data with Groq...")

    snapshot = json.dumps({
        "nodes": state.get("nodes", []),
        "operators": state.get("operators", []),
        "mcpools": state.get("mcpools", []),
        "etcd": state.get("etcd", {}),
        "pvcs": state.get("pvcs", []),
        "pods": state.get("pods", []),
        "certs": [
            c for c in state.get("certs", [])
            if c.get("days_remaining", 999) < 30
        ],
        "collection_errors": state.get("collection_errors", []),
    }, indent=2)

    # ── RAG: find similar past incidents ──
    print("  [RAG] Searching past incidents...")
    past_incidents = find_similar_incidents(
        f"Cluster issues: {snapshot[:500]}",
        rag_query_engine
    )
    print("  [RAG] Found relevant past incidents")

    # ── Enrich prompt with RAG context ──
    enriched_snapshot = f"""
CURRENT CLUSTER STATE:
{snapshot}

SIMILAR PAST INCIDENTS (from historical records):
{past_incidents}

Use the past incidents as additional context to improve your analysis.
"""

    response = analysis_chain.invoke({"snapshot": enriched_snapshot})

    # Clean response
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    result = json.loads(content)
    failures = result.get("failures", [])
    summary = result.get("summary", "Analysis complete.")

    print(f"  [LLM] Found {len(failures)} failure(s)")
    print(f"  [LLM] Summary: {summary[:100]}...")

    return failures, summary


# ─────────────────────────────────────────────
# Chain 2: Resolution Chain
# Failures → root cause + oc remediation steps
# ─────────────────────────────────────────────
resolution_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior OpenShift SRE expert.
You will receive a list of cluster failures.
For each failure provide remediation steps and return ONLY a JSON array:

[
  {{
    "failure_id": "same id as input",
    "root_cause": "explanation of why this happened",
    "steps": [
      "Step 1: description",
      "Step 2: description"
    ],
    "commands": [
      "oc get pods -n <namespace>",
      "oc describe pod <pod-name> -n <namespace>"
    ],
    "docs_ref": "https://docs.openshift.com/relevant-page"
  }}
]

Rules:
- Return ONLY the JSON array, no extra text, no markdown
- commands must be real, runnable oc commands
- steps must be clear and actionable
"""),
    ("user", "Generate remediation for these failures:\n{failures}")
])

resolution_chain = resolution_prompt | llm


# ─────────────────────────────────────────────
# Resolution Function
# ─────────────────────────────────────────────
def run_resolution(failures: list) -> list:
    """Run LLM resolution chain on failures. Returns list of remediation plans."""
    print("\n  [LLM] Generating remediation steps with Groq...")

    response = resolution_chain.invoke({
        "failures": json.dumps(failures, indent=2)
    })

    # Clean response
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    resolutions = json.loads(content)
    print(f"  [LLM] Generated {len(resolutions)} remediation plan(s)")
    return resolutions