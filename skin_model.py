import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


def predict_skin_disease(image_path):

    with open(image_path, "rb") as f:
        data = f.read()

    response = requests.post(
        API_URL,
        headers=headers,
        data=data
    )

    return response.json()