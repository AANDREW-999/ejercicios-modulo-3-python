"""Gestor de tareas con persistencia en archivo .txt y UI con Rich.

Este módulo permite agregar y listar tareas persistidas en data/tareas.txt
usando with open, readlines y writelines. Provee una interfaz de consola
con Rich, estilizada con un tema característico (magenta/rosa) y detalles
decorativos con estrellas.

Funciones principales:
- agregar_tarea: valida y escribe una nueva tarea (una por línea).
- ver_tareas: lee y devuelve todas las tareas como lista de cadenas.
- menu: interfaz interactiva para gestionar las tareas.
- main: punto de entrada estándar.

Tecnologías: Python 3.x, Rich.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = ["agregar_tarea", "ver_tareas", "menu", "main"]

# Tema distintivo para este ejercicio (magenta/rosa) con “estrellitas”
THEME = Theme(
    {
        "title": "bold deep_pink2",
        "subtitle": "orchid",
        "accent": "magenta",
        "muted": "dim",
        "menu.title": "bold deep_pink2",
        "menu.option": "orchid",
        "menu.key": "bold magenta",
        "menu.border": "deep_pink2",
        "table.header": "bold deep_pink2",
        "table.border": "orchid",
        "ok": "green3",
        "warn": "yellow3",
        "error": "red",
        "star": "deep_pink2",
    }
)
console = Console(theme=THEME)

# Carpeta de datos en la raíz del proyecto: <root>/data/tareas.txt
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_ARCHIVO_TAREAS = _DATA_DIR / "tareas.txt"


def _ruta_tareas(ruta: Path | None = None) -> Path:
    """Obtiene la ruta efectiva del archivo de tareas.

    Si se provee `ruta`, se usa tal cual; de lo contrario, se usa data/tareas.txt
    en la raíz del proyecto.

    Args:
        ruta: Ruta alternativa del archivo para sobreescribir la ubicación por defecto.

    Returns:
        Ruta del archivo de tareas a utilizar (Path).
    """
    return ruta if ruta is not None else _ARCHIVO_TAREAS


def _normalizar_tarea(texto: str) -> str:
    """Normaliza el texto de una tarea a una sola línea usable.

    Colapsa espacios y saltos de línea en un solo espacio y recorta extremos.
    Si el resultado queda vacío, se considera inválido.

    Args:
        texto: Texto libre de la tarea.

    Returns:
        Texto de tarea normalizado (sin saltos internos, con espacios colapsados).

    Raises:
        ValueError: Si la tarea resultante queda vacía.
    """
    tarea = " ".join(texto.split())
    if not tarea:
        raise ValueError("La tarea no puede estar vacía.")
    return tarea


def agregar_tarea(tarea: str, ruta: Path | None = None) -> None:
    """Agrega una nueva tarea al archivo (una por línea) usando writelines.

    Crea la carpeta data si no existe y añade la tarea normalizada
    al final del archivo.

    Args:
        tarea: Descripción de la tarea. No debe quedar vacía tras normalizar.
        ruta: Ruta alternativa del archivo (útil para pruebas). Si es None,
            se usa data/tareas.txt.

    Returns:
        None

    Raises:
        ValueError: Si la tarea queda vacía tras normalizar.
        OSError: Si ocurre un error de E/S al escribir.
    """
    tarea_limpia = _normalizar_tarea(tarea)
    archivo = _ruta_tareas(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)

    # Modo append y UTF-8. Se usa writelines como pide el enunciado.
    with open(archivo, "a", encoding="utf-8") as fh:
        fh.writelines([tarea_limpia + "\n"])


def ver_tareas(ruta: Path | None = None) -> list[str]:
    """Lee todas las tareas del archivo y las devuelve como lista de cadenas.

    Utiliza readlines y elimina el salto de línea final de cada registro.

    Args:
        ruta: Ruta alternativa del archivo (útil para pruebas). Si es None,
            se usa data/tareas.txt.

    Returns:
        Lista de tareas. Si el archivo no existe, retorna lista vacía.
    """
    archivo = _ruta_tareas(ruta)
    if not archivo.exists():
        return []

    with open(archivo, "r", encoding="utf-8") as fh:
        lineas = fh.readlines()
    return [linea.rstrip("\n") for linea in lineas]


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el panel de encabezado del gestor con decoración de estrellas.

    Returns:
        Panel estilizado con título, subtítulo y líneas de estrellas.
    """
    estrellas = "[star]" + "★ " * 18 + "[/star]"
    texto = (
        f"{estrellas}\n"
        "[title]Gestor de Tareas (.txt)[/title]\n"
        "[subtitle]Persistencia en data/tareas.txt[/subtitle]\n"
        f"{estrellas}"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 11[/accent]",
        subtitle="[muted]with open · readlines · writelines[/muted]",
        border_style="menu.border",
        box=box.DOUBLE,
    )


def _panel_menu() -> Panel:
    """Panel del menú con opciones resaltadas y claves coloreadas.

    Returns:
        Panel que enumera las acciones disponibles.
    """
    texto = (
        "[menu.title]Menú ✦ Opciones[/menu.title]\n"
        "[menu.key]1)[/menu.key] [menu.option]Ver tareas[/menu.option]\n"
        "[menu.key]2)[/menu.key] [menu.option]Agregar tarea[/menu.option]\n"
        "[menu.key]3)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(texto, title="[accent]Menú[/accent]", border_style="menu.border"
                 , box=box.HEAVY)


def _tabla_tareas(tareas: Iterable[str]) -> Table:
    """Crea la tabla de tareas con estilos del tema.

    Args:
        tareas: Iterable de descripciones de tareas a mostrar.

    Returns:
        Tabla Rich con numeración, descripción y separación por líneas.
    """
    tabla = Table(
        title="[accent]Lista de tareas ✦[/accent]",
        show_lines=True,
        expand=True,
        box=box.HEAVY_EDGE,
        header_style="table.header",
        border_style="table.border",
        title_style="table.header",
    )
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Descripción", overflow="fold")
    vacio = True
    for indice, tarea in enumerate(tareas, start=1):
        vacio = False
        tabla.add_row(str(indice), tarea)
    if vacio:
        tabla.add_row("—", "[muted]No hay tareas[/muted]")
    return tabla


def menu() -> None:
    """Interfaz interactiva con Rich para gestionar tareas.

    Muestra el título, la ubicación del archivo, un menú de opciones y
    paneles con resultados o mensajes de error.

    Args:
        None

    Returns:
        None
    """
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(
            Panel.fit(
                f"[muted]Archivo:[/muted] {_ARCHIVO_TAREAS}",
                title="[accent]Ubicación ✦[/accent]",
                border_style="menu.border",
                box=box.ROUNDED,
            )
        )
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[title]Elige una opción[/title]",
            choices=["1", "2", "3"],
            default="1",
        )

        if opcion == "1":
            tareas = ver_tareas()
            console.print(_tabla_tareas(tareas))

        elif opcion == "2":
            texto = Prompt.ask("[accent]Describe la nueva tarea[/accent]")
            try:
                agregar_tarea(texto)
                console.print(
                    Panel.fit(
                        "[ok]★ Tarea agregada correctamente ★[/ok]",
                        border_style="ok",
                        title="[accent]OK[/accent]",
                        box=box.ROUNDED,
                    )
                )
            except ValueError as exc:
                console.print(
                    Panel.fit(
                        f"[error]Error:[/error] {exc}",
                        border_style="error",
                        title="[accent]Entrada inválida[/accent]",
                        box=box.HEAVY,
                    )
                )

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
            "\n\n[bold red]Programa interrumpido por el usuario. "
            "Adiós.[/bold red]"
        )
