from __future__ import annotations

import re
from typing import Iterable

# NUEVO: estilos y cajas
from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

__all__ = [
    "palabras_mayusculas_largas",
    "longitudes_por_palabra",
    "menu",
    "main",
]

# NUEVO: tema para Ejercicio 8 (naranja/dorado)
THEME = Theme(
    {
        "title": "bold orange3",
        "subtitle": "dim",
        "accent": "orange3",
        "menu.border": "gold3",
        "menu.number": "bold orange3",
        "menu.option": "bold white",
        "label": "bold white",
        "value": "bright_white",  # corregido (antes: "bright white")
        "success": "green3",
        "warning": "yellow3",
        "error": "red3",
        "info": "cyan3",
    }
)
console = Console(theme=THEME)

_PATRON_PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


def palabras_mayusculas_largas(
    texto: str,
    min_longitud: int = 5,
) -> list[str]:
    """Obtiene palabras con más de `min_longitud` letras en MAYÚSCULAS.

    Usa List Comprehension para:
      - tokenizar por palabras (letras, incluyendo acentos en español),
      - filtrar por longitud estrictamente mayor a `min_longitud`,
      - convertir a mayúsculas.

    Args:
        texto: Texto de entrada.
        min_longitud: Umbral de longitud. Por defecto 5 (=> > 5).

    Returns:
        Lista de palabras transformadas a mayúsculas, en orden de aparición.
    """
    tokens = _PATRON_PALABRA.findall(texto)
    return [t.upper() for t in tokens if len(t) > int(min_longitud)]


def longitudes_por_palabra(palabras: Iterable[str]) -> dict[str, int]:
    """Construye un diccionario {PALABRA: longitud} con Dict Comprehension.

    Args:
        palabras: Secuencia de palabras (idealmente ya en MAYÚSCULAS).

    Returns:
        Diccionario con la longitud de cada palabra. Si una palabra se repite,
        la clave se sobrescribe con el mismo valor (idempotente).
    """
    return {p: len(p) for p in palabras}


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    # NUEVO: cabecera centrada y caja doble
    cuerpo = Align.center(
        Text.assemble(
            Text(" Transformación con Comprehensions ", style="title"),
            "\n",
            Text("List + Dict Comprehensions sobre un texto", style="subtitle"),
        )
    )
    return Panel(
        cuerpo,
        title="Ejercicio 8",
        subtitle="split, upper, filter por longitud",
        border_style="accent",
        box=DOUBLE,
        padding=(1, 2),
    )


def _panel_menu() -> Panel:
    # NUEVO: opciones coloreadas y caja pesada
    texto = (
        "[menu.number]1)[/menu.number] [menu.option]Ejemplo por defecto[/menu.option]\n"
        "[menu.number]2)[/menu.number] [menu.option]Texto personalizado[/menu.option]\n"
        "[menu.number]3)[/menu.number] [menu.option]Salir[/menu.option]"
    )
    return Panel(texto, title="Menú", border_style="menu.border", box=HEAVY)


def _tabla_palabras(palabras: list[str]) -> Table:
    tabla = Table(
        title="Palabras MAYÚSCULAS (> 5 letras)",
        show_lines=True,
        box=ROUNDED,
        header_style="label",
        title_style="label",
    )
    tabla.add_column("#", justify="right", style="label", no_wrap=True)
    tabla.add_column("Palabra", justify="left", overflow="fold", style="value")
    if not palabras:
        tabla.add_row("—", "—")
        return tabla
    for indice, palabra in enumerate(palabras, start=1):
        tabla.add_row(str(indice), palabra)
    return tabla


def _tabla_longitudes(mapa: dict[str, int]) -> Table:
    tabla = Table(
        title="Longitudes por palabra",
        show_lines=True,
        box=ROUNDED,
        header_style="label",
        title_style="label",
    )
    tabla.add_column("Palabra", style="label")
    tabla.add_column("Longitud", justify="right", style="value")
    if not mapa:
        tabla.add_row("—", "—")
        return tabla
    for palabra, longitud in sorted(mapa.items(), key=lambda kv: kv[0]):
        tabla.add_row(palabra, str(longitud))
    return tabla


def _flujo_con_texto(texto: str) -> None:
    palabras = palabras_mayusculas_largas(texto, min_longitud=5)
    conteos = longitudes_por_palabra(palabras)
    paneles = [
        _tabla_palabras(palabras),
        _tabla_longitudes(conteos),
        Panel.fit(
            f"[bold white]Total palabras:[/bold white] {len(palabras)}",
            border_style="green",
            title="Resumen",
        ),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def _flujo_ejemplo() -> None:
    texto = (
        "Hola mundo! La programación en Python permite escribir soluciones "
        "claras, concisas y mantenibles. Documentación extensa y pruebas "
        "automatizadas mejoran la calidad."
    )
    _flujo_con_texto(texto)


def _flujo_personalizado() -> None:
    texto = Prompt.ask(
        "Ingresa un texto (usa oraciones con puntuación y acentos si quieres)",
        default=(
            "Este es un texto de ejemplo para probar comprehensions y MAYÚSCULAS."
        ),
    )
    _flujo_con_texto(texto)


def menu() -> None:
    """Interfaz interactiva con Rich para transformar y contar palabras."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[bold]Elige una opción[/bold]",
            choices=["1", "2", "3"],
            default="1",
        )

        if opcion == "1":
            _flujo_ejemplo()
        elif opcion == "2":
            _flujo_personalizado()
        elif opcion == "3":
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
            "\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]"
        )
