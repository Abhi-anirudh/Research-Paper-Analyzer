import sys
import os
import json
import traceback
sys.path.append(os.path.dirname(__file__))

from app.generation.llm import generate

res = {}

try:
    print("Testing Groq...")
    groq_ans = generate("You are a bot.", "Hello", model_name="groq/llama-3.1-8b-instant")
    res["groq"] = groq_ans
except Exception as e:
    res["groq_err"] = str(e)

try:
    print("Testing Gemini...")
    gemini_ans = generate("You are a bot.", "Hello", model_name="gemini/gemini-2.0-flash")
    res["gemini"] = gemini_ans
except Exception as e:
    res["gemini_err"] = str(e)

with open("llm_results.json", "w") as f:
    json.dump(res, f, indent=2)
