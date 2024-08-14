from django.shortcuts import render, redirect
from django.http import HttpResponse
from .load_data import cargar_datos_empresas, cargar_datos_ventas, cargar_datos_portafolio

def run_etl(request):
    if request.method == 'POST':
        ruta_empresas = 'static/db/empresas.xlsx'
        ruta_ventas = 'static/db/ventas.xlsx'
        ruta_portafolio = 'static/db/portafolio.csv'
        
        # Ejecutar las funciones de carga con las rutas correctas
        cargar_datos_empresas(ruta_empresas)
        cargar_datos_ventas(ruta_ventas)
        cargar_datos_portafolio(ruta_portafolio)
        
        return HttpResponse("ETL ejecutado correctamente")
    
    return redirect('chat_home')
