from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from .api.serializer import ChatSerializer
from .models import InitialQuestion
from openai import AzureOpenAI
from xhtml2pdf import pisa
from pathlib import Path
import json 
import os
import re
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
portafolio = []

# Importar el JSON con la base de datos
try:
    portafolio_path = os.path.join(BASE_DIR, 'data', 'portafolio.json')
    with open(portafolio_path, 'r', encoding='utf-8') as f:
        portafolio = json.load(f)
except Exception as e:
    bot_response = f"Lo siento, ocurrió un error al cargar la base de datos. {str(e)}"
    print(bot_response)


example_1 = "Requiero buscar productos dentro del portafolio de la caja de Compensación de Comfama para la empresa con NIT: 123456789, cuya industria y sector en el que opera es Tecnología y Servicios, que tiene modalidad de trabajo: Mixto, y la conforman las siguientes áreas: Recursos Humanos, Finanzas, y Operaciones, la cual tiene 10 líderes y manejan el SST de manera interna."

output_example_1 = """
    <p>¡Hola! 😊 Entiendo que deseas recomendaciones de productos de Comfama para tu empresa. Aquí tienes una selección personalizada basada en las características y necesidades de tu empresa:</p>
    <h3><b>Recursos Humanos 🧑‍💼🧑‍💻</b></h3>
    <h4>Producto: Bienestar Integral</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de apoyo emocional y psicológico.</li>
            <li>Talleres de manejo del estrés y balance vida-trabajo.</li>
            <li>Actividades deportivas y recreativas.</li>
        </ul>
    </ul>
    <h4>Producto: Formación y Capacitación</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Cursos y talleres en habilidades blandas como liderazgo y trabajo en equipo.</li>
            <li>Capacitación en normativas laborales y SST.</li>
        </ul>
    </ul>
    <h3><b>Ventas 📈📊</b></h3>
    <h4>Producto: Desarrollo Profesional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en técnicas de ventas y negociación.</li>
            <li>Programas de desarrollo de habilidades comerciales.</li>
        </ul>
    </ul>
    <h4>Producto: Incentivos y Reconocimientos</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de incentivos para el equipo de ventas.</li>
            <li>Reconocimiento al empleado del mes.</li>
        </ul>
    </ul>
    <h3><b>Finanzas 💰📉</b></h3>
    <h4>Producto: Educación Financiera</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Talleres sobre manejo de finanzas personales.</li>
            <li>Asesorías sobre ahorro e inversión.</li>
        </ul>
    </ul>
    <h4>Producto: Planes de Retiro</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Información y asesoramiento sobre planes de pensiones y retiro.</li>
            <li>Talleres sobre planificación financiera a largo plazo.</li>
        </ul>
    </ul>
    <h3><b>Producción 🏭🔧</b></h3>
    <h4>Producto: Seguridad y Salud en el Trabajo (SST)</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en normativas de seguridad laboral.</li>
            <li>Programas de prevención de riesgos laborales.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Laboral</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de ergonomía y prevención de enfermedades laborales.</li>
            <li>Actividades de integración y motivación.</li>
        </ul>
    </ul>
    <h3><b>Tecnología 💻📲</b></h3>
    <h4>Producto: Innovación y Tecnología</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Talleres y cursos en tecnologías emergentes.</li>
            <li>Asesoría en transformación digital.</li>
        </ul>
    </ul>
    <h4>Producto: Desarrollo Personal y Profesional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de formación en habilidades técnicas y de gestión de proyectos.</li>
            <li>Seminarios sobre tendencias tecnológicas.</li>
        </ul>
    </ul>
    <h3><b>Servicio al Cliente 📞👥</b></h3>
    <h4>Producto: Atención al Cliente</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en habilidades de comunicación y resolución de conflictos.</li>
            <li>Talleres de técnicas de servicio al cliente.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Emocional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de manejo del estrés y burnout.</li>
            <li>Actividades de recreación y esparcimiento.</li>
        </ul>
    </ul>
    <h3><b>Líderes ⚖️🧩</b></h3>
    <h4>Producto: Liderazgo y Gestión</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de desarrollo de liderazgo y coaching.</li>
            <li>Talleres de gestión de equipos y proyectos.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Integral</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de apoyo emocional y manejo del estrés para líderes.</li>
            <li>Actividades de balance vida-trabajo y motivación.</li>
        </ul>
    </ul>
    <h3><b>Seguridad y Salud en el Trabajo (SST) 🛡️🔍</b></h3>
    <h4>Producto: Capacitación en SST</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Formación en normativas y mejores prácticas en SST.</li>
            <li>Talleres de primeros auxilios y prevención de accidentes.</li>
        </ul>
    </ul>
    <h4>Producto: Evaluación y Mejora</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Diagnóstico y evaluación de riesgos laborales.</li>
            <li>Programas de mejora continua en SST.</li>
        </ul>
    </ul>
    <p>Espero que estas recomendaciones sean útiles para tu empresa y ayuden a mejorar el bienestar y la productividad de tus equipos. ¡Si necesitas más información, no dudes en pedírmela! 😊📈💼</p>
    """

example_2 = "Requiero buscar productos dentro del portafolio de la caja de Compensación de Comfama para la empresa BANCOLOMBIA S.A. con NIT: 890903938, cuya industria y sector en el que opera es de Banca, Tecnología y Servicios, que tiene modalidad de trabajo: Mixto, y la conforman las siguientes áreas: Recursos Humanos, Finanzas, y Operaciones, la cual tiene 10 líderes y manejan el SST de manera interna."

output_example_2 = """
    <p>¡Hola! 😊 Entiendo que deseas recomendaciones de productos de Comfama para BANCOLOMBIA S.A. Aquí tienes una selección personalizada basada en las características y necesidades de tu empresa:</p>
    <h3><b>Recursos Humanos 🧑‍💼🧑‍💻</b></h3>
    <h4>Producto: XXXX</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de apoyo emocional y psicológico.</li>
            <li>Talleres de manejo del estrés y balance vida-trabajo.</li>
            <li>Actividades deportivas y recreativas.</li>
        </ul>
    </ul>
    <h4>Producto: Formación y Capacitación</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Cursos y talleres en habilidades blandas como liderazgo y trabajo en equipo.</li>
            <li>Capacitación en normativas laborales y SST.</li>
        </ul>
    </ul>
    <h3><b>Ventas 📈📊</b></h3>
    <h4>Producto: Desarrollo Profesional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en técnicas de ventas y negociación.</li>
            <li>Programas de desarrollo de habilidades comerciales.</li>
        </ul>
    </ul>
    <h4>Producto: Incentivos y Reconocimientos</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de incentivos para el equipo de ventas.</li>
            <li>Reconocimiento al empleado del mes.</li>
        </ul>
    </ul>
    <h3><b>Finanzas 💰📉</b></h3>
    <h4>Producto: Educación Financiera</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Talleres sobre manejo de finanzas personales.</li>
            <li>Asesorías sobre ahorro e inversión.</li>
        </ul>
    </ul>
    <h4>Producto: Planes de Retiro</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Información y asesoramiento sobre planes de pensiones y retiro.</li>
            <li>Talleres sobre planificación financiera a largo plazo.</li>
        </ul>
    </ul>
    <h3><b>Producción 🏭🔧</b></h3>
    <h4>Producto: Seguridad y Salud en el Trabajo (SST)</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en normativas de seguridad laboral.</li>
            <li>Programas de prevención de riesgos laborales.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Laboral</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de ergonomía y prevención de enfermedades laborales.</li>
            <li>Actividades de integración y motivación.</li>
        </ul>
    </ul>
    <h3><b>Tecnología 💻📲</b></h3>
    <h4>Producto: Innovación y Tecnología</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Talleres y cursos en tecnologías emergentes.</li>
            <li>Asesoría en transformación digital.</li>
        </ul>
    </ul>
    <h4>Producto: Desarrollo Personal y Profesional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de formación en habilidades técnicas y de gestión de proyectos.</li>
            <li>Seminarios sobre tendencias tecnológicas.</li>
        </ul>
    </ul>
    <h3><b>Servicio al Cliente 📞👥</b></h3>
    <h4>Producto: Atención al Cliente</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Capacitación en habilidades de comunicación y resolución de conflictos.</li>
            <li>Talleres de técnicas de servicio al cliente.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Emocional</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de manejo del estrés y burnout.</li>
            <li>Actividades de recreación y esparcimiento.</li>
        </ul>
    </ul>
    <h3><b>Líderes ⚖️🧩</b></h3>
    <h4>Producto: Liderazgo y Gestión</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de desarrollo de liderazgo y coaching.</li>
            <li>Talleres de gestión de equipos y proyectos.</li>
        </ul>
    </ul>
    <h4>Producto: Bienestar Integral</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Programas de apoyo emocional y manejo del estrés para líderes.</li>
            <li>Actividades de balance vida-trabajo y motivación.</li>
        </ul>
    </ul>
    <h3><b>Seguridad y Salud en el Trabajo (SST) 🛡️🔍</b></h3>
    <h4>Producto: Capacitación en SST</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Formación en normativas y mejores prácticas en SST.</li>
            <li>Talleres de primeros auxilios y prevención de accidentes.</li>
        </ul>
    </ul>
    <h4>Producto: Evaluación y Mejora</h4>
    <ul>
        <li><strong>Contenido:</strong></li>
        <ul>
            <li>Diagnóstico y evaluación de riesgos laborales.</li>
            <li>Programas de mejora continua en SST.</li>
        </ul>
    </ul>
    <p>Espero que estas recomendaciones sean útiles para tu empresa y ayuden a mejorar el bienestar y la productividad de tus equipos. ¡Si necesitas más información, no dudes en pedírmela! 😊📈💼</p>
    """

@login_required
def chat_home(request):
    global portafolio
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

            # Recuperar el NIT de las respuestas del usuario
            nit_empresa = request.session['responses'].get("¿Cuál es el NIT de la empresa?")

            # Filtrar los productos por el DocEmp (equivalente al NIT)
            productos_filtrados = [
                producto for producto in portafolio['productos'] 
                if producto['DocEmp'] == nit_empresa
            ]

            # Definir los datos de la solicitud
            data = {
                "messages": [
                    {"role": "system", "content": f"Eres un asistente útil, dinámico e introvertifo que me va a ayudar a proponer y recomendar productos de la caja de compensación Comfama a las empresas. Tu respuesta siempre debe ser en formato HTML compacta (sin muchos espacios entre parrafos y lineas), siempre traeme las recomendaciones agrupadas por 'Contenido' (debe ir en negrilla y de un tamaño de letra un poco mayor), los campos que debe reber las recomendaciones son: 1. El 'producto', que se refiere en si al nombre de producto que se oferta y el campo 'Contenido', 2. entregandome recomendaciones por cada contenido para la empresa consultada, asi mismo adorna tu respuesta con emoticones y todo lo que requieras para que se vea de manera agradable y fácil de leer peor de manera compacta sin muchos espacios entre lineas. Aquí tienes el portafolio: {json.dumps(productos_filtrados)}"},
                    {"role": "user", "content": example_1},
                    {"role": "assistant", "content": output_example_1},
                    {"role": "user", "content": example_2},
                    {"role": "assistant", "content": output_example_2},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 3000,
                "temperature": 0.7 
            }

            try:
                # Enviar la solicitud POST a la API
                response = requests.post(url, headers=headers, data=json.dumps(data))
                bot_response = bot_response.replace("\n", "<br>").replace("•", "<li>")

                if response.status_code == 200:
                    completion = response.json()
                    bot_response = completion["choices"][0]["message"]["content"].strip()
                else:
                    bot_response = f"Error: {response.status_code}, {response.text}"
                    bot_response = bot_response.replace("\n", "<br>").replace("•", "<li>")

            except Exception as e:
                bot_response = f"Lo siento, ocurrió un error al procesar tu mensaje. {str(e)}"

            # Añadir la respuesta del bot al historial de chat
            # request.session['chat_history'].append({"user": "Bot Comfama", "text": bot_response})
            request.session['chat_history'].append({"user": "Bot Comfama", "text": f"<p>{bot_response}</p>"})
            request.session.modified = True

            return redirect('chat_home')

        return render(request, 'chat/chat_home.html', {
            'chat_messages': request.session['chat_history'],
            'pdf_ready': request.session.get('pdf_ready', False)
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

            #request.session['chat_history'].append({"user": "Bot Comfama", "text": f"Texto a enviar a OpenAI:\n\n{text_to_send}"})
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

            # Recuperar el NIT de las respuestas del usuario
            nit_empresa = request.session['responses'].get("¿Cuál es el NIT de la empresa?")

            # Filtrar los productos por el DocEmp (equivalente al NIT)
            productos_filtrados = [
                producto for producto in portafolio['productos'] 
                if producto['DocEmp'] == nit_empresa
            ]

            data = {
                "messages": [
                    {"role": "system", "content": f"Eres un asistente útil, dinámico e introvertifo que me va a ayudar a proponer y recomendar productos de la caja de compensación Comfama a las empresas. Tu respuesta siempre debe ser en formato HTML compacta (sin muchos espacios entre parrafos y lineas), siempre traeme las recomendaciones agrupadas por 'Contenido' (debe ir en negrilla y de un tamaño de letra un poco mayor), los campos que debe reber las recomendaciones son: 1. El 'producto', que se refiere en si al nombre de producto que se oferta y el campo 'Contenido', 2. entregandome recomendaciones por cada contenido para la empresa consultada, asi mismo adorna tu respuesta con emoticones y todo lo que requieras para que se vea de manera agradable y fácil de leer peor de manera compacta sin muchos espacios entre lineas. Aquí tienes el portafolio: {json.dumps(productos_filtrados)}"},
                    {"role": "user", "content": example_1},
                    {"role": "assistant", "content": output_example_1},
                    {"role": "user", "content": text_to_send}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))

                if response.status_code == 200:
                    completion = response.json()
                    bot_response = completion["choices"][0]["message"]["content"].strip()
                else:
                    bot_response = f"Error: {response.status_code}, {response.text}"
                    
                #bot_response = bot_response.replace("\n", "<br>").replace("•", "<li>")
                print(bot_response)
            except Exception as e:
                bot_response = f"Lo siento, ocurrió un error al procesar tu mensaje. {str(e)}"

            # Guarda la respuesta de OpenAI en la sesión para ser usada en el PDF
            request.session['openai_recommendation'] = bot_response

            #request.session['chat_history'].append({"user": "Bot Comfama", "text": bot_response})
            request.session['chat_history'].append({"user": "Bot Comfama", "text": f"<p>{bot_response}</p>"})
            request.session['analysis_done'] = False
            request.session['openia_mode'] = True
            request.session['pdf_ready'] = True
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
def generate_pdf(request):
    # Recupera la recomendación de OpenAI de la sesión
    openai_recommendation = request.session.get('openai_recommendation', 'No hay recomendaciones disponibles.')

    # Filtra caracteres extraños de la recomendación
    openai_recommendation = clean_recommendation(openai_recommendation)

    # Renderiza el contenido HTML del PDF
    html = render_to_string('chat/pdf_template.html', {'recommendation': openai_recommendation})
    
    # Crear una respuesta HTTP con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="recomendaciones.pdf"'  # Inline para abrir en una nueva pestaña
    
    # Generar el PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Verifica si hubo un error durante la creación del PDF
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF', status=500)
    
    return response

def clean_recommendation(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ .,;:!?"\'\-\n/<>\\|]+', '', text)
    return cleaned_text


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
