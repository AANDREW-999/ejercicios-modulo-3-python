from __future__ import annotations

from typing import Any

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

__all__ = ["extraer_precios_con_descuento", "menu", "main"]

console = Console()


def extraer_precios_con_descuento(
    productos: list[dict[str, Any]], descuento: float = 0.10
) -> list[float]:
    """Devuelve una lista con los precios tras aplicar un descuento.

    Se usa programación funcional con map y lambda.

    Args:
        productos: Lista de diccionarios con al menos la clave "precio".
        descuento: Descuento en rango [0, 1]. Ejemplo: 0.10 para 10%.

    Returns:
        Lista de precios con descuento (redondeados a 2 decimales).

    Raises:
        TypeError: Si productos no es lista de dict o precio no es numérico.
        ValueError: Si descuento no está en [0, 1].
    """
    if not (0.0 <= float(descuento) <= 1.0):
        raise ValueError("descuento debe estar en el rango [0, 1].")
    if not isinstance(productos, list):
        raise TypeError("productos debe ser una lista.")
    for producto in productos:
        if not isinstance(producto, dict):
            raise TypeError("Cada elemento de productos debe ser dict.")
        if "precio" not in producto:
            raise TypeError("Cada dict debe incluir la clave 'precio'.")
        if not isinstance(producto["precio"], (int, float)):
            raise TypeError("El valor 'precio' debe ser numérico.")

    factor = 1.0 - float(descuento)
    # Uso explícito de map + lambda (requisito del ejercicio)
    return list(
        map(lambda p: round(float(p["precio"]) * factor, 2), productos)
    )


# ---------------------------
# Utilidades de interfaz
# ---------------------------


def _panel_titulo() -> Panel:
    texto = (
        "[bold cyan]Procesamiento con map y lambda[/bold cyan]\n"
        "[dim]Extrae precios con descuento desde productos[/dim]"
    )
    return Panel.fit(
        texto, title="Ejercicio 6", subtitle="map + lambda", border_style="cyan"
    )


def _panel_menu() -> Panel:
    texto = (
        "[bold]Opciones[/bold]\n"
        "1) Ejecutar ejemplo por defecto (10% de descuento)\n"
        "2) Ingresar productos y descuento personalizado\n"
        "3) Salir"
    )
    return Panel(texto, title="Menú", border_style="magenta")


def _tabla_productos(productos: list[dict[str, Any]]) -> Table:
    tabla = Table(title="Productos", show_lines=True, expand=True)
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Nombre")
    tabla.add_column("Precio", justify="right")
    if not productos:
        tabla.add_row("—", "—", "—")
        return tabla
    for indice, producto in enumerate(productos, start=1):
        nombre = str(producto.get("nombre", "—"))
        precio = float(producto.get("precio", 0.0))
        tabla.add_row(str(indice), nombre, f"{precio:.2f}")
    return tabla


def _tabla_precios(precios: list[float], descuento: float) -> Table:
    tabla = Table(
        title=f"Precios con descuento ({descuento*100:.0f}%)",
        show_lines=True,
        expand=True,
    )
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Precio descontado", justify="right")
    if not precios:
        tabla.add_row("—", "—")
        return tabla
    for indice, precio in enumerate(precios, start=1):
        tabla.add_row(str(indice), f"{precio:.2f}")
    return tabla


def _parse_productos(texto: str) -> list[dict[str, Any]]:
    """Convierte 'Nombre:Precio, Nombre:Precio' a lista de dicts."""
    if not texto.strip():
        return []
    productos: list[dict[str, Any]] = []
    partes = [t for t in texto.split(",") if t.strip()]
    for parte in partes:
        if ":" not in parte:
            # Formato inválido: se ignora silenciosamente
            # (UX; podrías lanzar ValueError si prefieres)
            continue
        nombre_txt, precio_txt = parte.split(":", 1)
        nombre = nombre_txt.strip()
        precio_str = precio_txt.strip().replace(",", ".")
        try:
            precio = float(precio_str)
        except ValueError:
            continue
        productos.append({"nombre": nombre or "—", "precio": precio})
    return productos


# ---------------------------
# Interfaz interactiva
# ---------------------------


def _flujo_ejemplo() -> None:
    productos = [
        {"nombre": "Camisa", "precio": 50000},
        {"nombre": "Pantalón", "precio": 80000},
        {"nombre": "Zapatos", "precio": 120000},
        {"nombre": "Medias", "precio": 9000},
    ]
    descuento = 0.10
    precios_desc = extraer_precios_con_descuento(productos, descuento)
    paneles = [
        _tabla_productos(productos),
        _tabla_precios(precios_desc, descuento),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def _flujo_personalizado() -> None:
    texto = Prompt.ask(
        "Ingresa productos 'Nombre:Precio' separados por coma",
        default="Camisa:50000, Pantalón:80000, Zapatos:120000",
    )
    productos = _parse_productos(texto)
    descuento = FloatPrompt.ask(
        "Descuento (0 a 1). Ej: 0.10 para 10%", default=0.10
    )
    try:
        precios_desc = extraer_precios_con_descuento(productos, descuento)
    except (TypeError, ValueError) as exc:
        console.print(
            Panel.fit(
                f"[red]Error:[/red] {exc}",
                border_style="red",
                title="Entrada inválida",
            )
        )
        return

    paneles = [
        _tabla_productos(productos),
        _tabla_precios(precios_desc, descuento),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def menu() -> None:
    """Interfaz interactiva con Rich para aplicar descuentos a productos."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        try:
            opcion = IntPrompt.ask(
                "[bold]Elige una opción[/bold]", choices=["1", "2", "3"]
            )
        except Exception:
            opcion = 3
        numero_2 = 2
        numero_3 = 3
        if opcion == 1:
            _flujo_ejemplo()
        elif opcion == numero_2:
            _flujo_personalizado()
        elif opcion == numero_3:
            break

        _ = Prompt.ask(
            "\n[dim]Enter para continuar (o escribe 'salir' para terminar)[/dim]",
            default="",
        )
        if _.strip().lower() == "salir":
            break


def main() -> None:
    """Punto de entrada: solo invoca el menú."""
    menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            "\n\n[bold red]Programa interrumpido por el usuario. "
            "Adiós.[/bold red]"
        )
