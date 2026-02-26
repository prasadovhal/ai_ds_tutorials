# llm_chains_tutorial
LLM chains &amp; Basic prompt engineering tutorial


## Set up Python & Poetry

1. cd transformers_tutorial
2. install poetry
`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
3. run `C:\Users\user_name\AppData\Roaming\Python\Scripts`
4. check poetry version `poetry --version`
5. set `poetry config virtualenvs.in-project true`
6. run `poetry install`
7. set venv 
   - for windows `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
   - for linux/mac `source .venv/bin/activate`

## changes you need to make

1. Create `constant.py` file inside `codes/` folder.
2. Add the following keys inside it:
   - `GOOGLE_API_KEY = "your_google_api_key"`
   - `OPENAI_KEY = "your_openai_key"`
   - `HUGGINGFACE_API_KEY = "your_huggingface_api_key"`
   - `LANGFUSE_SECRET_KEY = "your_langfuse_secret_key"`
   - `LANGFUSE_PUBLIC_KEY = "your_langfuse_public_key"`
   - `LANGFUSE_BASE_URL = "https://cloud.langfuse.com"`

## What it includes

1. Check gemini models
2. Zero shot learning prompt
3. Few shot learning prompt
4. Chain of thoughts prompting
5. Create your first chain
6. Create a sequential chain
7. Create a router chain
7. Access memory for past chats
8. How to get structured output from LLM
9. How to debug
10. Using ChatGPT/any other LLM instead of Gemini
11. LLM parameters
12. LLM cache
13. Token count and costing
14. using async (mainly used for apps/apis)
15. apps