from service.chatbot_service import ChatbotService
import os

chatbot_service = ChatbotService()


class MetricsService():
    def __init__(self):
        pass

    def test_data_set(self, files, result_obj: list):
        total = len(files)

        for i, file in enumerate(files, 1):
            name = os.path.basename(file.name)

            yield i / total

            result = chatbot_service.search_collect_points(file, None)

            result['name'] = name

            result_obj.append(result)
