# Registro de asistentes con firma

Django + SQLite (WAL, `synchronous=FULL`). Un usuario por recepcionista, registros que nunca se borran (solo se anulan), respaldos automáticos y exportación a Excel con firmas.

## Instalación (una vez)
    python -m venv venv
    venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser      # usuario del recepcionista (queda como staff)
    python manage.py collectstatic --noinput

## Uso en el evento
    waitress-serve --port=8000 config.wsgi:application
Abrir http://localhost:8000 (si la tableta se conecta a la laptop por Wi-Fi, usar la IP de la laptop y definir
`DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,IP_DE_LA_LAPTOP` y `DJANGO_CSRF_ORIGINS=http://IP_DE_LA_LAPTOP:8000`).

## Protección de la información
- Los datos viven en el servidor (`datos/registro.sqlite3`), no en el navegador: borrar el navegador no pierde nada.
- Respaldo automático cada 10 registros y en cada exportación → carpeta `respaldos/` (se conservan 200).
- `RESPALDO_EXTRA_DIR=E:\respaldo` copia cada respaldo a una memoria USB o carpeta sincronizada (segunda ubicación).
- Respaldo manual o programado: `python manage.py respaldar`.
- Restaurar: cerrar el servidor y reemplazar `datos/registro.sqlite3` por el respaldo elegido.
- Pruebas: `python manage.py test`.

## Antes de producción
- Definir `DJANGO_SECRET_KEY` propio y no usar `DJANGO_DEBUG=1`.
- Si se abre a una red, usar HTTPS (proxy inverso) y revisar el aviso de privacidad con el área jurídica.
