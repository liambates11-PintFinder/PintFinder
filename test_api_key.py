import os

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GOOGLE_MAPS_API_KEY")

if api_key:
    print("API key loaded successfully.")
    print(f"Key begins with: {api_key[:6]}...")
else:
    print("API key was not found.")