"""Pruebas unitarias para las funciones de negocio de la calculadora de IMC."""

import math

import pytest

from src.bloque1.ejercicio_1_refactorizacion_calculadora_imc import (
    calcular_imc,
    interpretar_imc,
)


@pytest.mark.parametrize(
    ("peso", "altura", "esperado"),
    [
        (70.0, 1.75, 22.86),
        (80.0, 1.80, 24.69),
        (45.0, 1.60, 17.58),
        (95.0, 1.70, 32.87),
        (120.0, 2.00, 30.0),
        (500.0, 2.50, 80.0),
    ],
)
def test_calcular_imc(peso: float, altura: float, esperado: float) -> None:
    """Valida el cálculo de IMC en casos típicos."""
    assert calcular_imc(peso, altura) == pytest.approx(esperado, abs=0.01)


@pytest.mark.parametrize(
    ("peso", "altura"),
    [
        (0.0, 1.75),
        (-50.0, 1.75),
        (70.0, 0.0),
        (70.0, -1.80),
    ],
)
def test_calcular_imc_valores_invalidos(peso: float, altura: float) -> None:
    """Verifica que se lancen errores con pesos/alturas inválidos."""
    with pytest.raises(ValueError):
        calcular_imc(peso, altura)


@pytest.mark.parametrize(
    ("imc", "esperado"),
    [
        (18.49, "Bajo peso"),
        (18.5, "Normal"),
        (24.99, "Normal"),
        (25.0, "Sobrepeso"),
        (29.99, "Sobrepeso"),
        (30.0, "Obesidad"),
        (35.0, "Obesidad"),
        (18.499, "Bajo peso"),
        (18.501, "Normal"),
        (24.999, "Normal"),
        (25.001, "Sobrepeso"),
        (29.999, "Sobrepeso"),
        (30.001, "Obesidad"),
    ],
)
def test_interpretar_imc_rangos(imc: float, esperado: str) -> None:
    """Comprueba la interpretación del IMC en bordes y rangos intermedios."""
    assert interpretar_imc(imc) == esperado


@pytest.mark.parametrize("valor_invalido", [0.0, -1e-6, -10.0])
def test_interpretar_imc_invalido(valor_invalido: float) -> None:
    """Confirma que valores no positivos de IMC generan ValueError."""
    with pytest.raises(ValueError):
        interpretar_imc(valor_invalido)


def test_integracion_calculo_mas_interpretacion() -> None:
    """Prueba de integración: calcular IMC y clasificarlo."""
    imc = calcular_imc(70.0, 1.75)
    categoria = interpretar_imc(imc)
    assert math.isfinite(imc)
    assert categoria == "Normal"
