from __future__ import annotations

import re
from collections.abc import Callable
from typing import TypeVar

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

__all__ = [
    "aplicar_validador",
    "es_email_valido",
    "es_mayor_a_10",
    "menu",
    "main",
]

console = Console()
T = TypeVar("T")


def aplicar_validador(datos: list[T], validador: Callable[[T], bool]) -> list[T]:
    """Filtra una lista aplicando una función validadora a cada elemento.

    Args:
        datos: Lista de elementos a validar.
        validador: Función que recibe un elemento y devuelve True si pasa.

    Returns:
        Nueva lista con los elementos que pasan la validación.

    Raises:
        TypeError: Si datos no es lista o validador no es invocable.
    """
    if not isinstance(datos, list):
        raise TypeError("datos debe ser una lista.")
    if not callable(validador):
        raise TypeError("validador debe ser invocable (callable).")

    return [elemento for elemento in datos if bool(validador(elemento))]


# ---------------------------
# Validadores de ejemplo
# ---------------------------

_PATRON_EMAIL = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)


def es_email_valido(correo: str) -> bool:
    """Valida un correo con una expresión regular simple.

    Args:
        correo: Dirección de correo a verificar.

    Returns:
        True si el formato es válido, False en caso contrario.
    """
    if not isinstance(correo, str):
        return False
    texto = correo.strip()
    if not texto or " " in texto:
        return False
    return bool(_PATRON_EMAIL.match(texto))


def es_mayor_a_10(numero: int) -> bool:
    """Indica si un número entero es mayor a 10.

    Args:
        numero: Número a evaluar.

    Returns:
        True si numero > 10; False en otro caso o si no es int.
    """
    num = 10
    if not isinstance(numero, int):
        return False
    return numero > num


# ---------------------------
# Utilidades de interfaz
# ---------------------------


def _panel_titulo() -> Panel:
    texto = (
        "[bold cyan]Validador de Datos Genérico[/bold cyan]\n"
        "[dim]Funciones de orden superior + Rich UI[/dim]"
    )
    return Panel.fit(
        texto,
        title="Ejercicio 4",
        subtitle="Callable, Type Hints",
        border_style="cyan",
    )


def _panel_menu() -> Panel:
    texto = (
        "[bold]Opciones[/bold]\n"
        "1) Validar correos electrónicos\n"
        "2) Filtrar números mayores a 10\n"
        "3) Salir"
    )
    return Panel(texto, title="Menú", border_style="blue")


def _tabla_lista(titulo: str, elementos: list[str]) -> Table:
    tabla = Table(title=titulo, show_lines=True, expand=True)
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Valor", overflow="fold")
    if not elementos:
        tabla.add_row("—", "—")
        return tabla
    for indice, valor in enumerate(elementos, start=1):
        tabla.add_row(str(indice), str(valor))
    return tabla


def _panel_resumen(total: int, validos: int) -> Panel:
    texto = (
        f"[bold white]Total:[/bold white] {total}\n"
        f"[bold green]Válidos:[/bold green] {validos}\n"
        f"[bold red]Inválidos:[/bold red] {total - validos}"
    )
    return Panel.fit(texto, title="Resumen", border_style="green")


def _parse_csv_texto(texto: str) -> list[str]:
    if not texto.strip():
        return []
    return [parte.strip() for parte in texto.split(",") if parte.strip()]


def _parse_csv_enteros(texto: str) -> tuple[list[int], list[str]]:
    """Devuelve (numeros_validos, tokens_invalidos)."""
    if not texto.strip():
        return [], []
    numeros: list[int] = []
    invalidos: list[str] = []
    for token in texto.split(","):
        pieza = token.strip()
        if not pieza:
            continue
        try:
            numero = int(pieza)
        except ValueError:
            invalidos.append(pieza)
        else:
            numeros.append(numero)
    return numeros, invalidos


# ---------------------------
# Interfaz interactiva
# ---------------------------


def menu() -> None:
    """Interfaz interactiva con Rich para validar datos."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        try:
            opcion = IntPrompt.ask(
                "[bold]Elige una opción[/bold]",
                choices=["1", "2", "3"],
            )
        except Exception:
            opcion = 3
        numero_1 = 1
        numero_2 = 2
        numero_3 = 3
        if opcion == numero_1:
            _flujo_validar_correos()
        elif opcion == numero_2:
            _flujo_filtrar_mayores()
        elif opcion == numero_3:
            break

        _ = Prompt.ask(
            "\n[dim]Enter para continuar (o escribe 'salir' para terminar)[/dim]",
            default="",
        )
        if _.strip().lower() == "salir":
            break


def _flujo_validar_correos() -> None:
    console.rule("[bold]Validación de correos[/bold]")
    entrada = Prompt.ask(
        "Ingresa correos separados por comas",
        default="ana@mail.com, malo, user@dominio.com",
    )
    correos = _parse_csv_texto(entrada)
    validos = aplicar_validador(correos, es_email_valido)
    no_validos = [c for c in correos if c not in validos]

    paneles = [
        _tabla_lista("Válidos", validos),
        _tabla_lista("Inválidos", no_validos),
        _panel_resumen(len(correos), len(validos)),
    ]
    console.print(Columns(paneles, equal=True))


def _flujo_filtrar_mayores() -> None:
    console.rule("[bold]Números mayores a 10[/bold]")
    entrada = Prompt.ask(
        "Ingresa números enteros separados por comas",
        default="4, 11, 9, 25, x, 10, 13",
    )
    numeros, tokens_invalidos = _parse_csv_enteros(entrada)
    mayores = aplicar_validador(numeros, es_mayor_a_10)
    no_mayores = [n for n in numeros if n not in mayores]

    paneles = [
        _tabla_lista("Mayores a 10", [str(n) for n in mayores]),
        _tabla_lista("No mayores", [str(n) for n in no_mayores]),
        _panel_resumen(len(numeros), len(mayores)),
    ]
    if tokens_invalidos:
        aviso = Panel(
            f"[yellow]Ignorados:[/yellow] {', '.join(tokens_invalidos)}",
            title="Tokens no numéricos",
            border_style="yellow",
        )
        paneles.append(aviso)

    console.print(Columns(paneles, equal=True))


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
