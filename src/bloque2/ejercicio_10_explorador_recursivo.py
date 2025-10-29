"""Explorador recursivo de estructuras anidadas (listas, tuplas, dicts, sets).

Este módulo permite:
- Filtrar valores atómicos de una secuencia heterogénea (filter + lambda).
- Recorrer recursivamente estructuras y devolver pares (valor, profundidad).
- Interactuar mediante una interfaz de consola estilizada con Rich.

Tecnologías: Python 3.x y Rich.
Notas:
- Estructuras admitidas: list, tuple, dict, set, frozenset.
- str, bytes y bytearray se tratan como valores atómicos (no estructuras).
"""

from __future__ import annotations

import ast
from typing import Any, Iterable

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = ["explorar_estructura", "filtrar_atomos", "menu", "main"]

# Tema característico (cian/teal) para diferenciar este ejercicio
THEME = Theme(
    {
        "title": "bold bright_cyan",
        "subtitle": "cyan",
        "accent": "bold cyan",
        "muted": "dim",
        "menu.title": "bold bright_cyan",
        "menu.option": "bold cyan",
        "menu.key": "bright_cyan",
        "menu.border": "cyan",
        "table.header": "bold bright_cyan",
        "table.border": "cyan",
        "ok": "bold green",
        "warn": "bold yellow",
        "error": "bold red",
    }
)
console = Console(theme=THEME)


def _es_estructura(objeto: Any) -> bool:
    """Indica si un objeto es una estructura anidable admitida.

    Se tratan como estructuras: list, tuple, dict, set y frozenset.
    Importante: str, bytes y bytearray NO se consideran estructura.

    Args:
        objeto: Valor a evaluar.

    Returns:
        True si es una estructura anidable admitida; False en caso contrario.
    """
    tipos = (list, tuple, dict, set, frozenset)
    atomicos = (str, bytes, bytearray)
    if isinstance(objeto, atomicos):
        return False
    return isinstance(objeto, tipos)


def filtrar_atomos(items: Iterable[Any]) -> list[Any]:
    """Devuelve solo los elementos atómicos (no estructurados) de la secuencia.

    Args:
        items: Secuencia con mezcla de atómicos y estructuras.

    Returns:
        Lista con los elementos atómicos en el mismo orden de aparición.
    """
    return list(filter(lambda x: not _es_estructura(x), items))


def explorar_estructura(elemento: Any, profundidad: int = 1) -> list[tuple[Any, int]]:
    """Explora recursivamente una estructura y devuelve (valor_atómico, profundidad).

    La profundidad comienza en 1 para elementos atómicos del nivel superior.
    Para diccionarios, se recorren solo los valores (no las claves).

    Args:
        elemento: Estructura arbitraria (list, tuple, dict, set, etc.) o valor atómico.
        profundidad: Nivel actual de profundidad (>= 1).

    Returns:
        Lista de tuplas (valor_atómico, profundidad) en orden de recorrido.

    Raises:
        ValueError: Si `profundidad` es menor a 1.
    """
    if profundidad < 1:
        raise ValueError("La profundidad inicial debe ser >= 1.")

    if not _es_estructura(elemento):
        return [(elemento, profundidad)]

    resultados: list[tuple[Any, int]] = []

    if isinstance(elemento, dict):
        valores = list(elemento.values())
        atomos = filtrar_atomos(valores)
        subestructuras = list(filter(_es_estructura, valores))
        resultados.extend((a, profundidad) for a in atomos)
        for sub in subestructuras:
            resultados.extend(explorar_estructura(sub, profundidad + 1))
        return resultados

    # Listas, tuplas, sets, frozensets
    if isinstance(elemento, (list, tuple, set, frozenset)):
        items = list(elemento)
        atomos = filtrar_atomos(items)
        subestructuras = list(filter(_es_estructura, items))
        resultados.extend((a, profundidad) for a in atomos)
        for sub in subestructuras:
            resultados.extend(explorar_estructura(sub, profundidad + 1))
        return resultados

    # Cualquier otro tipo "iterable" no contemplado se trata como atómico
    return [(elemento, profundidad)]


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el panel de título con estilos del tema.

    Returns:
        Panel con encabezado y subtítulo del ejercicio.
    """
    texto = (
        "[title]Explorador Recursivo de Estructuras[/title]\n"
        "[muted]Recorre listas/dicts anidados y "
        "lista valores atómicos con su profundidad[/muted]"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 10[/accent]",
        subtitle="[subtitle]Recursividad + filter + lambda[/subtitle]",
        border_style="menu.border",
        box=box.HEAVY,
    )


def _panel_menu() -> Panel:
    """Panel del menú principal con opciones numeradas.

    Returns:
        Panel estilizado con las opciones del menú.
    """
    texto = (
        "[menu.title]Opciones[/menu.title]\n"
        "[menu.key]1)[/menu.key] "
        "[menu.option]Ejecutar ejemplo por defecto[/menu.option]\n"
        "[menu.key]2)[/menu.key] [menu.option]"
        "Ingresar estructura personalizada (literal Python)[/menu.option]\n"
        "[menu.key]3)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(
        texto,
        title="[accent]Menú[/accent]",
        border_style="menu.border",
        box=box.ROUNDED,
    )


def _tabla_resultados(pares: list[tuple[Any, int]]) -> Table:
    """Crea la tabla de resultados con estilo coherente al tema.

    Args:
        pares: Lista de tuplas (valor_atómico, profundidad) a mostrar.

    Returns:
        Table con encabezados y filas formateadas.
    """
    tabla = Table(
        title="[accent]Valores atómicos encontrados[/accent]",
        show_lines=True,
        expand=True,
        box=box.MINIMAL_HEAVY_HEAD,
        header_style="table.header",
        border_style="table.border",
        title_style="table.header",
    )
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Valor", overflow="fold")
    tabla.add_column("Tipo", style="muted")
    tabla.add_column("Profundidad", justify="right", style="accent")
    if not pares:
        tabla.add_row("—", "—", "—", "—")
        return tabla

    for indice, (valor, nivel) in enumerate(pares, start=1):
        tipo = type(valor).__name__
        tabla.add_row(str(indice), repr(valor), tipo, str(nivel))
    return tabla


def _panel_resumen(pares: list[tuple[Any, int]]) -> Panel:
    """Construye un panel con métricas básicas del resultado.

    Args:
        pares: Lista de tuplas (valor_atómico, profundidad).

    Returns:
        Panel compacto con total y profundidad máxima.
    """
    total = len(pares)
    maximo = max((nivel for _, nivel in pares), default=0)
    texto = (
        f"[title]Total atómicos:[/title] [ok]{total}[/ok]\n"
        f"[title]Profundidad máxima:[/title] [accent]{maximo}[/accent]"
    )
    return Panel.fit(
        texto,
        title="[accent]Resumen[/accent]",
        border_style="menu.border",
        box=box.ROUNDED,
    )


def _flujo_ejemplo() -> None:
    """Ejecuta un ejemplo predefinido y muestra los resultados.

    Returns:
        None
    """
    estructura = [1, [2, 3], {"a": 4, "b": [5, {"c": 6}]}]
    pares = explorar_estructura(estructura)
    paneles = [_tabla_resultados(pares), _panel_resumen(pares)]
    console.print(Columns(paneles, equal=True, expand=True))


def _parse_literal(texto: str) -> Any:
    """Parsea un literal de Python de forma segura.

    Args:
        texto: Literal en sintaxis Python (ej.: "[1, [2, 3], {'a': 4}]").

    Returns:
        Objeto resultante de evaluar el literal (lista, dict, etc.) o un valor atómico.

    Raises:
        ValueError: Si el literal no puede interpretarse correctamente.
    """
    try:
        return ast.literal_eval(texto)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            "No se pudo interpretar el literal. Usa sintaxis de Python, "
            "por ejemplo: [1, [2, 3], {'a': 4}]"
        ) from exc


def _flujo_personalizado() -> None:
    """Solicita un literal de Python, lo evalúa y presenta los resultados.

    Returns:
        None
    """
    texto = Prompt.ask(
        "Ingresa una estructura (literal Python)",
        default="[1, [2, 3], {'a': 4}]",
    )
    try:
        estructura = _parse_literal(texto)
        pares = explorar_estructura(estructura)
    except ValueError as exc:
        console.print(
            Panel.fit(
                f"[error]Error:[/error] {exc}",
                border_style="error",
                title="[accent]Entrada inválida[/accent]",
                box=box.HEAVY,
            )
        )
        return

    paneles = [_tabla_resultados(pares), _panel_resumen(pares)]
    console.print(Columns(paneles, equal=True, expand=True))


def menu() -> None:
    """Interfaz interactiva para explorar estructuras recursivas.

    Muestra opciones, ejecuta un ejemplo predefinido o permite introducir un
    literal de Python que será evaluado y recorrido.

    Args:
        None

    Returns:
        None
    """
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[title]Elige una opción[/title]", choices=["1", "2", "3"], default="1"
        )

        if opcion == "1":
            _flujo_ejemplo()
        elif opcion == "2":
            _flujo_personalizado()
        elif opcion == "3":
            break

        _ = Prompt.ask(
            "\n[muted]Enter para continuar (o escribe 'salir' para terminar)[/muted]",
            default="",
        )
        if _.strip().lower() == "salir":
            break


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
