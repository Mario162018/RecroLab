class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __repr__(self):
        return f"{self.codigo}: {self.nombre} (${self.precio})"


def catalogo_inicial():
    return [
        Producto("A01", "Agua", 1000, 8),
        Producto("A02", "Jugo", 1200, 6),
        Producto("A03", "Alfajor", 800, 10),
        Producto("A04", "Galletitas", 900, 2),
        Producto("A05", "Barrita", 700, 5),
        Producto("A06", "Caramelos", 300, 0),
    ]


def buscar(productos, codigo):
    for producto in productos:
        if producto.codigo == codigo:
            return producto
    raise ValueError("El producto no existe.")


def cantidad_en_carrito(carrito, codigo):
    cantidad = 0
    for producto in carrito:
        if producto.codigo == codigo:
            cantidad += 1
    return cantidad


def total_carrito(carrito):
    total = 0
    for producto in carrito:
        total += producto.precio
    return total


def agregar(productos, carrito, codigo):
    producto = buscar(productos, codigo)
    if cantidad_en_carrito(carrito, codigo) >= producto.stock:
        raise ValueError("No queda stock para agregar otra unidad.")
    carrito.append(producto)


def confirmar(carrito, ventas):
    if not carrito:
        raise ValueError("El carrito está vacío.")
    for producto in carrito:
        cantidad = cantidad_en_carrito(carrito, producto.codigo)
        if cantidad > producto.stock:
            raise ValueError("El stock cambió. Revisá el carrito.")
    total = total_carrito(carrito)
    for producto in carrito:
        producto.stock -= 1
    ventas.append(total)
    carrito.clear()
    return total


def sugerir_pares(productos, presupuesto):
    if presupuesto <= 0:
        raise ValueError("El presupuesto debe ser mayor que cero.")
    opciones = []
    for i in range(len(productos)):
        for j in range(i + 1, len(productos)):
            primero = productos[i]
            segundo = productos[j]
            total = primero.precio + segundo.precio
            if primero.stock > 0 and segundo.stock > 0:
                if total <= presupuesto:
                    opciones.append([primero.nombre, segundo.nombre,
                                      total, presupuesto - total])
    return opciones
