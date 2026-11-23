"""Traducción local inglés → español con OPUS-MT y CTranslate2."""

import hashlib
import logging
import re
import urllib.error
import urllib.request
from pathlib import Path

LOG = logging.getLogger(__name__)
REVISION = "76ec296588e2234f9b7dfad5254219a0f5ecb7af"
BASE_MODELO = (
    "https://huggingface.co/michaelfeil/ct2fast-opus-mt-en-es/resolve/"
    + REVISION + "/"
)
ARCHIVOS = {
    "model.bin": "36cd9bcb181fc6d5832deeaf770ce183ff4edbbc5e4fe0f86cec92da4379f3b7",
    "config.json": "0c2f6fa2057c7264d052fb4a62ba3476eeae70487acddfa8e779a53a00cbf44c",
    "source.spm": "4dd547c24816a335e7b0b2e63376a8f1b3cbfc671eda5ab808dd44fdadaa8791",
    "target.spm": "e236ee6d866b635c0142114f8647f39831f9d92534aa2aad75c942f6a78ad0e3",
    "shared_vocabulary.txt": "77aee99211b7b8e569e0fb5b95dac01aba9f31bca2d1380b1fc6050797825ec6",
}


def preparar_modelo(carpeta: Path, descargar: bool) -> None:
    """Descarga una versión fija; nunca deja un archivo incompleto como definitivo."""
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, esperado in ARCHIVOS.items():
        destino = carpeta / nombre
        if destino.exists():
            if esperado:
                with destino.open("rb") as archivo:
                    digest = hashlib.file_digest(archivo, "sha256").hexdigest()
                if digest != esperado:
                    raise RuntimeError(f"Modelo dañado: {destino}. Elimina ese archivo y vuelve a descargarlo.")
            continue
        if not descargar:
            raise RuntimeError("Falta el modelo de traducción. Ejecuta con --descargar-modelo una vez.")
        LOG.info("Descargando %s (modelo completo: aproximadamente 158 MB)...", nombre)
        temporal = destino.with_suffix(destino.suffix + ".part")
        try:
            peticion = urllib.request.Request(BASE_MODELO + nombre, headers={"User-Agent": "AnimeAcademico/1.0"})
            digest = hashlib.sha256()
            with urllib.request.urlopen(peticion, timeout=60) as respuesta, temporal.open("wb") as archivo:
                while bloque := respuesta.read(1024 * 1024):
                    digest.update(bloque)
                    archivo.write(bloque)
            if esperado and digest.hexdigest() != esperado:
                raise RuntimeError(f"La verificación SHA-256 falló para {nombre}.")
            temporal.replace(destino)
        except (OSError, urllib.error.URLError) as error:
            raise RuntimeError(f"No se pudo descargar {nombre}: {error}") from error
        finally:
            temporal.unlink(missing_ok=True)


class TraductorLocal:
    def __init__(self, carpeta: Path, descargar: bool = False):
        try:
            import ctranslate2
            import sentencepiece
        except ImportError as error:
            raise RuntimeError("Instala las dependencias: python -m pip install -r requirements.txt") from error
        preparar_modelo(carpeta, descargar)
        self.tokenizador = sentencepiece.SentencePieceProcessor(model_file=str(carpeta / "source.spm"))
        self.destino = sentencepiece.SentencePieceProcessor(model_file=str(carpeta / "target.spm"))
        self.motor = ctranslate2.Translator(str(carpeta), device="cpu", compute_type="int8", intra_threads=2)

    def traducir(self, texto: str) -> str:
        if not texto.strip():
            return ""
        # Dividir primero por oraciones y después por tokens evita truncar sinopsis largas.
        fragmentos = []
        for oracion in re.split(r"(?<=[.!?])\s+", texto):
            tokens = self.tokenizador.encode(oracion, out_type=str)
            fragmentos.extend(tokens[i:i + 180] + ["</s>"] for i in range(0, len(tokens), 180))
        traducciones = self.motor.translate_batch(
            fragmentos, beam_size=4, max_batch_size=8,
            max_input_length=0, max_decoding_length=800, replace_unknowns=True,
        )
        partes = [self.destino.decode(resultado.hypotheses[0]) for resultado in traducciones]
        resultado = " ".join(partes).strip()
        if not resultado:
            raise RuntimeError("El modelo devolvió una traducción vacía; el registro queda pendiente.")
        return resultado
