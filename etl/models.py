from django.db import models

class Empresa(models.Model):
    DocEmp = models.CharField(max_length=100)
    TipoDocEmp = models.CharField(max_length=50)
    MunicipioEmp = models.CharField(max_length=100)
    VisionComercial2 = models.TextField()
    empleados = models.IntegerField()
    SeccionEconomicaEmp = models.CharField(max_length=100)
    GrupoDeAtencion = models.CharField(max_length=100)
    Sector = models.CharField(max_length=100)

class Venta(models.Model):
    periodo = models.CharField(max_length=10)
    DocEmp = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    pedidos = models.IntegerField()

class Portafolio(models.Model):
    CodigoSAP = models.CharField(max_length=50)
    Contenido = models.TextField()
    producto = models.CharField(max_length=100)
    Minimo = models.IntegerField()
    Maximo = models.IntegerField()
