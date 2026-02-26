import os
from constant import GOOGLE_API_KEY
import google.generativeai as genai

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


print("Available Models:")
for m in genai.list_models():
    # Only show models that support text generation
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")
