import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load model
model = genai.GenerativeModel("models/gemini-2.5-flash")


def ask_gemini(symptoms):

    prompt = f"""
    You are an AI Medical Assistant.

    The patient reports:
    {symptoms}

    Provide your response in this format:

    🩺 Possible Condition:
    ...

   💊 Precautions:
   - ...
   - ...

   👨‍⚕️ When to Consult a Doctor:
    - ...

    ⚠ Disclaimer:
    This information is for educational purposes only and is not a substitute for professional medical advice.
    """

    response = model.generate_content(prompt)

    return response.text


# Test
if __name__ == "__main__":

    print(ask_gemini("My skin is itchy and red"))