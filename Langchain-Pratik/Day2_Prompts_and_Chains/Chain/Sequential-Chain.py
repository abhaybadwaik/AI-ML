from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

parser = StrOutputParser()

# Step 1 — Generate story
story_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a creative story writer."),
    ("human", "Write a very short story (3-4 lines) about {topic}.")
])

# Step 2 — Translate to Hindi
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a translator."),
    ("human", "Translate this to french:\n\n{story}")
])

# Step 3 — Summarize
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a summarizer."),
    ("human", "Summarize this in one single line:\n\n{translated_story}")
])

# Build each sub-chain
story_chain = story_prompt | chat | parser
translate_chain = translate_prompt | chat | parser
summary_chain = summary_prompt | chat | parser

# Connect all three — output of each goes to next automatically
full_chain = (
    story_chain
    | (lambda story: {"story": story})
    | translate_chain
    | (lambda translated: {"translated_story": translated})
    | summary_chain
)

topic = "a lost dog finding its way home"

# Step 1
story = story_chain.invoke({"topic": topic})
print("=== STEP 1 - Story ===")
print(story)
print()

# Step 2
translated = translate_chain.invoke({"story": story})
print("=== STEP 2 - Translated ===")
print(translated)
print()

# Step 3
summary = summary_chain.invoke({"translated_story": translated})
print("=== STEP 3 - Summary ===")
print(summary)

# Run it
final_output = full_chain.invoke({"topic": "a lost dog finding its way home"})
# print("Final Summary:", final_output)