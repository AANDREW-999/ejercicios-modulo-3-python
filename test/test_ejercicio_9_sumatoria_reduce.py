from __future__ import annotations

import pytest

from src.bloque2.ejercicio_9_sumatoria_reduce import (
    concatenar_reduce,
    sumatoria_reduce,
)


def test_sumatoria_ejemplo() -> None:
    numeros = [1, 2, 3, 4, 5]
    total = sumatoria_reduce(numeros)
    assert total == pytest.approx(15.0, abs=1e-9)


def test_concatenacion_ejemplo() -> None:
    partes = ["Hola", " ", "SENA", "!"]
    frase = concatenar_reduce(partes)
    assert frase == "Hola SENA!"


def test_sumatoria_vacia_da_cero() -> None:
    assert sumatoria_reduce([]) == 0.0


def test_concatenacion_vacia_da_vacio() -> None:
    assert concatenar_reduce([]) == ""


def test_sumatoria_con_floats() -> None:
    numeros = [1.5, 2.25, 0.25]
    total = sumatoria_reduce(numeros)
    assert total == pytest.approx(4.0, abs=1e-9)


def test_validaciones_tipo() -> None:
    with pytest.raises(TypeError):
        sumatoria_reduce([1, "x", 3])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        concatenar_reduce(["ok", 2])  # type: ignore[list-item]
