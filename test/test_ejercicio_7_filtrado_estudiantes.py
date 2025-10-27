from __future__ import annotations

import pytest
from src.bloque2.ejercicio_7_filtrado_estudiantes import filtrar_aprobados


def test_ejemplo_por_defecto() -> None:
    estudiantes = [("Ana", 4.5), ("Juan", 2.8), ("Maria", 3.9)]
    aprobados = filtrar_aprobados(estudiantes, 3.0)
    assert aprobados == [("Ana", 4.5), ("Maria", 3.9)]


def test_umbral_personalizado() -> None:
    estudiantes = [("A", 2.9), ("B", 3.0), ("C", 4.0)]
    aprobados = filtrar_aprobados(estudiantes, 4.0)
    assert aprobados == [("C", 4.0)]


def test_incluye_borde() -> None:
    estudiantes = [("A", 3.0), ("B", 2.99)]
    aprobados = filtrar_aprobados(estudiantes, 3.0)
    assert aprobados == [("A", 3.0)]


def test_validaciones_tipo_y_rango() -> None:
    with pytest.raises(ValueError):
        filtrar_aprobados([("A", 3.5)], -0.1)
    with pytest.raises(ValueError):
        filtrar_aprobados([("A", 3.5)], 5.1)
    with pytest.raises(TypeError):
        filtrar_aprobados("no lista", 3.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        filtrar_aprobados([("A",)], 3.0)  # tupla de longitud incorrecta
    with pytest.raises(TypeError):
        filtrar_aprobados([(1, 3.0)], 3.0)  # nombre no es str
    with pytest.raises(TypeError):
        filtrar_aprobados([("A", "3.0")], 3.0)  # nota no numérica
