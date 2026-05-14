# Day 2 — Prompts & Chains

## What is the concept?
**Prompts** are structured templates that tell the LLM exactly how to respond.  
**Chains** are pipelines that connect Prompt → LLM → Output Parser in a single flow using the `|` (pipe) operator.

---

## Why do we use it?
- Raw prompts are messy strings — templates make them reusable and dynamic
- Chains remove boilerplate code; you describe the flow once and invoke it cleanly
- Sequential chains allow multi-step AI workflows (generate → translate → summarize)

---

## Part 1: PromptTemplate

### What it is
A simple fill-in-the-blank template for single text inputs.

### Real-Life Use Case
Auto-generating questions, emails, or reports where only one variable changes.

### From your code (`PromptTemplate.py`)
```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["country"],
    template="What is the capital of {country}?"
)

filled_prompt = template.format(country="Japan")
print(filled_prompt)
# Output: "What is the capital of Japan?"
```

---

## Part 2: ChatPromptTemplate

### What it is
A template for chat-based models that supports System + Human messages with multiple variables.

### Real-Life Use Case
Building role-based assistants (doctor bot, HR bot, tutor) that respond in specific styles.

### From your code (`ChatPromptTemplate.py`)
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chat = ChatGroq(model="llama-3.1-8b-instant", api_key="...")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {role}. Always answer in {language}."),
    ("human", "{question}")
])

chain = prompt | chat

response = chain.invoke({
    "role": "Doctor",
    "language": "English",
    "question": "What causes fever?"
})
print(response.content)
```

---

## Part 3: Basic Chain

### What it is
Prompt → LLM → Parser linked with `|`. The `StrOutputParser` converts the `AIMessage` object into a plain Python string.

### From your code (`Chain/Basic-Chain.py`)
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

chat = ChatGroq(model="llama-3.1-8b-instant", api_key="...")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Tell me one interesting fact about {topic}.")
])
parser = StrOutputParser()

# Chain: prompt → model → parser
chain = prompt | chat | parser

response = chain.invoke({"topic": "black holes"})
print(response)        # plain string, not AIMessage object
print(type(response))  # <class 'str'>
```

---

## Part 4: Sequential Chain

### What it is
Multiple chains connected in sequence — the output of one becomes the input of the next.

### Real-Life Use Case
Content pipeline: Generate blog draft → Translate to another language → Summarize in one line.

### From your code (`Chain/Sequential-Chain.py`)
```python
# Step 1 → Generate story
story_chain = story_prompt | chat | parser

# Step 2 → Translate to French
translate_chain = translate_prompt | chat | parser

# Step 3 → Summarize
summary_chain = summary_prompt | chat | parser

# Run step by step
story     = story_chain.invoke({"topic": "a lost dog finding its way home"})
translated = translate_chain.invoke({"story": story})
summary    = summary_chain.invoke({"translated_story": translated})
```

---

## Part 5: Zero-Shot vs Few-Shot Prompting

### Zero-Shot
No examples given — just give instructions and ask directly.

### Few-Shot
Give 2-3 examples first so the AI learns the exact format you want.

### From your code (`Types/Zero-Shot.py`)
```python
# Zero-Shot: no examples, direct instruction
zero_shot_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify sentiment as Positive, Negative, or Neutral only."),
    ("human", "{text}")
])
```

### From your code (`Types/Few-Shot.py`)
```python
examples = [
    {"input": "I love this product!", "output": "Positive"},
    {"input": "Worst experience ever.", "output": "Negative"},
    {"input": "The product is fine but delivery was late.", "output": "Mixed"}
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)
```

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `PromptTemplate` | Simple string template with `{variables}` |
| `ChatPromptTemplate` | Template for system + human messages |
| `FewShotChatMessagePromptTemplate` | Template with pre-loaded examples |
| `StrOutputParser` | Converts `AIMessage` → plain `str` |
| `|` pipe operator | LCEL (LangChain Expression Language) — chains steps |
| `chain.invoke()` | Run the chain with input data |
| `Zero-Shot` | AI guesses with no examples |
| `Few-Shot` | AI learns pattern from given examples |

---

## Beginner-Friendly Summary
- **PromptTemplate** = Mad Libs game — you fill in the blanks
- **ChatPromptTemplate** = Full chat script with System instructions + Human question
- **Chain** = Assembly line: raw input → formatted prompt → AI brain → clean output
- **Sequential Chain** = Conveyor belt: Step 1 → Step 2 → Step 3, each using previous output
- **Zero-Shot** = Ask without examples (like asking a stranger)
- **Few-Shot** = Show examples first, then ask (like training an intern)
