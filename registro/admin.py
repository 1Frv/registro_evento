from django.contrib import admin
from .models import Asistente

admin.site.login_template = "registro/login.html"
admin.site.site_header = "Programa de trabajo Mesas con Campeche"
admin.site.site_title = "Mesas con Campeche"
admin.site.index_title = "Administración de registros"


@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "institucion", "cargo", "creado", "anulado")
    list_filter = ("anulado",)
    search_fields = ("nombre", "institucion", "correo")
    readonly_fields = ("creado", "anulado_en", "anulado_por")

    def has_delete_permission(self, request, obj=None):
        return False