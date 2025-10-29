from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.bloque3.ejercicio_12_analizador_csv import analizar_csv


def _crear_csv_tmp(tmp_path: Path, nombre: str) -> Path:
    ruta = tmp_path / nombre
    filas = [
        {"nombre": "Ana", "edad": "20", "calificacion": "4.5"},
        {"nombre": "Juan", "edad": "22", "calificacion": "2.8"},
        {"nombre": "María", "edad": "21", "calificacion": "3.9"},
        {"nombre": "Luis", "edad": "23", "calificacion": "4.8"},
        {"nombre": "Sofía", "edad": "20", "calificacion": "3.5"},
    ]
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(
            fh, fieldnames=["nombre", "edad", "calificacion"]
        )
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def test_analiza_columna_calificacion(tmp_path: Path) -> None:
    ruta = _crear_csv_tmp(tmp_path, "est.csv")
    res = analizar_csv(str(ruta), "calificacion")
    # Valores: 4.5, 2.8, 3.9, 4.8, 3.5
    assert res["max"] == pytest.approx(4.8, abs=0.01)
    assert res["min"] == pytest.approx(2.8, abs=0.01)
    assert res["promedio"] == pytest.approx(3.9, abs=0.01)


def test_analiza_columna_edad(tmp_path: Path) -> None:
    ruta = _crear_csv_tmp(tmp_path, "est2.csv")
    res = analizar_csv(str(ruta), "edad")
    # Valores: 20, 22, 21, 23, 20
    assert res["max"] == 23
    assert res["min"] == 20
    assert res["promedio"] == pytest.approx(21.2, abs=0.01)


def test_columna_inexistente(tmp_path: Path) -> None:
    ruta = _crear_csv_tmp(tmp_path, "est3.csv")
    with pytest.raises(KeyError):
        analizar_csv(str(ruta), "nota")


def test_ignora_no_numericos(tmp_path: Path) -> None:
    ruta = tmp_path / "est4.csv"
    filas = [
        {"nombre": "A", "edad": "20", "calificacion": "4.5"},
        {"nombre": "B", "edad": "x", "calificacion": "mala"},
        {"nombre": "C", "edad": "22.5", "calificacion": ""},
    ]
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(
            fh, fieldnames=["nombre", "edad", "calificacion"]
        )
        escritor.writeheader()
        escritor.writerows(filas)

    res_edad = analizar_csv(str(ruta), "edad")  # usa 20 y 22.5
    assert res_edad["max"] == pytest.approx(22.5, abs=0.01)
    assert res_edad["min"] == pytest.approx(20.0, abs=0.01)
    assert res_edad["promedio"] == pytest.approx(21.25, abs=0.01)

    with pytest.raises(ValueError):
        analizar_csv(str(ruta), "calificacion")  # no hay numéricos válidos


def test_archivo_no_existe() -> None:
    with pytest.raises(FileNotFoundError):
        analizar_csv("no_existe.csv", "edad")