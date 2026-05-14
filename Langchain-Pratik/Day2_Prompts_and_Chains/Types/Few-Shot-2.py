from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotChatMessagePromptTemplate
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)


examples = [
    {
        "input": "apple",
        "output": "Fruit | Red or Green | Sweet | Used in pies"
    },
    {
        "input": "carrot",
        "output": "Vegetable | Orange | Crunchy | Used in salads"
    }
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Give info about the item in this exact format: Category | Color | Texture | Common Use"),
    few_shot_prompt,
    ("human", "{text}")
])

chain = final_prompt | chat
response = chain.invoke({"text": "banana"})
print(response.content)



