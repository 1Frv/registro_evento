import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# Carpetas de trabajo (no van al repositorio; se crean solas en cada equipo)
DATOS_DIR = BASE_DIR / "datos"
DATOS_DIR.mkdir(exist_ok=True)


def _obtener_secret_key():
    """Usa DJANGO_SECRET_KEY si existe; si no, genera una clave aleatoria
    y la guarda en datos/.secret_key (carpeta ignorada por git)."""
    clave = os.environ.get("DJANGO_SECRET_KEY")
    if clave:
        return clave
    archivo = DATOS_DIR / ".secret_key"
    if archivo.exists():
        return archivo.read_text(encoding="utf-8").strip()
    clave = get_random_secret_key()
    archivo.write_text(clave, encoding="utf-8")
    return clave


SECRET_KEY = _obtener_secret_key()
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("DJANGO_CSRF_ORIGINS", "").split(",") if o.strip()
]

# Activar solo cuando el sistema se sirva por HTTPS (DJANGO_HTTPS=1)
if os.environ.get("DJANGO_HTTPS", "0") == "1":
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "registro",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages"]},
}]

DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": DATOS_DIR / "registro.sqlite3",
    # WAL + synchronous=FULL: cada registro queda escrito en disco antes de confirmar
    "OPTIONS": {"init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;",
                "transaction_mode": "IMMEDIATE"},
}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Merida"
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "/admin/login/"
LOGOUT_REDIRECT_URL = "/admin/login/?next=/"
SESSION_COOKIE_AGE = 60 * 60 * 12

# Respaldos
RESPALDOS_DIR = BASE_DIR / "respaldos"
RESPALDOS_DIR.mkdir(exist_ok=True)
RESPALDO_EXTRA_DIR = os.environ.get("RESPALDO_EXTRA_DIR", "")  # p. ej. memoria USB o carpeta sincronizada
RESPALDO_CADA = int(os.environ.get("RESPALDO_CADA", "10"))     # respaldo automático cada N registros