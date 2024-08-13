from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from .api.serializer import ChatSerializer
from .models import InitialQuestion
from openai import AzureOpenAI
import json 
import os
import requests


@login_required
def chat_home(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
        request.session['question_index'] = 0
        request.session['responses'] = {}
        request.session['analysis_done'] = False
        request.session['openia_mode'] = False

        first_name = request.user.first_name

        welcome_message = f"¡Hola! {first_name}, Bienvenid@ al chat de Portafolio Inteligente de Empresas.\n\nQuiero ayudarte a encontrar las mejores propuestas desde el Portafolio de Comfama para la empresa que diagnósticas. Por favor responde estas preguntas:"
        request.session['chat_history'].append({"user": "Bot Comfama", "text": welcome_message})
        request.session.modified = True

        questions = InitialQuestion.objects.all()
        if questions:
            first_question = questions[0]
            request.session['chat_history'].append({"user": "Bot Comfama", "text": format_question(first_question)})
            request.session.modified = True
            request.session['question_index'] += 1

    if request.session['openia_mode']:
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
    else:
        if request.method == "POST":
            user_message = request.POST.get("message")
            request.session['chat_history'].append({"user": request.user.username, "text": user_message})

            question_index = request.session['question_index'] - 1
            questions = InitialQuestion.objects.all()
            if question_index < len(questions):
                current_question = questions[question_index]
                request.session['responses'][current_question.question] = user_message
                print(f"Respuesta guardada: {current_question.question}: {user_message}")  # Depuración
                request.session.modified = True

            if request.session['question_index'] < len(questions):
                next_question = questions[request.session['question_index']]
                bot_response = format_question(next_question)
                request.session['question_index'] += 1
                request.session['chat_history'].append({"user": "Bot Comfama", "text": bot_response})
            elif request.session['question_index'] == len(questions) and not request.session['analysis_done']:
                request.session['chat_history'].append({"user": "Bot Comfama", "text": "Gracias por tu información."})
                summary = "\n".join([f"{key}: {value}" for key, value in request.session['responses'].items()])
                request.session['chat_history'].append({"user": "Bot Comfama", "text": f"Aquí tienes un resumen de tus respuestas:\n\n{summary}\n\n"})
                request.session['chat_history'].append({"user": "Bot Comfama", "text": "Ahora procederé a analizar la información."})
                
                request.session['analysis_done'] = True
                request.session.modified = True

                return redirect('chat_home')

        if request.session['analysis_done']:
            responses = request.session['responses']
            print(f"Respuestas almacenadas: {responses}")  # Depuración

            text_to_send = (
                f"Requiero buscar productos dentro del portafolio de la caja de Compesación de Comfama para la empresa con NIT: {responses.get('¿Cuál es el NIT de la empresa?')}, "
                f"cuya industria y sector en el que opera es {responses.get('¿Cuál es la industria y sector en el que opera la empresa?')}, "
                f"que tiene modalidad de trabajo: {responses.get('¿Cuál es la modalidad de trabajo?')}, "
                f"y la conforman las siguientes áreas {responses.get('¿Qué áreas conforman la empresa?')}, "
                f"la cual tiene {responses.get('¿Cuántos líderes tiene la organización?')} líderes "
                f"y manejan el SST de manera {responses.get('¿Cómo manejan el SST?')}."
            )

            print(f"Texto a enviar a OpenAI: {text_to_send}")  # Depuración

            request.session['chat_history'].append({"user": "Bot Comfama", "text": f"Texto a enviar a OpenAI:\n\n{text_to_send}"})
            request.session.modified = True

            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            deployment_name = os.getenv('AZURE_OPENAI_LLM_DEPLOYMENT')
            api_version = os.getenv('AZURE_OPENAI_API_VERSION')

            url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

            headers = {
                "Content-Type": "application/json",
                "api-key": api_key
            }

            data = {
                "messages": [
                    {"role": "system", "content": "Eres un asistente útil que me va a ayudar a proponer productos de la caja de compensación Comfama a las empresas."},
                    {"role": "user", "content": text_to_send}
                ],
                "max_tokens": 500
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))

                if response.status_code == 200:
                    completion = response.json()
                    bot_response = completion["choices"][0]["message"]["content"].strip()
                else:
                    bot_response = f"Error: {response.status_code}, {response.text}"

            except Exception as e:
                bot_response = f"Lo siento, ocurrió un error al procesar tu mensaje. {str(e)}"

            request.session['chat_history'].append({"user": "Bot Comfama", "text": bot_response})
            request.session['analysis_done'] = False
            request.session['openia_mode'] = True
            request.session.modified = True

            return redirect('chat_home')

        return render(request, 'chat/chat_home.html', {
            'chat_messages': request.session['chat_history']
        })
        

def format_question(question):
    """Formatea la pregunta para incluir opciones si están disponibles."""
    if question.options:
        options = question.options.split(',')
        formatted_options = "\n".join(f"| {option}" for option in options)
        return f"{question.question}\nOpciones:\n{formatted_options}"
    return question.question

@login_required
def chat_home_ok(request):
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
