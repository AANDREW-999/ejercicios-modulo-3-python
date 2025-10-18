"""Módulo de la calculadora de Índice de Masa Corporal (IMC).

Proporciona funciones reutilizables para calcular e interpretar el IMC
y una interfaz de consola basada en rich. Se incluye una función `menú`
que encapsula la interacción y validación de datos para mantener `main`
limpio y enfocado en el flujo principal.
"""

from typing import Final

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

__all__ = [
    "calcular_imc",
    "interpretar_imc",
    "menu",
    "ejecutar_calculadora_interactiva",
    "main",
]

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

    imc = peso / (altura ** 2)
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


def menu(console: Console) -> tuple[float, float] | None:
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
        header = Text(" Calculadora de IMC ", style="bold white on dark_blue")
        console.print(
            Panel(Align.center(header), expand=False, border_style="bright_blue")
        )

        console.print("[bold cyan]1)[/bold cyan] Calcular IMC")
        console.print("[bold magenta]2)[/bold magenta] Salir")

        opcion = console.input("[bold]Selecciona una opción (1-2) [1]: [/bold]").strip()
        if not opcion:
            opcion = "1"  # Enter toma la opción por defecto

        if opcion == "1":
            # Solicitar peso y altura con validación
            while True:
                try:
                    peso_txt = console.input("[bold]Ingresa tu peso (kg): [/bold]")
                    altura_txt = console.input("[bold]Ingresa tu altura (m): [/bold]")

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
                        )
                    )
                    # repetir la entrada de peso/altura
                    continue
        elif opcion == "2":
            return None
        else:
            console.print(
                Panel.fit(
                    "[bold red]Opción inválida. Usa 1 o 2.[/bold red]",
                    border_style="red",
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

    # Mapeo de colores/emoji por categoría para mejorar presentación
    estilo_categoria = {
        "Bajo peso": ("cyan", "🟦"),
        "Normal": ("green", "✅"),
        "Sobrepeso": ("yellow", "⚠️"),
        "Obesidad": ("red", "🚨"),
    }

    # Bucle principal: permite repetir cálculos hasta que el usuario salga
    while True:
        result = menu(console)
        if result is None:
            console.print(
                Panel.fit(
                    "[bold yellow]Saliendo... "
                    "Gracias por usar la calculadora.[/bold yellow]",
                    border_style="yellow",
                )
            )
            return

        peso, altura = result
        imc = calcular_imc(peso, altura)
        categoria = interpretar_imc(imc)

        color, emoji = estilo_categoria.get(categoria, ("white", ""))
        titulo = "IMC" if mostrar_titulo else None

        contenido = (
            f"{emoji} [bold white]Resultados[/bold white]\n"
            f"Peso: [bold]{peso} kg[/bold]\n"
            f"Altura: [bold]{altura} m[/bold]\n"
            f"IMC: [bold {color}]{imc}[/]\n"
            f"Interpretación: [bold {color}]{categoria}[/]"
        )

        console.print(Panel.fit(contenido, title=titulo, border_style=color))

        # Preguntar si desea otro cálculo; repetir la pregunta hasta respuesta válida
        pregunta = (
            "¿Deseas hacer otro cálculo? ([bold green]S[/bold green]/n) [S]: "
            if continuar_por_defecto
            else "¿Deseas hacer otro cálculo? (s/[bold red]N[/bold red]) [n]: "
        )
        while True:
            respuesta_raw = console.input(pregunta)
            if respuesta_raw is None:
                respuesta = ""
            else:
                respuesta = str(respuesta_raw).strip().lower()

            if not respuesta:
                # Enter -> tomar la sugerencia
                respuesta = "s" if continuar_por_defecto else "n"

            if respuesta in ("s", "si", "y", "yes"):
                console.print(
                    Panel.fit(
                        "[bold blue]Preparando nuevo cálculo...[/bold blue]",
                        border_style="blue",
                    )
                )
                break  # salir del bucle de la pregunta y repetir cálculo
            if respuesta in ("n", "no"):
                console.print(
                    Panel.fit(
                        "[bold yellow]Gracias. Hasta luego![/bold yellow]",
                        border_style="yellow",
                    )
                )
                return  # salir de la función y terminar
            # Si la respuesta no es ni S ni N, indicar error y volver a preguntar
            console.print(
                Panel.fit(
                    "[bold red]Respuesta inválida. "
                    "Por favor responde S o N.[/bold red]",
                    border_style="red",
                )
            )
            # repetir el while True de la pregunta


def main() -> None:
    """Punto de entrada del script cuando se ejecuta como programa.

    Inicializa la consola, delega en el menú y muestra el resultado del IMC.
    """
    console = Console()
    try:
        ejecutar_calculadora_interactiva(console)
    except ValueError as err:
        console.print(
            Panel.fit(
                f"[bold red]Error:[/bold red] {err}",
                title="Entrada inválida",
                border_style="red",
            )
        )


if __name__ == "__main__":
    main()
