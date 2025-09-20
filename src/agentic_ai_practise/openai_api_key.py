from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
  api_key=openai_key
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

def start():
    print(response.output_text)