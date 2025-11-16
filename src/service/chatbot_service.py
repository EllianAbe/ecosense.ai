import google.generativeai as genai
import os
from PIL import Image
import io
import streamlit as st
from service.vectorstore_service import VectorStoreService
from service.collect_point_type_service import CollectPointCollectTypeService
MAX_DESCRIPTION_TOKENS = int(os.getenv('MAX_DESCRIPTION_TOKENS', "100"))

collect_point_type_service = CollectPointCollectTypeService()
vector_store_service = VectorStoreService()


class ChatbotService:

    def __init__(self):
        # Use environment variable or Streamlit secrets
        genai.configure(api_key=st.secrets['GOOGLE_GENAIAI_KEY'])
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def get_response(self, user_message: str):
        return f"Echo: {user_message}"

    def analyze_image(self, image_file: io.BytesIO):
        """Analyze an uploaded image and return description"""
        try:

            image = Image.open(image_file)

            response = self.model.generate_content(
                [
                    (
                        "Você é um assistente de um fluxo de economia circular. Sua atividade é identificar "
                        "o resíduo presente na imagem, que pode ser de natureza de lixo eletrônico, orgânico, e outros. "
                        "Caso a imagem não seja de detrito, lixo orgânico, lixo eletrônico ou similar; ou se a foto tiver "
                        "rostos humanos, responda apenas INVÁLIDO, para que isso possa ser capturado adequadamente. "
                        "Instruções para a resposta (caso não seja INVÁLIDO): Liste os produtos de forma "
                        "direta, separados por vírgula. Responda apenas com os nomes dos itens (ex: cascas de "
                        "banana, folhas verdes, latas de alumínio, placa mãe, garrafa de vidro). Não use frases "
                        "completas, parágrafos ou descrições detalhadas. Responda em português do Brasil."
                    ), image]
            )

            return response.text
        except Exception as e:
            return f"Error analyzing image: {e}"

    def search_collect_points(self, image_file: io.BytesIO):
        img_description = self.analyze_image(image_file)
        found_db_ids, found_distances = vector_store_service.search_faiss_index(
            img_description, k=3)

        if found_db_ids:
            query_result = collect_point_type_service.get_collect_points_by_collect_type(
                found_db_ids[0])

            collect_points = []

            if query_result['status'] == 'success':
                collect_points = query_result['data']
        else:
            collect_points = []

        return {
            'description': img_description,
            'collect_points': collect_points
        }
