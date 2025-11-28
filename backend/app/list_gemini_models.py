import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
print("API Key gefunden:", bool(api_key))

genai.configure(api_key=api_key)

print("\nVerfügbare Modelle für deinen API-Key:\n")
for m in genai.list_models():
    print("-", m.name)
