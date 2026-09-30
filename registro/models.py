import base64
from django.conf import settings
from django.db import models


class Asistente(models.Model):
    nombre = models.CharField(max_length=150)
    institucion = models.CharField("institución", max_length=150, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    firma = models.BinaryField()
    aviso_aceptado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    # Los registros nunca se borran: se anulan y queda constancia de quién y cuándo.
    anulado = models.BooleanField(default=False)
    anulado_en = models.DateTimeField(null=True, blank=True)
    anulado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.nombre

    @property
    def firma_b64(self):
        return base64.b64encode(bytes(self.firma)).decode()

    def delete(self, *args, **kwargs):
        raise PermissionError("Los registros no se borran; se anulan.")
