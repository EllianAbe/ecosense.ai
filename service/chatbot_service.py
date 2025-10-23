import google.generativeai as genai
import os
from PIL import Image
import io

class ChatbotService:
    def __init__(self):
        # Use environment variable or Streamlit secrets
        genai.configure(api_key="AIzaSyCQ3Xn3xWpJCSNUxDKOudWUTbKO2AszXDU")
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def get_response(self, user_message: str):
        return f"Echo: {user_message}"

    def analyze_image(self, image_file):
        """Analyze an uploaded image and return description"""
        try:
            # Convert Streamlit UploadedFile to a PIL Image
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes))

            response = self.model.generate_content(
                ["Describe what you see in this image:", image]
            )

            return response.text
        except Exception as e:
            return f"Error analyzing image: {e}"
