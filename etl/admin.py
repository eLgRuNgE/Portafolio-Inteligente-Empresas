from django.contrib import admin
from .models import Empresa, Venta, Portafolio

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('DocEmp', 'TipoDocEmp', 'MunicipioEmp', 'Sector', 'empleados')
    search_fields = ('DocEmp', 'MunicipioEmp', 'Sector')
    list_filter = ('Sector', 'MunicipioEmp')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'DocEmp', 'material', 'pedidos')
    search_fields = ('DocEmp', 'material')
    list_filter = ('periodo',)

@admin.register(Portafolio)
class PortafolioAdmin(admin.ModelAdmin):
    list_display = ('CodigoSAP', 'producto', 'Minimo', 'Maximo')
    search_fields = ('CodigoSAP', 'producto')
    list_filter = ('producto',)
