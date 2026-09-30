import json
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TransactionTestCase, override_settings

PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


class FlujoTest(TransactionTestCase):
    def test_registro_respaldo_y_excel(self):
        User.objects.create_user("recepcion", password="x", is_staff=True)
        with tempfile.TemporaryDirectory() as tmp, override_settings(RESPALDOS_DIR=Path(tmp), RESPALDO_CADA=1):
            self.assertEqual(self.client.get("/").status_code, 302)  # exige inicio de sesión
            self.client.login(username="recepcion", password="x")
            datos = {"nombre": "Ana Pérez", "institucion": "Gobierno", "firma": PNG, "aviso": True}
            post = lambda d: self.client.post("/guardar/", json.dumps(d), content_type="application/json")
            self.assertEqual(post(datos).status_code, 200)
            self.assertEqual(post(datos).status_code, 409)                  # duplicado
            self.assertEqual(post({**datos, "firma": ""}).status_code, 400)  # sin firma
            self.assertEqual(len(list(Path(tmp).glob("registro-*.sqlite3"))), 1)
            r = self.client.get("/exportar/")
            self.assertTrue(r.content.startswith(b"PK"))
            self.assertEqual(self.client.get("/").status_code, 200)
