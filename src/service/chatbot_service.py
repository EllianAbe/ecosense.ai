import google.generativeai as genai
import os
from PIL import Image
import io
import streamlit as st
from service.vectorstore_service import VectorStoreService
from service.collect_point_type_service import CollectPointCollectTypeService
from service.geo_location_service import GeoLocationService
from utils.logger import logger

MAX_DESCRIPTION_TOKENS = int(os.getenv('MAX_DESCRIPTION_TOKENS', "100"))

collect_point_type_service = CollectPointCollectTypeService()
vector_store_service = VectorStoreService()
geo_location_service = GeoLocationService()


class ChatbotService:

    def __init__(self):
        # Use environment variable or Streamlit secrets
        genai.configure(api_key=st.secrets['GOOGLE_GENAIAI_KEY'])
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def analyze_image(self, image_file: io.BytesIO):
        """Analyze an uploaded image and return description"""

        logger.info('Descrevendo a imagem')
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

    def describe_materials(self, materials):
        """Generate a concise description of materials from the image analysis."""

        logger.info('Buscando lista detalhada de materiais e componentes')
        prompt = (
            "Utilize markdown para formatar sua resposta.\n\n"
            "Com base na seguinte lista de materiais, gere uma lista concisa dos elementos ou materiais"
            " contaminantes presentes nos resíduos mencionados. A lista deve ser separada por vírgulas "
            "e conter apenas os nomes dos materiais. "
            f"Lista de materiais: {materials}\n\n"
            "Descrição concisa dos materiais:"
        )

        response = self.model.generate_content(
            [
                prompt
            ])

        return response.text.strip()

    def describe_environment_impact(self, description, materials):
        """Generate an environmental impact description based on the image analysis."""
        logger.info('buscando impactos ambientais')
        prompt = (
            "Utilize markdown para formatar sua resposta.\n\n"
            "Com base na seguinte descrição, forneça uma breve explicação do impacto ambiental "
            "associado aos materiais ou tipos de resíduos mencionados. Se a descrição não mencionar "
            "nenhum material ou resíduo, responda apenas com 'INVÁLIDO'.\n\n"
            f"Descrição: {description}\n\n"
            f"Materiais: {materials}\n\n"
            "Impacto ambiental:"
        )

        response = self.model.generate_content(
            [
                prompt
            ]
        )

        return response.text.strip()

    def describe_health_impact(self, description, materials):
        """Generate a health impact description based on the image analysis."""
        logger.info('buscando impactos na saúde')
        prompt = (
            "Utilize markdown para formatar sua resposta.\n\n"
            "Com base na seguinte descrição, forneça uma breve explicação do impacto na saúde "
            "associado aos materiais ou tipos de resíduos mencionados. Se a descrição não mencionar "
            "nenhum material ou resíduo, responda apenas com 'INVÁLIDO'.\n\n"
            f"Descrição: {description}\n\n"
            f"Materiais: {materials}\n\n"
            "Impacto na saúde:"
        )

        response = self.model.generate_content(
            [
                prompt
            ]
        )

        return response.text.strip()

    def search_collect_points(self, image_file: io.BytesIO, user_location=None):
        logger.info('buscando pontos de coleta')

        img_description = self.analyze_image(image_file)
        found_db_ids, found_distances = vector_store_service.search_faiss_index(
            img_description, k=3)

        if not found_db_ids:
            return {
                'description': img_description,
                'collect_points': []
            }

        query_result = collect_point_type_service.get_collect_points_by_collect_type(
            found_db_ids[0])

        collect_points = []

        if query_result['status'] != 'success':
            return {
                'description': img_description,
                'collect_points': []
            }

        collect_points = query_result['data']

        if user_location:
            for point in collect_points:
                if not user_location:
                    point['geographic_distance'] = None
                    continue

                point_coords = (point['collect_point'].latitude,
                                point['collect_point'].longitude)

                distance = geo_location_service.distance_between(
                    user_location,
                    point_coords
                )
                point['geographic_distance'] = distance

            collect_points.sort(
                key=lambda x: x['geographic_distance'])

        return {
            'description': img_description,
            'collect_points': collect_points
        }

    def chatbot(self, image_file: io.BytesIO, user_question: str):
        img_description = self.analyze_image(image_file)

        prompt = (
            "Você é um assistente especializado em economia circular e gestão de resíduos sólidos. "
            "Responda exclusivamente a questões relacionadas a descarte, reciclagem, reuso e práticas sustentáveis. "
            "Utilize a descrição a seguir da imagem para fornecer respostas claras, objetivas e informativas.\n\n"
            f"Descrição da imagem: {img_description}\n\n"
            f"Pergunta do usuário: {user_question}\n\n"
            "Responda de forma educada, prática e focada no contexto apresentado."
        )

        response = self.model.generate_content(
            [
                prompt
            ]
        )

        return response.text.strip()
