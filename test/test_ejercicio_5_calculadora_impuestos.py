from __future__ import annotations

import math

import pytest

from src.bloque1 import ejercicio_5_calculadora_impuestos as mod


@pytest.fixture(autouse=True)
def _restaurar_tasa() -> None:
    """Restaura la tasa global tras cada prueba."""
    tasa_original = mod.TASA_IVA
    yield
    mod.actualizar_tasa_iva(tasa_original)


def test_calcular_iva_por_defecto() -> None:
    # TASA_IVA por defecto = 0.19
    precio_base = 100.0
    iva = mod.calcular_iva(precio_base)
    assert iva == pytest.approx(19.0, abs=0.01)


def test_actualizar_tasa_afecta_calculo() -> None:
    precio_base = 100.0
    _ = mod.calcular_iva(precio_base)  # 19.0 con 0.19
    mod.actualizar_tasa_iva(0.2)
    iva_nuevo = mod.calcular_iva(precio_base)
    assert iva_nuevo == pytest.approx(20.0, abs=0.01)


def test_validaciones() -> None:
    with pytest.raises(ValueError):
        mod.calcular_iva(-1.0)
    for tasa in (-0.1, 1.5):
        with pytest.raises(ValueError):
            mod.actualizar_tasa_iva(tasa)


def test_redondeo_dos_decimales() -> None:
    mod.actualizar_tasa_iva(0.19)
    precio_base = 19999.99
    iva = mod.calcular_iva(precio_base)
    esperado = round(precio_base * 0.19, 2)
    assert math.isfinite(iva)
    assert iva == esperado


def test_cambio_multiple_de_tasa() -> None:
    precio_base = 250.0
    mod.actualizar_tasa_iva(0.1)
    iva_1 = mod.calcular_iva(precio_base)  # 25.0
    mod.actualizar_tasa_iva(0.21)
    iva_2 = mod.calcular_iva(precio_base)  # 52.5
    assert iva_1 == pytest.approx(25.0, abs=0.01)
    assert iva_2 == pytest.approx(52.5, abs=0.01)
