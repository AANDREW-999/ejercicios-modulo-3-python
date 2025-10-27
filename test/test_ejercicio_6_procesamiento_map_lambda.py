from __future__ import annotations

import pytest

from src.bloque2.ejercicio_6_procesamiento_map_lambda import (
    extraer_precios_con_descuento,
)


def test_descuento_10_por_ciento() -> None:
    productos = [
        {"nombre": "Camisa", "precio": 50000},
        {"nombre": "Pantalón", "precio": 80000},
        {"nombre": "Zapatos", "precio": 120000},
        {"nombre": "Medias", "precio": 9000},
    ]
    precios = extraer_precios_con_descuento(productos, 0.10)
    assert precios == [45000.0, 72000.0, 108000.0, 8100.0]


def test_descuento_personalizado() -> None:
    productos = [
        {"nombre": "A", "precio": 100.0},
        {"nombre": "B", "precio": 199.99},
    ]
    precios = extraer_precios_con_descuento(productos, 0.25)
    assert precios == [75.0, 149.99]


def test_redondeo_dos_decimales() -> None:
    """Verifica que el resultado se redondea a 2 decimales de forma consistente."""
    precio_unitario = 123.456
    descuento = 0.1234
    factor = 1 - descuento
    esperado = round(precio_unitario * factor, 2)  # 108.2215296 -> 108.22

    productos = [{"nombre": "A", "precio": precio_unitario}]
    precios = extraer_precios_con_descuento(productos, descuento)

    assert precios == [esperado]


def test_entradas_invalidas() -> None:
    with pytest.raises(ValueError):
        extraer_precios_con_descuento([], -0.1)
    with pytest.raises(TypeError):
        extraer_precios_con_descuento(  # type: ignore[arg-type]
            "no lista", 0.1
        )
    with pytest.raises(TypeError):
        extraer_precios_con_descuento([{"nombre": "X"}], 0.1)
    with pytest.raises(TypeError):
        extraer_precios_con_descuento([{"precio": "xx"}], 0.1)
