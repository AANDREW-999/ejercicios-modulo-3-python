from __future__ import annotations

from pathlib import Path

import pytest

from src.bloque3.ejercicio_11_gestor_tareas_txt import agregar_tarea, ver_tareas


def test_archivo_inexistente_retorna_lista_vacia(tmp_path: Path) -> None:
    ruta = tmp_path / "tareas.txt"
    assert ver_tareas(ruta) == []


def test_agregar_y_ver_tareas(tmp_path: Path) -> None:
    ruta = tmp_path / "tareas.txt"
    agregar_tarea(" Comprar pan  ", ruta=ruta)
    agregar_tarea("Estudiar Python", ruta=ruta)
    assert ver_tareas(ruta) == ["Comprar pan", "Estudiar Python"]
    numero_2 = 2
    # Verifica que realmente hay dos líneas con salto al final.
    contenido = ruta.read_text(encoding="utf-8")
    lineas = contenido.splitlines(keepends=True)
    assert len(lineas) == numero_2
    assert all(linea.endswith("\n") for linea in lineas)


def test_crea_carpeta_si_no_existe(tmp_path: Path) -> None:
    ruta = tmp_path / "subdir" / "tareas.txt"
    agregar_tarea("Tarea en subcarpeta", ruta=ruta)
    assert ruta.exists()
    assert ver_tareas(ruta) == ["Tarea en subcarpeta"]


def test_no_permite_tareas_vacias(tmp_path: Path) -> None:
    ruta = tmp_path / "tareas.txt"
    with pytest.raises(ValueError):
        agregar_tarea("   \n  ", ruta=ruta)
