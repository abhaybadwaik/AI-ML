from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

# Step 1 → Explanation
prompt1 = ChatPromptTemplate.from_template(
    "Explain clearly: {input}"
)

# Step 2 → Summary
prompt2 = ChatPromptTemplate.from_template(
    "Summarize this in 1 line: {text}"
)

# User input
user_input = input("Enter topic: ")

# Step 1 execution
response1 = llm.invoke(prompt1.format(input=user_input))

# Step 2 execution
response2 = llm.invoke(prompt2.format(text=response1.content))

print("Final Output:", response2.content)


# Types of Chains:
# 🔥 Multiple chains 🔥 Dynamic chains 🔥 Real-world use
# 

# Multiple chain Code👇🏾👇🏾
# Input → Explain → Simplify → Bullet Points → Final Output
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

# Step 1
prompt1 = ChatPromptTemplate.from_template(
    "Explain clearly: {input}"
)

# Step 2
prompt2 = ChatPromptTemplate.from_template(
    "Simplify this: {text}"
)

# Step 3
prompt3 = ChatPromptTemplate.from_template(
    "Convert into bullet points: {text}"
)

user_input = input("Enter topic: ")

res1 = llm.invoke(prompt1.format(input=user_input))
res2 = llm.invoke(prompt2.format(text=res1.content))
res3 = llm.invoke(prompt3.format(text=res2.content))

print("Final Output:\n", res3.content)

# 🔥 2. Dynamic Chains (SMART SYSTEM 🤯)
# 🧠 Idea
# 👉 Chain changes based on input
user_input = input("You: ")

if "explain" in user_input:
    prompt = "Explain clearly: {input}"
elif "summarize" in user_input:
    prompt = "Summarize in 1 line: {input}"
else:
    prompt = "Answer normally: {input}"

response = llm.invoke(prompt.format(input=user_input))

print(response.content)


