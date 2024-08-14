import pandas as pd
from django.db import connection
from .models import Empresa, Venta, Portafolio


def truncate_table(model):
    """Trunca la tabla asociada al modelo dado."""
    with connection.cursor() as cursor:
        table_name = model._meta.db_table
        cursor.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;')


def cargar_datos_empresas(ruta_archivo):
    df = pd.read_excel(ruta_archivo)
    try:
        truncate_table(Empresa)
        for _, row in df.iterrows():
            Empresa.objects.create(
                DocEmp=row['DocEmp'],
                TipoDocEmp=row['TipoDocEmp'],
                MunicipioEmp=row['MuncipioEmp'],
                VisionComercial2=row['VisionComercial2'],
                empleados=row['empleados'],
                SeccionEconomicaEmp=row['SeccionEconomicaEmp'],
                GrupoDeAtencion=row['GrupoDeAtencion'],
                Sector=row['Sector']
            )
    except Exception as e:
        print(f"Excepción en cargar_datos_empresas: {e}")


def cargar_datos_ventas(ruta_archivo):
    try:
        df = pd.read_csv(ruta_archivo, encoding='latin1', on_bad_lines='skip')
        truncate_table(Venta)
        for _, row in df.iterrows():
            Venta.objects.create(
                periodo=row['periodo'],
                DocEmp=row['DocEmp'],
                material=row['material'],
                pedidos=row['pedidos']
            )
    except Exception as e:
        print(f"Excepción en cargar_datos_ventas: {e}")


def cargar_datos_portafolio(ruta_archivo):
    try:
        df = pd.read_csv(ruta_archivo, encoding='latin1', on_bad_lines='skip')
        truncate_table(Portafolio)
        for _, row in df.iterrows():
            Portafolio.objects.create(
                CodigoSAP=row['CodigoSAP'],
                Contenido=row['Contenido'],
                producto=row['producto'],
                Minimo=row['Minimo'],
                Maximo=row['Maximo']
            )
    except Exception as e:
        print(f"Excepción en cargar_datos_portafolio: {e}")


