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

1. create constant.py file inside code/ folder
2. add below things in it, and add your values
    a. GOOGLE_API_KEY= \n
    b. openai_key= \n
    c. huggingface_api_key= \n
    d. LANGFUSE_SECRET_KEY= \n
    e. LANGFUSE_PUBLIC_KEY= \n
    f. LANGFUSE_BASE_URL= \n

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