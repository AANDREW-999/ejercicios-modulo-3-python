from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import src.bloque3.ejercicio_15_biblioteca_json as bib


def _guardar_tmp(path: Path, libros: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(libros, ensure_ascii=False, indent=2), encoding="utf-8")


def test_cargar_y_guardar_biblioteca(tmp_path: Path) -> None:
    ruta = tmp_path / "biblioteca.json"
    libros = [
        {"libro_id": "001", "titulo": "Rayuela", "prestado_a": None},
        {"libro_id": "002", "titulo": "Cien años de soledad", "prestado_a": None},
    ]
    _guardar_tmp(ruta, libros)
    cargado = bib.cargar_biblioteca(ruta=ruta)
    assert len(cargado) == 2
    # Persistencia tras guardar
    bib.guardar_biblioteca(cargado, ruta=ruta)
    re = bib.cargar_biblioteca(ruta=ruta)
    assert re[0]["libro_id"] == "001"


def test_prestar_y_devolver_validaciones(tmp_path: Path) -> None:
    ruta = tmp_path / "biblioteca.json"
    libros = [
        {"libro_id": "A1", "titulo": "Libro A", "prestado_a": None},
        {"libro_id": "B2", "titulo": "Libro B", "prestado_a": None},
    ]
    _guardar_tmp(ruta, libros)
    biblioteca = bib.cargar_biblioteca(ruta=ruta)

    prestado = bib.prestar_libro(biblioteca, "a1", "Ana", ruta=ruta)
    assert prestado["prestado_a"] == "Ana"

    with pytest.raises(ValueError):
        bib.prestar_libro(biblioteca, "A1", "Otra", ruta=ruta)
    with pytest.raises(KeyError):
        bib.prestar_libro(biblioteca, "NO", "X", ruta=ruta)

    devuelto = bib.devolver_libro(biblioteca, "A1", ruta=ruta)
    assert devuelto["prestado_a"] is None

    with pytest.raises(ValueError):
        bib.devolver_libro(biblioteca, "A1", ruta=ruta)
    with pytest.raises(KeyError):
        bib.devolver_libro(biblioteca, "NO", ruta=ruta)


def test_buscar_y_filtrar_prestados(tmp_path: Path) -> None:
    ruta = tmp_path / "biblioteca.json"
    libros = [
        {"libro_id": "1", "titulo": "Python Básico", "prestado_a": "Ana"},
        {"libro_id": "2", "titulo": "JavaScript Avanzado", "prestado_a": None},
        {"libro_id": "3", "titulo": "Introducción a Bases de Datos", "prestado_a": "Luis"},
    ]
    _guardar_tmp(ruta, libros)
    biblioteca = bib.cargar_biblioteca(ruta=ruta)

    encontrados = bib.buscar_libro(biblioteca, "python")
    assert [l["libro_id"] for l in encontrados] == ["1"]

    prestados = bib.ver_libros_prestados(biblioteca)
    assert sorted([l["libro_id"] for l in prestados]) == ["1", "3"]


def test_mostrar_libros_no_revienta(tmp_path: Path, monkeypatch) -> None:
    # No validamos el rendering; solo que la llamada no falle y que imprima algo.
    ruta = tmp_path / "biblioteca.json"
    libros = [
        {"libro_id": "10", "titulo": "X", "prestado_a": None},
    ]
    _guardar_tmp(ruta, libros)
    biblioteca = bib.cargar_biblioteca(ruta=ruta)

    capturado: dict[str, Any] = {}

    def _fake_print(obj: Any) -> None:
        capturado["obj"] = obj

    monkeypatch.setattr(bib.console, "print", _fake_print)
    bib.mostrar_libros(biblioteca, "Prueba")
    assert "obj" in capturado