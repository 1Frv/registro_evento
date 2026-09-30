# Registro de asistentes con firma

Django + SQLite (WAL, `synchronous=FULL`). Un usuario por recepcionista, registros que nunca se borran (solo se anulan), respaldos automáticos y exportación a Excel con firmas.

## Requisitos previos (una sola vez por computadora)

Instala estos tres programas. Si ya los tienes, pasa a la siguiente sección.

1. **Python 3.10 o superior**: https://www.python.org/downloads/
   - En Windows, durante la instalación marca la casilla **"Add python.exe to PATH"**.
2. **Git**: https://git-scm.com/downloads (acepta las opciones por defecto).
3. **Visual Studio Code**: https://code.visualstudio.com/

Para comprobar que quedaron instalados, abre una terminal y ejecuta:

```
python --version
git --version
```

> En Linux/Mac puede que el comando sea `python3` en lugar de `python`.

## Descargar el proyecto

**Opción A: desde VS Code (sin usar comandos)**

1. Abre VS Code.
2. Pulsa `Ctrl + Shift + P` (en Mac, `Cmd + Shift + P`), escribe **Git: Clone** y pulsa Enter.
3. Pega la URL del repositorio: `https://github.com/TU_USUARIO/TU_REPOSITORIO.git`
4. Elige la carpeta donde se guardará el proyecto.
5. Cuando VS Code pregunte si quieres abrir el repositorio clonado, pulsa **Open**.

**Opción B: desde la terminal**

```
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
code .
```

## Instalación (una vez)

Abre la terminal integrada de VS Code (menú **Terminal → New Terminal**) y verifica que estás dentro de la carpeta del proyecto (donde está el archivo `manage.py`). Luego ejecuta, en orden:

```
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser      # usuario del recepcionista (queda como staff)
python manage.py collectstatic --noinput
```

Notas:

- Cuando el entorno virtual está activo, verás `(venv)` al inicio de la línea de la terminal.
- `createsuperuser` te pedirá un usuario, un correo (opcional) y una contraseña. Al escribir la contraseña no se muestran caracteres; es normal.
- Si VS Code pregunta si quieres usar el nuevo entorno virtual como intérprete de Python, responde **Yes**.

## Uso en el evento

Con el entorno virtual activo (`venv\Scripts\activate`), ejecuta:

```
waitress-serve --port=8000 config.wsgi:application
```

Abre http://localhost:8000 en el navegador e inicia sesión con el usuario que creaste.

Si la tableta se conecta a la laptop por Wi-Fi, usa la IP de la laptop en lugar de `localhost` y define antes de iniciar el servidor:

```
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,IP_DE_LA_LAPTOP
DJANGO_CSRF_ORIGINS=http://IP_DE_LA_LAPTOP:8000
```

(En Windows PowerShell se definen así: `$env:DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,IP_DE_LA_LAPTOP"` y `$env:DJANGO_CSRF_ORIGINS="http://IP_DE_LA_LAPTOP:8000"`.)

Para detener el servidor, pulsa `Ctrl + C` en la terminal.

## Uso en días siguientes

No hace falta volver a instalar nada. Solo abre la carpeta en VS Code, abre una terminal, activa el entorno virtual y arranca el servidor:

```
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
waitress-serve --port=8000 config.wsgi:application
```

## Protección de la información

- Los datos viven en el servidor (`datos/registro.sqlite3`), no en el navegador: borrar el navegador no pierde nada.
- Respaldo automático cada 10 registros y en cada exportación → carpeta `respaldos/` (se conservan 200).
- `RESPALDO_EXTRA_DIR=E:\respaldo` copia cada respaldo a una memoria USB o carpeta sincronizada (segunda ubicación).
- Respaldo manual o programado: `python manage.py respaldar`.
- Restaurar: cerrar el servidor y reemplazar `datos/registro.sqlite3` por el respaldo elegido.
- Pruebas: `python manage.py test`.
- La base de datos y los respaldos **no forman parte del repositorio** (están en `.gitignore`): se crean en cada computadora al ejecutar `migrate` y usar el sistema.

## Antes de producción

- Definir `DJANGO_SECRET_KEY` propio y no usar `DJANGO_DEBUG=1`.
- Si se abre a una red, usar HTTPS (proxy inverso) y revisar el aviso de privacidad con el área jurídica.

## Solución de problemas

| Problema | Solución |
|---|---|
| `python` no se reconoce como comando | Reinstala Python marcando **"Add python.exe to PATH"**, o prueba con `py` (Windows) o `python3` (Linux/Mac). |
| PowerShell dice que la ejecución de scripts está deshabilitada al activar el entorno virtual | Ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar. También puedes usar `venv\Scripts\activate.bat` desde una terminal CMD. |
| `No module named 'django'` | El entorno virtual no está activo. Ejecuta `venv\Scripts\activate` y verifica que aparezca `(venv)`. |
| `unable to open database file` | Crea la carpeta `datos` en la raíz del proyecto y repite `python manage.py migrate`. |
| Los estilos no cargan o la página se ve sin formato | Ejecuta `python manage.py collectstatic --noinput` y reinicia el servidor. |
| La tableta no puede abrir la página | Verifica que estén en la misma red Wi-Fi, que las variables `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_ORIGINS` tengan la IP correcta y que el firewall permita el puerto 8000. |