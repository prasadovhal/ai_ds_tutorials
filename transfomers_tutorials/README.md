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
    a. GOOGLE_API_KEY=
    b. openai_key=
    c. huggingface_api_key=
    d. LANGFUSE_SECRET_KEY=
    e. LANGFUSE_PUBLIC_KEY=
    f. LANGFUSE_BASE_URL=