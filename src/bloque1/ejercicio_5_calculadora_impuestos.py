from __future__ import annotations

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

__all__ = [
    "TASA_IVA",
    "calcular_iva",
    "actualizar_tasa_iva",
    "menu",
    "main",
]

console = Console()

# Variable global de tasa (19%)
TASA_IVA: float = 0.19


def calcular_iva(precio_base: float) -> float:
    """Calcula el IVA a partir del precio base usando la tasa global TASA_IVA.

    Args:
        precio_base: Precio antes de impuestos. Debe ser >= 0.

    Returns:
        El valor del IVA (redondeado a 2 decimales).

    Raises:
        ValueError: Si el precio_base es negativo.
    """
    if precio_base < 0:
        raise ValueError("El precio base no puede ser negativo.")
    iva = precio_base * TASA_IVA
    return round(iva, 2)


def actualizar_tasa_iva(nueva_tasa: float) -> None:
    """Actualiza la tasa global de IVA.

    Args:
        nueva_tasa: Nueva tasa en rango [0, 1]. Ej: 0.19 para 19%.

    Raises:
        ValueError: Si la tasa no está en el rango [0, 1].
    """
    if not (0.0 <= nueva_tasa <= 1.0):
        raise ValueError("La tasa debe estar en el rango [0, 1].")
    global TASA_IVA
    TASA_IVA = float(nueva_tasa)


# ---------------------------
# Utilidades de interfaz
# ---------------------------


def _parse_float(texto: str) -> float:
    """Convierte texto a float aceptando coma o punto decimal."""
    try:
        return float(texto.replace(",", ".").strip())
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Valor no numérico: '{texto}'") from exc


def _panel_titulo() -> Panel:
    texto = (
        "[bold cyan]Calculadora de Impuestos[/bold cyan]\n"
        "[dim]Tasa global editable con demostración en vivo[/dim]"
    )
    return Panel.fit(
        texto,
        title="Ejercicio 5",
        subtitle="Scope Global, global",
        border_style="cyan",
    )


def _panel_estado() -> Panel:
    porcentaje = round(TASA_IVA * 100, 2)
    return Panel.fit(
        f"[bold white]Tasa actual (TASA_IVA):[/bold white] [bold]{porcentaje}%[/bold]",
        title="Estado",
        border_style="blue",
    )


def _panel_menu() -> Panel:
    texto = (
        "[bold]Opciones[/bold]\n"
        "1) Calcular IVA y Total con la tasa actual\n"
        "2) Actualizar TASA_IVA\n"
        "3) Demostración Antes/Después\n"
        "4) Salir"
    )
    return Panel(texto, title="Menú", border_style="magenta")


def _tabla_resultado(precio_base: float, iva: float) -> Table:
    total = round(precio_base + iva, 2)
    tabla = Table(title="Detalle de cálculo", show_lines=True, expand=True)
    tabla.add_column("Concepto", style="bold")
    tabla.add_column("Valor", justify="right")
    tabla.add_row("Precio base", f"{precio_base:.2f}")
    tabla.add_row("IVA", f"{iva:.2f}")
    tabla.add_row("Total", f"{total:.2f}")
    return tabla


def _panel_demo(precio_base: float, tasa_old: float, tasa_new: float) -> Panel:
    iva_old = round(precio_base * tasa_old, 2)
    total_old = round(precio_base + iva_old, 2)
    iva_new = round(precio_base * tasa_new, 2)
    total_new = round(precio_base + iva_new, 2)

    t1 = Table(title="Antes", expand=True)
    t1.add_column("Campo", style="bold")
    t1.add_column("Valor", justify="right")
    t1.add_row("Tasa", f"{tasa_old*100:.2f}%")
    t1.add_row("Precio base", f"{precio_base:.2f}")
    t1.add_row("IVA", f"{iva_old:.2f}")
    t1.add_row("Total", f"{total_old:.2f}")

    t2 = Table(title="Después", expand=True)
    t2.add_column("Campo", style="bold green")
    t2.add_column("Valor", justify="right")
    t2.add_row("Tasa", f"{tasa_new*100:.2f}%")
    t2.add_row("Precio base", f"{precio_base:.2f}")
    t2.add_row("IVA", f"{iva_new:.2f}")
    t2.add_row("Total", f"{total_new:.2f}")

    columnas = Columns([t1, t2], equal=True, expand=True)
    return Panel(
        columnas,
        title="Demostración de cambio de tasa",
        border_style="green",
    )


# ---------------------------
# Interfaz interactiva
# ---------------------------


def menu() -> None:
    """Interfaz interactiva con Rich para calcular y actualizar IVA."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_estado())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[bold]Elige una opción[/bold]",
            choices=["1", "2", "3", "4"],
            default="1",
        )

        if opcion == "1":
            try:
                precio_txt = Prompt.ask("Precio base (ej. 199.99)")
                precio_base = _parse_float(precio_txt)
                iva = calcular_iva(precio_base)
                tabla = _tabla_resultado(precio_base, iva)
                console.print(Panel(tabla, border_style="green"))
            except ValueError as exc:
                console.print(
                    Panel.fit(
                        f"[red]Error:[/red] {exc}",
                        border_style="red",
                        title="Entrada inválida",
                    )
                )

        elif opcion == "2":
            try:
                tasa_txt = Prompt.ask("Nueva tasa (0 a 1). Ej: 0.19 para 19%")
                nueva_tasa = _parse_float(tasa_txt)
                actualizar_tasa_iva(nueva_tasa)
                console.print(
                    Panel.fit(
                        f"[green]TASA_IVA actualizada a {nueva_tasa*100:.2f}%[/green]",
                        border_style="green",
                        title="OK",
                    )
                )
            except ValueError as exc:
                console.print(
                    Panel.fit(
                        f"[red]Error:[/red] {exc}",
                        border_style="red",
                        title="Entrada inválida",
                    )
                )

        elif opcion == "3":
            try:
                precio_txt = Prompt.ask("Precio base para la demostración")
                precio_base = _parse_float(precio_txt)
                tasa_old = TASA_IVA
                tasa_txt = Prompt.ask("Nueva tasa (0 a 1) para comparar. Ej: 0.2")
                tasa_new = _parse_float(tasa_txt)
                if not (0.0 <= tasa_new <= 1.0):
                    raise ValueError("La tasa debe estar en el rango [0, 1].")
                panel = _panel_demo(precio_base, tasa_old, tasa_new)
                console.print(panel)
            except ValueError as exc:
                console.print(
                    Panel.fit(
                        f"[red]Error:[/red] {exc}",
                        border_style="red",
                        title="Entrada inválida",
                    )
                )

        elif opcion == "4":
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
