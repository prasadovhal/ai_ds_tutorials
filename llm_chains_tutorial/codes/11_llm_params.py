# Temperature
"""
Range: 0.0 to 1.0 (sometimes up to 2.0 for OpenAI).
Low (0.0 - 0.3): Factual, deterministic, repetitive. Use for Coding, Math, Data Extraction.
High (0.7 - 1.0): Creative, diverse, unpredictable. Use for Brainstorming, Poetry, Chatbots.
"""

llm_strict = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

# Max Output Tokens (Length Limit)
"""
This sets a hard limit on how much the model can write.
"""
llm = ChatOpenAI(model="gpt-4o", max_tokens=150)

# 3. Stop Sequences ( The "Kill Switch")

# Stop strictly when it tries to start a new heading
"""
You can tell the model to strictly stop generating if it hits a specific word or character.
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    stop=["\n\n", "User:"] 
)

# 4. Top_P and Top_K (Advanced Sampling)

"""
1. Top_K (Google specific): "Only consider the top K most likely next words."
    - Low K (e.g., 1): Greedy decoding (always picks the most likely word).
    - High K (e.g., 40): More variety.
2. Top_P (Nucleus Sampling): "Consider the smallest set of words whose cumulative probability is P."
    - Low P (0.1): Very conservative.
    - High P (0.9): Diverse.

"""
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    top_k=40,
    top_p=0.95
)

# 5. Timeout (The "Don't Hang" Rule)
"""
Sometimes the API hangs or is slow. You don't want your app to freeze forever.
"""
# Raise an error if the model doesn't answer within 10 seconds
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    request_timeout=10 
)

## all together

llm_sniper = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,        # No creativity allowed
    max_output_tokens=500,  # Don't write an essay
    top_p=0.8,             # Slight flexibility for grammar
    timeout=10             # Fail fast if API is slow
)