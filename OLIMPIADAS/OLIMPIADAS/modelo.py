import json
import sqlite3
from pathlib import Path
from datetime import datetime
import random

RUTA_BD = "recreolab.db"

class Producto:
    def __init__(self, codigo, nombre, precio, stock, categoria, descripcion="", emoji="🍴", activo=True):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = int(precio)
        self.stock = int(stock)
        self.categoria = categoria
        self.descripcion = descripcion
        self.emoji = emoji
        self.activo = activo

    def __repr__(self):
        return f"{self.codigo}: {self.nombre} (${self.precio})"

    def disponible(self):
        return self.activo and self.stock > 0

    def datos(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "emoji": self.emoji,
            "activo": self.activo
        }


class Catalogo:
    """Tipo de Dato Abstracto: representa el catálogo de productos
    del kiosco. La lista interna (_productos) queda oculta — el
    resto del programa nunca la toca directamente, solo a través de
    lo que expone esta clase: recorrerlo (for producto in catalogo),
    consultar cuántos productos tiene (len(catalogo)) y agregar uno
    nuevo (catalogo.append(...), que es justo lo único que hacía
    falta para que las 60 funciones de este archivo —buscar_productos,
    agregar_producto, reponer_stock, etc.— sigan funcionando exactamente
    igual, sin cambiarles una línea, pensadas para recibir "el
    catálogo" sin necesitar saber si por dentro es una lista, un
    diccionario o cualquier otra cosa.

    alta()/buscar()/existe() son la forma "prolija" de usar el TDA
    (con sus propias validaciones); agregar_producto() y
    encontrar_producto(), más abajo en este archivo, terminan usando
    lo mismo por otro camino, para no duplicar la lógica de
    validación que ya tenían."""

    def __init__(self, productos_iniciales=None):
        self._productos = list(productos_iniciales or [])

    def __iter__(self):
        return iter(self._productos)

    def __len__(self):
        return len(self._productos)

    def append(self, producto):
        self._productos.append(producto)

    def existe(self, codigo):
        codigo = str(codigo).strip().upper()
        return any(p.codigo == codigo for p in self._productos)

    def buscar(self, codigo):
        codigo = str(codigo).strip().upper()
        for producto in self._productos:
            if producto.codigo == codigo:
                return producto
        raise ValueError("El producto no existe.")

    def alta(self, producto):
        if self.existe(producto.codigo):
            raise ValueError("Ya existe un producto con ese código.")
        self._productos.append(producto)
        return producto

def crear_catalogo():
    productos = [
        ("A01","Agua",1000,8,"Bebidas","Agua fresca para el recreo.","💧"),
        ("A02","Jugo",1200,6,"Bebidas","Jugo frutal bien frío.","🧃"),
        ("A03","Alfajor",800,10,"Dulces","Alfajor clásico de chocolate.","🍫"),
        ("A04","Galletitas",900,7,"Dulces","Galletitas crocantes.","🍪"),
        ("A05","Barrita",700,8,"Snacks","Barrita para una merienda rápida.","🍫"),
        ("A06","Caramelos",300,15,"Dulces","Caramelos surtidos.","🍬"),
        ("A07","Chips",1100,8,"Snacks","Papas tipo chips crocantes.","🥔"),
        ("A08","Chocolate",1300,6,"Dulces","Chocolate para compartir.","🍫"),
        ("A09","Medialuna",1000,8,"Panadería","Medialuna recién preparada.","🥐"),
        ("A10","Sándwich",2000,5,"Comida","Sándwich completo para el recreo.","🥪"),
        ("A11","Gaseosa",1500,7,"Bebidas","Bebida gaseosa fría.","🥤"),
        ("A12","Papas",1200,8,"Snacks","Papas clásicas saladas.","🍟"),
        ("A13","Cookie",950,7,"Dulces","Cookie con chips de chocolate.","🍪"),
        ("A14","Tostado",2200,5,"Comida","Tostado caliente de jamón y queso.","🥪"),
        ("A15","Limonada",1400,7,"Bebidas","Limonada fresca.","🍋"),
        ("A16","Muffin",1100,6,"Panadería","Muffin suave de chocolate.","🧁"),
        ("A17","Café",1300,8,"Bebidas","Café caliente.","☕"),
        ("A18","Té",900,8,"Bebidas","Té caliente.","🍵"),
        ("A19","Yogur",1400,6,"Bebidas","Yogur individual.","🥛"),
        ("A20","Jugo de naranja",1600,5,"Bebidas","Jugo de naranja natural.","🍊"),
        ("A21","Brownie",1500,6,"Dulces","Brownie de chocolate.","🍰"),
        ("A22","Donut",1200,7,"Dulces","Donut glaseada.","🍩"),
        ("A23","Chocotorta",1800,4,"Dulces","Porción individual.","🍰"),
        ("A24","Mix de frutos secos",1700,6,"Snacks","Mix energético.","🥜"),
        ("A25","Nachos",1600,7,"Snacks","Nachos crocantes.","🌮"),
        ("A26","Pochoclos",800,9,"Snacks","Pochoclos dulces.","🍿"),
        ("A27","Pancho",1900,6,"Comida","Pancho completo.","🌭"),
        ("A28","Hamburguesa",2800,5,"Comida","Hamburguesa simple.","🍔"),
        ("A29","Pizza",2500,5,"Comida","Porción de pizza.","🍕"),
        ("A30","Empanada",1400,10,"Comida","Empanada al horno.","🥟"),
        ("A31","Tarta",1800,6,"Comida","Porción de tarta.","🥧"),
        ("A32","Croissant",1500,6,"Panadería","Croissant de manteca.","🥐"),
        ("A33","Budín",1300,7,"Panadería","Porción de budín.","🍞"),
        ("A34","Medialuna rellena",1400,5,"Panadería","Medialuna rellena.","🥐"),
        ("A35","Pan de queso",1000,8,"Panadería","Pan de queso horneado.","🧀"),
        ("A36","Donut chocolate",1400,5,"Dulces","Donut cubierta de chocolate.","🍩"),
        ("A37","Licuado",1800,5,"Bebidas","Licuado de fruta.","🥤"),
        ("A38","Agua saborizada",1200,7,"Bebidas","Agua saborizada fría.","💧"),
        ("A39","Churros",1300,7,"Dulces","Churros para la merienda.","🥨"),
        ("A40","Combo recreo",4200,4,"Combos","Combo con bebida, snack y dulce.","🍱"),
    ]
    return Catalogo([Producto(*p) for p in productos])

def encontrar_producto(catalogo, codigo):
    codigo = str(codigo).strip().upper()
    for producto in catalogo:
        if producto.codigo == codigo:
            return producto
    raise ValueError("El producto no existe.")

def buscar_productos(catalogo, texto="", categoria="Todos", solo_disponibles=False):
    texto = str(texto).strip().lower()
    resultado = []
    for p in catalogo:
        if not p.activo:
            continue
        if categoria != "Todos" and p.categoria != categoria:
            continue
        if texto and texto not in p.nombre.lower() and texto not in p.codigo.lower() and texto not in p.descripcion.lower():
            continue
        if solo_disponibles and not p.disponible():
            continue
        resultado.append(p)
    return resultado

def categorias(catalogo):
    resultado = []
    for p in catalogo:
        if p.categoria not in resultado:
            resultado.append(p.categoria)
    return resultado

def unidades_en_carrito(carrito, codigo):
    cantidad = 0
    for producto in carrito:
        if producto.codigo == codigo:
            cantidad += 1
    return cantidad

def resumen_carrito(carrito):
    resumen = {}
    for p in carrito:
        if p.codigo not in resumen:
            resumen[p.codigo] = {"producto": p, "cantidad": 0, "subtotal": 0}
        resumen[p.codigo]["cantidad"] += 1
        resumen[p.codigo]["subtotal"] += p.precio
    return list(resumen.values())

def calcular_total(carrito):
    return sum(p.precio for p in carrito)

def calcular_subtotal_producto(producto, cantidad):
    if cantidad < 0:
        raise ValueError("La cantidad no puede ser negativa.")
    return producto.precio * cantidad

def sumar_al_carrito(catalogo, carrito, codigo, cantidad=1):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva.")
    producto = encontrar_producto(catalogo, codigo)
    if not producto.activo:
        raise ValueError("El producto está desactivado.")
    if unidades_en_carrito(carrito, codigo) + cantidad > producto.stock:
        raise ValueError("No queda stock suficiente para agregar esa cantidad.")
    for _ in range(cantidad):
        carrito.append(producto)
    return producto

def quitar_del_carrito(carrito, codigo, cantidad=1):
    codigo = str(codigo).strip().upper()
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva.")
    eliminadas = 0
    nuevo = []
    for p in carrito:
        if p.codigo == codigo and eliminadas < cantidad:
            eliminadas += 1
        else:
            nuevo.append(p)
    carrito[:] = nuevo
    return eliminadas

def vaciar_carrito(carrito):
    cantidad = len(carrito)
    carrito.clear()
    return cantidad

def validar_carrito(carrito):
    cantidades = {}
    for p in carrito:
        cantidades[p.codigo] = cantidades.get(p.codigo, 0) + 1
    for p in carrito:
        if cantidades[p.codigo] > p.stock:
            return False
    return True

def aplicar_descuento(total, porcentaje):
    porcentaje = float(porcentaje)
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError("El descuento debe estar entre 0 y 100.")
    descuento = int(round(total * porcentaje / 100))
    return total - descuento, descuento

def validar_cupon(codigo):
    cupones = {
        "RECREO10": 10,
        "PREMIUM15": 15,
        "KIOSCO20": 20,
        "VUELTA5": 5
    }
    return cupones.get(str(codigo).strip().upper(), 0)

def precio_con_cupon(total, codigo):
    porcentaje = validar_cupon(codigo)
    if porcentaje == 0:
        return total, 0
    return aplicar_descuento(total, porcentaje)

def registrar_venta(carrito, ventas, descuento=0, cupon=""):
    if not carrito:
        raise ValueError("El carrito está vacío.")
    if not validar_carrito(carrito):
        raise ValueError("El stock cambió. Revisá el carrito.")
    subtotal = calcular_total(carrito)
    total, ahorro = aplicar_descuento(subtotal, descuento)
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detalle = []
    for item in resumen_carrito(carrito):
        detalle.append({
            "codigo": item["producto"].codigo,
            "nombre": item["producto"].nombre,
            "cantidad": item["cantidad"],
            "precio": item["producto"].precio,
            "subtotal": item["subtotal"]
        })
    for producto in carrito:
        producto.stock -= 1
    registro = {
        "fecha": ahora,
        "subtotal": subtotal,
        "descuento": ahorro,
        "cupon": cupon,
        "total": total,
        "productos": detalle
    }
    ventas.append(registro)
    carrito.clear()
    return total

def reponer_stock(catalogo, codigo, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva.")
    producto = encontrar_producto(catalogo, codigo)
    producto.stock += cantidad
    return producto

def cambiar_precio(catalogo, codigo, nuevo_precio):
    if nuevo_precio <= 0:
        raise ValueError("El precio debe ser mayor que cero.")
    producto = encontrar_producto(catalogo, codigo)
    producto.precio = int(nuevo_precio)
    return producto

def agregar_producto(catalogo, codigo, nombre, precio, stock, categoria, descripcion="", emoji="🍴"):
    codigo = str(codigo).strip().upper()
    if not codigo or not nombre.strip():
        raise ValueError("Código y nombre son obligatorios.")
    if precio <= 0 or stock < 0:
        raise ValueError("Precio o stock inválido.")
    producto = Producto(codigo, nombre.strip(), precio, stock, categoria, descripcion, emoji)
    return catalogo.alta(producto)  # valida duplicados y lo agrega

def eliminar_producto(catalogo, codigo):
    producto = encontrar_producto(catalogo, codigo)
    producto.activo = False
    return producto

def activar_producto(catalogo, codigo):
    producto = encontrar_producto(catalogo, codigo)
    producto.activo = True
    return producto

def cambiar_categoria(catalogo, codigo, nueva_categoria):
    producto = encontrar_producto(catalogo, codigo)
    if not nueva_categoria.strip():
        raise ValueError("La categoría no puede estar vacía.")
    producto.categoria = nueva_categoria.strip()
    return producto

def producto_mas_barato(catalogo):
    disponibles = [p for p in catalogo if p.activo]
    return min(disponibles, key=lambda p: p.precio) if disponibles else None

def producto_mas_caro(catalogo):
    disponibles = [p for p in catalogo if p.activo]
    return max(disponibles, key=lambda p: p.precio) if disponibles else None

def productos_agotados(catalogo):
    return [p for p in catalogo if p.activo and p.stock == 0]

def productos_stock_bajo(catalogo, limite=2):
    return [p for p in catalogo if p.activo and 0 < p.stock <= limite]

def valor_inventario(catalogo):
    total = 0
    for p in catalogo:
        total += p.precio * p.stock
    return total

def cantidad_total_stock(catalogo):
    return sum(p.stock for p in catalogo if p.activo)

def estadisticas_ventas(ventas):
    total = 0
    unidades = 0
    for venta in ventas:
        if isinstance(venta, dict):
            total += int(venta.get("total", 0))
            for p in venta.get("productos", []):
                unidades += int(p.get("cantidad", 0))
        else:
            total += int(venta)
            unidades += 1
    return {"ventas": len(ventas), "ingresos": total, "unidades": unidades}

def productos_mas_vendidos(ventas):
    conteo = {}
    for venta in ventas:
        if not isinstance(venta, dict):
            continue
        for p in venta.get("productos", []):
            nombre = p.get("nombre", "Producto")
            conteo[nombre] = conteo.get(nombre, 0) + int(p.get("cantidad", 0))
    return sorted(conteo.items(), key=lambda x: x[1], reverse=True)

def ventas_por_dia(ventas):
    resultado = {}
    for venta in ventas:
        if not isinstance(venta, dict):
            continue
        fecha = str(venta.get("fecha", ""))[:10]
        resultado[fecha] = resultado.get(fecha, 0) + int(venta.get("total", 0))
    return resultado

def recomendacion(catalogo, presupuesto):
    disponibles = [p for p in catalogo if p.disponible() and p.precio <= presupuesto]
    if not disponibles:
        return None
    disponibles.sort(key=lambda p: (p.precio, p.stock), reverse=True)
    return disponibles[0]

def generar_combinaciones(productos, tamano):
    """Genera, de forma recursiva, todos los subconjuntos de
    'tamano' productos distintos (sin repetir productos ni generar
    el mismo grupo en otro orden). La usan combinaciones_posibles
    (con tamano fijo en 2) y combinaciones_avanzadas (probando varios
    tamaños), en vez de itertools.combinations.

    Caso base: elegir 0 productos siempre da exactamente una
    combinación posible, la vacía ([[]]). Si ya no quedan productos
    para elegir pero todavía falta elegir alguno, no hay ninguna
    combinación posible ([]).
    Caso recursivo: separamos el primer producto del resto. Cada
    combinación final o lo incluye (y el resto sale de elegir
    tamano-1 productos más entre los que quedan) o no lo incluye (y
    sale de elegir esos mismos tamano productos, pero sin él)."""
    if tamano == 0:
        return [[]]
    if not productos:
        return []
    primero, *resto = productos
    con_primero = [[primero] + combo
                   for combo in generar_combinaciones(resto, tamano - 1)]
    sin_primero = generar_combinaciones(resto, tamano)
    return con_primero + sin_primero


def combinaciones_posibles(catalogo, presupuesto):
    if presupuesto <= 0:
        raise ValueError("El presupuesto debe ser mayor que cero.")
    resultado = []
    disponibles = [p for p in catalogo if p.disponible()]
    for primero, segundo in generar_combinaciones(disponibles, 2):
        total = primero.precio + segundo.precio
        if total <= presupuesto:
            resultado.append([primero.nombre, segundo.nombre, total, presupuesto-total])
    resultado.sort(key=lambda opcion: opcion[3])
    return resultado

def combinaciones_avanzadas(catalogo, presupuesto, cantidad_maxima=3):
    disponibles = [p for p in catalogo if p.disponible()]
    resultado = []
    for cantidad in range(2, cantidad_maxima + 1):
        for grupo in generar_combinaciones(disponibles, cantidad):
            total = sum(p.precio for p in grupo)
            if total <= presupuesto:
                resultado.append({
                    "productos": [p.nombre for p in grupo],
                    "total": total,
                    "sobra": presupuesto - total
                })
    resultado.sort(key=lambda x: (x["sobra"], -len(x["productos"])))
    return resultado

def importar_catalogo(catalogo, datos):
    if not isinstance(datos, list):
        raise ValueError("El catálogo importado no tiene formato válido.")
    for item in datos:
        codigo = str(item.get("codigo", "")).upper()
        if not codigo:
            continue
        try:
            producto = encontrar_producto(catalogo, codigo)
            producto.nombre = item.get("nombre", producto.nombre)
            producto.precio = int(item.get("precio", producto.precio))
            producto.stock = int(item.get("stock", producto.stock))
            producto.categoria = item.get("categoria", producto.categoria)
            producto.descripcion = item.get("descripcion", producto.descripcion)
            producto.emoji = item.get("emoji", producto.emoji)
            producto.activo = item.get("activo", producto.activo)
        except ValueError:
            try:
                agregar_producto(
                    catalogo, codigo, item.get("nombre","Producto"),
                    int(item.get("precio", 1)), int(item.get("stock", 0)),
                    item.get("categoria","Otros"), item.get("descripcion",""),
                    item.get("emoji","🍴")
                )
            except ValueError:
                pass

def inicializar_base_datos(ruta=RUTA_BD):
    """Crea las tablas si todavía no existen. Se puede llamar las
    veces que hagan falta: CREATE TABLE IF NOT EXISTS no rompe nada
    si ya estaban creadas.

    Estructura relacional:
    - productos: una fila por producto (la "foto" actual del catálogo).
    - ventas: una fila por venta confirmada.
    - detalle_venta: una fila por cada producto vendido dentro de una
      venta, referenciando a productos y a ventas por clave foránea
      (integridad referencial: no puede haber un detalle que apunte a
      una venta o a un producto que no exista)."""
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            codigo      TEXT PRIMARY KEY,
            nombre      TEXT NOT NULL,
            precio      INTEGER NOT NULL,
            stock       INTEGER NOT NULL,
            categoria   TEXT NOT NULL,
            descripcion TEXT,
            emoji       TEXT,
            activo      INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT NOT NULL,
            subtotal  INTEGER NOT NULL,
            descuento INTEGER NOT NULL,
            cupon     TEXT,
            total     INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS detalle_venta (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id         INTEGER NOT NULL REFERENCES ventas(id),
            producto_codigo  TEXT NOT NULL REFERENCES productos(codigo),
            nombre           TEXT NOT NULL,
            cantidad         INTEGER NOT NULL,
            precio           INTEGER NOT NULL,
            subtotal         INTEGER NOT NULL
        );
    """)
    conexion.commit()
    conexion.close()


def guardar_en_base_datos(catalogo, ventas, ruta=RUTA_BD):
    """Vuelca el catálogo y las ventas a la base SQLite. Se llama
    siempre desde guardar_datos(), en el mismo momento que se
    reescribe el JSON — así los dos quedan siempre sincronizados,
    porque salen de los mismos objetos en memoria (el catalogo y las
    ventas que tiene cargados la aplicación en ese instante).

    Estrategia simple, igual que con el JSON: en vez de ir aplicando
    cambios incrementales (que podrían desincronizarse si algo falla
    a mitad de camino), se borra todo y se vuelve a insertar completo
    a partir del estado actual. Para el tamaño de datos de un kiosco
    escolar, es más simple y más seguro que sea así."""
    inicializar_base_datos(ruta)
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")

    conexion.execute("DELETE FROM detalle_venta")
    conexion.execute("DELETE FROM ventas")
    conexion.execute("DELETE FROM productos")

    for p in catalogo:
        conexion.execute(
            "INSERT INTO productos (codigo, nombre, precio, stock, "
            "categoria, descripcion, emoji, activo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (p.codigo, p.nombre, p.precio, p.stock, p.categoria,
             p.descripcion, p.emoji, int(p.activo)),
        )

    for venta in ventas:
        if not isinstance(venta, dict):
            continue  # ventas guardadas en un formato viejo (solo el total)
        cursor = conexion.execute(
            "INSERT INTO ventas (fecha, subtotal, descuento, cupon, total) "
            "VALUES (?, ?, ?, ?, ?)",
            (venta.get("fecha", ""), venta.get("subtotal", 0),
             venta.get("descuento", 0), venta.get("cupon", ""),
             venta.get("total", 0)),
        )
        venta_id = cursor.lastrowid
        for item in venta.get("productos", []):
            conexion.execute(
                "INSERT INTO detalle_venta (venta_id, producto_codigo, "
                "nombre, cantidad, precio, subtotal) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (venta_id, item.get("codigo", ""), item.get("nombre", ""),
                 item.get("cantidad", 0), item.get("precio", 0),
                 item.get("subtotal", 0)),
            )

    conexion.commit()
    conexion.close()


def top_productos_sql(ruta=RUTA_BD, limite=5):
    """Los productos más vendidos, calculados con una consulta SQL
    (JOIN + GROUP BY + ORDER BY) en vez de recorrer las ventas a mano
    con Python — la diferencia frente a productos_mas_vendidos(), que
    hace lo mismo pero iterando la lista en memoria. Con pocos datos
    da igual, pero es la consulta que conviene a medida que crece el
    historial de ventas."""
    inicializar_base_datos(ruta)
    conexion = sqlite3.connect(ruta)
    filas = conexion.execute("""
        SELECT producto_codigo, nombre, SUM(cantidad) AS unidades
        FROM detalle_venta
        GROUP BY producto_codigo, nombre
        ORDER BY unidades DESC
        LIMIT ?
    """, (limite,)).fetchall()
    conexion.close()
    return [{"codigo": codigo, "nombre": nombre, "unidades": unidades}
            for codigo, nombre, unidades in filas]


def guardar_datos(catalogo, ventas, archivo="recreolab_datos.json", ruta_bd=RUTA_BD):
    datos = {
        "version": 3,
        "fecha_guardado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "productos": [p.datos() for p in catalogo],
        "ventas": ventas
    }
    Path(archivo).write_text(
        json.dumps(datos, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    # La base de datos se guarda acá mismo, con el mismo catalogo y
    # las mismas ventas que se acaban de volcar al JSON — así los dos
    # quedan siempre sincronizados entre sí. Si algo falla del lado
    # de la base (por ejemplo, el archivo .db bloqueado por otro
    # programa), no se pierde el guardado del JSON, que es el que
    # usa la aplicación para arrancar.
    try:
        guardar_en_base_datos(catalogo, ventas, ruta_bd)
    except sqlite3.Error as error:
        print(f"Aviso: no se pudo actualizar la base de datos ({error}).")

def cargar_datos(catalogo, archivo="recreolab_datos.json"):
    ruta = Path(archivo)
    if not ruta.exists():
        return []
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    importar_catalogo(catalogo, datos.get("productos", []))
    ventas = datos.get("ventas", [])
    if not isinstance(ventas, list):
        return []
    return ventas

def exportar_resumen(ventas, archivo="recreolab_reporte.txt"):
    estadisticas = estadisticas_ventas(ventas)
    lineas = [
        "RECREOLAB - REPORTE DE VENTAS",
        "=" * 40,
        f"Ventas: {estadisticas['ventas']}",
        f"Unidades: {estadisticas['unidades']}",
        f"Ingresos: ${estadisticas['ingresos']}",
        "",
        "PRODUCTOS MÁS VENDIDOS"
    ]
    for nombre, cantidad in productos_mas_vendidos(ventas):
        lineas.append(f"- {nombre}: {cantidad} unidad(es)")
    Path(archivo).write_text("\n".join(lineas), encoding="utf-8")
    return Path(archivo)

def generar_codigo(catalogo):
    numeros = []
    for p in catalogo:
        if p.codigo.startswith("A") and p.codigo[1:].isdigit():
            numeros.append(int(p.codigo[1:]))
    siguiente = max(numeros, default=0) + 1
    return f"A{siguiente:02d}"

def duplicar_producto(catalogo, codigo, nuevo_codigo):
    original = encontrar_producto(catalogo, codigo)
    return agregar_producto(
        catalogo, nuevo_codigo, original.nombre + " copia",
        original.precio, original.stock, original.categoria,
        original.descripcion, original.emoji
    )

def ordenar_catalogo(catalogo, criterio="nombre"):
    activos = [p for p in catalogo if p.activo]
    if criterio == "precio":
        return sorted(activos, key=lambda p: p.precio)
    if criterio == "precio_desc":
        return sorted(activos, key=lambda p: p.precio, reverse=True)
    if criterio == "stock":
        return sorted(activos, key=lambda p: p.stock, reverse=True)
    return sorted(activos, key=lambda p: p.nombre.lower())

def copiar_carrito(carrito):
    return list(carrito)

def restaurar_carrito(carrito, copia):
    carrito[:] = copia

def calcular_cambio(dinero, total):
    if dinero < total:
        raise ValueError("El dinero no alcanza.")
    return dinero - total

def dinero_requerido_para_producto(producto, cantidad=1):
    if cantidad < 1:
        raise ValueError("Cantidad inválida.")
    return producto.precio * cantidad

def verificar_presupuesto(carrito, dinero):
    return calcular_total(carrito) <= dinero

def porcentaje_gastado(carrito, dinero):
    if dinero <= 0:
        return 100 if carrito else 0
    return min(100, round(calcular_total(carrito) * 100 / dinero, 1))

def mensaje_stock(producto):
    if producto.stock == 0:
        return "Agotado"
    if producto.stock <= 2:
        return f"Stock bajo: {producto.stock}"
    return f"Disponible: {producto.stock}"

def contar_por_categoria(catalogo):
    resultado = {}
    for p in catalogo:
        if not p.activo:
            continue
        resultado[p.categoria] = resultado.get(p.categoria, 0) + 1
    return resultado

def valor_stock_por_categoria(catalogo):
    resultado = {}
    for p in catalogo:
        if not p.activo:
            continue
        resultado[p.categoria] = resultado.get(p.categoria, 0) + p.precio * p.stock
    return resultado

def obtener_productos_favoritos(catalogo, favoritos):
    return [p for p in catalogo if p.codigo in favoritos and p.activo]

def alternar_favorito(favoritos, codigo):
    codigo = str(codigo).upper()
    if codigo in favoritos:
        favoritos.remove(codigo)
        return False
    favoritos.add(codigo)
    return True

def limpiar_favoritos(favoritos, catalogo):
    validos = {p.codigo for p in catalogo}
    favoritos.intersection_update(validos)
    return favoritos

def pedido_desde_codigos(catalogo, codigos):
    carrito = []
    for codigo in codigos:
        try:
            p = encontrar_producto(catalogo, codigo)
            if p.disponible():
                carrito.append(p)
        except ValueError:
            pass
    return carrito

def combo_recomendado(catalogo, presupuesto):
    opciones = combinaciones_avanzadas(catalogo, presupuesto, 3)
    return opciones[0] if opciones else None

def resumen_inventario(catalogo):
    return {
        "productos": len([p for p in catalogo if p.activo]),
        "stock": cantidad_total_stock(catalogo),
        "valor": valor_inventario(catalogo),
        "agotados": len(productos_agotados(catalogo)),
        "bajo_stock": len(productos_stock_bajo(catalogo))
    }

def validar_producto(nombre, precio, stock, categoria):
    if not str(nombre).strip():
        raise ValueError("El nombre es obligatorio.")
    if int(precio) <= 0:
        raise ValueError("El precio debe ser mayor que cero.")
    if int(stock) < 0:
        raise ValueError("El stock no puede ser negativo.")
    if not str(categoria).strip():
        raise ValueError("La categoría es obligatoria.")
    return True

def producto_random(catalogo):
    disponibles = [p for p in catalogo if p.disponible()]
    return random.choice(disponibles) if disponibles else None

