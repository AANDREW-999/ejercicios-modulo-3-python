"""Analizador de columnas numéricas en CSV con interfaz enriquecida con Rich.

Este módulo lee un CSV con DictReader, convierte de forma segura una columna
a números (tolerando coma decimal), filtra no numéricos y devuelve un resumen
estadístico (promedio, máximo y mínimo). Incluye una interfaz de consola
coloreada con Rich para ejecutar un ejemplo o analizar un archivo personalizado.

Tecnologías:
- Python 3.x, csv.DictReader, Rich (con Table, Panel, Columns, Prompt).

Notas:
- Se busca el archivo en la ruta indicada o en la carpeta data/ del proyecto.
- Los valores no numéricos o vacíos se descartan con una conversión tolerante.
"""

from __future__ import annotations

import csv
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = ["analizar_csv", "menu", "main"]

# Tema exclusivo (dorado/ámbar) con “estrellitas”
THEME = Theme(
    {
        "title": "bold gold3",
        "subtitle": "tan",
        "accent": "bold orange3",
        "muted": "grey66",
        "menu.title": "bold gold3",
        "menu.option": "sandy_brown",
        "menu.key": "yellow3",
        "menu.border": "gold3",
        "table.header": "bold gold3",
        "table.border": "orange3",
        "ok": "green4",
        "warn": "yellow3",
        "error": "red",
        "star": "gold1",
    }
)
console = Console(theme=THEME)

# Carpeta de datos en la raíz del proyecto.
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_CSV_EJEMPLO = _DATA_DIR / "estudiantes.csv"


def _resolver_ruta_csv(nombre_archivo: str) -> Path:
    """Resuelve la ruta final al archivo CSV.

    Si `nombre_archivo` es una ruta existente (absoluta o relativa), se usa tal cual.
    En caso contrario, se intenta en la carpeta data/ del proyecto.

    Args:
        nombre_archivo: Nombre de archivo o ruta al CSV.

    Returns:
        Ruta final al archivo CSV (Path).

    Raises:
        FileNotFoundError: Si el archivo no existe en ninguna ubicación.
    """
    ruta = Path(nombre_archivo)
    if ruta.exists():
        return ruta
    candidato = _DATA_DIR / nombre_archivo
    if candidato.exists():
        return candidato
    raise FileNotFoundError(
        f"No se encontró el archivo CSV: '{nombre_archivo}'. "
        f"Busca en: {ruta} o {candidato}"
    )


def _to_float_or_none(texto: str | None) -> float | None:
    """Convierte un string a float de forma tolerante.

    Acepta coma decimal (',') y recorta espacios. Si no es convertible, retorna None.

    Args:
        texto: Cadena a convertir (puede ser None).

    Returns:
        float convertido o None si no es numérico.
    """
    if texto is None:
        return None
    valor = texto.strip().replace(",", ".")
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        return None


def analizar_csv(nombre_archivo: str, columna: str) -> dict[str, float]:
    """Analiza una columna numérica de un CSV y devuelve promedio, máximo y mínimo.

    Se usa csv.DictReader. Los valores se convierten a float con _to_float_or_none y
    se filtran no numéricos.

    Args:
        nombre_archivo: Ruta o nombre del CSV (se busca en data/ si no existe).
        columna: Nombre de la columna a analizar (p. ej., 'edad' o 'calificacion').

    Returns:
        Diccionario con claves: 'promedio', 'max', 'min' (floats redondeados a 2 dec.).

    Raises:
        FileNotFoundError: Si el archivo no existe.
        KeyError: Si la columna no está en el CSV.
        ValueError: Si no hay datos numéricos válidos o no hay encabezados.
    """
    ruta = _resolver_ruta_csv(nombre_archivo)

    with open(ruta, "r", encoding="utf-8-sig", newline="") as fh:
        lector = csv.DictReader(fh)
        if lector.fieldnames is None:
            raise ValueError("El CSV no contiene encabezados.")
        campos = [c.strip() for c in lector.fieldnames]
        if columna not in campos:
            raise KeyError(
                f"La columna '{columna}' no existe. "
                f"Columnas disponibles: {', '.join(campos)}"
            )

        # Extrae valores de la columna y filtra los no numéricos.
        valores_raw = [fila.get(columna) for fila in lector]
        valores_num = list(
            filter(lambda x: x is not None, map(_to_float_or_none, valores_raw))
        )

    if not valores_num:
        raise ValueError(
            f"No hay datos numéricos válidos en la columna '{columna}'."
        )

    promedio = round(sum(valores_num) / len(valores_num), 2)
    maximo = round(max(valores_num), 2)
    minimo = round(min(valores_num), 2)

    return {"promedio": promedio, "max": maximo, "min": minimo}


# ---------------------------
# Utilidades de interfaz
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el encabezado principal con decoración de estrellitas.

    Returns:
        Panel con título, subtítulo y borde estilizado del tema.
    """
    estrellas = "[star]" + "★ " * 18 + "[/star]"
    texto = (
        f"{estrellas}\n"
        "[title]Analizador de Datos CSV[/title]\n"
        "[subtitle]DictReader, conversión de tipos y resumen estadístico[/subtitle]\n"
        f"{estrellas}"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 12[/accent]",
        subtitle="[muted]csv + filter + lambda[/muted]",
        border_style="menu.border",
        box=box.DOUBLE,
    )


def _panel_menu() -> Panel:
    """Panel del menú principal con opciones y claves resaltadas.

    Returns:
        Panel estilizado con las opciones disponibles.
    """
    texto = (
        "[menu.title]Opciones[/menu.title]\n"
        "[menu.key]1)[/menu.key] "
        "[menu.option]Ejecutar ejemplo por defecto "
        "(data/estudiantes.csv)[/menu.option]\n"
        "[menu.key]2)[/menu.key] "
        "[menu.option]Analizar archivo y columna personalizados[/menu.option]\n"
        "[menu.key]3)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(
        texto, title="[accent]Menú[/accent]", border_style="menu.border"
        , box=box.HEAVY)


def _tabla_resultados(
    resultados: dict[str, float], archivo: Path, columna: str
) -> Table:
    """Crea la tabla de resultados con estilos y alineaciones.

    Args:
        resultados: Diccionario con 'promedio', 'max' y 'min'.
        archivo: Ruta del archivo analizado.
        columna: Nombre de la columna analizada.

    Returns:
        Tabla Rich con los valores formateados y estilos del tema.
    """
    tabla = Table(
        title="[accent]Resultados del análisis[/accent]",
        show_lines=True,
        expand=True,
        box=box.MINIMAL_HEAVY_HEAD,
        header_style="table.header",
        border_style="table.border",
        title_style="table.header",
    )
    tabla.add_column("Archivo", overflow="fold")
    tabla.add_column("Columna")
    tabla.add_column("Promedio", justify="right")
    tabla.add_column("Máximo", justify="right")
    tabla.add_column("Mínimo", justify="right")
    tabla.add_row(
        str(archivo),
        columna,
        f"{resultados['promedio']:.2f}",
        f"{resultados['max']:.2f}",
        f"{resultados['min']:.2f}",
    )
    return tabla


def _panel_info_archivo(archivo: Path) -> Panel:
    """Panel informativo con la ubicación del archivo de datos.

    Args:
        archivo: Ruta al CSV utilizado.

    Returns:
        Panel compacto con la ruta mostrada.
    """
    return Panel.fit(
        f"[muted]Archivo:[/muted] [accent]{archivo}[/accent]",
        title="[accent]Ubicación de datos[/accent]",
        border_style="menu.border",
        box=box.ROUNDED,
    )


def _asegurar_csv_ejemplo() -> Path:
    """Crea un CSV de ejemplo en data/ si no existe.

    Returns:
        Ruta al archivo CSV de ejemplo.
    """
    if _CSV_EJEMPLO.exists():
        return _CSV_EJEMPLO
    filas = [
        {"nombre": "Ana", "edad": "20", "calificacion": "4.5"},
        {"nombre": "Juan", "edad": "22", "calificacion": "2.8"},
        {"nombre": "María", "edad": "21", "calificacion": "3.9"},
        {"nombre": "Luis", "edad": "23", "calificacion": "4.8"},
        {"nombre": "Sofía", "edad": "20", "calificacion": "3.5"},
    ]
    with open(_CSV_EJEMPLO, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(
            fh, fieldnames=["nombre", "edad", "calificacion"]
        )
        escritor.writeheader()
        escritor.writerows(filas)
    return _CSV_EJEMPLO


# ---------------------------
# Interfaz interactiva
# ---------------------------


def _flujo_ejemplo() -> None:
    """Ejecuta el análisis sobre el CSV de ejemplo y presenta resultados.

    Returns:
        None
    """
    archivo = _asegurar_csv_ejemplo()
    columna = Prompt.ask(
        "[accent]Columna a analizar[/accent]",
        choices=["edad", "calificacion"],
        default="calificacion",
    )
    try:
        res = analizar_csv(str(archivo), columna)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(
            Panel.fit(
                f"[error]Error:[/error] {exc}",
                border_style="error",
                title="[accent]Entrada inválida[/accent]",
                box=box.HEAVY,
            )
        )
        return

    paneles = [_panel_info_archivo(archivo), _tabla_resultados(res, archivo, columna)]
    console.print(Columns(paneles, equal=True, expand=True))


def _flujo_personalizado() -> None:
    """Solicita archivo y columna, ejecuta el análisis y muestra resultados.

    Returns:
        None
    """
    nombre = Prompt.ask(
        "[accent]Nombre de archivo[/accent] "
        "[muted](se buscará en data/ si no es una ruta)[/muted]",
        default="estudiantes.csv",
    )
    columna = Prompt.ask("[accent]Columna a analizar[/accent]", default="calificacion")
    try:
        ruta = _resolver_ruta_csv(nombre)
        res = analizar_csv(nombre, columna)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(
            Panel.fit(
                f"[error]Error:[/error] {exc}",
                border_style="error",
                title="[accent]Entrada inválida[/accent]",
                box=box.HEAVY,
            )
        )
        return

    paneles = [_panel_info_archivo(ruta), _tabla_resultados(res, ruta, columna)]
    console.print(Columns(paneles, equal=True, expand=True))


def menu() -> None:
    """Interfaz con Rich para analizar columnas numéricas en archivos CSV.

    Muestra un menú con opciones para ejecutar el ejemplo por defecto o
    analizar un archivo y columna personalizados. Presenta resultados en tablas.

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
            choices=["1", "2", "3"],
            default="1",
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
            "\n\n[bold red]Programa interrumpido por el usuario. "
            "Adiós.[/bold red]"
        )
