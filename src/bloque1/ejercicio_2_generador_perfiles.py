"""Módulo interactivo para generar perfiles de usuario.

Valida entradas (nombre, edad, hobbies y redes) y muestra resultados con Rich.
"""
from __future__ import annotations

import re
from typing import Iterable, Mapping

# NUEVO: imports para diseño
from rich.align import Align
from rich.box import HEAVY, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

__all__ = ["crear_perfil", "menu", "main"]

# NUEVO: tema y consola global con theme
THEME = Theme(
    {
        "title": "bold #00d1ff",
        "subtitle": "italic #8be9fd",
        "prompt": "bold #ffd166",
        "label": "bold #c792ea",
        "value": "bold #80e27e",
        "border": "#44506b",
        "accent": "#00bcd4",
        "error": "bold red",
        "warning": "bold #ffb86c",
        "info": "#8be9fd",
        "success": "bold #50fa7b",
        "muted": "#a6accd",
    }
)
console = Console(theme=THEME)

# Reglas de validación
NOMBRE_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$")
HOBBY_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9' _-]+$")
RED_KEY_REGEX = re.compile(r"^[a-z][a-z0-9_-]{1,29}$")


def _validar_nombre(nombre: str) -> str:
    """Valida y normaliza el nombre del usuario.

    Args:
        nombre: Texto del nombre a validar.

    Returns:
        El nombre limpio, con espacios normalizados.

    Raises:
        ValueError: Si está vacío, contiene caracteres no permitidos
            o su longitud no está entre 2 y 60 caracteres.
    """
    limpio = " ".join(nombre.split())
    numero_min= 2
    numero_max= 60
    if not limpio:
        raise ValueError("El nombre no puede estar vacío.")
    if not NOMBRE_REGEX.match(limpio):
        raise ValueError("El nombre solo permite letras"
                         ", espacios, guiones y apóstrofes.")
    if not (numero_min <= len(limpio) <= numero_max):
        raise ValueError("El nombre debe tener entre 2 y 60 caracteres.")
    return limpio


def _validar_edad(edad: int) -> int:
    """Valida el rango de edad permitido.

    Args:
        edad: Edad a validar.

    Returns:
        La edad válida como entero.

    Raises:
        ValueError: Si no está en el rango [0, 120].
    """
    numero_max=120
    if not (0 <= int(edad) <= numero_max):
        raise ValueError("La edad debe estar entre 0 y 120.")
    return int(edad)


def _limpiar_hobbies(hobbies: Iterable[str]) -> tuple[list[str], list[str]]:
    """Normaliza una colección de hobbies.

    - Elimina vacíos y duplicados (insensible a mayúsculas).
    - Valida caracteres y longitud máxima (30).

    Args:
        hobbies: Iterable de textos de hobbies.

    Returns:
        Una tupla (validos, descartados) donde:
        - validos: lista de hobbies válidos conservando el orden.
        - descartados: entradas rechazadas por formato o longitud.
    """
    validos: list[str] = []
    descartados: list[str] = []
    vistos: set[str] = set()
    numero = 30
    for h in hobbies:
        if not isinstance(h, str):
            descartados.append(str(h))
            continue
        item = h.strip()
        if not item:
            continue
        if len(item) > numero or not HOBBY_REGEX.match(item):
            descartados.append(item)
            continue
        llave = item.lower()
        if llave in vistos:
            continue
        vistos.add(llave)
        validos.append(item)
    return validos, descartados


def _limpiar_redes(redes: Mapping[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """Normaliza pares red=usuario.

    - Normaliza la clave: minúsculas sin espacios.
    - Valida la clave con RED_KEY_REGEX.
    - Añade '@' si falta para twitter/instagram/tiktok.
    - Rechaza valores vacíos o > 50 caracteres.

    Args:
        redes: Mapeo de nombre de red a usuario.

    Returns:
        Una tupla (validas, descartadas) con:
        - validas: dict normalizado de redes aceptadas.
        - descartadas: dict de entradas omitidas (originales).
    """
    validas: dict[str, str] = {}
    descartadas: dict[str, str] = {}
    numero= 50
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

        if len(v0) > numero:
            descartadas[k0] = v0
            continue

        validas[k_norm] = v0

    return validas, descartadas


def crear_perfil(nombre: str, edad: int, *hobbies: str, **redes_sociales: str) -> str:
    """Genera un perfil de usuario a partir de argumentos posicionales y nombrados.

    Salida (multilínea):
        Perfil de Usuario
        Nombre: <nombre>
        Edad: <edad>
        Hobbies: <h1, h2, ...> | Ninguno
        Redes sociales: <k1=v1, k2=v2, ...> | Ninguna

    Args:
        nombre: Nombre de la persona.
        edad: Edad de la persona (entero >= 0).
        *hobbies: Colección variable de hobbies.
        **redes_sociales: Pares red=usuario (p. ej. twitter='@user').

    Returns:
        Un string formateado con el perfil.

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
            f"{k}={v}" for k, v in sorted(redes_limpias.items()
                                          , key=lambda kv: kv[0].lower())
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
    """Convierte una cadena CSV en lista de hobbies.

    Args:
        texto: Cadena con valores separados por comas.

    Returns:
        Lista de hobbies limpiados (sin vacíos).
    """
    if not texto.strip():
        return []
    return [h.strip() for h in texto.split(",") if h.strip()]


def _parse_redes(texto: str) -> dict[str, str]:
    """Convierte una cadena CSV de pares clave=valor a un diccionario.

    Args:
        texto: Cadena con pares separados por comas (clave=valor).

    Returns:
        Diccionario {clave: valor} con pares válidos encontrados.
    """
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
    """Construye el panel de cabecera.

    Args:
        None

    Returns:
        Panel estilizado con título y subtítulo.
    """
    titulo = Text("Generador de Perfiles de Usuario", style="title")
    subtitulo = Text("Completa el formulario y obtén tu perfil formateado"
                     , style="subtitle")
    contenido = Align.center(Text.assemble(titulo, "\n", subtitulo))
    return Panel.fit(contenido, border_style="accent"
                     , title="[magenta]Ejercicio 2[/magenta]", box=HEAVY)


def _panel_instrucciones() -> Panel:
    """Construye el panel de instrucciones del formulario.

    Args:
        None

    Returns:
        Panel con texto formateado de instrucciones.
    """
    instrucciones = (
        "[cyan]Cómo completar:[/cyan]\n"
        "[cyan]-[/cyan] [bold]Nombre:[/bold] obligatorio.\n"
        "[cyan]-[/cyan] [bold]Edad:[/bold] entero entre [green]0 y 120[/green].\n"
        "[cyan]-[/cyan] [bold]Hobbies:[/bold] separados por comas (Maximo 30).\n"
        "[cyan]-[/cyan] [bold]Redes:[/bold] pares [yellow]clave=valor[/yellow] "
        "separados por comas. "
        "Ej: [dim]twitter=@AANDREW, github=ANDREW-999[/dim]\n"
        "[dim]Deja vacío los campos opcionales si no aplican.[/dim]"
    )
    # NUEVO: caja redondeada y borde azul
    return Panel(instrucciones, border_style="accent"
                 , title="[white]Instrucciones[/white]", box=ROUNDED)


def _panel_resultado(perfil: str) -> Panel:
    """Envuelve la representación de perfil en una tabla dentro de un Panel.

    Args:
        perfil: Texto multilínea generado por crear_perfil.

    Returns:
        Panel con una tabla de campos clave/valor del perfil.
    """
    # Renderiza el string de perfil dentro de una tabla para mejor legibilidad
    lineas = perfil.splitlines()
    tabla = Table.grid(padding=(0, 1))
    tabla.add_column(justify="right", style="label", no_wrap=True)
    tabla.add_column(style="value")
    tabla.title = ("[bold white]"
                   + (lineas[0] if lineas else "Perfil de Usuario") + "[/bold white]")
    for linea in lineas[1:]:
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            tabla.add_row(clave.strip(), f"[value]{valor.strip()}[/value]")
        else:
            tabla.add_row("", linea.strip())
    # NUEVO: caja pesada y borde destacado
    return Panel(tabla, border_style="accent"
                 , title="[green]Perfil generado[/green]", box=HEAVY)


def menu() -> None:
    """Muestra la interfaz interactiva con Rich para crear perfiles.

    Args:
        None

    Returns:
        None
    """
    while True:
        console.clear()
        # NUEVO: reglas separadoras estilizadas
        console.print(Rule(style="accent"))
        console.print(_panel_titulo())
        console.print(Rule(style="accent"))
        console.print(_panel_instrucciones())

        try:
            # Nombre (validación inmediata)
            while True:
                nombre_in = Prompt.ask("[prompt]» Nombre[/prompt]"
                                       " [dim](obligatorio)[/dim]").strip()
                try:
                    nombre = _validar_nombre(nombre_in)
                    break
                except ValueError as e:
                    console.print(
                        Panel.fit(
                            f"[warning]{e}[/warning]",
                            border_style="warning",
                            title="[white]Validación[/white]",
                            box=ROUNDED,
                        )
                    )

            # Edad (validación inmediata)
            while True:
                edad_in = IntPrompt.ask("[prompt]» Edad[/prompt] [dim](0–120)[/dim]"
                                        , default=0, show_default=True)
                try:
                    edad = _validar_edad(int(edad_in))
                    break
                except ValueError as e:
                    console.print(
                        Panel.fit(
                            f"[warning]{e}[/warning]",
                            border_style="warning",
                            title="[white]Validación[/white]",
                            box=ROUNDED,
                        )
                    )

            # Campos opcionales con guía de formato
            hobbies_txt = Prompt.ask("[prompt]» Hobbies[/prompt] "
                                     "[dim](separa por comas, opcional)[/dim]"
                                     , default="", show_default=False)
            redes_txt = Prompt.ask("[prompt]» Redes sociales[/prompt] "
                                   "[dim](pares clave=usuario, opcional)[/dim]"
                                   , default="", show_default=False)

            hobbies_raw = _parse_hobbies(hobbies_txt)
            redes_raw = _parse_redes(redes_txt)

            # Limpieza y avisos
            hobbies, hobbies_desc = _limpiar_hobbies(hobbies_raw)
            redes, redes_desc = _limpiar_redes(redes_raw)
            max_preview = 5
            if hobbies_desc:
                lista = (", ".join(hobbies_desc[:max_preview])
                         + ("..." if len(hobbies_desc) > max_preview else ""))
                console.print(
                    Panel.fit(
                        f"[warning]Algunos hobbies"
                        f" fueron omitidos por formato o longitud:[/warning]\n{lista}",
                        border_style="warning",
                        title="[white]Aviso[/white]",
                        box=ROUNDED,
                    )
                )
            if redes_desc:
                lista = ", ".join(f"{k}={v}".strip("=")
                                  for k, v in list(redes_desc.items())[:max_preview])
                lista += "..." if len(redes_desc) > max_preview else ""
                console.print(
                    Panel.fit(
                        "[warning]Algunas redes fueron omitidas"
                        " por clave/valor inválido.[/warning]\n" + lista,
                        border_style="warning",
                        title="[white]Aviso[/white]",
                        box=ROUNDED,
                    )
                )

            perfil = crear_perfil(nombre, edad, *hobbies, **redes)
            console.print(_panel_resultado(perfil))
        except ValueError as exc:
            console.print(
                Panel.fit(
                    f"[error]Error:[/error] {exc}",
                    border_style="error",
                    title="[white]Entrada inválida[/white]",
                    box=ROUNDED,
                )
            )

        # Preguntar si se desea crear otro perfil (acepta solo S/N)
        while True:
            continuar = Prompt.ask(
                "[bold]¿Deseas crear otro perfil?"
                "[/bold] ([green]S[/green]/[red]N[/red])",
                default="S",
                show_default=True,
            ).strip().lower()
            if continuar in {"s", "n"}:
                break
            console.print(
                Panel.fit(
                    "[warning]Opción no válida. Responde S o N.[/warning]",
                    border_style="warning",
                    title="[white]Atención[/white]",
                    box=ROUNDED,
                )
            )
        if continuar == "n":
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
