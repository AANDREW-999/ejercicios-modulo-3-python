"""Módulo interactivo para generar perfiles de usuario.

Valida entradas (nombre, edad, hobbies y redes) y muestra resultados con Rich.
"""

from __future__ import annotations

import re
from typing import Iterable, Mapping

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

__all__ = ["crear_perfil", "menu", "main"]

# Consola global para usarla también en el bloque KeyboardInterrupt
console = Console()

# Reglas de validación
NOMBRE_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$")
HOBBY_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9' _-]+$")
RED_KEY_REGEX = re.compile(r"^[a-z][a-z0-9_-]{1,29}$")


def _validar_nombre(nombre: str) -> str:
    """Valida y normaliza el nombre (2–60 chars, letras/espacios/guiones/apóstrofes)."""
    limpio = " ".join(nombre.split())
    if not limpio:
        raise ValueError("El nombre no puede estar vacío.")
    if not NOMBRE_REGEX.match(limpio):
        raise ValueError("El nombre solo permite letras, espacios, guiones y apóstrofes.")
    if not (2 <= len(limpio) <= 60):
        raise ValueError("El nombre debe tener entre 2 y 60 caracteres.")
    return limpio


def _validar_edad(edad: int) -> int:
    """Valida el rango de edad [0, 120]."""
    if not (0 <= int(edad) <= 120):
        raise ValueError("La edad debe estar entre 0 y 120.")
    return int(edad)


def _limpiar_hobbies(hobbies: Iterable[str]) -> tuple[list[str], list[str]]:
    """Normaliza hobbies: quita vacíos, valida caracteres/largo, y elimina duplicados.
    Returns: (hobbies_validos, hobbies_descartados)
    """
    validos: list[str] = []
    descartados: list[str] = []
    vistos: set[str] = set()

    for h in hobbies:
        if not isinstance(h, str):
            descartados.append(str(h))
            continue
        item = h.strip()
        if not item:
            continue
        if len(item) > 30 or not HOBBY_REGEX.match(item):
            descartados.append(item)
            continue
        llave = item.lower()
        if llave in vistos:
            continue
        vistos.add(llave)
        validos.append(item)
    return validos, descartados


def _limpiar_redes(redes: Mapping[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """Normaliza redes: claves en minúsculas sin espacios, valida patrón y valor.
    Añade '@' en twitter/instagram/tiktok si falta.
    Returns: (redes_validas, redes_descartadas)
    """
    validas: dict[str, str] = {}
    descartadas: dict[str, str] = {}

    for k, v in redes.items():
        k0 = (k or "").strip()
        v0 = (v or "").strip()
        if not k0 or not v0:
            if k0 or v0:
                descartadas[k0] = v0
            continue

        k_norm = k0.lower().replace(" ", "")
        if not RED_KEY_REGEX.match(k_norm):
            descartadas[k0] = v0
            continue

        if k_norm in {"twitter", "instagram", "tiktok"} and not v0.startswith("@"):
            v0 = f"@{v0}"

        if len(v0) > 50:
            descartadas[k0] = v0
            continue

        validas[k_norm] = v0

    return validas, descartadas


def crear_perfil(nombre: str, edad: int, *hobbies: str, **redes_sociales: str) -> str:
    """Genera un perfil de usuario a partir de argumentos posicionales, *args y **kwargs.

    Salida (multilínea):
        Perfil de Usuario
        Nombre: <nombre>
        Edad: <edad>
        Hobbies: <h1, h2, ...> | Ninguno
        Redes sociales: <k1=v1, k2=v2, ...> | Ninguna

    Args:
        nombre: Nombre de la persona. No vacío tras recortar espacios.
        edad: Edad de la persona. Entero >= 0.
        *hobbies: Colección variable de hobbies.
        **redes_sociales: Pares red=usuario (por ejemplo, twitter='@user').

    Returns:
        Un string formateado con todo el perfil.

    Raises:
        ValueError: Si el nombre es inválido o si la edad está fuera de rango.
    """
    nombre_limpio = _validar_nombre(nombre)
    edad_valida = _validar_edad(int(edad))

    hobbies_limpios, _ = _limpiar_hobbies(hobbies)
    redes_limpias, _ = _limpiar_redes(redes_sociales)

    hobbies_txt = ", ".join(hobbies_limpios) if hobbies_limpios else "Ninguno"
    if redes_limpias:
        pares_redes = [
            f"{k}={v}" for k, v in sorted(redes_limpias.items(), key=lambda kv: kv[0].lower())
        ]
        redes_txt = ", ".join(pares_redes)
    else:
        redes_txt = "Ninguna"

    return (
        "Perfil de Usuario\n"
        f"Nombre: {nombre_limpio}\n"
        f"Edad: {edad_valida}\n"
        f"Hobbies: {hobbies_txt}\n"
        f"Redes sociales: {redes_txt}"
    )


def _parse_hobbies(texto: str) -> list[str]:
    """Convierte 'h1, h2, ...' en lista de hobbies limpiando espacios."""
    if not texto.strip():
        return []
    return [h.strip() for h in texto.split(",") if h.strip()]


def _parse_redes(texto: str) -> dict[str, str]:
    """Convierte 'clave=valor, clave=valor' en dict."""
    redes: dict[str, str] = {}
    if not texto.strip():
        return redes
    for par in texto.split(","):
        if "=" not in par:
            continue
        k, v = par.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k and v:
            redes[k] = v
    return redes


def _panel_titulo() -> Panel:
    return Panel.fit(
        "[bold cyan]Generador de Perfiles de Usuario[/bold cyan]\n"
        "[white]Completa el formulario y obtén tu perfil formateado.[/white]\n"
        "[dim]Presiona Ctrl+C para salir en cualquier momento.[/dim]",
        border_style="cyan",
        title="[magenta]Ejercicio 2[/magenta]",
    )


def _panel_instrucciones() -> Panel:
    instrucciones = (
        "[bold]Cómo completar:[/bold]\n"
        "[cyan]-[/cyan] [bold]Nombre:[/bold] obligatorio (2–60 chars; letras, espacios, guiones, ').\n"
        "[cyan]-[/cyan] [bold]Edad:[/bold] entero entre [green]0 y 120[/green].\n"
        "[cyan]-[/cyan] [bold]Hobbies:[/bold] separados por comas (máx 30 chars c/u).\n"
        "[cyan]-[/cyan] [bold]Redes:[/bold] pares [yellow]clave=valor[/yellow] separados por comas. "
        "Ej: [dim]twitter=@ana, github=ana28[/dim]\n"
        "[dim]Deja vacío los campos opcionales si no aplican.[/dim]"
    )
    return Panel(instrucciones, border_style="blue", title="[white]Instrucciones[/white]")


def _panel_resultado(perfil: str) -> Panel:
    # Renderiza el string de perfil dentro de una tabla para mejor legibilidad
    lineas = perfil.splitlines()
    tabla = Table.grid(padding=(0, 1))
    tabla.add_column(justify="right", style="bold cyan")
    tabla.add_column(style="white")
    tabla.title = "[bold white]" + (lineas[0] if lineas else "Perfil de Usuario") + "[/bold white]"
    for linea in lineas[1:]:
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            tabla.add_row(clave.strip(), f"[bold]{valor.strip()}[/bold]")
        else:
            tabla.add_row("", linea.strip())
    return Panel(tabla, border_style="green", title="[green]Perfil generado[/green]")


def menu() -> None:
    """Muestra la interfaz interactiva con Rich para crear perfiles."""
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_instrucciones())

        try:
            # Nombre (validación inmediata)
            while True:
                nombre_in = Prompt.ask("[bold cyan]Nombre[/bold cyan] [dim](obligatorio)[/dim]").strip()
                try:
                    nombre = _validar_nombre(nombre_in)
                    break
                except ValueError as e:
                    console.print(
                        Panel.fit(
                            f"[yellow]{e}[/yellow]",
                            border_style="yellow",
                            title="[white]Validación[/white]",
                        )
                    )

            # Edad (validación inmediata)
            while True:
                edad_in = IntPrompt.ask(
                    "[bold magenta]Edad[/bold magenta] [dim](0–120)[/dim]",
                    default=0,
                    show_default=True,
                )
                try:
                    edad = _validar_edad(int(edad_in))
                    break
                except ValueError as e:
                    console.print(
                        Panel.fit(
                            f"[yellow]{e}[/yellow]",
                            border_style="yellow",
                            title="[white]Validación[/white]",
                        )
                    )

            # Campos opcionales con guía de formato
            hobbies_txt = Prompt.ask(
                "[bold green]Hobbies[/bold green] [dim](separa por comas, opcional)[/dim]",
                default="",
                show_default=False,
            )
            redes_txt = Prompt.ask(
                "[bold blue]Redes sociales[/bold blue] "
                "[dim](pares clave=usuario separados por comas, opcional)[/dim]",
                default="",
                show_default=False,
            )

            hobbies_raw = _parse_hobbies(hobbies_txt)
            redes_raw = _parse_redes(redes_txt)

            # Limpieza y avisos
            hobbies, hobbies_desc = _limpiar_hobbies(hobbies_raw)
            redes, redes_desc = _limpiar_redes(redes_raw)

            if hobbies_desc:
                lista = ", ".join(hobbies_desc[:5]) + ("..." if len(hobbies_desc) > 5 else "")
                console.print(
                    Panel.fit(
                        f"[yellow]Algunos hobbies fueron omitidos por formato o longitud:[/yellow]\n{lista}",
                        border_style="yellow",
                        title="[white]Aviso[/white]",
                    )
                )
            if redes_desc:
                lista = ", ".join(f"{k}={v}".strip("=") for k, v in list(redes_desc.items())[:5])
                lista += "..." if len(redes_desc) > 5 else ""
                console.print(
                    Panel.fit(
                        "[yellow]Algunas redes fueron omitidas por clave/valor inválido.[/yellow]\n"
                        f"{lista}",
                        border_style="yellow",
                        title="[white]Aviso[/white]",
                    )
                )

            perfil = crear_perfil(nombre, edad, *hobbies, **redes)
            console.print(_panel_resultado(perfil))
        except ValueError as exc:
            console.print(
                Panel.fit(
                    f"[red]Error:[/red] {exc}",
                    border_style="red",
                    title="[white]Entrada inválida[/white]",
                )
            )

        # Preguntar si se desea crear otro perfil (acepta solo S/N)
        while True:
            continuar = (
                Prompt.ask(
                    "[bold]¿Deseas crear otro perfil?[/bold] "
                    "([green]S[/green]/[red]N[/red])",
                    default="S",
                    show_default=True,
                )
                .strip()
                .lower()
            )
            if continuar in {"s", "n"}:
                break
            console.print(
                Panel.fit(
                    "[yellow]Opción no válida. Responde S o N.[/yellow]",
                    border_style="yellow",
                    title="[white]Atención[/white]",
                )
            )
        if continuar == "n":
            break


def main() -> None:
    """Punto de entrada: solo invoca el menú."""
    menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            "\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]"
        )