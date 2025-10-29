from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pytest

from src.bloque3.ejercicio_14_generador_reportes import (
    generar_reporte,
    leer_csv_estudiantes,
    leer_json_cursos,
)


def _csv_tmp(tmp_path: Path, nombre: str, filas: list[dict[str, Any]]) -> Path:
    ruta = tmp_path / nombre
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=["nombre", "cursos"])
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def _json_tmp_mapa(tmp_path: Path, nombre: str, mapa: dict[str, str]) -> Path:
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(mapa, ensure_ascii=False), encoding="utf-8")
    return ruta


def _json_tmp_lista(tmp_path: Path, nombre: str, lista: list[dict[str, str]]) -> Path:
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(lista, ensure_ascii=False), encoding="utf-8")
    return ruta


def test_lectura_csv_basica(tmp_path: Path) -> None:
    ruta = _csv_tmp(
        tmp_path,
        "est.csv",
        [
            {"nombre": "Ana", "cursos": "PY;JS"},
            {"nombre": "SinNombre", "cursos": ""},
            {"nombre": "Juan", "cursos": "DB; ;PY"},
        ],
    )
    estudiantes = leer_csv_estudiantes(str(ruta))
    assert estudiantes[0]["nombre"] == "Ana"
    assert estudiantes[0]["cursos"] == ["PY", "JS"]
    assert estudiantes[1]["cursos"] == ["DB", "PY"]


def test_lectura_json_formato_mapa_y_lista(tmp_path: Path) -> None:
    ruta_mapa = _json_tmp_mapa(tmp_path, "c1.json", {"PY": "Python", "JS": "JS"})
    ruta_lista = _json_tmp_lista(
        tmp_path, "c2.json", [{"id": "DB", "nombre": "Bases"}]
    )
    cursos_mapa = leer_json_cursos(str(ruta_mapa))
    cursos_lista = leer_json_cursos(str(ruta_lista))
    assert cursos_mapa["PY"] == "Python"
    assert cursos_mapa["JS"] == "JS"
    assert cursos_lista["DB"] == "Bases"


def test_generar_reporte_combina_y_filtra(tmp_path: Path) -> None:
    ruta_csv = _csv_tmp(
        tmp_path,
        "est.csv",
        [
            {"nombre": "Ana", "cursos": "PY;JS"},
            {"nombre": "María", "cursos": "XXX;PY; ;NO"},
            {"nombre": "Sofía", "cursos": ""},
        ],
    )
    ruta_json = _json_tmp_mapa(
        tmp_path, "cursos.json", {"PY": "Python", "JS": "JavaScript"}
    )
    estudiantes = leer_csv_estudiantes(str(ruta_csv))
    cursos = leer_json_cursos(str(ruta_json))
    reporte = generar_reporte(estudiantes, cursos)
    lineas = [l for l in reporte.splitlines() if l.strip()]
    assert lineas[0] == "Ana: Python, JavaScript"
    # XXX y NO no existen -> se filtran. Cadena vacía también se filtra
    assert lineas[1] == "María: Python"
    assert lineas[2] == "Sofía: (sin cursos)"


def test_validaciones_y_errores(tmp_path: Path) -> None:
    # CSV sin encabezados válidos
    ruta_mala = tmp_path / "bad.csv"
    ruta_mala.write_text("x,y\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        leer_csv_estudiantes(str(ruta_mala))

    # JSON estructura no compatible
    ruta_json_mal = tmp_path / "bad.json"
    ruta_json_mal.write_text(json.dumps(123), encoding="utf-8")
    with pytest.raises(ValueError):
        leer_json_cursos(str(ruta_json_mal))

    # Archivos inexistentes
    with pytest.raises(FileNotFoundError):
        leer_csv_estudiantes("no_existe.csv")
    with pytest.raises(FileNotFoundError):
        leer_json_cursos("no_existe.json")


def test_reporte_termina_con_salto_de_linea(tmp_path: Path) -> None:
    ruta_csv = _csv_tmp(
        tmp_path,
        "est.csv",
        [{"nombre": "Ana", "cursos": "PY"}],
    )
    ruta_json = _json_tmp_mapa(tmp_path, "cursos.json", {"PY": "Python"})
    estudiantes = leer_csv_estudiantes(str(ruta_csv))
    cursos = leer_json_cursos(str(ruta_json))
    reporte = generar_reporte(estudiantes, cursos)
    assert reporte.endswith("\n")
