"""
Phase 1 · Lesson 4 — Output Parsers
Real-world scenario: TechStore complaint classifier

WHAT WE ARE TRYING TO ACHIEVE:
LLM always replies in plain text.
Output Parsers convert that plain text into formats our code can use.

StrOutputParser    → plain string (show to user)
JsonOutputParser   → dictionary (access by key)
PydanticOutputParser → Python object (access by field, type validated)

Rule:
  Just showing reply to user → StrOutputParser
  Using reply in code/DB     → PydanticOutputParser
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)

# customer complaint we will classify
complaint = "My laptop stopped working after 2 days. This is completely unacceptable!"


# ── 1. StrOutputParser ────────────────────────────────────────
# Use when: just showing reply to user, no further processing
# Output: plain string

str_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a TechStore complaint classifier. Analyze the complaint and classify it."),
    ("human", "Complaint: {complaint}"),
])

str_chain = str_prompt | llm | StrOutputParser()
str_response = str_chain.invoke({"complaint": complaint})

print("=== StrOutputParser ===")
print("Type   :", type(str_response).__name__)   # str
print("Output :", str_response)
print()
# problem → one big string, cant access sentiment or priority separately


# ── 2. JsonOutputParser ───────────────────────────────────────
# Use when: need structured data, quick scripts, no strict validation
# Output: Python dictionary, access by key

json_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a TechStore complaint classifier.
Analyze the complaint and reply ONLY in this JSON format, nothing else:
{{
    "sentiment": "positive/negative/neutral",
    "priority": "high/medium/low",
    "reason": "one line reason",
    "category": "delivery/product/service/other"
}}"""),
    ("human", "Complaint: {complaint}"),
])

json_chain = json_prompt | llm | JsonOutputParser()
json_response = json_chain.invoke({"complaint": complaint})

print("=== JsonOutputParser ===")
print("Type      :", type(json_response).__name__)   # dict
print("Full output:", json_response)
print()
# access individual fields by key
print("Sentiment :", json_response["sentiment"])
print("Priority  :", json_response["priority"])
print("Reason    :", json_response["reason"])
print("Category  :", json_response["category"])
print()
# real world usage
if json_response["priority"] == "high":
    print("⚠️  HIGH PRIORITY — sending alert to support team!")
print()


# ── 3. PydanticOutputParser ───────────────────────────────────
# Use when: production apps, saving to DB, strict type validation
# Output: proper Python object with defined fields and types

# Step 1 — define your data structure
class ComplaintAnalysis(BaseModel):
    sentiment: str = Field(description="positive, negative, or neutral")
    priority: str  = Field(description="high, medium, or low")
    reason: str    = Field(description="one line reason for the classification")
    category: str  = Field(description="delivery, product, service, or other")

# Step 2 — create parser from your class
pydantic_parser = PydanticOutputParser(pydantic_object=ComplaintAnalysis)

# Step 3 — parser gives you format instructions to add to prompt
pydantic_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a TechStore complaint classifier.
Analyze the complaint and reply in the following format:
{format_instructions}"""),
    ("human", "Complaint: {complaint}"),
])

# Step 4 — chain with pydantic parser
pydantic_chain = pydantic_prompt | llm | pydantic_parser

pydantic_response = pydantic_chain.invoke({
    "complaint": complaint,
    "format_instructions": pydantic_parser.get_format_instructions(),
})

print("=== PydanticOutputParser ===")
print("Type      :", type(pydantic_response).__name__)   # ComplaintAnalysis
print("Full output:", pydantic_response)
print()
# access like proper Python object — not dictionary!
print("Sentiment :", pydantic_response.sentiment)   # dot notation
print("Priority  :", pydantic_response.priority)
print("Reason    :", pydantic_response.reason)
print("Category  :", pydantic_response.category)
print()
# real world usage — save to database
print("=== Saving to Database ===")
print(f"db.save(sentiment='{pydantic_response.sentiment}', priority='{pydantic_response.priority}')")
print(f"db.save(reason='{pydantic_response.reason}', category='{pydantic_response.category}')")
if pydantic_response.priority == "high":
    print("⚠️  HIGH PRIORITY — triggering alert system!")
print()


# ── Summary ───────────────────────────────────────────────────
print("""
=== When to use which parser ===
StrOutputParser     → just showing text to user, conversational bots, RAG apps
JsonOutputParser    → quick scripts, need dict access, no strict validation needed
PydanticOutputParser→ production apps, saving to DB, APIs, strict type validation

Key difference JsonOutputParser vs PydanticOutputParser:
  json_response["sentiment"]    → dictionary, key access, no validation
  pydantic_response.sentiment   → object, dot access, type validated
""")