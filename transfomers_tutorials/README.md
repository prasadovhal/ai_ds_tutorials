# transfomers_tutorials
Understanding transformers architecture from basic to advance hands-on with python


## Set up Python & Poetry

1. cd transformers_tutorial
2. install poetry
`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
3. run `C:\Users\user_name\AppData\Roaming\Python\Scripts`
4. check poetry version `poetry --version`
5. set `poetry config virtualenvs.in-project true`
6. run `poetry install`
7. set venv 
    for windows `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
    for linux/mac `source .venv/bin/activate`


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

1. basic transformer pipeline use
2. load a specific model from huggingface
3. how to use it for text generation
4. fine tune full model
5. fine tune full model with torch custom parameters
6. PEFT - LoRA, QLoRA
7. Model representation - ONNX, GGUF
8. Quantization 
9. encodings