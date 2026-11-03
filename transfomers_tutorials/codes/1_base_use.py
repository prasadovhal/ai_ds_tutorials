from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("Transformers are incredibly powerful!")
print(result)


"""
#Under the hood:

1. Loads tokenizer
2. Loads model
3. Handles preprocessing
4. Applies softmax

"""

"""
Other Pipeline Tasks
- pipeline("text-generation")
- pipeline("question-answering")
- pipeline("summarization")
- pipeline("translation")
- pipeline("ner")

"""