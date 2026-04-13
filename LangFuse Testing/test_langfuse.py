from dotenv import load_dotenv
load_dotenv()

from langfuse import observe, Langfuse

langfuse = Langfuse()

print("Auth check:", langfuse.auth_check())

@observe()
def test_trace():
    return "connection successful"

result = test_trace()
langfuse.flush()

print("Result:", result)
print("Done. Check http://localhost:3000 → Traces tab")