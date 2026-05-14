from langchain_core.prompts import PromptTemplate

# Define template with variables in curly braces
template = PromptTemplate(
    input_variables=["country"],
    template="What is the capital of {country}?"
)

# Fill the variable
filled_prompt = template.format(country="Japan")
print(filled_prompt)