from __future__ import annotations

from collections.abc import Callable

from src.modulo3.ejercicio_3_contador_closure import crear_contador


def test_incrementos_secuenciales() -> None:
    c = crear_contador()
    assert callable(c)
    assert isinstance(c, Callable)
    secuencia = [c(), c(), c()]
    assert secuencia == list(range(1, len(secuencia) + 1))


def test_contadores_independientes() -> None:
    c1 = crear_contador()
    c2 = crear_contador()

    operaciones = [("c1", c1), ("c1", c1), ("c2", c2), ("c1", c1), ("c2", c2)]
    resultados: list[int] = []
    for _, fn in operaciones:
        resultados.append(fn())

    # Esperado sin valores mágicos: contar ocurrencias por alias
    conteo = {"c1": 0, "c2": 0}
    esperado: list[int] = []
    for nombre, _ in operaciones:
        conteo[nombre] += 1
        esperado.append(conteo[nombre])

    assert resultados == esperado


def test_tipo_retorno_entero() -> None:
    c = crear_contador()
    valor = c()
    assert isinstance(valor, int)
