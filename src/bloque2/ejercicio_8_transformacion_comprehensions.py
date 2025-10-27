from __future__ import annotations

import re
from typing import Iterable

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

__all__ = [
    "palabras_mayusculas_largas",
    "longitudes_por_palabra",
    "menu",
    "main",
]

console = Console()

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
    texto = (
        "[bold cyan]Transformación con Comprehensions[/bold cyan]\n"
        "[dim]List + Dict Comprehensions sobre un texto[/dim]"
    )
    return Panel.fit(
        texto,
        title="Ejercicio 8",
        subtitle="split, upper, filter por longitud",
        border_style="cyan",
    )


def _panel_menu() -> Panel:
    texto = (
        "[bold]Opciones[/bold]\n"
        "1) Ejecutar ejemplo por defecto\n"
        "2) Ingresar texto personalizado\n"
        "3) Salir"
    )
    return Panel(texto, title="Menú", border_style="magenta")


def _tabla_palabras(palabras: list[str]) -> Table:
    tabla = Table(title="Palabras MAYÚSCULAS (> 5 letras)", show_lines=True)
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Palabra", justify="left", overflow="fold")
    if not palabras:
        tabla.add_row("—", "—")
        return tabla
    for indice, palabra in enumerate(palabras, start=1):
        tabla.add_row(str(indice), palabra)
    return tabla


def _tabla_longitudes(mapa: dict[str, int]) -> Table:
    tabla = Table(title="Longitudes por palabra", show_lines=True)
    tabla.add_column("Palabra", style="bold")
    tabla.add_column("Longitud", justify="right")
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
            "\n[dim]Enter para continuar (o escribe 'salir' para terminar)"
            "[/dim]",
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
