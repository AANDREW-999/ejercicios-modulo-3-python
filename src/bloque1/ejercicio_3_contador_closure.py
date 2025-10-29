"""Contadores con closure y una interfaz de consola colorida con Rich.

Incluye: tema de colores, cabecera centrada, paneles con distintos bordes,
reglas separadoras y tablas estilizadas para una mejor experiencia.
"""

from __future__ import annotations

from collections.abc import Callable

from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

__all__ = ["crear_contador", "menu", "main"]

# Consola global para usar también en el bloque KeyboardInterrupt
THEME = Theme(
    {
        "title": "bold cyan",
        "subtitle": "italic #8be9fd",
        "prompt": "bold #ffd166",
        "info": "#8be9fd",
        "success": "bold #50fa7b",
        "warning": "bold #f1fa8c",
        "error": "bold #ff5555",
        "border": "#44475a",
        "accent": "#ff79c6",
        "table.header": "bold #c792ea",
        "table.value": "#e6e6e6",
    }
)
console = Console(theme=THEME)


def crear_contador() -> Callable[[], int]:
    """Crea un contador independiente usando un closure.

    Args:
        None

    Returns:
        Una función sin argumentos que incrementa y devuelve el conteo actual.

    Ejemplo:
        >>> c = crear_contador()
        >>> c()
        1
        >>> c()
        2
    """
    conteo = 0

    def incrementar() -> int:
        nonlocal conteo
        conteo += 1
        return conteo

    return incrementar


# ---------------------------
# Interfaz Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye la cabecera principal estilizada.

    Args:
        None

    Returns:
        Panel con título y subtítulo centrados.
    """
    title = Text("Fábrica de contadores (Closure)", style="title")
    subtitle = Text(
        "Cada contador es independiente y recuerda su estado", style="subtitle"
    )
    group = Group(Align.center(title), Align.center(subtitle))
    return Panel.fit(
        group,
        border_style="cyan",
        box=DOUBLE,
        title="Ejercicio 3",
        subtitle="nonlocal • funciones anidadas",
    )


def _panel_instrucciones() -> Panel:
    """Construye el panel de instrucciones del menú.

    Args:
        None

    Returns:
        Panel con la lista de opciones disponible.
    """
    tabla = Table.grid(padding=(0, 2))
    tabla.add_column(justify="right", style="prompt", no_wrap=True)
    tabla.add_column(style="table.value")

    tabla.add_row("1)", "Crear un nuevo contador")
    tabla.add_row("2)", "Incrementar un contador existente")
    tabla.add_row("3)", "Probar independencia automáticamente")
    tabla.add_row("4)", "Salir")

    return Panel(tabla, border_style="blue", title="Instrucciones", box=ROUNDED)


def _tabla_contadores(contadores: list[Callable[[], int]], valores: list[int]) -> Table:
    """Construye una tabla con el estado actual de los contadores.

    Args:
        contadores: Lista de funciones contador.
        valores: Lista espejo con los valores actuales de cada contador.

    Returns:
        Tabla con dos columnas: índice y valor actual.
    """
    tabla = Table(
        title="[table.header]Contadores[/table.header]",
        box=HEAVY,
        show_lines=True,
        border_style="border",
        header_style="table.header",
    )
    tabla.add_column("#", justify="right")
    tabla.add_column("Valor actual", justify="right", style="table.value")
    if not contadores:
        tabla.add_row("—", "—")
        return tabla

    for idx, valor in enumerate(valores, start=1):
        tabla.add_row(str(idx), str(valor))
    return tabla


def _demo_independencia_panel() -> Panel:
    """Genera un panel que demuestra la independencia de dos contadores.

    Args:
        None

    Returns:
        Panel con tabla de llamadas y resultados.
    """
    c1 = crear_contador()
    c2 = crear_contador()

    resultados = [
        ("c1()", c1()),
        ("c1()", c1()),
        ("c2()", c2()),
        ("c1()", c1()),
        ("c2()", c2()),
    ]
    tabla = Table(
        title="[table.header]Demostración de independencia[/table.header]",
        show_lines=True,
        box=ROUNDED,
        border_style="green",
    )
    tabla.add_column("Llamada", justify="left", style="bold magenta")
    tabla.add_column("Resultado", justify="right", style="success")
    for llamada, res in resultados:
        tabla.add_row(llamada, str(res))

    nota = (
        "[dim]Observa que c1 y c2 mantienen estados distintos"
        "; incrementar uno no afecta al otro.[/dim]"
    )
    panel_tabla = Panel(tabla, border_style="green", box=ROUNDED)
    return Panel(
        Group(panel_tabla, Align.center(Text.from_markup(nota))),
        title="Prueba automática",
        border_style="green",
        box=HEAVY,
    )


def menu() -> None:
    """Muestra la interfaz interactiva con Rich para gestionar contadores.

    Args:
        None

    Returns:
        None
    """
    contadores: list[Callable[[], int]] = []
    valores: list[int] = []  # espejo de valores actuales (inician en 0)

    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(Rule(style="accent"))
        console.print(_panel_instrucciones())
        console.print(_tabla_contadores(contadores, valores))
        numero_2 = 2
        numero_3 = 3
        numero_4 = 4
        try:
            opcion = IntPrompt.ask(
                "[prompt]Elige una opción[/prompt]", choices=["1", "2", "3", "4"]
            )
        except Exception:  # noqa: BLE001
            opcion = 4

        if opcion == 1:
            # Crear nuevo contador
            contadores.append(crear_contador())
            valores.append(0)
            console.print(
                Panel.fit(
                    "[success]Nuevo contador creado.[/success]",
                    border_style="green",
                    box=ROUNDED,
                )
            )
        elif opcion == numero_2:
            if not contadores:
                console.print(
                    Panel.fit(
                        "[warning]No hay contadores aún. Crea uno primero.[/warning]",
                        border_style="yellow",
                        box=ROUNDED,
                    )
                )

            else:
                idx_txt = Prompt.ask(
                    "[prompt]Ingresa el número de contador a incrementar[/prompt]",
                    default="1",
                ).strip()
                try:
                    idx = int(idx_txt)
                    if not (1 <= idx <= len(contadores)):
                        raise ValueError("Índice fuera de rango.")
                    nuevo_valor = contadores[idx - 1]()  # incrementa y devuelve
                    valores[idx - 1] = nuevo_valor
                    console.print(
                        Panel.fit(
                            f"[bold]Contador #{idx}[/bold] "
                            f"→ nuevo valor: [success]{nuevo_valor}[/success]",
                            border_style="green",
                            box=ROUNDED,
                        )
                    )
                except ValueError as exc:
                    console.print(
                        Panel.fit(
                            f"[error]Error:[/error] {exc}",
                            border_style="red",
                            box=ROUNDED,
                        )
                    )
        elif opcion == numero_3:
            console.print(_demo_independencia_panel())
        elif opcion == numero_4:
            break

        cont = Prompt.ask(
            "\n[info]Pulsa Enter para continuar[/info] "
            "[dim](o escribe 'salir' para terminar)[/dim]",
            default="",
        )
        if cont.strip().lower() == "salir":
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
        console.print("\n\n[error]Programa interrumpido por el usuario. Adiós.[/error]")
