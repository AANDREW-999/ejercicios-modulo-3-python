from __future__ import annotations

from src.bloque2.ejercicio_8_transformacion_comprehensions import (
    longitudes_por_palabra,
    palabras_mayusculas_largas,
)


def test_lista_palabras_mayusculas_y_longas() -> None:
    texto = (
        "Hola mundo! Programación en Python, pruebas y documentación extensa."
    )
    resultado = palabras_mayusculas_largas(texto, min_longitud=5)
    esperado = [
        "PROGRAMACIÓN",
        "PYTHON",
        "PRUEBAS",
        "DOCUMENTACIÓN",
        "EXTENSA",
    ]
    assert resultado == esperado


def test_longitudes_por_palabra() -> None:
    palabras = ["PROGRAMACIÓN", "PYTHON", "PRUEBAS", "DOCUMENTACIÓN", "EXTENSA"]
    conteos = longitudes_por_palabra(palabras)
    assert conteos["PROGRAMACIÓN"] == len("PROGRAMACIÓN")
    assert conteos["PYTHON"] == len("PYTHON")
    assert conteos["PRUEBAS"] == len("PRUEBAS")
    assert conteos["DOCUMENTACIÓN"] == len("DOCUMENTACIÓN")
    assert conteos["EXTENSA"] == len("EXTENSA")


def test_excluye_longitud_cinco() -> None:
    texto = "corto LARGO media exacto Cinco letras"
    # Palabras de len 5 (Cinco) no deben aparecer (condición es > 5)
    resultado = palabras_mayusculas_largas(texto, min_longitud=5)
    assert "CINCO" not in resultado


def test_mantiene_orden_de_aparicion() -> None:
    texto = "uno dos tres programar organizar Programar"
    res = palabras_mayusculas_largas(texto, min_longitud=5)
    assert res == ["PROGRAMAR", "ORGANIZAR", "PROGRAMAR"]
