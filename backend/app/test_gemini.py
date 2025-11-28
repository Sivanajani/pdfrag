import os
import google.generativeai as genai

print("GOOGLE_API_KEY gesetzt?", bool(os.getenv("GOOGLE_API_KEY")))

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")

resp = model.generate_content("Sag mir kurz, ob du funktionierst.")
print(resp.text)
