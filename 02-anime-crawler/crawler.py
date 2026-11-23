#!/usr/bin/env python3
"""Recopila anime desde Kitsu y exporta título en rōmaji y sinopsis en español.

Ejemplo: python crawler.py --limite 100 --descargar-modelo
Solo usa la biblioteca estándar para descargar y guardar; la traducción es local.
"""

import argparse
import csv
import html
import json
import logging
import math
import re
import socket
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

from traduccion import REVISION, TraductorLocal

BASE = Path(__file__).resolve().parent
API = "https://kitsu.io/api/edge/anime"
LOG = logging.getLogger("anime")
GENEROS = {
    "action": "Acción", "adventure": "Aventura", "comedy": "Comedia",
    "drama": "Drama", "sci-fi": "Ciencia ficción", "science fiction": "Ciencia ficción",
    "space": "Espacio", "mystery": "Misterio", "magic": "Magia",
    "supernatural": "Sobrenatural", "police": "Policial", "fantasy": "Fantasía",
    "sports": "Deportes", "romance": "Romance", "slice of life": "Vida cotidiana",
    "horror": "Terror", "psychological": "Psicológico", "thriller": "Suspenso",
    "historical": "Histórico", "military": "Militar", "music": "Música",
    "school": "Escolar", "martial arts": "Artes marciales", "samurai": "Samuráis",
    "super power": "Superpoderes", "super powers": "Superpoderes", "demons": "Demonios",
    "vampire": "Vampiros", "vampires": "Vampiros", "kids": "Infantil",
    "game": "Juegos", "cars": "Automovilismo", "parody": "Parodia",
    "harem": "Harén", "shoujo ai": "Shōjo ai", "shounen ai": "Shōnen ai",
    "shounen": "Shōnen", "shoujo": "Shōjo", "seinen": "Seinen", "josei": "Josei",
    "mecha": "Mecha", "ecchi": "Ecchi", "hentai": "Hentai", "yaoi": "Yaoi", "yuri": "Yuri",
}


class TextoHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []

    def handle_data(self, data):
        self.partes.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in {"br", "p", "div", "li"}:
            self.partes.append(" ")

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li"}:
            self.partes.append(" ")


def limpiar(texto):
    parser = TextoHTML()
    parser.feed(texto or "")
    return re.sub(r"\s+", " ", html.unescape("".join(parser.partes))).strip()


def titulo_preferido(atributos):
    titulos = atributos.get("titles") or {}
    candidatos = [titulos.get("en_jp"), titulos.get("en"), titulos.get("en_us"), atributos.get("canonicalTitle")]
    for indice, candidato in enumerate(candidatos):
        titulo = limpiar(candidato)
        # No inventar una lectura del kanji cuando no se ofrece una romanización.
        if titulo and not any(
            any(nombre in unicodedata.name(c, "") for nombre in ("CJK", "HIRAGANA", "KATAKANA"))
            for c in titulo
        ):
            return titulo, indice != 0
    return "", True


def espera_servidor(valor, ahora=None):
    ahora = time.time() if ahora is None else ahora
    try:
        return max(0, int(valor))
    except (ValueError, TypeError):
        try:
            return max(0, parsedate_to_datetime(valor).timestamp() - ahora)
        except (ValueError, TypeError, OverflowError):
            return 60


class Pausa(Exception):
    """Finalización controlada: el progreso se conserva."""


class Estado:
    def __init__(self, ruta, busqueda):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(ruta)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS anime (
                id TEXT PRIMARY KEY, titulo TEXT NOT NULL, titulo_alternativo INTEGER NOT NULL,
                sinopsis_original TEXT NOT NULL, generos_originales TEXT NOT NULL,
                sinopsis_es TEXT, generos_es TEXT
            );
            CREATE TABLE IF NOT EXISTS traduccion (original TEXT PRIMARY KEY, espanol TEXT NOT NULL);
        """)
        anterior = self.obtener("busqueda")
        if anterior is not None and anterior != busqueda:
            self.db.close()
            raise RuntimeError("La búsqueda difiere del progreso guardado. Usa otro archivo --estado.")
        with self.db:
            self.guardar("busqueda", busqueda)
            self.guardar("fuente", API)

    def obtener(self, clave, defecto=None):
        fila = self.db.execute("SELECT valor FROM meta WHERE clave=?", (clave,)).fetchone()
        return fila[0] if fila else defecto

    def guardar(self, clave, valor):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (clave, str(valor)))

    def cantidad(self):
        return self.db.execute("SELECT COUNT(*) FROM anime").fetchone()[0]

    def guardar_pagina(self, pagina):
        datos = pagina.get("data")
        if not isinstance(datos, list) or not isinstance(pagina.get("links"), dict):
            raise RuntimeError("Respuesta inesperada de Kitsu: se esperaba una colección JSON:API.")
        siguiente = pagina["links"].get("next")
        offset = int(self.obtener("offset", 0))
        if siguiente:
            partes = urllib.parse.urlsplit(siguiente)
            if partes.scheme != "https" or partes.netloc not in {"kitsu.io", "kitsu.app"} or partes.path != "/api/edge/anime":
                raise RuntimeError("La API devolvió una paginación inesperada.")
            siguiente_offset = int(urllib.parse.parse_qs(partes.query)["page[offset]"][0])
            if not datos or siguiente_offset <= offset:
                raise RuntimeError("La paginación no avanza; se detiene para evitar solicitudes repetidas.")
        else:
            siguiente_offset = offset + len(datos)
        generos = {
            str(g["id"]): limpiar(g.get("attributes", {}).get("name"))
            for g in pagina.get("included", []) if g.get("type") == "genres"
        }
        # Insertar la página y avanzar el cursor en una misma transacción.
        with self.db:
            for anime in datos:
                atributos = anime["attributes"]
                titulo, alternativo = titulo_preferido(atributos)
                relaciones = anime.get("relationships", {}).get("genres", {}).get("data")
                if not isinstance(relaciones, list):
                    raise RuntimeError("Faltan los géneros incluidos; no se avanzará el progreso.")
                nombres = []
                for relacion in relaciones:
                    nombre = generos.get(str(relacion["id"]))
                    if not nombre:
                        raise RuntimeError("La API omitió un género relacionado; vuelve a intentar más tarde.")
                    nombres.append(nombre)
                self.db.execute(
                    "INSERT OR IGNORE INTO anime VALUES (?, ?, ?, ?, ?, NULL, NULL)",
                    (str(anime["id"]), titulo, alternativo,
                     limpiar(atributos.get("synopsis") or atributos.get("description")),
                     json.dumps(sorted(set(nombres)), ensure_ascii=False)),
                )
            self.guardar("offset", siguiente_offset)
            self.guardar("completo", int(not siguiente))
            self.guardar("ultima_consulta_utc", datetime.now(timezone.utc).isoformat())
            if "count" in pagina.get("meta", {}):
                self.guardar("total_fuente", pagina["meta"]["count"])


class ClienteKitsu:
    def __init__(self, estado, intervalo, presupuesto, user_agent, abrir=urllib.request.urlopen):
        self.estado = estado
        self.intervalo = intervalo
        self.presupuesto = presupuesto
        self.user_agent = user_agent
        self.abrir = abrir
        self.solicitudes = 0

    def consultar(self, url):
        for intento in range(3):
            if self.solicitudes >= self.presupuesto:
                raise Pausa("Se alcanzó el máximo de solicitudes de esta ejecución. Puedes reanudar más tarde.")
            ahora = time.time()
            bloqueo = float(self.estado.obtener("no_antes_de", 0))
            if bloqueo > ahora:
                fecha = datetime.fromtimestamp(bloqueo).astimezone().isoformat(timespec="seconds")
                raise Pausa(f"Espera solicitada por el servidor. No se harán consultas antes de {fecha}.")
            ultima = float(self.estado.obtener("ultima_peticion", 0))
            espera = ultima + self.intervalo - ahora
            if espera > 0:
                time.sleep(espera)
            # Registrar también las solicitudes fallidas y conservar la pausa entre ejecuciones.
            with self.estado.db:
                self.estado.guardar("ultima_peticion", time.time())
            self.solicitudes += 1
            peticion = urllib.request.Request(url, headers={
                "User-Agent": self.user_agent,
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            })
            try:
                with self.abrir(peticion, timeout=30) as respuesta:
                    tipo = respuesta.headers.get("Content-Type", "")
                    if "json" not in tipo.lower():
                        raise Pausa("La API devolvió HTML u otro formato. Puede ser una página de bloqueo.")
                    return json.load(respuesta)
            except urllib.error.HTTPError as error:
                error.close()
                if error.code in {403, 429}:
                    segundos = max(60, espera_servidor(error.headers.get("Retry-After")))
                    if error.code == 403:
                        segundos = max(segundos, 3600)
                    with self.estado.db:
                        self.estado.guardar("no_antes_de", time.time() + segundos)
                    raise Pausa(f"HTTP {error.code}: se detiene la descarga. Espera al menos {math.ceil(segundos)} segundos.") from error
                if error.code < 500:
                    raise RuntimeError(f"Kitsu devolvió HTTP {error.code}; revisa la configuración.") from error
                if error.headers.get("Retry-After"):
                    segundos = max(60, espera_servidor(error.headers["Retry-After"]))
                    with self.estado.db:
                        self.estado.guardar("no_antes_de", time.time() + segundos)
                    raise Pausa(f"HTTP {error.code}: el servidor solicita esperar {math.ceil(segundos)} segundos.") from error
                error_transitorio = error
            except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
                error_transitorio = error
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                raise Pausa("La API no devolvió JSON válido; se conserva el cursor.") from error
            if intento == 2:
                raise Pausa(f"Tres fallos de red/servidor: {error_transitorio}. Reanuda más tarde.")
            if self.solicitudes >= self.presupuesto:
                raise Pausa("Se agotó el presupuesto de solicitudes con los reintentos; reanuda más tarde.")
            retraso = max(self.intervalo, 10 * (2 ** intento))
            LOG.warning("Fallo temporal. Próximo intento en %.0f segundos.", retraso)
            time.sleep(retraso)


def recopilar(estado, cliente, limite):
    while estado.obtener("completo", "0") != "1":
        cantidad = estado.cantidad()
        if limite and cantidad >= limite:
            break
        tamano = min(20, limite - cantidad) if limite else 20
        parametros = {
            "page[limit]": tamano, "page[offset]": estado.obtener("offset", 0),
            "sort": "id", "include": "genres",
            "fields[anime]": "titles,canonicalTitle,synopsis,description,genres",
            "fields[genres]": "name",
        }
        busqueda = estado.obtener("busqueda", "")
        if busqueda:
            parametros["filter[text]"] = busqueda
        pagina = cliente.consultar(API + "?" + urllib.parse.urlencode(parametros))
        estado.guardar_pagina(pagina)
        LOG.info("Guardados: %d; total informado por la fuente: %s; solicitudes: %d/%d",
                 estado.cantidad(), estado.obtener("total_fuente", "desconocido"),
                 cliente.solicitudes, cliente.presupuesto)


def traducir_pendientes(estado, traductor):
    def traducir(texto):
        if not texto:
            return ""
        fila = estado.db.execute("SELECT espanol FROM traduccion WHERE original=?", (texto,)).fetchone()
        if fila:
            return fila[0]
        resultado = traductor.traducir(texto)
        estado.db.execute("INSERT INTO traduccion VALUES (?, ?)", (texto, resultado))
        return resultado

    pendientes = estado.db.execute(
        "SELECT * FROM anime WHERE sinopsis_es IS NULL AND titulo != '' ORDER BY CAST(id AS INTEGER)"
    )
    for anime in pendientes:
        with estado.db:
            sinopsis = traducir(anime["sinopsis_original"])
            generos = [GENEROS.get(nombre.casefold()) or traducir(nombre)
                       for nombre in json.loads(anime["generos_originales"])]
            estado.db.execute("UPDATE anime SET sinopsis_es=?, generos_es=? WHERE id=?",
                              (sinopsis, "|".join(sorted(set(generos))), anime["id"]))
        LOG.info("Traducido %s: %s", anime["id"], anime["titulo"])


def exportar(estado, salida):
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_suffix(salida.suffix + ".tmp")
    cantidad = 0
    try:
        with temporal.open("w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["titulo", "sinopsis", "genero"])
            for anime in estado.db.execute(
                "SELECT titulo, sinopsis_es, generos_es FROM anime "
                "WHERE titulo != '' AND sinopsis_es IS NOT NULL AND generos_es IS NOT NULL "
                "ORDER BY CAST(id AS INTEGER)"
            ):
                escritor.writerow(tuple(anime))
                cantidad += 1
        temporal.replace(salida)
    finally:
        temporal.unlink(missing_ok=True)
    return cantidad


def argumentos(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limite", type=int, default=0, help="Máximo total de registros guardados; 0 = catálogo accesible (por sesiones).")
    parser.add_argument("--max-peticiones", type=int, default=50, help="Presupuesto de consultas a Kitsu por ejecución (incluye reintentos). Predeterminado: 50.")
    parser.add_argument("--intervalo", type=float, default=5, help="Segundos mínimos entre consultas (predeterminado: 5; mínimo configurable: 2).")
    parser.add_argument("--buscar", default="", help="Buscar por nombre; usa un --estado distinto para cada búsqueda.")
    parser.add_argument("--estado", type=Path, default=BASE / "datos/catalogo.sqlite3", help="Base de progreso y caché.")
    parser.add_argument("--salida", type=Path, default=BASE / "datos/animes.csv")
    parser.add_argument("--modelo", type=Path, default=BASE / "modelos/opus-en-es")
    parser.add_argument("--descargar-modelo", action="store_true", help="Descargar el modelo local si falta (aprox. 158 MB, una vez).")
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--solo-descargar", action="store_true", help="Guardar originales sin cargar el traductor ni exportar CSV.")
    modos.add_argument("--solo-exportar", action="store_true", help="Traducir y exportar lo guardado, sin consultar Kitsu.")
    parser.add_argument("--user-agent", default="AnimeAcademico/1.0 (proyecto educativo)")
    args = parser.parse_args(argv)
    if args.limite < 0 or args.max_peticiones < 1:
        parser.error("--limite debe ser >= 0 y --max-peticiones debe ser >= 1.")
    if not math.isfinite(args.intervalo) or args.intervalo < 2:
        parser.error("--intervalo debe ser un número finito de al menos 2 segundos.")
    rutas = [args.estado.resolve(), args.salida.resolve()]
    if rutas[0] == rutas[1]:
        parser.error("--estado y --salida deben ser archivos diferentes.")
    return args


def main(argv=None):
    args = argumentos(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    estado = None
    codigo = 0
    try:
        # Verificar el traductor antes de descargar datos, salvo el modo de originales.
        traductor = None if args.solo_descargar else TraductorLocal(args.modelo, args.descargar_modelo)
        estado = Estado(args.estado, args.buscar)
        if not args.solo_exportar:
            cliente = ClienteKitsu(estado, args.intervalo, args.max_peticiones, args.user_agent)
            try:
                recopilar(estado, cliente, args.limite)
            except Pausa as pausa:
                LOG.warning("%s", pausa)
                codigo = 2
        if traductor:
            with estado.db:
                estado.guardar("modelo_traduccion", REVISION)
            traducir_pendientes(estado, traductor)
    except KeyboardInterrupt:
        LOG.warning("Interrumpido. El progreso confirmado está guardado; vuelve a ejecutar para continuar.")
        codigo = 130
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        LOG.error("%s", error)
        codigo = 1
    finally:
        if estado is not None:
            try:
                if not args.solo_descargar:
                    cantidad = exportar(estado, args.salida)
                    LOG.info("CSV: %s (%d animes)", args.salida.resolve(), cantidad)
                total = estado.cantidad()
                sin_titulo = estado.db.execute("SELECT COUNT(*) FROM anime WHERE titulo=''").fetchone()[0]
                alternativos = estado.db.execute("SELECT COUNT(*) FROM anime WHERE titulo_alternativo=1 AND titulo!=''").fetchone()[0]
                LOG.info("Caché: %d registros; sin título latino: %d; títulos alternativos: %d.", total, sin_titulo, alternativos)
                LOG.info("Recorrido completo: %s. Progreso: %s", estado.obtener("completo", "0") == "1", args.estado.resolve())
            except (OSError, sqlite3.Error) as error:
                LOG.error("No se pudo exportar/resumir: %s. Los datos permanecen en SQLite.", error)
                codigo = 1
            finally:
                estado.db.close()
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
