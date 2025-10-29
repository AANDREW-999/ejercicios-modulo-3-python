from __future__ import annotations

from functools import reduce
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

__all__ = ["sumatoria_reduce", "concatenar_reduce", "menu", "main"]

# NUEVO: tema para Ejercicio 9 (púrpura)
THEME = Theme(
    {
        "title": "bold medium_purple3",
        "subtitle": "dim",
        "accent": "medium_purple3",
        "menu.border": "plum3",
        "menu.number": "bold medium_purple3",
        "menu.option": "bold white",
        "label": "bold white",
        "value": "bright_white",
        "success": "spring_green3",
        "warning": "yellow3",
        "error": "red3",
        "info": "cyan3",
    }
)
console = Console(theme=THEME)


def sumatoria_reduce(numeros: Iterable[float | int]) -> float:
    """Suma todos los elementos usando functools.reduce y lambda.

    Args:
        numeros: Colección de números (int o float).

    Returns:
        La suma total como float. Para colección vacía, retorna 0.0.

    Raises:
        TypeError: Si algún elemento no es numérico.
    """
    lista = list(numeros)
    if any(not isinstance(n, (int, float)) for n in lista):
        raise TypeError("Todos los elementos deben ser numéricos (int o float).")
    return reduce(lambda acc, x: acc + float(x), lista, 0.0)


def concatenar_reduce(partes: Iterable[str]) -> str:
    """Concatena todos los strings usando functools.reduce y lambda.

    Args:
        partes: Colección de cadenas.

    Returns:
        La concatenación completa. Para colección vacía, retorna "".

    Raises:
        TypeError: Si algún elemento no es str.
    """
    lista = list(partes)
    if any(not isinstance(s, str) for s in lista):
        raise TypeError("Todos los elementos deben ser cadenas (str).")
    return reduce(lambda acc, s: acc + s, lista, "")


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    # NUEVO: cabecera centrada y caja doble
    cuerpo = Align.center(
        Text.assemble(
            Text(" Sumatoria y Concatenación con reduce ", style="title"),
            "\n",
            Text("functools.reduce + lambda", style="subtitle"),
        )
    )
    return Panel(
        cuerpo,
        title="Ejercicio 9",
        subtitle="Programación funcional",
        border_style="accent",
        box=DOUBLE,
        padding=(1, 2),
    )


def _panel_menu() -> Panel:
    # NUEVO: opciones coloreadas y caja pesada
    texto = (
        "[menu.number]1)[/menu.number]"
        " [menu.option]Ejemplos por defecto[/menu.option]\n"
        "[menu.number]2)[/menu.number]"
        " [menu.option]Listas personalizadas[/menu.option]\n"
        "[menu.number]3)[/menu.number] [menu.option]Salir[/menu.option]"
    )
    return Panel(texto, title="Menú", border_style="menu.border", box=HEAVY)


def _tabla_lista_numeros(titulo: str, numeros: list[float]) -> Table:
    tabla = Table(
        title=titulo,
        show_lines=True,
        expand=True,
        box=ROUNDED,
        header_style="label",
        title_style="label",
    )
    tabla.add_column("#", justify="right", style="label", no_wrap=True)
    tabla.add_column("Número", justify="right", style="value")
    if not numeros:
        tabla.add_row("—", "—")
        return tabla
    for indice, numero in enumerate(numeros, start=1):
        tabla.add_row(str(indice), f"{float(numero):.2f}")
    return tabla


def _panel_resultado_suma(valor: float) -> Panel:
    return Panel.fit(
        f"[label]Suma total:[/label] [success]{valor:.2f}[/success]",
        title="Resultado suma",
        border_style="success",
        box=ROUNDED,
    )


def _tabla_lista_textos(titulo: str, textos: list[str]) -> Table:
    tabla = Table(
        title=titulo,
        show_lines=True,
        expand=True,
        box=ROUNDED,
        header_style="label",
        title_style="label",
    )
    tabla.add_column("#", justify="right", style="label", no_wrap=True)
    tabla.add_column("Texto", overflow="fold", style="value")
    if not textos:
        tabla.add_row("—", "—")
        return tabla
    for indice, texto in enumerate(textos, start=1):
        tabla.add_row(str(indice), texto)
    return tabla


def _panel_resultado_concat(texto: str) -> Panel:
    return Panel.fit(
        f"[label]Concatenación:[/label] [success]{texto}[/success]",
        title="Resultado concatenación",
        border_style="success",
        box=ROUNDED,
    )


def _parse_csv_numeros(texto: str) -> list[float]:
    if not texto.strip():
        return []
    numeros: list[float] = []
    for token in texto.split(","):
        pieza = token.strip().replace(",", ".")
        if not pieza:
            continue
        try:
            numero = float(pieza)
        except ValueError:
            continue
        numeros.append(numero)
    return numeros


def _parse_csv_textos(texto: str) -> list[str]:
    if not texto.strip():
        return []
    return [p.strip() for p in texto.split(",") if p.strip()]


def _flujo_ejemplo() -> None:
    numeros = [1, 2, 3, 4, 5]
    textos = ["Hola", " ", "SENA", "!"]

    suma_total = sumatoria_reduce(numeros)
    frase = concatenar_reduce(textos)

    paneles = [
        _tabla_lista_numeros("Números (ejemplo)", [float(n) for n in numeros]),
        _panel_resultado_suma(suma_total),
        _tabla_lista_textos("Partes (ejemplo)", textos),
        _panel_resultado_concat(frase),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def _flujo_personalizado() -> None:
    entrada_nums = Prompt.ask(
        "Ingresa números separados por coma", default="1, 2, 3, 4, 5"
    )
    entrada_txts = Prompt.ask(
        "Ingresa textos separados por coma", default="Hola,  , SENA, !"
    )
    numeros = _parse_csv_numeros(entrada_nums)
    textos = _parse_csv_textos(entrada_txts)

    try:
        suma_total = sumatoria_reduce(numeros)
        frase = concatenar_reduce(textos)
    except TypeError as exc:
        console.print(
            Panel.fit(
                f"[red]Error:[/red] {exc}", border_style="red", title="Entrada inválida"
            )
        )
        return

    paneles = [
        _tabla_lista_numeros("Números", numeros),
        _panel_resultado_suma(suma_total),
        _tabla_lista_textos("Textos", textos),
        _panel_resultado_concat(frase),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def menu() -> None:
    """Interfaz interactiva con Rich para reduce (suma y concatenación)."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[bold]Elige una opción[/bold]", choices=["1", "2", "3"], default="1"
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
            "\n\n[bold red]Programa interrumpido por el usuario. "
            "Adiós.[/bold red]"
        )
