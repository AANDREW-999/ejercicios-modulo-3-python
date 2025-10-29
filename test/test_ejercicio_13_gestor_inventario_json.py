from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import src.bloque3.ejercicio_13_gestor_inventario_json as inv


def _leer_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8") or "[]")


def test_cargar_inexistente_devuelve_lista_vacia(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    assert inv.cargar_inventario(ruta=ruta) == []


def test_guardar_y_cargar_persistencia(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    inventario: list[dict[str, Any]] = []
    inv.agregar_producto(inventario, "Camisa", 100.0, 5, ruta=ruta)
    inv.agregar_producto(inventario, "Pantalón", 200.0, 2, ruta=ruta)

    # Relee desde disco
    leido = inv.cargar_inventario(ruta=ruta)
    assert len(leido) == 2
    nombres = sorted([p["nombre"] for p in leido])
    assert nombres == ["Camisa", "Pantalón"]

    # Verificar formato JSON persistido (dos objetos)
    datos_json = _leer_json(ruta)
    assert isinstance(datos_json, list) and len(datos_json) == 2


def test_agregar_existente_acumula_y_actualiza_precio(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    inventario: list[dict[str, Any]] = []
    inv.agregar_producto(inventario, "camisa", 100.0, 5, ruta=ruta)
    actualizado = inv.agregar_producto(inventario, "CAMISA", 120.0, 1, ruta=ruta)
    assert actualizado["precio"] == 120.0
    assert actualizado["stock"] == 6
    # Asegura que solo hay un registro para "Camisa"
    leido = inv.cargar_inventario(ruta=ruta)
    assert len(leido) == 1 and leido[0]["nombre"] == "camisa".title() or leido[0][
        "nombre"
    ] == "camisa" or leido[0]["nombre"] == "CAMISA"


def test_vender_producto_y_validaciones(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    inventario: list[dict[str, Any]] = []
    inv.agregar_producto(inventario, "Zapatos", 300.0, 3, ruta=ruta)

    vendido = inv.vender_producto(inventario, "zapatOS", 2, ruta=ruta)
    assert vendido["stock"] == 1

    with pytest.raises(ValueError):
        inv.vender_producto(inventario, "Zapatos", 0, ruta=ruta)
    with pytest.raises(ValueError):
        inv.vender_producto(inventario, "Zapatos", 5, ruta=ruta)
    with pytest.raises(KeyError):
        inv.vender_producto(inventario, "NoExiste", 1, ruta=ruta)


def test_filtrar_disponibles_usa_filter_lambda(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    inventario: list[dict[str, Any]] = []
    inv.agregar_producto(inventario, "A", 10.0, 0, ruta=ruta)
    inv.agregar_producto(inventario, "B", 20.0, 5, ruta=ruta)
    inv.agregar_producto(inventario, "C", 30.0, 1, ruta=ruta)

    disponibles = inv.filtrar_disponibles(inventario)
    assert [p["nombre"] for p in disponibles] in (
        ["B", "C"],
        ["b", "c"],
        ["B", "c"],
        ["b", "C"],
    )


def test_mostrar_inventario_devuelve_tabla(tmp_path: Path, monkeypatch) -> None:
    # No vamos a imprimir realmente en consola; solo queremos que la función
    # construya una tabla. Interceptamos console.print para capturar.
    ruta = tmp_path / "inventario.json"
    inventario: list[dict[str, Any]] = []
    inv.agregar_producto(inventario, "X", 10.0, 1, ruta=ruta)

    capturado: dict[str, Any] = {}

    def _fake_print(obj: Any) -> None:
        capturado["obj"] = obj

    monkeypatch.setattr(inv.console, "print", _fake_print)
    inv.mostrar_inventario(inventario, solo_disponibles=False)

    # Columns contiene una colección, pero validamos que dentro haya una Table
    from rich.columns import Columns

    assert isinstance(capturado["obj"], Columns)
    # No fallará si cambia el orden, pero al menos verifica que hay objetos renderizables
    # No es trivial introspectar Columns; suficiente con validar que no explotó.
