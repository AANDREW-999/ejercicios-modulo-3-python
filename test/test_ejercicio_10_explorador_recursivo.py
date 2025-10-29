from __future__ import annotations

from src.bloque2.ejercicio_10_explorador_recursivo import (
    explorar_estructura,
    filtrar_atomos,
)


def test_ejemplo_basico_lista_y_dict() -> None:
    estructura = [1, [2, 3], {"a": 4}]
    pares = explorar_estructura(estructura)
    assert pares == [(1, 1), (2, 2), (3, 2), (4, 2)]


def test_diccionarios_anidados_y_listas() -> None:
    estructura = {"x": {"y": 10}, "arr": [0, {"k": 1}]}
    # Orden esperado: valores recorriendo por orden de inserción del dict:
    # - "x" -> dict -> 10 a profundidad 2
    # - "arr" -> lista -> 0 a profundidad 2, 1 a profundidad 3
    pares = explorar_estructura(estructura)
    assert pares == [(10, 2), (0, 2), (1, 3)]


def test_valor_atomico_raiz() -> None:
    pares = explorar_estructura("texto")
    assert pares == [("texto", 1)]


def test_filtrar_atomos_en_mixto() -> None:
    datos = ["a", [1, 2], {"k": 3}, 4, ("x", "y")]
    atomos = filtrar_atomos(datos)
    # Solo 'a' y 4 son atómicos al nivel superior
    assert atomos == ["a", 4]


def test_profundiad_invalida_da_error() -> None:
    try:
        explorar_estructura([1, 2], profundidad=0)
        assert False, "Se esperaba ValueError"
    except ValueError:
        assert True
