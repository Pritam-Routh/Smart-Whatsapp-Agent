import os
from langchain.chat_models import init_chat_model

apiKey = "AIzaSyBV4R1Kc32LplWEyzRpq0_d0WLOmrKA2fU"


model = init_chat_model("google_genai:gemini-2.5-flash-lite", api_key = "AIzaSyBV4R1Kc32LplWEyzRpq0_d0WLOmrKA2fU")
# model = api_key(apiKey)

for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="|", flush=True)