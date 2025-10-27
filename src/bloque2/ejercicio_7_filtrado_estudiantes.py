from __future__ import annotations

from typing import Iterable

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

__all__ = ["filtrar_aprobados", "menu", "main"]

# Constantes para evitar valores mágicos
NOTA_MIN: float = 0.0
NOTA_MAX: float = 5.0
PAR_ESTRUCTURA_TAM: int = 2
OPCION_EJEMPLO: int = 1
OPCION_PERSONALIZADA: int = 2
OPCION_SALIR: int = 3

console = Console()


def filtrar_aprobados(
    estudiantes: list[tuple[str, float]],
    nota_minima: float = 3.0,
) -> list[tuple[str, float]]:
    """Devuelve solo los estudiantes con nota >= nota_minima.

    Se implementa usando filter() y una función lambda.

    Args:
        estudiantes: Lista de tuplas (nombre, nota).
        nota_minima: Nota mínima de aprobación. Por defecto 3.0.

    Returns:
        Nueva lista con los estudiantes que aprobaron, respetando el orden.

    Raises:
        TypeError: Si la estructura de estudiantes no es válida.
        ValueError: Si nota_minima no está en el rango [0, 5].
    """
    if not (NOTA_MIN <= float(nota_minima) <= NOTA_MAX):
        raise ValueError("nota_minima debe estar en el rango [0, 5].")
    if not isinstance(estudiantes, list):
        raise TypeError("estudiantes debe ser una lista de tuplas.")
    for par in estudiantes:
        if not isinstance(par, tuple) or len(par) != PAR_ESTRUCTURA_TAM:
            raise TypeError("Cada elemento debe ser una tupla (nombre, nota).")
        nombre, nota = par
        if not isinstance(nombre, str):
            raise TypeError("El nombre debe ser str.")
        if not isinstance(nota, (int, float)):
            raise TypeError("La nota debe ser numérica (int o float).")

    return list(
        filter(
            lambda par: float(par[1]) >= float(nota_minima),
            estudiantes,
        )
    )


# ---------------------------
# Utilidades de interfaz
# ---------------------------


def _panel_titulo() -> Panel:
    texto = (
        "[bold cyan]Filtrado de Estudiantes con filter + lambda[/bold cyan]\n"
        "[dim]Obtén únicamente los aprobados[/dim]"
    )
    return Panel.fit(
        texto,
        title="Ejercicio 7",
        subtitle="Programación funcional",
        border_style="cyan",
    )


def _panel_menu() -> Panel:
    texto = (
        "[bold]Opciones[/bold]\n"
        "1) Ejecutar ejemplo por defecto (nota mínima 3.0)\n"
        "2) Ingresar lista y nota mínima personalizada\n"
        "3) Salir"
    )
    return Panel(texto, title="Menú", border_style="magenta")


def _tabla_estudiantes(
    titulo: str,
    items: Iterable[tuple[str, float]],
) -> Table:
    tabla = Table(title=titulo, show_lines=True, expand=True)
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Nombre")
    tabla.add_column("Nota", justify="right")
    vacio = True
    for indice, (nombre, nota) in enumerate(items, start=1):
        vacio = False
        tabla.add_row(str(indice), nombre, f"{float(nota):.2f}")
    if vacio:
        tabla.add_row("—", "—", "—")
    return tabla


def _panel_resumen(total: int, aprobados: int, nota_minima: float) -> Panel:
    texto = (
        f"[bold white]Total:[/bold white] {total}\n"
        f"[bold green]Aprobados (>= {nota_minima:.2f}):[/bold green] "
        f"{aprobados}\n"
        f"[bold red]No aprobados:[/bold red] {total - aprobados}"
    )
    return Panel.fit(texto, title="Resumen", border_style="green")


def _parse_estudiantes(texto: str) -> list[tuple[str, float]]:
    """Convierte 'Nombre:Nota, Nombre:Nota' en lista de tuplas."""
    if not texto.strip():
        return []
    pares: list[tuple[str, float]] = []
    piezas = [t for t in texto.split(",") if t.strip()]
    for pieza in piezas:
        if ":" not in pieza:
            # UX: ignoramos entradas inválidas silenciosamente
            continue
        nombre_txt, nota_txt = pieza.split(":", 1)
        nombre = nombre_txt.strip()
        try:
            nota = float(nota_txt.strip().replace(",", "."))
        except ValueError:
            continue
        pares.append((nombre or "—", nota))
    return pares


# ---------------------------
# Interfaz interactiva
# ---------------------------


def _flujo_ejemplo() -> None:
    estudiantes = [("Ana", 4.5), ("Juan", 2.8), ("Maria", 3.9)]
    nota_minima = 3.0
    aprobados = filtrar_aprobados(estudiantes, nota_minima)
    no_aprobados = [e for e in estudiantes if e not in aprobados]

    paneles = [
        _tabla_estudiantes("Ingresados", estudiantes),
        _tabla_estudiantes("Aprobados", aprobados),
        _tabla_estudiantes("No aprobados", no_aprobados),
        _panel_resumen(len(estudiantes), len(aprobados), nota_minima),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def _flujo_personalizado() -> None:
    texto = Prompt.ask(
        "Ingresa estudiantes 'Nombre:Nota' separados por coma",
        default="Ana:4.5, Juan:2.8, Maria:3.9",
    )
    estudiantes = _parse_estudiantes(texto)
    nota_minima = FloatPrompt.ask(
        "Nota mínima de aprobación (0 a 5)",
        default=3.0,
    )
    try:
        aprobados = filtrar_aprobados(estudiantes, nota_minima)
    except (TypeError, ValueError) as exc:
        console.print(
            Panel.fit(
                f"[red]Error:[/red] {exc}",
                border_style="red",
                title="Entrada inválida",
            )
        )
        return

    no_aprobados = [e for e in estudiantes if e not in aprobados]
    paneles = [
        _tabla_estudiantes("Ingresados", estudiantes),
        _tabla_estudiantes("Aprobados", aprobados),
        _tabla_estudiantes("No aprobados", no_aprobados),
        _panel_resumen(len(estudiantes), len(aprobados), nota_minima),
    ]
    console.print(Columns(paneles, equal=True, expand=True))


def menu() -> None:
    """Interfaz interactiva con Rich para filtrar estudiantes aprobados."""
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
            opcion = OPCION_SALIR

        if opcion == OPCION_EJEMPLO:
            _flujo_ejemplo()
        elif opcion == OPCION_PERSONALIZADA:
            _flujo_personalizado()
        elif opcion == OPCION_SALIR:
            break

        _ = Prompt.ask(
            "\n[dim]Enter para continuar "
            "(o escribe 'salir' para terminar)[/dim]",
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
