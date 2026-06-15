import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HF_TOKEN")

print("Token loaded:", API_TOKEN[:10] + "...")
