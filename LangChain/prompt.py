from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

prompt_template = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Explain clearly: {input}"
    "You are a strict teacher. Explain in bullet points: {input}"
)

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    prompt = prompt_template.format(input=user_input)

    response = llm.invoke(prompt)

    print("AI:", response.content)