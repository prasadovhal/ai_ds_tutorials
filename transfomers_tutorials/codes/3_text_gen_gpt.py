from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

input_text = "Artificial intelligence will"

inputs = tokenizer(input_text, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_length=50,
    temperature=0.7,
    top_k=50
)

new_text = tokenizer.decode(outputs[0], skip_special_tokens=True)