"""Pruebas sin red: python -m unittest discover -s scripts/anime_crawler -v."""

import csv
import io
import json
import tempfile
import unittest
import urllib.error
import urllib.parse
from email.message import Message
from pathlib import Path
from unittest.mock import Mock, patch

import crawler


def pagina(ids=(1,), siguiente=None):
    return {
        "data": [{
            "id": str(id_), "type": "anime",
            "attributes": {"titles": {"en_jp": f"Anime {id_}", "ja_jp": "鬼滅の刃"},
                           "synopsis": '<p>A boy, his sister and their adventures.</p>'},
            "relationships": {"genres": {"data": [{"type": "genres", "id": "1"}]}},
        } for id_ in ids],
        "included": [{"type": "genres", "id": "1", "attributes": {"name": "Action"}}],
        "links": {"next": siguiente}, "meta": {"count": 4},
    }


class Respuesta(io.BytesIO):
    def __init__(self, contenido, tipo="application/vnd.api+json"):
        super().__init__(json.dumps(contenido).encode())
        self.headers = {"Content-Type": tipo}


class Pruebas(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name)
        self.estado = crawler.Estado(self.ruta / "estado.sqlite3", "")

    def tearDown(self):
        self.estado.db.close()
        self.temporal.cleanup()

    def cliente(self, abrir, presupuesto=50):
        return crawler.ClienteKitsu(self.estado, 5, presupuesto, "prueba", abrir=abrir)

    def test_prefiere_romaji_y_excluye_kanji(self):
        self.assertEqual(crawler.titulo_preferido({"titles": {"en_jp": "Kimetsu no Yaiba", "en": "Demon Slayer"}}),
                         ("Kimetsu no Yaiba", False))
        self.assertEqual(crawler.titulo_preferido({"titles": {"en_jp": "鬼滅の刃", "en": "Demon Slayer"}}),
                         ("Demon Slayer", True))
        self.assertEqual(crawler.titulo_preferido({"canonicalTitle": "進撃の巨人"}), ("", True))

    def test_limpia_html_sin_pegar_parrafos(self):
        self.assertEqual(crawler.limpiar('<p>Una &amp; otra.</p><p>Historia<br>nueva.</p>'),
                         "Una & otra. Historia nueva.")

    def test_pagina_y_cursor_se_guardan_juntos(self):
        siguiente = crawler.API + "?page%5Boffset%5D=2"
        self.estado.guardar_pagina(pagina((1, 2), siguiente))
        self.assertEqual(self.estado.cantidad(), 2)
        self.assertEqual(self.estado.obtener("offset"), "2")
        self.estado.guardar_pagina(pagina((2, 3)))
        self.assertEqual(self.estado.cantidad(), 3)
        self.assertEqual(self.estado.obtener("completo"), "1")

    def test_error_en_pagina_no_pierde_registros_ni_avanza_cursor(self):
        datos = pagina((1, 2), crawler.API + "?page%5Boffset%5D=2")
        datos["data"][1]["relationships"]["genres"]["data"][0]["id"] = "999"
        with self.assertRaises(RuntimeError):
            self.estado.guardar_pagina(datos)
        self.assertEqual(self.estado.cantidad(), 0)
        self.assertIsNone(self.estado.obtener("offset"))

    def test_detiene_paginacion_repetida(self):
        with self.assertRaises(RuntimeError):
            self.estado.guardar_pagina(pagina((1,), crawler.API + "?page%5Boffset%5D=0"))
        self.assertEqual(self.estado.cantidad(), 0)

    def test_429_persiste_espera_incluso_al_reabrir(self):
        cabeceras = Message()
        cabeceras["Retry-After"] = "120"
        abrir = Mock(side_effect=urllib.error.HTTPError(crawler.API, 429, "Too many", cabeceras, None))
        with patch("crawler.time.time", return_value=1000):
            with self.assertRaises(crawler.Pausa):
                self.cliente(abrir).consultar(crawler.API)
        self.assertEqual(float(self.estado.obtener("no_antes_de")), 1120)
        nuevo = crawler.Estado(self.ruta / "estado.sqlite3", "")
        try:
            abrir2 = Mock()
            with patch("crawler.time.time", return_value=1050):
                with self.assertRaises(crawler.Pausa):
                    crawler.ClienteKitsu(nuevo, 5, 50, "prueba", abrir2).consultar(crawler.API)
            abrir2.assert_not_called()
        finally:
            nuevo.db.close()
        self.assertEqual(abrir.call_count, 1)

    def test_403_no_reintenta(self):
        abrir = Mock(side_effect=urllib.error.HTTPError(crawler.API, 403, "Forbidden", Message(), None))
        with self.assertRaises(crawler.Pausa):
            self.cliente(abrir).consultar(crawler.API)
        self.assertEqual(abrir.call_count, 1)

    def test_503_respeta_retry_after_sin_reintentar(self):
        cabeceras = Message()
        cabeceras["Retry-After"] = "180"
        abrir = Mock(side_effect=urllib.error.HTTPError(crawler.API, 503, "Unavailable", cabeceras, None))
        with patch("crawler.time.time", return_value=1000), self.assertRaises(crawler.Pausa):
            self.cliente(abrir).consultar(crawler.API)
        self.assertEqual(float(self.estado.obtener("no_antes_de")), 1180)
        self.assertEqual(abrir.call_count, 1)

    def test_retry_after_acepta_fecha_http(self):
        self.assertEqual(crawler.espera_servidor("Thu, 01 Jan 1970 00:02:00 GMT", ahora=60), 60)
        self.assertEqual(crawler.espera_servidor("no válido", ahora=60), 60)

    def test_limite_peticiones_incluye_reintentos(self):
        abrir = Mock(side_effect=urllib.error.URLError("sin conexión"))
        cliente = self.cliente(abrir, presupuesto=2)
        with patch("crawler.time.sleep"), self.assertRaises(crawler.Pausa):
            cliente.consultar(crawler.API)
        self.assertEqual(abrir.call_count, 2)

    def test_espera_se_conserva_entre_sesiones(self):
        with self.estado.db:
            self.estado.guardar("ultima_peticion", 1000)
        abrir = Mock(return_value=Respuesta(pagina()))
        with patch("crawler.time.time", return_value=1001), patch("crawler.time.sleep") as dormir:
            self.cliente(abrir).consultar(crawler.API)
        dormir.assert_called_once_with(4)

    def test_reanudacion_no_descarga_pagina_anterior(self):
        self.estado.guardar_pagina(pagina((1, 2), crawler.API + "?page%5Boffset%5D=2"))
        cliente = Mock()
        cliente.solicitudes, cliente.presupuesto = 1, 50
        cliente.consultar.return_value = pagina((3, 4))
        crawler.recopilar(self.estado, cliente, limite=4)
        parametros = urllib.parse.parse_qs(urllib.parse.urlsplit(cliente.consultar.call_args.args[0]).query)
        self.assertEqual(parametros["page[offset]"], ["2"])
        self.assertEqual(parametros["page[limit]"], ["2"])
        self.assertEqual(self.estado.cantidad(), 4)
        crawler.recopilar(self.estado, cliente, limite=4)
        self.assertEqual(cliente.consultar.call_count, 1)

    def test_csv_solo_espanol_comillas_y_cache_traducciones(self):
        self.estado.guardar_pagina(pagina((1, 2)))
        # Antes de traducir no se exportan sinopsis en inglés accidentalmente.
        salida = self.ruta / "animes.csv"
        self.assertEqual(crawler.exportar(self.estado, salida), 0)
        traductor = Mock()
        traductor.traducir.return_value = 'Un chico, su hermana y sus "aventuras".'
        crawler.traducir_pendientes(self.estado, traductor)
        self.assertEqual(traductor.traducir.call_count, 1)
        self.assertEqual(crawler.exportar(self.estado, salida), 2)
        self.assertTrue(salida.read_bytes().startswith(b"\xef\xbb\xbf"))
        with salida.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo))
        self.assertEqual(filas[0]["sinopsis"], 'Un chico, su hermana y sus "aventuras".')
        self.assertEqual(filas[0]["genero"], "Acción")
        crawler.traducir_pendientes(self.estado, traductor)
        self.assertEqual(traductor.traducir.call_count, 1)

    def test_busquedas_no_mezclan_cache(self):
        with self.assertRaisesRegex(RuntimeError, "búsqueda"):
            crawler.Estado(self.ruta / "estado.sqlite3", "naruto")

    def test_traduccion_fallida_queda_pendiente_y_no_se_exporta(self):
        self.estado.guardar_pagina(pagina((1, 2)))
        traductor = Mock()
        traductor.traducir.side_effect = RuntimeError("fallo del traductor")
        with self.assertRaises(RuntimeError):
            crawler.traducir_pendientes(self.estado, traductor)
        self.assertEqual(crawler.exportar(self.estado, self.ruta / "animes.csv"), 0)
        self.assertEqual(self.estado.db.execute("SELECT COUNT(*) FROM anime WHERE sinopsis_es IS NULL").fetchone()[0], 2)

    def test_html_bloqueo_no_avanza(self):
        abrir = Mock(return_value=Respuesta({}, tipo="text/html"))
        with self.assertRaises(crawler.Pausa):
            self.cliente(abrir).consultar(crawler.API)
        self.assertIsNone(self.estado.obtener("offset"))


if __name__ == "__main__":
    unittest.main()
