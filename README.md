🤖 AI-ML
A hands-on collection of projects exploring LangChain, LangGraph, and LangFuse — building intelligent, observable, and production-ready AI workflows.

📁 Project Structure
AI-ML/
├── LangChain/          # LLM chains, prompts, and app logic
├── LangGraph/          # Graph-based decision making & loops
└── LangFuse Testing/   # LLM observability & tracing
🚀 Projects
🔗 LangChain
Building LLM-powered applications using chains, prompt templates, and modular components.

🕸️ LangGraph
Implementing stateful, graph-based AI workflows — including decision-making pipelines and loop handling.

📊 LangFuse Testing
Integrating LangFuse for tracing, monitoring, and evaluating LLM calls in real-time.

⚙️ Setup
Clone the repository

git clone https://github.com/abhaybadwaik/AI-ML.git
cd AI-ML
Install dependencies

pip install -r requirements.txt
Configure environment variables

cp .env.example .env
# Add your API keys in the .env file
🔑 Environment Variables
Each project uses a .env file. Required keys may include:

Variable	Description
GROQ_API_KEY	Groq LLM API Key
LANGFUSE_PUBLIC_KEY	LangFuse public key
LANGFUSE_SECRET_KEY	LangFuse secret key
⚠️ Never commit your .env files. They are excluded via .gitignore.

🛠️ Tech Stack
Python LangChain LangGraph LangFuse Groq

👤 Author
Abhay Badwaik
GitHub

⭐ If you find this helpful, consider giving it a star!
