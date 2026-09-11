from itertools import combinations
import json
from pathlib import Path


class Producto:
    """Representa un artículo del catálogo del kiosco."""

    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self):
        return f"{self.codigo}: {self.nombre} (${self.precio})"


def crear_catalogo():
    """Arma la lista de productos con la que arranca la aplicación."""
    return [
        Producto("A01", "Agua", 1000, 8),
        Producto("A02", "Jugo", 1200, 6),
        Producto("A03", "Alfajor", 800, 10),
        Producto("A04", "Galletitas", 900, 2),
        Producto("A05", "Barrita", 700, 5),
        Producto("A06", "Caramelos", 300, 0),
    ]


def encontrar_producto(catalogo, codigo):
    """Devuelve el producto con ese código, o avisa si no existe."""
    for articulo in catalogo:
        if articulo.codigo == codigo:
            return articulo
    raise ValueError("El producto no existe.")


def unidades_en_carrito(carrito, codigo):
    """Cuenta cuántas unidades de un producto ya están en el carrito."""
    return sum(1 for articulo in carrito if articulo.codigo == codigo)


def calcular_total(carrito):
    """Suma el precio de todo lo que hay cargado en el carrito."""
    return sum(articulo.precio for articulo in carrito)


def sumar_al_carrito(catalogo, carrito, codigo):
    """Agrega una unidad del producto, si todavía queda stock disponible."""
    producto = encontrar_producto(catalogo, codigo)
    if unidades_en_carrito(carrito, codigo) >= producto.stock:
        raise ValueError("No queda stock para agregar otra unidad.")
    carrito.append(producto)


def registrar_venta(carrito, ventas):
    """Confirma la venta: descuenta el stock vendido y vacía el carrito."""
    if not carrito:
        raise ValueError("El carrito está vacío.")

    for articulo in carrito:
        pedidas = unidades_en_carrito(carrito, articulo.codigo)
        if pedidas > articulo.stock:
            raise ValueError("El stock cambió. Revisá el carrito.")

    total = calcular_total(carrito)
    for articulo in carrito:
        articulo.stock -= 1

    ventas.append(total)
    carrito.clear()
    return total


def reponer_stock(catalogo, codigo, cantidad):
    """Aumenta el stock de un producto existente. Rechaza cantidades
    que no sean enteros positivos (cero, negativos o no numéricos ya
    quedan afuera antes de llegar acá, al convertir el texto a int)."""
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser un entero positivo.")
    producto = encontrar_producto(catalogo, codigo)
    producto.stock += cantidad
    return producto


def combinaciones_posibles(catalogo, presupuesto):
    """Lista los pares de productos distintos que entran en el presupuesto,
    ordenados de menor a mayor sobrante. list.sort() en Python es estable,
    así que los empates conservan el orden en que itertools.combinations
    generó los pares (el mismo orden del catálogo) — ese es el criterio
    de desempate."""
    if presupuesto <= 0:
        raise ValueError("El presupuesto debe ser mayor que cero.")

    resultado = []
    for primero, segundo in combinations(catalogo, 2):
        if primero.stock == 0 or segundo.stock == 0:
            continue
        total = primero.precio + segundo.precio
        if total <= presupuesto:
            resultado.append([primero.nombre, segundo.nombre,
                               total, presupuesto - total])

    resultado.sort(key=lambda opcion: opcion[3])
    return resultado


def guardar_datos(catalogo, ventas, archivo="recreolab_datos.json"):
    """Guarda localmente el stock y las ventas."""
    datos = {"productos": [], "ventas": ventas}

    for producto in catalogo:
        datos["productos"].append({
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock
        })

    Path(archivo).write_text(
        json.dumps(datos, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def cargar_datos(catalogo, archivo="recreolab_datos.json"):
    """Carga los datos guardados si el archivo existe."""
    ruta = Path(archivo)

    if not ruta.exists():
        return []

    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    for guardado in datos.get("productos", []):
        for producto in catalogo:
            if producto.codigo == guardado.get("codigo"):
                producto.stock = guardado.get("stock", producto.stock)

    return datos.get("ventas", [])
