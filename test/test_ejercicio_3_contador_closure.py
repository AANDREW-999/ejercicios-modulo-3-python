from __future__ import annotations

from collections.abc import Callable

from src.modulo3.ejercicio_3_contador_closure import crear_contador


def test_incrementos_secuenciales() -> None:
    c = crear_contador()
    assert callable(c)
    assert isinstance(c, Callable)
    assert c() == 1
    assert c() == 2
    assert c() == 3


def test_contadores_independientes() -> None:
    c1 = crear_contador()
    c2 = crear_contador()

    assert c1() == 1
    assert c1() == 2
    assert c2() == 1
    assert c1() == 3
    assert c2() == 2


def test_tipo_retorno_entero() -> None:
    c = crear_contador()
    valor = c()
    assert isinstance(valor, int)