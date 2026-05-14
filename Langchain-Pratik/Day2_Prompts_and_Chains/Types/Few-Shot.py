# ---- FEW SHOT ----
# Give examples to show exact format you want
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import FewShotChatMessagePromptTemplate
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)


# Define your examples
examples = [
    {
        "input": "I love this product! It works perfectly.",
        "output": "Positive"
    },
    {
        "input": "Worst experience ever. Total waste of money.",
        "output": "Negative"
    },
    {
        "input": "The product is fine but delivery was late.",
        "output": "Mixed"
    }
]

# Template for each example
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

# Few-shot prompt combining all examples
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)

# Final prompt with system + few shot examples + actual question
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the sentiment. Reply with only one word: Positive, Negative, or Mixed."),
    few_shot_prompt,
    ("human", "{text}")
])

chain = final_prompt | chat

response = chain.invoke({"text": "we given one task to employee he has complete as expected but communication was not upto point"})
print("Few-Shot Output:", response.content)