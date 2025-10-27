from __future__ import annotations

import pytest

from src.bloque1.ejercicio_4_validador_generico import (
    aplicar_validador,
    es_email_valido,
    es_mayor_a_10,
)


def test_aplicar_validador_con_emails() -> None:
    correos = [
        "ana@mail.com",
        "malo",
        "user@dominio.com",
        "x@y",
        "otro@site.org",
    ]
    filtrados = aplicar_validador(correos, es_email_valido)
    assert filtrados == ["ana@mail.com", "user@dominio.com", "otro@site.org"]


def test_aplicar_validador_con_enteros() -> None:
    numeros = [4, 11, 9, 25, 10, 13]
    filtrados = aplicar_validador(numeros, es_mayor_a_10)
    assert filtrados == [11, 25, 13]


def test_aplicar_validador_tipo_incorrecto() -> None:
    with pytest.raises(TypeError):
        aplicar_validador(("no", "lista"), es_email_valido)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        aplicar_validador(["a"], "no callable")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "correo, esperado",
    [
        ("a@b.co", True),
        ("user.name+tag@example.com", True),
        ("invalido", False),
        ("a@b", False),
        ("", False),
        (" con_espacios@dom.com ", True),
    ],
)
def test_es_email_valido(correo: str, esperado: bool) -> None:
    assert es_email_valido(correo) == esperado


@pytest.mark.parametrize(
    "numero, esperado",
    [
        (11, True),
        (10, False),
        (0, False),
        (-1, False),
        (9999, True),
    ],
)
def test_es_mayor_a_10(numero: int, esperado: bool) -> None:
    assert es_mayor_a_10(numero) == esperado
