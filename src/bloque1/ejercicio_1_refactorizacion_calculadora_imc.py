"""Módulo de la calculadora de Índice de Masa Corporal (IMC).

Proporciona funciones reutilizables para calcular e interpretar el IMC
y una interfaz de consola basada en rich. Se incluye una función `menú`
que encapsula la interacción y validación de datos para mantener `main`
limpio y enfocado en el flujo principal.
"""

from typing import Final

from rich.align import Align

# NUEVO: estilos, tablas y cajas
from rich.box import HEAVY, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

console = Console(theme=Theme({}))

__all__ = [
    "calcular_imc",
    "interpretar_imc",
    "menu_interactivo",
    "ejecutar_calculadora_interactiva",
    "menu",
    "main",
]

# NUEVO: tema de colores para la app
THEME = Theme(
    {
        "title": "bold white on #0b3d91",
        "subtitle": "bold #8be9fd",
        "prompt": "bold #ffd166",
        "value": "bold #50fa7b",
        "label": "bold #c792ea",
        "border": "#44506b",
        "accent": "#00bcd4",
        "error": "bold red",
        "warning": "bold #ffb86c",
        "info": "#8be9fd",
        "success": "bold #50fa7b",
        # categorías IMC
        "imc.bajo": "bold #2aa198",
        "imc.normal": "bold #50fa7b",
        "imc.sobre": "bold #f1fa8c",
        "imc.ob": "bold #ff5555",
    }
)

# Umbrales de interpretación del IMC (OMS simplificada)
IMC_BAJO_PESO_MAX: Final = 18.5
IMC_NORMAL_MAX: Final = 25.0
IMC_SOBREPESO_MAX: Final = 30.0


def calcular_imc(peso: float, altura: float) -> float:
    """Calcula el Índice de Masa Corporal (IMC).

    El IMC se define como peso (kg) dividido entre la altura (m) al cuadrado.

    Args:
        peso: Peso en kilogramos. Debe ser mayor que 0.
        altura: Altura en metros. Debe ser mayor que 0.

    Returns:
        El IMC redondeado a 2 decimales.

    Raises:
        ValueError: Si `peso` <= 0 o `altura` <= 0.
    """
    if peso <= 0:
        raise ValueError("El peso debe ser mayor que 0.")
    if altura <= 0:
        raise ValueError("La altura debe ser mayor que 0.")

    imc = peso / (altura**2)
    return round(imc, 2)


def interpretar_imc(imc: float) -> str:
    """Devuelve la categoría nutricional a partir del IMC.

    Rangos:
      - < 18.5: "Bajo peso"
      - [18.5, 25): "Normal"
      - [25, 30): "Sobrepeso"
      - >= 30: "Obesidad"

    Args:
        imc: Índice de masa corporal. Debe ser mayor que 0.

    Returns:
        La categoría correspondiente al rango del IMC.

    Raises:
        ValueError: Si `imc` <= 0.
    """
    if imc <= 0:
        raise ValueError("El IMC debe ser mayor que 0.")

    if imc < IMC_BAJO_PESO_MAX:
        return "Bajo peso"
    if imc < IMC_NORMAL_MAX:
        return "Normal"
    if imc < IMC_SOBREPESO_MAX:
        return "Sobrepeso"
    return "Obesidad"


def _parse_float(value: str) -> float:
    """Convierte una cadena a float aceptando coma o punto decimal.

    Args:
        value: Texto a convertir. Se ignoran espacios; admite ',' o '.'.

    Returns:
        El valor convertido como número de punto flotante.

    Raises:
        ValueError: Si `value` no representa un número válido.
    """
    try:
        return float(value.replace(",", ".").strip())
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"Valor no numérico: '{value}'") from exc


def menu_interactivo(console: Console) -> tuple[float, float] | None:
    """Muestra el menú, valida entradas y devuelve peso/altura.

    Args:
        console: Instancia de rich.console. Console para entrada/salida.

    Returns:
        Una tupla (peso, altura) cuando el usuario elige calcular,
        o None si el usuario decide salir.

    Raises:
        ValueError: Reemite errores de validación de entradas numéricas.
    """
    while True:
        # NUEVO: cabecera más vistosa
        console.print(Rule(style="accent"))
        header = Text(" Calculadora de IMC ", style="title")
        sub = Text("Salud • Bienestar • Educación", style="subtitle")
        console.print(
            Panel(
                Align.center(Text.assemble(header, "\n", sub)),
                border_style="accent",
                box=HEAVY,
            )
        )
        console.print(Rule(style="accent"))

        console.print("[bold cyan]1)[/bold cyan] Calcular IMC")
        console.print("[bold magenta]2)[/bold magenta] Salir")

        opcion = console.input("[bold]Selecciona una opción (1-2) [1]: [/bold]").strip()
        if not opcion:
            opcion = "1"  # Enter toma la opción por defecto

        if opcion == "1":
            # Solicitar peso y altura with validación
            while True:
                try:
                    peso_txt = console.input(
                        "[prompt]» Ingresa tu peso (kg): [/prompt]"
                    )
                    altura_txt = console.input(
                        "[prompt]» Ingresa tu altura (m): [/prompt]"
                    )

                    # Validar vacíos e informar de inmediato
                    missing = []
                    if peso_txt is None or not peso_txt.strip():
                        missing.append("peso")
                    if altura_txt is None or not altura_txt.strip():
                        missing.append("altura")
                    if missing:
                        if len(missing) == 1:
                            raise ValueError(
                                f"El campo '{missing[0]}' no puede estar vacío."
                            )
                        raise ValueError(
                            f"Los campos {', '.join(missing)} no pueden estar vacíos."
                        )

                    peso = _parse_float(peso_txt)
                    altura = _parse_float(altura_txt)

                    if peso <= 0 or altura <= 0:
                        raise ValueError("Peso y altura deben ser mayores que 0.")

                    return peso, altura
                except ValueError as err:
                    console.print(
                        Panel.fit(
                            f"[bold red]Error:[/bold red] {err}",
                            title="Entrada inválida",
                            border_style="red",
                            box=ROUNDED,
                        )
                    )
                    continue
        elif opcion == "2":
            return None
        else:
            console.print(
                Panel.fit(
                    "[bold red]Opción inválida. Usa 1 o 2.[/bold red]",
                    border_style="red",
                    box=ROUNDED,
                )
            )
            continue


def ejecutar_calculadora_interactiva(console: Console, **kwargs) -> None:
    """Orquesta el flujo interactivo de la calculadora de IMC.

    Pregunta datos al usuario, muestra resultados y permite repetir
    cálculos hasta que el usuario decida salir.

    Args:
        console: Instancia de rich.console. Console para I/O.
        **kwargs: Argumentos adicionales. Reconoce:
            - mostrar_titulo (bool): Muestra título en el panel
              (por defecto True).
            - continuar_por_defecto (bool): Enter equivale a S si True
              (por defecto True).

    Returns:
        None
    """
    mostrar_titulo = kwargs.get("mostrar_titulo", True)
    continuar_por_defecto = kwargs.get("continuar_por_defecto", True)

    # Mapeo de colores por categoría (sin emojis)
    estilo_categoria = {
        "Bajo peso": "imc.bajo",
        "Normal": "imc.normal",
        "Sobrepeso": "imc.sobre",
        "Obesidad": "imc.ob",
    }

    # Bucle principal: permite repetir cálculos hasta que el usuario salga
    while True:
        result = menu_interactivo(console)
        if result is None:
            console.print(
                Panel.fit(
                    "[bold yellow]Saliendo... "
                    "Gracias por usar la calculadora.[/bold yellow]",
                    border_style="yellow",
                    box=ROUNDED,
                )
            )
            return

        peso, altura = result
        # NUEVO: atrapar errores en cálculo/interpretación y volver a preguntar
        try:
            imc = calcular_imc(peso, altura)
            categoria = interpretar_imc(imc)
        except ValueError as err:
            console.print(
                Panel.fit(
                    f"[bold red]Error:[/bold red] {err}",
                    title="Entrada inválida",
                    border_style="red",
                    box=ROUNDED,
                )
            )
            continue  # vuelve a preguntar

        color_style = estilo_categoria.get(categoria, "value")
        titulo = "IMC" if mostrar_titulo else None

        # NUEVO: tabla de resultados
        tabla = Table.grid(padding=(0, 2))
        tabla.add_column(justify="right", style="label", no_wrap=True)
        tabla.add_column(style="value")
        tabla.add_row("Peso", f"{peso} kg")
        tabla.add_row("Altura", f"{altura} m")
        tabla.add_row("IMC", f"[{color_style}]{imc:.2f}[/]")
        tabla.add_row("Interpretación", f"[{color_style}]{categoria}[/]")

        console.print(
            Panel(
                tabla,
                title=titulo,
                title_align="left",
                border_style=color_style,
                box=HEAVY,
            )
        )

        # Preguntar si desea otro cálculo; repetir la pregunta hasta respuesta válida
        pregunta = (
            "¿Deseas hacer otro cálculo? ([bold green]S[/bold green]/n) [S]: "
            if continuar_por_defecto
            else "¿Deseas hacer otro cálculo? (s/[bold red]N[/bold red]) [n]: "
        )
        while True:
            respuesta_raw = console.input(pregunta)
            respuesta = (
                "" if respuesta_raw is None else str(respuesta_raw).strip().lower()
            )
            if not respuesta:
                respuesta = "s" if continuar_por_defecto else "n"

            if respuesta in ("s", "si", "y", "yes"):
                console.print(
                    Panel.fit(
                        "[success]Preparando nuevo cálculo...[/success]",
                        border_style="accent",
                        box=ROUNDED,
                    )
                )
                break
            if respuesta in ("n", "no"):
                console.print(
                    Panel.fit(
                        "[success]Gracias. Hasta luego![/success]",
                        border_style="accent",
                        box=ROUNDED,
                    )
                )
                return
            console.print(
                Panel.fit(
                    "[warning]Respuesta inválida. Por favor responde S o N.[/warning]",
                    border_style="warning",
                    box=ROUNDED,
                )
            )


def menu() -> None:
    """Punto de entrada del script cuando se ejecuta como programa.

    Inicializa la consola, delega en el menú y muestra el resultado del IMC.
    """
    console = Console(theme=THEME)
    try:
        ejecutar_calculadora_interactiva(console)
    except ValueError as err:
        console.print(
            Panel.fit(
                f"[bold red]Error:[/bold red] {err}",
                title="Entrada inválida",
                border_style="red",
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
