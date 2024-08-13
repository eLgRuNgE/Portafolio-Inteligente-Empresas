from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from .api.serializer import ChatSerializer
from openai import AzureOpenAI
import json 
import os
import requests

@login_required
def chat_home(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
        # Añadir un mensaje de bienvenida
        welcome_message = "¡Hola! Bienvenid@ al chat de Portafolio Inteligente de Empresas. ¿Cómo puedo ayudarte hoy?"
        request.session['chat_history'].append({"user": "Bot Comfama", "text": welcome_message})
        request.session.modified = True

    if request.method == "POST":
        user_message = request.POST.get("message")
        request.session['chat_history'].append({"user": request.user.username, "text": user_message})

        # Recuperar variables de entorno
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment_name = os.getenv('AZURE_OPENAI_LLM_DEPLOYMENT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION')

        # Generar la URL para una solicitud POST
        url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

        # Configurar los encabezados de la solicitud
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }

        # Definir los datos de la solicitud
        data = {
            "messages": [
                {"role": "system", "content": "Eres un asistente útil que me va a ayudar a proponer productos de la caja de compensación Comfama a las empresas."},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500
        }

        try:
            # Enviar la solicitud POST a la API
            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                completion = response.json()
                bot_response = completion["choices"][0]["message"]["content"].strip()
            else:
                bot_response = f"Error: {response.status_code}, {response.text}"

        except Exception as e:
            bot_response = f"Lo siento, ocurrió un error al procesar tu mensaje. {str(e)}"

        # Añadir la respuesta del bot al historial de chat
        request.session['chat_history'].append({"user": "Bot Comfama", "text": bot_response})
        request.session.modified = True

        return redirect('chat_home')

    return render(request, 'chat/chat_home.html', {
        'chat_messages': request.session['chat_history']
    })

@login_required
def chat_home_basic(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
        # Añadir un mensaje de bienvenida
        welcome_message = "¡Hola! Bienvenid@ al chat de Portafolio Inteligente de Empresas. ¿Cómo puedo ayudarte hoy?"
        request.session['chat_history'].append({"user": "Bot Comfama", "text": welcome_message})
        request.session.modified = True

    if request.method == "POST":
        user_message = request.POST.get("message")
        request.session['chat_history'].append({"user": request.user.username, "text": user_message})

        # Simular efecto de "pensar"
        request.session['chat_history'].append({"user": "Bot Comfama", "text": "Procesando..."})
        request.session.modified = True
        return redirect('chat_think')

    return render(request, 'chat/chat_home.html', {
        'chat_messages': request.session['chat_history']
    })

@login_required
def chat_think(request):
    # Elimina el mensaje de "Procesando..." y agrega la respuesta real
    chat_history = request.session.get('chat_history', [])
    if chat_history and chat_history[-1]["text"] == "Procesando...":
        chat_history.pop()
        # Respuesta automática del bot
        if "hola" in chat_history[-1]["text"].lower():
            bot_response = "Hola como estas... Yo super bien, por favor confirmame el nit de la empresa"
        else:
            bot_response = "Lo siento, no entiendo tu mensaje."
        chat_history.append({"user": "Bot Comfama", "text": bot_response})
        request.session['chat_history'] = chat_history
        request.session.modified = True
    
    return redirect('chat_home')


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

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
