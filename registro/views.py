import base64
import io
import json
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from PIL import Image

from . import servicios
from .models import Asistente

PREFIJO = "data:image/png;base64,"
SOLO_LETRAS = re.compile(r"^[^\W\d_]+(?: [^\W\d_]+)*$")  # letras (con acentos y ñ) separadas por un espacio
ETIQUETAS = {"nombre": "El nombre", "institucion": "La institución / empresa / municipio", "cargo": "El cargo"}


def _limpio(d, campo):
    """Texto en mayúsculas y sin espacios repetidos."""
    return " ".join(str(d.get(campo, "")).split()).upper()


def _firma_valida(dato):
    if not dato.startswith(PREFIJO):
        return None
    try:
        raw = base64.b64decode(dato[len(PREFIJO):], validate=True)
        if len(raw) > 300_000:
            return None
        img = Image.open(io.BytesIO(raw))
        img.verify()
        return raw if img.format == "PNG" else None
    except Exception:
        return None


@login_required
def inicio(request):
    q = request.GET.get("q", "").strip()
    activos = Asistente.objects.filter(anulado=False)
    lista = (activos.filter(nombre__icontains=q) if q else activos)[:200]
    return render(request, "registro/inicio.html", {"lista": lista, "total": activos.count(), "q": q})


@login_required
@require_POST
def guardar(request):
    try:
        d = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Datos inválidos"}, status=400)
    nombre, institucion, cargo = (_limpio(d, c) for c in ("nombre", "institucion", "cargo"))
    telefono = str(d.get("telefono", "")).strip()
    correo = str(d.get("correo", "")).strip().lower()
    firma = _firma_valida(str(d.get("firma", "")))
    if not nombre:
        return JsonResponse({"error": "El nombre es obligatorio"}, status=400)
    if not institucion:
        return JsonResponse({"error": "La institución / empresa / municipio es obligatoria"}, status=400)
    if not cargo:
        return JsonResponse({"error": "El cargo es obligatorio"}, status=400)
    for campo, valor in (("nombre", nombre), ("institucion", institucion), ("cargo", cargo)):
        if valor and not SOLO_LETRAS.match(valor):
            return JsonResponse({"error": f"{ETIQUETAS[campo]} solo admite letras y espacios"}, status=400)
    if telefono and not (telefono.isascii() and telefono.isdigit() and len(telefono) <= 10):
        return JsonResponse({"error": "El teléfono solo admite números, máximo 10 dígitos"}, status=400)
    if not firma:
        return JsonResponse({"error": "Falta la firma"}, status=400)
    if not d.get("aviso"):
        return JsonResponse({"error": "Debe aceptarse el aviso de privacidad"}, status=400)
    if correo:
        try:
            validate_email(correo)
        except ValidationError:
            return JsonResponse({"error": "El correo no es válido"}, status=400)
    if not d.get("confirmar"):
        activos = Asistente.objects.filter(anulado=False)
        repetidos = []
        if activos.filter(nombre__iexact=nombre).exists():
            repetidos.append("nombre")
        if correo and activos.filter(correo__iexact=correo).exists():
            repetidos.append("correo")
        if telefono and activos.filter(telefono=telefono).exists():
            repetidos.append("teléfono")
        if repetidos:
            return JsonResponse({"duplicado": True, "campos": repetidos}, status=409)
    Asistente.objects.create(
        nombre=nombre[:150], institucion=institucion[:150], cargo=cargo[:100],
        correo=correo, telefono=telefono, firma=firma, aviso_aceptado=True)
    total = Asistente.objects.filter(anulado=False).count()
    if total % settings.RESPALDO_CADA == 0:
        servicios.respaldar()
    return JsonResponse({"ok": True, "total": total})


@login_required
@require_POST
def anular(request, pk):
    a = get_object_or_404(Asistente, pk=pk, anulado=False)
    a.anulado, a.anulado_en, a.anulado_por = True, timezone.now(), request.user
    a.save(update_fields=["anulado", "anulado_en", "anulado_por"])
    return redirect("inicio")


@login_required
def exportar(request):
    servicios.respaldar()  # cada exportación deja también un respaldo de la base
    resp = HttpResponse(servicios.exportar_xlsx(),
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="registro-{timezone.localtime():%Y%m%d-%H%M}.xlsx"'
    return resp