"""Mini sistema de biblioteca (JSON) con interfaz enriquecida con Rich.

Funciones:
- Persistencia: cargar_biblioteca, guardar_biblioteca.
- Negocio: prestar_libro, devolver_libro, buscar_libro, ver_libros_prestados.
- UI: mostrar_libros, menu, main.

Tecnologías:
- Python 3.x, JSON (json.load/json.dump), Rich (Panel, Table, Columns, Prompt).

Notas:
- La base de datos se guarda en data/biblioteca.json.
- El diseño usa un tema característico (verde/menta) con estrellitas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = [
    "cargar_biblioteca",
    "guardar_biblioteca",
    "prestar_libro",
    "devolver_libro",
    "buscar_libro",
    "ver_libros_prestados",
    "mostrar_libros",
    "menu",
    "main",
]

# Tema característico (verde/menta) con estrellitas
THEME = Theme(
    {
        "title": "bold spring_green3",
        "subtitle": "sea_green3",
        "accent": "bold aquamarine1",
        "muted": "grey62",
        "menu.title": "bold spring_green3",
        "menu.option": "sea_green2",
        "menu.key": "bold aquamarine1",
        "menu.border": "spring_green3",
        "table.header": "bold spring_green3",
        "table.border": "sea_green3",
        "ok": "green3",
        "warn": "yellow3",
        "error": "red",
        "star": "spring_green3",
    }
)
console = Console(theme=THEME)

# Carpeta de datos: <root>/data/biblioteca.json
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_ARCHIVO_BIB = _DATA_DIR / "biblioteca.json"


# ---------------------------
# Utilidades y validaciones
# ---------------------------


def _ruta_biblioteca(ruta: Path | None = None) -> Path:
    """Obtiene la ruta efectiva del archivo JSON de la biblioteca.

    Args:
        ruta: Ruta alternativa del archivo (opcional).

    Returns:
        Ruta del archivo a utilizar (Path).
    """
    return ruta if ruta is not None else _ARCHIVO_BIB


def _normalizar_id(texto: str) -> str:
    """Normaliza y valida el id del libro.

    Colapsa espacios y verifica que no quede vacío.

    Args:
        texto: Identificador del libro.

    Returns:
        ID normalizado (sin espacios duplicados).

    Raises:
        ValueError: Si el id queda vacío tras normalizar.
    """
    limpio = " ".join(str(texto).split())
    if not limpio:
        raise ValueError("El id del libro no puede estar vacío.")
    return limpio


def _normalizar_nombre(texto: str) -> str:
    """Normaliza y valida el nombre del aprendiz.

    Args:
        texto: Nombre libre del aprendiz.

    Returns:
        Nombre normalizado.

    Raises:
        ValueError: Si el nombre queda vacío tras normalizar.
    """
    limpio = " ".join(str(texto).split())
    if not limpio:
        raise ValueError("El nombre del aprendiz no puede estar vacío.")
    return limpio


def _normalizar_titulo(texto: str) -> str:
    """Normaliza y valida el título del libro.

    Args:
        texto: Título del libro.

    Returns:
        Título normalizado.

    Raises:
        ValueError: Si el título queda vacío tras normalizar.
    """
    limpio = " ".join(str(texto).split())
    if not limpio:
        raise ValueError("El título no puede estar vacío.")
    return limpio


def _validar_libro_dict(libro: dict[str, Any]) -> dict[str, Any]:
    """Valida y normaliza un diccionario de libro.

    Reglas:
      - libro_id: str no vacío.
      - titulo: str no vacío.
      - prestado_a: str no vacío o None.

    Args:
        libro: Diccionario con claves libro_id, titulo, prestado_a.

    Returns:
        Diccionario normalizado con tipos y campos validados.

    Raises:
        TypeError: Si faltan claves o tipos inválidos.
        ValueError: Si algún valor es inválido (por ejemplo, vacío).
    """
    if not isinstance(libro, dict):
        raise TypeError("Cada libro debe ser un diccionario.")
    for clave in ("libro_id", "titulo", "prestado_a"):
        if clave not in libro:
            raise TypeError(f"Falta la clave obligatoria: {clave!r}")

    libro_id = _normalizar_id(str(libro["libro_id"]))
    titulo = _normalizar_titulo(str(libro["titulo"]))
    prest_raw = libro["prestado_a"]
    if prest_raw is None:
        prestado_a: str | None = None
    else:
        prestado_a = _normalizar_nombre(str(prest_raw))

    return {"libro_id": libro_id, "titulo": titulo, "prestado_a": prestado_a}


def _buscar_indice(biblioteca: list[dict[str, Any]], libro_id: str) -> int | None:
    """Busca el índice de un libro por id (insensible a mayúsculas).

    Args:
        biblioteca: Lista de libros.
        libro_id: Identificador a localizar.

    Returns:
        Índice del libro si se encuentra; None en caso contrario.
    """
    objetivo = _normalizar_id(libro_id).lower()
    for idx, libro in enumerate(biblioteca):
        if str(libro.get("libro_id", "")).lower() == objetivo:
            return idx
    return None


# ---------------------------
# Persistencia
# ---------------------------


def cargar_biblioteca(ruta: Path | None = None) -> list[dict[str, Any]]:
    """Carga la biblioteca desde JSON; ignora entradas inválidas.

    Args:
        ruta: Ruta alternativa del archivo (opcional).

    Returns:
        Lista de libros normalizados. Si el archivo no existe o es inválido, [].
    """
    archivo = _ruta_biblioteca(ruta)
    if not archivo.exists():
        return []
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError:
        return []

    if not isinstance(datos, list):
        return []

    libros: list[dict[str, Any]] = []
    for item in datos:
        try:
            libros.append(_validar_libro_dict(item))
        except (TypeError, ValueError):
            continue
    return libros


def guardar_biblioteca(
    biblioteca: list[dict[str, Any]],
    ruta: Path | None = None,
) -> None:
    """Guarda la biblioteca en disco (JSON indentado, UTF-8).

    Args:
        biblioteca: Lista de libros a persistir.
        ruta: Ruta alternativa del archivo (opcional).

    Returns:
        None

    Raises:
        TypeError: Si la estructura no es una lista.
        ValueError: Si algún libro no pasa la validación.
        OSError: Si ocurre un error de E/S al escribir.
    """

    if not isinstance(biblioteca, list):
        raise TypeError("biblioteca debe ser una lista de libros.")
    normalizados = [_validar_libro_dict(_) for _ in biblioteca]

    archivo = _ruta_biblioteca(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with open(archivo, "w", encoding="utf-8") as fh:
        json.dump(normalizados, fh, ensure_ascii=False, indent=2)


# ---------------------------
# Operaciones de negocio
# ---------------------------


def prestar_libro(
    biblioteca: list[dict[str, Any]],
    libro_id: str,
    nombre_aprendiz: str,
    ruta: Path | None = None,
) -> dict[str, Any]:
    """Marca un libro como prestado a un aprendiz y persiste el cambio.

    Args:
        biblioteca: Lista en memoria a modificar.
        libro_id: Identificador del libro a prestar.
        nombre_aprendiz: Nombre del aprendiz beneficiario.
        ruta: Ruta de persistencia (opcional).

    Returns:
        El diccionario del libro actualizado.

    Raises:
        KeyError: Si el libro no existe.
        ValueError: Si ya está prestado o entradas inválidas.
    """
    indice = _buscar_indice(biblioteca, libro_id)
    if indice is None:
        raise KeyError(f"No existe el libro con id: {libro_id!r}")

    aprendiz = _normalizar_nombre(nombre_aprendiz)
    libro = biblioteca[indice]
    if libro["prestado_a"] is not None:
        raise ValueError("El libro ya está prestado.")
    libro["prestado_a"] = aprendiz

    guardar_biblioteca(biblioteca, ruta=ruta)
    return libro


def devolver_libro(
    biblioteca: list[dict[str, Any]],
    libro_id: str,
    ruta: Path | None = None,
) -> dict[str, Any]:
    """Marca un libro como disponible (prestado_a = None) y persiste.

    Args:
        biblioteca: Lista en memoria a modificar.
        libro_id: Identificador del libro a devolver.
        ruta: Ruta de persistencia (opcional).

    Returns:
        El diccionario del libro actualizado.

    Raises:
        KeyError: Si el libro no existe.
        ValueError: Si el libro no estaba prestado.
    """
    indice = _buscar_indice(biblioteca, libro_id)
    if indice is None:
        raise KeyError(f"No existe el libro con id: {libro_id!r}")

    libro = biblioteca[indice]
    if libro["prestado_a"] is None:
        raise ValueError("El libro no estaba prestado.")
    libro["prestado_a"] = None

    guardar_biblioteca(biblioteca, ruta=ruta)
    return libro


def buscar_libro(
    biblioteca: list[dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:
    """Busca libros por título (contiene, insensible a mayúsculas).

    Usa filter + lambda.

    Args:
        biblioteca: Lista de libros.
        query: Texto a buscar dentro del título.

    Returns:
        Lista de libros cuyo título contiene la consulta.
    """
    consulta = " ".join(query.split()).casefold()
    if not consulta:
        return []

    return list(
        filter(
            lambda _: consulta in str(_.get("titulo", "")).casefold(),
            biblioteca,
        )
    )


def ver_libros_prestados(biblioteca: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Devuelve todos los libros actualmente prestados.

    Usa filter + lambda.

    Args:
        biblioteca: Lista de libros.

    Returns:
        Lista de libros con prestado_a no vacío.
    """
    return list(
        filter(
            lambda _: (_.get("prestado_a") is not None)
            and bool(str(_.get("prestado_a")).strip()),
            biblioteca,
        )
    )


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el panel de encabezado con estrellitas y estilos del tema.

    Returns:
        Panel con título y subtítulo del ejercicio.
    """
    estrellas = "[star]" + "★ " * 18 + "[/star]"
    texto = (
        f"{estrellas}\n"
        "[title]Mini Sistema de Biblioteca[/title]\n"
        "[subtitle]Persistencia en data/biblioteca.json[/subtitle]\n"
        f"{estrellas}"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 15[/accent]",
        subtitle="[muted]JSON + filter + lambda[/muted]",
        border_style="menu.border",
        box=box.DOUBLE,
    )


def _panel_menu() -> Panel:
    """Panel del menú con opciones y claves resaltadas.

    Returns:
        Panel estilizado con las opciones disponibles.
    """
    texto = (
        "[menu.title]Opciones[/menu.title]\n"
        "[menu.key]1)[/menu.key] [menu.option]Ver todos los libros[/menu.option]\n"
        "[menu.key]2)[/menu.key] [menu.option]Ver libros prestados[/menu.option]\n"
        "[menu.key]3)[/menu.key] [menu.option]Buscar libro por título[/menu.option]\n"
        "[menu.key]4)[/menu.key] [menu.option]Prestar libro[/menu.option]\n"
        "[menu.key]5)[/menu.key] [menu.option]Devolver libro[/menu.option]\n"
        "[menu.key]6)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(texto, title="[accent]Menú[/accent]"
                 , border_style="menu.border", box=box.HEAVY)


def _tabla_libros(libros: list[dict[str, Any]], titulo: str) -> Table:
    """Crea la tabla Rich de libros con estilos del tema.

    Args:
        libros: Lista de diccionarios de libros.
        titulo: Título a mostrar en la tabla.

    Returns:
        Tabla Rich con numeración, id, título y prestatario.
    """
    tabla = Table(
        title=f"[accent]{titulo}[/accent]",
        show_lines=True,
        expand=True,
        box=box.MINIMAL_HEAVY_HEAD,
        header_style="table.header",
        border_style="table.border",
        title_style="table.header",
    )
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("ID")
    tabla.add_column("Título")
    tabla.add_column("Prestado a", justify="left", style="muted")
    if not libros:
        tabla.add_row("—", "—", "—", "—")
        return tabla
    for idx, _ in enumerate(libros, start=1):
        tabla.add_row(str(idx), _["libro_id"], _["titulo"], str(_["prestado_a"]))
    return tabla


def _panel_info_archivo(archivo: Path) -> Panel:
    """Panel informativo con la ubicación del archivo de datos.

    Args:
        archivo: Ruta del JSON de biblioteca.

    Returns:
        Panel compacto estilizado con el tema.
    """
    return Panel.fit(
        f"[muted]Archivo:[/muted] [accent]{archivo}[/accent]",
        title="[accent]Ubicación de datos[/accent]",
        border_style="menu.border",
        box=box.ROUNDED,
    )


def mostrar_libros(
    libros: list[dict[str, Any]],
    titulo: str = "Libros",
) -> None:
    """Muestra libros en una tabla Rich con un panel de ubicación.

    Args:
        libros: Lista de diccionarios de libros a mostrar.
        titulo: Texto del título de la tabla.

    Returns:
        None
    """
    paneles = [_panel_info_archivo(_ARCHIVO_BIB), _tabla_libros(libros, titulo)]
    console.print(Columns(paneles, equal=True, expand=True))


def _asegurar_ejemplo() -> None:
    """Crea biblioteca de ejemplo si no existe el archivo.

    Returns:
        None
    """
    if _ARCHIVO_BIB.exists():
        return
    ejemplo = [
        {"libro_id": "001", "titulo": "Cien Años de Soledad", "prestado_a": None},
        {"libro_id": "002", "titulo":
            "El Amor en los Tiempos del Cólera", "prestado_a": None},
        {"libro_id": "003", "titulo": "La Ciudad y los Perros", "prestado_a": None},
        {"libro_id": "004", "titulo": "Rayuela", "prestado_a": None},
    ]
    guardar_biblioteca(ejemplo)


# ---------------------------
# Interfaz interactiva
# ---------------------------


def menu() -> None:
    """Interfaz con Rich para gestionar préstamos de la biblioteca.

    Muestra un menú interactivo para listar, buscar, prestar y devolver libros.

    Args:
        None

    Returns:
        None
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _asegurar_ejemplo()
    biblioteca = cargar_biblioteca()

    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[title]Elige una opción[/title]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1",
        )

        if opcion == "1":
            mostrar_libros(biblioteca, "Todos los libros")

        elif opcion == "2":
            mostrar_libros(ver_libros_prestados(biblioteca), "Prestados")

        elif opcion == "3":
            q = Prompt.ask("[accent]Título o parte "
                           "del título a buscar[/accent]").strip()
            mostrar_libros(buscar_libro(biblioteca, q), f"Búsqueda: {q}")

        elif opcion == "4":
            try:
                libro_id = Prompt.ask("[accent]ID del libro[/accent]").strip()
                aprendiz = Prompt.ask("[accent]Nombre del aprendiz[/accent]").strip()
                libro = prestar_libro(biblioteca, libro_id, aprendiz)
                console.print(
                    Panel.fit(
                        f"[ok]★ Préstamo registrado:[/ok] {libro['titulo']}"
                        f" -> [accent]{libro['prestado_a']}[/accent]",
                        border_style="ok",
                        title="[accent]OK[/accent]",
                        box=box.ROUNDED,
                    )
                )
            except (KeyError, ValueError) as exc:
                console.print(
                    Panel.fit(
                        f"[error]Error:[/error] {exc}",
                        border_style="error",
                        title="[accent]Operación inválida[/accent]",
                        box=box.HEAVY,
                    )
                )

        elif opcion == "5":
            try:
                libro_id = Prompt.ask("[accent]ID del libro[/accent]").strip()
                libro = devolver_libro(biblioteca, libro_id)
                console.print(
                    Panel.fit(
                        f"[ok]★ Devolución completada:[/ok] {libro['titulo']}",
                        border_style="ok",
                        title="[accent]OK[/accent]",
                        box=box.ROUNDED,
                    )
                )
            except (KeyError, ValueError) as exc:
                console.print(
                    Panel.fit(
                        f"[error]Error:[/error] {exc}",
                        border_style="error",
                        title="[accent]Operación inválida[/accent]",
                        box=box.HEAVY,
                    )
                )

        elif opcion == "6":
            break

        _ = Prompt.ask(
            "\n[muted]Enter para continuar (o escribe 'salir' para terminar)[/muted]",
            default="",
        )
        if _.strip().lower() == "salir":
            break


def main() -> None:
    """Punto de entrada: solo invoca el menú.

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
