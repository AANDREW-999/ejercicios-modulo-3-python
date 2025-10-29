"""Gestor de inventario con persistencia en JSON y UI con Rich.

Este módulo permite:
- Cargar y guardar un inventario de productos en data/inventario.json.
- Agregar y vender productos con validaciones robustas.
- Filtrar productos disponibles (stock > 0) con filter + lambda.
- Visualizar el inventario en una interfaz de consola estilizada con Rich.

Tecnologías:
- Python 3.x, JSON (json.load/json.dump), Rich (Panel, Table, Columns, Prompt).

Notas:
- Las operaciones de archivo usan UTF-8 e indentación.
- El diseño de consola usa un tema exclusivo (aqua/violeta) y “estrellitas”.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.theme import Theme

__all__ = [
    "cargar_inventario",
    "guardar_inventario",
    "agregar_producto",
    "vender_producto",
    "filtrar_disponibles",
    "mostrar_inventario",
    "menu",
    "main",
]

# Tema distintivo (aqua/violeta) con líneas de “estrellitas”
THEME = Theme(
    {
        "title": "bold aquamarine1",
        "subtitle": "medium_purple3",
        "accent": "bold cyan3",
        "muted": "grey66",
        "menu.title": "bold aquamarine1",
        "menu.option": "plum2",
        "menu.key": "bold cyan3",
        "menu.border": "cyan3",
        "table.header": "bold aquamarine1",
        "table.border": "medium_purple3",
        "ok": "spring_green3",
        "warn": "yellow3",
        "error": "red",
        "star": "aquamarine1",
    }
)
console = Console(theme=THEME)

# Carpeta de datos en la raíz del proyecto: <root>/data/inventario.json
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_ARCHIVO_INV = _DATA_DIR / "inventario.json"


def _ruta_inventario(ruta: Path | None = None) -> Path:
    """Obtiene la ruta efectiva del archivo de inventario.

    Si se provee `ruta`, se usa tal cual; de lo contrario se usa data/inventario.json
    en la raíz del proyecto.

    Args:
        ruta: Ruta alternativa del archivo para sobreescribir la ubicación por defecto.

    Returns:
        Ruta del archivo de inventario a utilizar (Path).
    """
    return ruta if ruta is not None else _ARCHIVO_INV


def _normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre colapsando espacios y recortando extremos.

    Args:
        nombre: Texto del nombre a normalizar.

    Returns:
        Nombre limpio (sin espacios duplicados y sin espacios extremos).

    Raises:
        ValueError: Si el nombre queda vacío tras limpiar.
    """
    limpio = " ".join(nombre.split())
    if not limpio:
        raise ValueError("El nombre no puede estar vacío.")
    return limpio


def _validar_producto_dict(producto: dict[str, Any]) -> dict[str, Any]:
    """Valida y normaliza un diccionario de producto.

    Reglas:
      - nombre: str no vacío.
      - precio: float >= 0.
      - stock: int >= 0.

    Args:
        producto: Diccionario con claves esperadas (nombre, precio, stock).

    Returns:
        Copia normalizada del producto con tipos correctos.

    Raises:
        TypeError: Si faltan claves o tipos no son los esperados.
        ValueError: Si los valores son inválidos (p. ej., negativos).
    """
    if not isinstance(producto, dict):
        raise TypeError("Cada producto debe ser un diccionario.")
    for clave in ("nombre", "precio", "stock"):
        if clave not in producto:
            raise TypeError(f"Falta la clave obligatoria: {clave!r}")

    nombre = _normalizar_nombre(str(producto["nombre"]))
    try:
        precio = float(producto["precio"])
    except Exception as exc:  # noqa: BLE001
        raise TypeError("precio debe ser numérico.") from exc
    try:
        stock = int(producto["stock"])
    except Exception as exc:  # noqa: BLE001
        raise TypeError("stock debe ser entero.") from exc

    if precio < 0:
        raise ValueError("El precio no puede ser negativo.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")

    return {"nombre": nombre, "precio": float(precio), "stock": int(stock)}


def cargar_inventario(ruta: Path | None = None) -> list[dict[str, Any]]:
    """Carga el inventario desde JSON; si no existe o es inválido, devuelve lista vacía.

    Args:
        ruta: Ruta alternativa del archivo (útil para pruebas). Si es None,
            se usa data/inventario.json.

    Returns:
        Lista de diccionarios de productos normalizados. Si el archivo no existe
        o su contenido no es una lista válida, retorna [].
    """
    archivo = _ruta_inventario(ruta)
    if not archivo.exists():
        return []

    with open(archivo, "r", encoding="utf-8") as fh:
        try:
            datos = json.load(fh)
        except json.JSONDecodeError:
            # Si está corrupto, asumimos inventario vacío (opción UX segura).
            return []

    if not isinstance(datos, list):
        return []

    inventario: list[dict[str, Any]] = []
    for item in datos:
        try:
            inventario.append(_validar_producto_dict(item))
        except (TypeError, ValueError):
            # Ignora líneas inválidas para robustez.
            continue
    return inventario


def guardar_inventario(
    inventario: list[dict[str, Any]],
    ruta: Path | None = None,
) -> None:
    """Guarda el inventario en disco (JSON, UTF-8, indentado).

    Args:
        inventario: Lista de productos a persistir (se validan antes de guardar).
        ruta: Ruta alternativa del archivo (útil para pruebas).

    Returns:
        None

    Raises:
        TypeError: Si la estructura de inventario no es una lista.
        ValueError: Si algún producto es inválido al normalizarse.
        OSError: Si ocurre un error de E/S al escribir.
    """
    if not isinstance(inventario, list):
        raise TypeError("inventario debe ser una lista de dicts.")

    normalizados = [_validar_producto_dict(p) for p in inventario]
    archivo = _ruta_inventario(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with open(archivo, "w", encoding="utf-8") as fh:
        json.dump(normalizados, fh, ensure_ascii=False, indent=2)


def _buscar_indice(
    inventario: list[dict[str, Any]],
    nombre_objetivo: str,
) -> int | None:
    """Busca el índice de un producto por nombre (insensible a mayúsculas).

    Args:
        inventario: Lista de productos en memoria.
        nombre_objetivo: Nombre del producto a localizar.

    Returns:
        Índice del producto si se encuentra; None en caso contrario.
    """
    objetivo = _normalizar_nombre(nombre_objetivo).lower()
    for idx, prod in enumerate(inventario):
        if str(prod.get("nombre", "")).lower() == objetivo:
            return idx
    return None


def agregar_producto(
    inventario: list[dict[str, Any]],
    nombre: str,
    precio: float,
    stock: int,
    ruta: Path | None = None,
) -> dict[str, Any]:
    """Agrega o actualiza un producto y persiste el inventario.

    Si el producto ya existe (por nombre insensible a mayúsculas):
      - Actualiza su precio al valor dado.
      - Incrementa el stock con la cantidad proporcionada.

    Args:
        inventario: Lista en memoria a modificar.
        nombre: Nombre del producto (no vacío).
        precio: Precio unitario (>= 0).
        stock: Cantidad a agregar (>= 0).
        ruta: Ruta del archivo para persistir.

    Returns:
        El producto agregado/actualizado (diccionario normalizado).

    Raises:
        TypeError: Si precio/stock no son numéricos (float/int).
        ValueError: Si precio o stock son negativos.
    """
    nombre_ok = _normalizar_nombre(nombre)
    try:
        precio_ok = float(precio)
        stock_ok = int(stock)
    except Exception as exc:  # noqa: BLE001
        raise TypeError("precio debe ser float y stock debe ser int.") from exc
    if precio_ok < 0:
        raise ValueError("El precio no puede ser negativo.")
    if stock_ok < 0:
        raise ValueError("El stock no puede ser negativo.")

    indice = _buscar_indice(inventario, nombre_ok)
    if indice is None:
        producto = {"nombre": nombre_ok, "precio": precio_ok, "stock": stock_ok}
        inventario.append(producto)
    else:
        producto = inventario[indice]
        producto["precio"] = precio_ok
        producto["stock"] = int(producto["stock"]) + stock_ok

    guardar_inventario(inventario, ruta=ruta)
    return producto


def vender_producto(
    inventario: list[dict[str, Any]],
    nombre: str,
    cantidad: int,
    ruta: Path | None = None,
) -> dict[str, Any]:
    """Registra una venta descontando stock del producto y persiste.

    Args:
        inventario: Lista en memoria a modificar.
        nombre: Nombre del producto a vender.
        cantidad: Unidades a descontar (entero > 0).
        ruta: Ruta del archivo para persistir.

    Returns:
        El producto actualizado tras la venta.

    Raises:
        KeyError: Si el producto no existe.
        ValueError: Si cantidad <= 0 o stock insuficiente.
    """
    if int(cantidad) <= 0:
        raise ValueError("La cantidad a vender debe ser mayor que 0.")

    indice = _buscar_indice(inventario, nombre)
    if indice is None:
        raise KeyError(f"No existe el producto: {nombre!r}")

    producto = inventario[indice]
    stock_actual = int(producto["stock"])
    if stock_actual < cantidad:
        raise ValueError("Stock insuficiente para la venta.")
    producto["stock"] = stock_actual - int(cantidad)

    guardar_inventario(inventario, ruta=ruta)
    return producto


def filtrar_disponibles(
    inventario: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filtra productos con stock disponible usando filter + lambda.

    Args:
        inventario: Lista de productos.

    Returns:
        Lista de productos cuyo stock es mayor a 0.
    """
    return list(filter(lambda p: int(p.get("stock", 0)) > 0, inventario))


# ---------------------------
# Interfaz con Rich (menú)
# ---------------------------


def _panel_titulo() -> Panel:
    """Construye el encabezado principal con decoración de estrellitas.

    Returns:
        Panel con título/subtítulo y borde estilizado del tema.
    """
    estrellas = "[star]" + "★ " * 18 + "[/star]"
    texto = (
        f"{estrellas}\n"
        "[title]Gestor de Inventario (JSON)[/title]\n"
        "[subtitle]Persistencia en data/inventario.json[/subtitle]\n"
        f"{estrellas}"
    )
    return Panel.fit(
        texto,
        title="[accent]Ejercicio 13[/accent]",
        subtitle="[muted]json.load/json.dump + filter + lambda[/muted]",
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
        "[menu.key]1)[/menu.key] [menu.option]Ver inventario completo[/menu.option]\n"
        "[menu.key]2)[/menu.key] "
        "[menu.option]Ver solo disponibles (stock > 0)[/menu.option]\n"
        "[menu.key]3)[/menu.key] [menu.option]Agregar producto[/menu.option]\n"
        "[menu.key]4)[/menu.key] [menu.option]Vender producto[/menu.option]\n"
        "[menu.key]5)[/menu.key] [menu.option]Salir[/menu.option]"
    )
    return Panel(
        texto, title="[accent]Menú[/accent]", border_style="menu.border", box=box.HEAVY
    )


def _tabla_inventario(items: list[dict[str, Any]], titulo: str) -> Table:
    """Crea la tabla del inventario con estilos y resumen.

    Args:
        items: Lista de productos a mostrar.
        titulo: Título de la tabla.

    Returns:
        Tabla Rich con numeración, precio, stock y valor total.
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
    tabla.add_column("Nombre")
    tabla.add_column("Precio", justify="right")
    tabla.add_column("Stock", justify="right")
    tabla.add_column("Valor", justify="right")
    if not items:
        tabla.add_row("—", "—", "—", "—", "—")
        return tabla
    total_valor = 0.0
    for indice, p in enumerate(items, start=1):
        precio = float(p.get("precio", 0.0))
        stock = int(p.get("stock", 0))
        valor = round(precio * stock, 2)
        total_valor += valor
        tabla.add_row(
            str(indice),
            str(p.get("nombre", "—")),
            f"{precio:.2f}",
            str(stock),
            f"{valor:.2f}",
        )
    tabla.caption = (
        f"[muted]Valor total inventario mostrado:[/muted] [accent]"
        f"{total_valor:.2f}[/accent]"
    )
    return tabla


def _panel_info_archivo(archivo: Path) -> Panel:
    """Panel informativo con la ubicación del archivo de datos.

    Args:
        archivo: Ruta al archivo de inventario.

    Returns:
        Panel compacto con la ruta mostrada.
    """
    return Panel.fit(
        f"[muted]Archivo:[/muted] [accent]{archivo}[/accent]",
        title="[accent]Ubicación de datos[/accent]",
        border_style="menu.border",
        box=box.ROUNDED,
    )


def mostrar_inventario(
    inventario: list[dict[str, Any]],
    solo_disponibles: bool = False,
) -> None:
    """Muestra el inventario en una tabla Rich.

    Args:
        inventario: Lista de productos a mostrar.
        solo_disponibles: Si True, filtra por stock > 0 antes de renderizar.

    Returns:
        None
    """
    items = filtrar_disponibles(inventario) if solo_disponibles else list(inventario)
    tabla = _tabla_inventario(
        items, "Inventario disponible" if solo_disponibles else "Inventario"
    )
    paneles = [_panel_info_archivo(_ARCHIVO_INV), tabla]
    console.print(Columns(paneles, equal=True, expand=True))


# ---------------------------
# Interfaz interactiva
# ---------------------------


def menu() -> None:
    """Interfaz interactiva con Rich para gestionar el inventario.

    Presenta opciones para ver el inventario, filtrar disponibles, agregar y
    vender productos. Los resultados se muestran en paneles y tablas estilizadas.

    Args:
        None

    Returns:
        None
    """
    inventario = cargar_inventario()
    while True:
        console.clear()
        console.print(_panel_titulo())
        console.print(_panel_menu())

        opcion = Prompt.ask(
            "[title]Elige una opción[/title]",
            choices=["1", "2", "3", "4", "5"],
            default="1",
        )

        if opcion == "1":
            mostrar_inventario(inventario, solo_disponibles=False)

        elif opcion == "2":
            mostrar_inventario(inventario, solo_disponibles=True)

        elif opcion == "3":
            try:
                nombre = Prompt.ask("[accent]Nombre del producto[/accent]").strip()
                precio = FloatPrompt.ask("[accent]Precio (>= 0)[/accent]", default=0.0)
                stock = IntPrompt.ask("[accent]Stock (entero >= 0)[/accent]", default=0)
                producto = agregar_producto(
                    inventario, nombre=nombre, precio=precio, stock=stock
                )
                console.print(
                    Panel.fit(
                        f"[ok]★ Producto guardado:[/ok] {producto}",
                        border_style="ok",
                        title="[accent]OK[/accent]",
                        box=box.ROUNDED,
                    )
                )
            except (TypeError, ValueError) as exc:
                console.print(
                    Panel.fit(
                        f"[error]Error:[/error] {exc}",
                        border_style="error",
                        title="[accent]Entrada inválida[/accent]",
                        box=box.HEAVY,
                    )
                )

        elif opcion == "4":
            try:
                nombre = Prompt.ask("[accent]Nombre del producto[/accent]").strip()
                cantidad = IntPrompt.ask(
                    "[accent]Cantidad a vender (> 0)[/accent]", default=1
                )
                producto = vender_producto(inventario, nombre=nombre, cantidad=cantidad)
                console.print(
                    Panel.fit(
                        f"[ok]★ Venta registrada[/ok]\n"
                        f"[muted]Stock restante de[/muted] "
                        f"[accent]{producto['nombre']}[/accent]: "
                        f"[ok]{producto['stock']}[/ok]",
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
            "\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]"
        )
