"""Generador de reportes (CSV + JSON -> TXT) con interfaz Rich.

Funciones:
- Entrada: leer_csv_estudiantes, leer_json_cursos.
- Transformación: generar_reporte.
- UI: vista previa del reporte, guardado, menú y main.

Tecnologías:
- Python 3.x, csv.DictReader, json, Rich (Panel, Table, Columns, Prompt).

Notas:
- Archivos por defecto en data/: estudiantes.csv, cursos.json, reporte.txt.
- Tema visual exclusivo (zafiro/azul) y estrellitas decorativas.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = [
    "leer_csv_estudiantes",
    "leer_json_cursos",
    "generar_reporte",
    "menu",
    "main",
]

# Tema zafiro/azul con estrellitas
THEME = Theme(
    {
        "title": "bold royal_blue1",
        "subtitle": "steel_blue",
        "accent": "bold deep_sky_blue1",
        "muted": "grey62",
        "menu.title": "bold royal_blue1",
        "menu.option": "steel_blue",
        "menu.key": "bold deep_sky_blue1",
        "menu.border": "royal_blue1",
        "table.header": "bold royal_blue1",
        "table.border": "sky_blue2",
        "ok": "green3",
        "warn": "yellow3",
        "error": "red",
        "star": "royal_blue1",
    }
)
console = Console(theme=THEME)

# Carpeta de datos en la raíz del proyecto
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_ARCH_CSV_DEF = _DATA_DIR / "estudiantes.csv"
_ARCH_JSON_DEF = _DATA_DIR / "cursos.json"
_ARCH_REP_DEF = _DATA_DIR / "reporte.txt"


def _resolver_en_data(nombre_archivo: str) -> Path:
    """Resuelve la ruta real de un archivo, buscando en data/ si no existe localmente.

    Args:
        nombre_archivo: Nombre o ruta del archivo a resolver.

    Returns:
        Ruta final al archivo.

    Raises:
        FileNotFoundError: Si no se encuentra en ninguna ubicación.
    """
    ruta = Path(nombre_archivo)
    if ruta.exists():
        return ruta
    candidato = _DATA_DIR / nombre_archivo
    if candidato.exists():
        return candidato
    raise FileNotFoundError(
        f"No se encontró el archivo: '{nombre_archivo}'. "
        f"Buscado en {ruta} y {candidato}"
    )


def _parsear_cursos(texto: str) -> list[str]:
    """Convierte 'ID1;ID2;ID3' en lista de IDs, limpiando espacios y vacíos.

    Usa filter + lambda para filtrar tokens vacíos.

    Args:
        texto: Cadena con IDs separados por ';'.

    Returns:
        Lista de IDs de cursos no vacíos.
    """
    tokens = [t.strip() for t in texto.split(";")]
    return list(filter(lambda s: bool(s), tokens))


def leer_csv_estudiantes(nombre_archivo: str | Path) -> list[dict[str, Any]]:
    """Lee estudiantes desde un CSV y devuelve una lista de dicts normalizados.

    Formato esperado del CSV (encabezados obligatorios):
      - nombre: str
      - cursos: cadena separada por ';' con IDs de cursos (ej. 'PY;JS;DB').

    Args:
        nombre_archivo: Ruta o nombre del CSV. Si no existe, se busca en data/.

    Returns:
        Lista de dicts con 'nombre' (str) y 'cursos' (list[str]).

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si faltan encabezados o el CSV está vacío.
    """
    ruta = _resolver_en_data(str(nombre_archivo))
    with open(ruta, "r", encoding="utf-8-sig", newline="") as fh:
        lector = csv.DictReader(fh)
        if lector.fieldnames is None:
            raise ValueError("El CSV no contiene encabezados.")
        campos = [c.strip() for c in lector.fieldnames]
        requeridos = {"nombre", "cursos"}
        if not requeridos.issubset(set(campos)):
            raise ValueError(
                "Encabezados inválidos. Se requieren: 'nombre' y 'cursos'. "
                f"Encontrados: {', '.join(campos)}"
            )

        estudiantes: list[dict[str, Any]] = []
        for fila in lector:
            nombre = (fila.get("nombre") or "").strip()
            cursos_txt = (fila.get("cursos") or "").strip()
            if not nombre:
                continue
            cursos_ids = _parsear_cursos(cursos_txt)
            estudiantes.append({"nombre": nombre, "cursos": cursos_ids})
    return estudiantes


def leer_json_cursos(nombre_archivo: str | Path) -> dict[str, str]:
    """Lee cursos desde JSON y devuelve un mapeo id -> nombre.

    Formatos aceptados:
      - Objeto: {"PY": "Python", "JS": "JavaScript"}
      - Lista: [{"id": "PY", "nombre": "Python"}, ...]

    Args:
        nombre_archivo: Ruta o nombre del JSON. Si no existe, se busca en data/.

    Returns:
        Diccionario id -> nombre del curso.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la estructura no es compatible.
    """
    ruta = _resolver_en_data(str(nombre_archivo))
    with open(ruta, "r", encoding="utf-8") as fh:
        datos = json.load(fh)

    if isinstance(datos, dict):
        return {str(k): str(v) for k, v in datos.items()}

    if isinstance(datos, list):
        cursos: dict[str, str] = {}
        for item in datos:
            if not isinstance(item, dict):
                continue
            cid = str(item.get("id", "")).strip()
            nombre = str(item.get("nombre", "")).strip()
            if cid and nombre:
                cursos[cid] = nombre
        return cursos

    raise ValueError("Estructura JSON no compatible para cursos.")


def generar_reporte(
    estudiantes: list[dict[str, Any]],
    cursos: dict[str, str],
) -> str:
    """Genera el contenido de reporte como texto a partir de estudiantes/cursos.

    Para cada estudiante:
      - Mapea sus IDs de curso a nombres legibles.
      - Omite IDs desconocidos.
      - Si no tiene cursos válidos, usa '(sin cursos)'.

    Args:
        estudiantes: Lista de dicts con 'nombre' y 'cursos'.
        cursos: Mapa id->nombre de cursos.

    Returns:
        Texto listo para guardar en reporte.txt (termina con salto final si hay líneas).

    Raises:
        TypeError: Si las estructuras de entrada no tienen el formato esperado.
    """
    if not isinstance(estudiantes, list):
        raise TypeError("estudiantes debe ser una lista.")
    if not isinstance(cursos, dict):
        raise TypeError("cursos debe ser un diccionario.")

    lineas: list[str] = []
    for est in estudiantes:
        if not isinstance(est, dict):
            raise TypeError("Cada estudiante debe ser un diccionario.")
        nombre = str(est.get("nombre", "")).strip()
        ids: list[str] = list(est.get("cursos", []))
        if not nombre:
            continue
        ids_validos = list(filter(lambda cid: cid in cursos, ids))
        nombres = [cursos[cid] for cid in ids_validos]
        cursos_txt = ", ".join(nombres) if nombres else "(sin cursos)"
        lineas.append(f"{nombre}: {cursos_txt}")

    return "\n".join(lineas) + ("\n" if lineas else "")


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el encabezado principal con estrellitas y estilos del tema.

    Returns:
        Panel con título y subtítulo del ejercicio.
    """
    estrellas = "[star]" + "★ " * 18 + "[/star]"
    texto = (
        f"{estrellas}\n"
        "[title]Generador de Reportes[/title]\n"
        "[subtitle]CSV + JSON -> reporte.txt en data/[/subtitle]\n"
        f"{estrellas}"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 14[/accent]",
        subtitle="[muted]csv + json + filter + lambda[/muted]",
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
        "[menu.key]1)[/menu.key] "
        "[menu.option]Ejecutar ejemplo por defecto "
        "(data/estudiantes.csv y cursos.json)[/menu.option]\n"
        "[menu.key]2)[/menu.key] "
        "[menu.option]Usar archivos personalizados[/menu.option]\n"
        "[menu.key]3)[/menu.key] "
        "[menu.option]Ver reporte actual (data/reporte.txt)[/menu.option]\n"
        "[menu.key]4)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(texto, title="[accent]Menú[/accent]", border_style="menu.border"
                 , box=box.HEAVY)


def _tabla_reporte(contenido: str) -> Table:
    """Crea la tabla de vista previa del reporte.

    Args:
        contenido: Texto del reporte a mostrar.

    Returns:
        Tabla Rich con numeración y contenido.
    """
    tabla = Table(
        title="[accent]Vista previa del reporte[/accent]",
        show_lines=True,
        expand=True,
        box=box.MINIMAL_HEAVY_HEAD,
        header_style="table.header",
        border_style="table.border",
        title_style="table.header",
    )
    tabla.add_column("#", justify="right", style="bold")
    tabla.add_column("Línea", overflow="fold")
    if not contenido.strip():
        tabla.add_row("—", "—")
        return tabla
    for idx, linea in enumerate(contenido.splitlines(), start=1):
        tabla.add_row(str(idx), linea)
    return tabla


def _panel_info_archivos(csv_path: Path, json_path: Path) -> Panel:
    """Panel informativo con las ubicaciones de los archivos de datos.

    Args:
        csv_path: Ruta al CSV de estudiantes.
        json_path: Ruta al JSON de cursos.

    Returns:
        Panel compacto estilizado con el tema.
    """
    texto = (
        f"[muted]CSV:[/muted] [accent]{csv_path}[/accent]\n"
        f"[muted]JSON:[/muted] [accent]{json_path}[/accent]\n"
        f"[muted]Reporte destino:[/muted] [accent]{_ARCH_REP_DEF}[/accent]"
    )
    return Panel.fit(texto, title="[accent]Ubicaciones[/accent]"
                     , border_style="menu.border", box=box.ROUNDED)


def _asegurar_datos_ejemplo() -> tuple[Path, Path]:
    """Crea archivos de ejemplo en data/ si no existen.

    Returns:
        Tupla con rutas a (CSV, JSON) creados o existentes.
    """
    if not _ARCH_CSV_DEF.exists():
        filas = [
            {"nombre": "Ana", "cursos": "PY;JS"},
            {"nombre": "Juan", "cursos": "DB;JS"},
            {"nombre": "María", "cursos": "PY;DATA;XXX"},
            {"nombre": "Sofía", "cursos": ""},
        ]
        with open(_ARCH_CSV_DEF, "w", encoding="utf-8", newline="") as fh:
            escritor = csv.DictWriter(fh, fieldnames=["nombre", "cursos"])
            escritor.writeheader()
            escritor.writerows(filas)
    if not _ARCH_JSON_DEF.exists():
        cursos = [
            {"id": "PY", "nombre": "Python"},
            {"id": "JS", "nombre": "JavaScript"},
            {"id": "DB", "nombre": "Bases de Datos"},
            {"id": "DATA", "nombre": "Análisis de Datos"},
        ]
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(_ARCH_JSON_DEF, "w", encoding="utf-8") as fh:
            json.dump(cursos, fh, ensure_ascii=False, indent=2)
    return _ARCH_CSV_DEF, _ARCH_JSON_DEF


def _generar_y_mostrar(csv_path: Path, json_path: Path) -> str:
    """Genera el reporte y lo muestra en consola con tablas y paneles.

    Args:
        csv_path: Ruta al CSV de estudiantes.
        json_path: Ruta al JSON de cursos.

    Returns:
        El contenido del reporte generado.
    """
    estudiantes = leer_csv_estudiantes(str(csv_path))
    cursos = leer_json_cursos(str(json_path))
    contenido = generar_reporte(estudiantes, cursos)
    paneles = [
        _panel_info_archivos(csv_path, json_path),
        _tabla_reporte(contenido),
    ]
    console.print(Columns(paneles, equal=True, expand=True))
    return contenido


def _guardar_reporte(texto: str, destino: Path | None = None) -> None:
    """Guarda el reporte en data/reporte.txt (o ruta indicada).

    Args:
        texto: Contenido a persistir.
        destino: Ruta alternativa del archivo (opcional).

    Returns:
        None

    Raises:
        OSError: Si ocurre un error al escribir.
    """
    destino = destino or _ARCH_REP_DEF
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(texto)


# ---------------------------
# Interfaz interactiva
# ---------------------------


def menu() -> None:
    """Interfaz con Rich para generar y guardar reportes por alumno.

    Presenta opciones para ejecutar el ejemplo por defecto, usar archivos
    personalizados y ver el reporte actual.

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
            "[title]Elige una opción[/title]",
            choices=["1", "2", "3", "4"],
            default="1",
        )

        if opcion == "1":
            csv_path, json_path = _asegurar_datos_ejemplo()
            contenido = _generar_y_mostrar(csv_path, json_path)
            if Confirm.ask("¿Guardar en [accent]data/reporte.txt[/accent]?"
                    , default=True):
                _guardar_reporte(contenido)
                console.print(
                    Panel.fit(
                        "[ok]★ Reporte guardado en data/reporte.txt[/ok]",
                        border_style="ok",
                        title="[accent]OK[/accent]",
                        box=box.ROUNDED,
                    )
                )

        elif opcion == "2":
            try:
                nombre_csv = Prompt.ask(
                    "[accent]Nombre o ruta del CSV de estudiantes[/accent]",
                    default=str(_ARCH_CSV_DEF.name),
                )
                nombre_json = Prompt.ask(
                    "[accent]Nombre o ruta del JSON de cursos[/accent]",
                    default=str(_ARCH_JSON_DEF.name),
                )
                csv_path = _resolver_en_data(nombre_csv)
                json_path = _resolver_en_data(nombre_json)
                contenido = _generar_y_mostrar(csv_path, json_path)
                if Confirm.ask("¿Guardar en [accent]data/reporte.txt[/accent]?"
                        , default=True):
                    _guardar_reporte(contenido)
                    console.print(
                        Panel.fit(
                            "[ok]★ Reporte guardado en data/reporte.txt[/ok]",
                            border_style="ok",
                            title="[accent]OK[/accent]",
                            box=box.ROUNDED,
                        )
                    )
            except (FileNotFoundError, ValueError) as exc:
                console.print(
                    Panel.fit(
                        f"[error]Error:[/error] {exc}",
                        border_style="error",
                        title="[accent]Entrada inválida[/accent]",
                        box=box.HEAVY,
                    )
                )

        elif opcion == "3":
            if not _ARCH_REP_DEF.exists():
                console.print(
                    Panel.fit(
                        "[warn]No existe data/reporte.txt[/warn]",
                        border_style="warn",
                        title="[accent]Aviso[/accent]",
                        box=box.ROUNDED,
                    )
                )
            else:
                contenido = _ARCH_REP_DEF.read_text(encoding="utf-8")
                console.print(_tabla_reporte(contenido))

        elif opcion == "4":
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
