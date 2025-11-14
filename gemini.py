from google import genai

client = genai.Client(api_key="AIzaSyBV4R1Kc32LplWEyzRpq0_d0WLOmrKA2fU")

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="what is todays date",
)

print(response.text)