from rest_framework import viewsets
from rest_framework.response import Response
from .serializer import ChatSerializer
import openai

class ChatViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']
            response = openai.ChatCompletion.create(
                model="text-davinci-003",
                messages=[
                    {"role": "user", "content": message},
                ]
            )
            return Response({'response': response.choices[0].message['content']})
        return Response(serializer.errors, status=400)
