from __future__ import annotations

import re
from collections.abc import Callable
from typing import TypeVar

from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

__all__ = [
    "aplicar_validador",
    "es_email_valido",
    "es_mayor_a_10",
    "menu",
    "main",
]

# NUEVO: tema y consola estilizada
THEME = Theme(
    {
        "title": "bold cyan",
        "subtitle": "dim",
        "accent": "magenta",
        "menu.border": "blue",
        "menu.number": "bold cyan",
        "menu.option": "bold white",
        "label": "bold white",
        "value": "bright_white",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "cyan",
    }
)
console = Console(theme=THEME)
T = TypeVar("T")

# Constantes para opciones del menú (evitar valores mágicos)
OPCION_VALIDAR = 1
OPCION_FILTRAR = 2
OPCION_SALIR = 3


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

_PATRON_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


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
    """Construye el panel de título principal.

    Args:
        None

    Returns:
        Panel con título y subtítulo del ejercicio.
    """
    # NUEVO: cabecera centrada y caja doble
    titulo = Text(" Validador de Datos Genérico ", style="title")
    sub = Text("Funciones de orden superior + Rich UI", style="subtitle")
    cuerpo = Align.center(Text.assemble(titulo, "\n", sub))
    return Panel(
        cuerpo,
        title="Ejercicio 4",
        subtitle="Callable, Type Hints",
        border_style="accent",
        box=DOUBLE,
        padding=(1, 2),
    )


def _panel_menu() -> Panel:
    """Construye el panel con las opciones del menú.

    Args:
        None

    Returns:
        Panel con las opciones disponibles.
    """
    # NUEVO: opciones coloreadas y caja pesada
    texto = (
        "[menu.number]1)[/menu.number] "
        "[menu.option]Validar correos electrónicos[/menu.option]\n"
        "[menu.number]2)[/menu.number] "
        "[menu.option]Filtrar números mayores a 10[/menu.option]\n"
        "[menu.number]3)[/menu.number] "
        "[menu.option]Salir[/menu.option]"
    )
    return Panel(
        Align.left(texto),
        title="Menú",
        border_style="menu.border",
        box=HEAVY,
        padding=(1, 2),
    )


def _tabla_lista(titulo: str, elementos: list[str]) -> Table:
    """Crea una tabla simple con índice y valor.

    Args:
        titulo: Título a mostrar en la tabla.
        elementos: Lista de elementos a renderizar.

    Returns:
        Tabla con dos columnas (# y Valor). Si la lista está vacía,
        muestra una fila con guiones.
    """
    tabla = Table(
        title=titulo,
        show_lines=True,
        expand=True,
        box=ROUNDED,
        header_style="label",
        title_style="label",
    )
    tabla.add_column("#", justify="right", style="label", no_wrap=True)
    tabla.add_column("Valor", overflow="fold", style="value")
    if not elementos:
        tabla.add_row("—", "—")
        return tabla
    for indice, valor in enumerate(elementos, start=1):
        tabla.add_row(str(indice), str(valor))
    return tabla


def _panel_resumen(total: int, validos: int) -> Panel:
    """Construye un panel con el resumen de validación.

    Args:
        total: Cantidad total evaluada.
        validos: Cantidad que pasó la validación.

    Returns:
        Panel con totales de válidos e inválidos.
    """
    texto = (
        f"[label]Total:[/label] [value]{total}[/value]\n"
        f"[success]Válidos:[/success] [value]{validos}[/value]\n"
        f"[error]Inválidos:[/error] [value]{total - validos}[/value]"
    )
    return Panel.fit(
        texto,
        title="Resumen",
        border_style="success",
        box=ROUNDED,
    )


def _parse_csv_texto(texto: str) -> list[str]:
    """Convierte una cadena CSV en lista de textos.

    Args:
        texto: Cadena con valores separados por comas.

    Returns:
        Lista de tokens no vacíos, sin espacios laterales.
    """
    if not texto.strip():
        return []
    return [parte.strip() for parte in texto.split(",") if parte.strip()]


def _parse_csv_enteros(texto: str) -> tuple[list[int], list[str]]:
    """Parsea enteros desde una cadena CSV.

    Args:
        texto: Cadena con enteros separados por comas.

    Returns:
        Una tupla (numeros_validos, tokens_invalidos):
        - numeros_validos: Lista de ints parseados correctamente.
        - tokens_invalidos: Lista de tokens que no pudieron convertirse.
    """
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
    """Interfaz interactiva con Rich para validar datos.

    Args:
        None

    Returns:
        None
    """
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(Rule(style="accent"))
        console.print(_panel_menu())

        try:
            opcion = IntPrompt.ask(
                "[bold]Elige una opción[/bold]",
                choices=["1", "2", "3"],
            )
        except Exception:
            opcion = OPCION_SALIR

        if opcion == OPCION_VALIDAR:
            _flujo_validar_correos()
        elif opcion == OPCION_FILTRAR:
            _flujo_filtrar_mayores()
        elif opcion == OPCION_SALIR:
            break

        # NUEVO: separador y prompt de continuación con estilo
        console.print(Rule(style="accent"))
        seguir = Prompt.ask(
            "[dim]Enter para continuar (o escribe 'salir' para terminar)[/dim]",
            default="",
        )
        if seguir.strip().lower() == "salir":
            break


def _flujo_validar_correos() -> None:
    """Flujo interactivo para validar correos ingresados por el usuario.

    Args:
        None

    Returns:
        None
    """
    console.print(Rule(Text(" Validación de correos ", style="title"), style="accent"))
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
    # NUEVO: enmarca los paneles para mayor cohesión visual
    console.print(
        Panel(
            Columns(paneles, equal=True, expand=True),
            border_style="accent",
            box=ROUNDED,
        )
    )


def _flujo_filtrar_mayores() -> None:
    """Flujo interactivo para filtrar enteros mayores a 10.

    Args:
        None

    Returns:
        None
    """
    console.print(Rule(Text(" Números mayores a 10 ", style="title"), style="accent"))
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
            (
                "[warning]Ignorados:[/warning] "
                f"[value]{', '.join(tokens_invalidos)}[/value]"
            ),
            title="Tokens no numéricos",
            border_style="warning",
            box=ROUNDED,
        )
        paneles.append(aviso)

    console.print(
        Panel(
            Columns(paneles, equal=True, expand=True),
            border_style="accent",
            box=ROUNDED,
        )
    )


def main() -> None:
    """Punto de entrada: invoca el menú.

    Args:
        None

    Returns:
        None
    """
    menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            "\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]"
        )
