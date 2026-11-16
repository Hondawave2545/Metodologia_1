"""Prueba de arranque de la API con el comando documentado.

Levanta el comando que figura en el README.md, acotado a loopback, y comprueba
que el documento de contrato y la interfaz de documentacion responden y que el
contrato describe exactamente las cinco operaciones de la API.

El comando se lee del README para que la documentacion y la prueba no puedan
divergir. Solo se adaptan el interprete (el que corre las pruebas) y el puerto
(uno libre, para no chocar con una demostracion manual).
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
README = PROJECT_ROOT / "README.md"

START_MARKER = "<!-- comando-de-arranque: inicio -->"
END_MARKER = "<!-- comando-de-arranque: fin -->"

EXPECTED_OPERATIONS = {
    ("/clinics/{clinic_id}/appointments", "post"),
    ("/clinics/{clinic_id}/appointments/{appointment_id}", "get"),
    ("/clinics/{clinic_id}/appointments/{appointment_id}", "patch"),
    ("/clinics/{clinic_id}/appointments/{appointment_id}/cancel", "post"),
    ("/clinics/{clinic_id}/availability", "get"),
}


def _documented_command() -> str:
    """Extrae del README el comando de arranque documentado."""

    text = README.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        raise AssertionError(
            "El README.md no documenta el comando de arranque entre "
            f"{START_MARKER!r} y {END_MARKER!r}."
        )
    block = text.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    commands = [line for line in lines if "uvicorn" in line]
    if len(commands) != 1:
        raise AssertionError(
            f"Se esperaba un unico comando de arranque en el README.md, hay {len(commands)}."
        )
    return commands[0]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _wait_for(url: str, process: subprocess.Popen, timeout: float = 30.0) -> str:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(
                f"El proceso de la API termino con codigo {process.returncode}."
            )
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.read().decode("utf-8")
        except (urllib.error.URLError, ConnectionError, OSError) as error:
            last_error = error
            time.sleep(0.25)
    output = ""
    if process.stdout is not None:
        process.stdout.flush()
    raise AssertionError(f"La API no respondio en {url}: {last_error}. Salida: {output}")


class StartupTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.database_path = Path(temporary_directory.name) / "appointments.sqlite3"

        command = _documented_command()
        self.assertIn("uvicorn", command)
        self.assertIn("src.api.main:app", command)
        self.assertIn("--host 127.0.0.1", command)

        self.port = _free_port()
        # El puerto se sustituye sobre el comando completo: "--port 8000" son dos
        # argumentos separados y el reemplazo debe atravesar el espacio.
        command = re.sub(r"--port\s+\d+", f"--port {self.port}", command)
        arguments = command.split()
        if arguments[0].lower().endswith(("python.exe", "python")):
            arguments[0] = sys.executable

        environment = os.environ.copy()
        environment["APPOINTMENTS_DB_PATH"] = str(self.database_path)
        self.process = subprocess.Popen(
            arguments,
            cwd=PROJECT_ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        def stop() -> None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
            if self.process.stdout is not None:
                self.process.stdout.close()

        self.addCleanup(stop)

    def test_documented_command_serves_the_contract_and_the_documentation(self):
        base_url = f"http://127.0.0.1:{self.port}"

        contract = _wait_for(f"{base_url}/openapi.json", self.process)
        documentation = _wait_for(f"{base_url}/docs", self.process)

        self.assertIn("openapi", json.loads(contract))
        self.assertTrue(documentation.strip())

    def test_contract_describes_exactly_the_five_operations_and_no_listing(self):
        base_url = f"http://127.0.0.1:{self.port}"
        contract = json.loads(_wait_for(f"{base_url}/openapi.json", self.process))

        operations = {
            (path, method)
            for path, definition in contract["paths"].items()
            for method in definition
            if method in {"get", "post", "put", "patch", "delete"}
        }

        self.assertEqual(EXPECTED_OPERATIONS, operations)

        # Listado de turnos: no puede haber un GET sobre la coleccion.
        collection_path = "/clinics/{clinic_id}/appointments"
        self.assertNotIn("get", contract["paths"][collection_path])
        self.assertEqual(
            {"post"},
            {
                method
                for method in contract["paths"][collection_path]
                if method in {"get", "post", "put", "patch", "delete"}
            },
        )

    def test_api_only_listens_on_loopback(self):
        base_url = f"http://127.0.0.1:{self.port}"
        _wait_for(f"{base_url}/openapi.json", self.process)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(2)
            self.assertEqual(
                0,
                probe.connect_ex(("127.0.0.1", self.port)),
                "La API deberia estar escuchando en loopback.",
            )


if __name__ == "__main__":
    unittest.main()
