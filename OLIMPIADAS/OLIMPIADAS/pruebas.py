"""Casos de prueba de RecreoLab.

No dependen de la interfaz gráfica (customtkinter): prueban
directamente las funciones de modelo.py. Se corren con:

    python3 pruebas.py

Cada prueba es una función aparte. Si algo falla, se ve exactamente
cuál y por qué, y el resto de las pruebas se sigue ejecutando igual.
"""

import os

from modelo import (
    Catalogo, Producto,
    crear_catalogo, encontrar_producto, buscar_productos, categorias,
    sumar_al_carrito, quitar_del_carrito, calcular_total,
    registrar_venta, reponer_stock, cambiar_precio, agregar_producto,
    eliminar_producto, activar_producto, validar_producto,
    validar_cupon, precio_con_cupon, combinaciones_posibles,
    combinaciones_avanzadas, generar_combinaciones, guardar_datos,
    cargar_datos, alternar_favorito, estadisticas_ventas,
    producto_mas_barato, producto_mas_caro, ordenar_catalogo,
    productos_agotados, inicializar_base_datos, guardar_en_base_datos,
    top_productos_sql,
)
import sqlite3
from itertools import combinations as combinations_referencia


# ---------------------------------------------------------------
# Catálogo y búsqueda
# ---------------------------------------------------------------

def prueba_crear_catalogo_devuelve_40_productos():
    catalogo = crear_catalogo()
    assert len(catalogo) == 40


def prueba_encontrar_producto_por_codigo():
    catalogo = crear_catalogo()
    producto = encontrar_producto(catalogo, "a01")  # minúscula a propósito
    assert producto.nombre == "Agua"


def prueba_encontrar_producto_inexistente_lanza_error():
    catalogo = crear_catalogo()
    try:
        encontrar_producto(catalogo, "Z99")
        assert False, "Debía rechazar un código inexistente"
    except ValueError:
        pass


def prueba_buscar_productos_por_texto():
    catalogo = crear_catalogo()
    resultado = buscar_productos(catalogo, texto="choco")
    nombres = [p.nombre for p in resultado]
    assert "Chocolate" in nombres


def prueba_buscar_productos_por_categoria():
    catalogo = crear_catalogo()
    resultado = buscar_productos(catalogo, categoria="Bebidas")
    assert len(resultado) > 0
    assert all(p.categoria == "Bebidas" for p in resultado)


def prueba_buscar_productos_solo_disponibles_excluye_agotados():
    catalogo = crear_catalogo()
    encontrar_producto(catalogo, "A01").stock = 0
    resultado = buscar_productos(catalogo, solo_disponibles=True)
    assert "A01" not in [p.codigo for p in resultado]


def prueba_categorias_sin_repetidos():
    catalogo = crear_catalogo()
    lista = categorias(catalogo)
    assert len(lista) == len(set(lista))
    assert "Bebidas" in lista


# ---------------------------------------------------------------
# Carrito
# ---------------------------------------------------------------

def prueba_sumar_al_carrito_respeta_stock():
    catalogo = crear_catalogo()
    producto = encontrar_producto(catalogo, "A06")  # Caramelos, stock 15
    producto.stock = 2
    carrito = []
    sumar_al_carrito(catalogo, carrito, "A06", cantidad=2)
    try:
        sumar_al_carrito(catalogo, carrito, "A06", cantidad=1)
        assert False, "Debía rechazar superar el stock"
    except ValueError:
        pass


def prueba_sumar_al_carrito_rechaza_producto_desactivado():
    catalogo = crear_catalogo()
    eliminar_producto(catalogo, "A02")  # lo desactiva
    try:
        sumar_al_carrito(catalogo, [], "A02")
        assert False, "Debía rechazar un producto desactivado"
    except ValueError:
        pass


def prueba_quitar_del_carrito():
    catalogo = crear_catalogo()
    carrito = []
    sumar_al_carrito(catalogo, carrito, "A03", cantidad=3)
    eliminadas = quitar_del_carrito(carrito, "A03", cantidad=2)
    assert eliminadas == 2
    assert len(carrito) == 1


# ---------------------------------------------------------------
# Ventas y cupones
# ---------------------------------------------------------------

def prueba_registrar_venta_descuenta_stock_y_guarda_registro():
    catalogo = crear_catalogo()
    producto = encontrar_producto(catalogo, "A03")
    stock_inicial = producto.stock
    carrito = []
    sumar_al_carrito(catalogo, carrito, "A03", cantidad=2)
    ventas = []
    total = registrar_venta(carrito, ventas)
    assert total == producto.precio * 2
    assert len(ventas) == 1
    assert ventas[0]["total"] == total
    assert carrito == []
    assert producto.stock == stock_inicial - 2


def prueba_registrar_venta_rechaza_carrito_vacio():
    try:
        registrar_venta([], [])
        assert False, "Debía rechazar un carrito vacío"
    except ValueError:
        pass


def prueba_validar_cupon_codigos_validos_e_invalidos():
    assert validar_cupon("recreo10") == 10  # no distingue mayúsculas
    assert validar_cupon("NOEXISTE") == 0


def prueba_precio_con_cupon_aplica_el_descuento_correcto():
    total, ahorro = precio_con_cupon(1000, "KIOSCO20")
    assert ahorro == 200
    assert total == 800


def prueba_precio_con_cupon_invalido_no_descuenta():
    total, ahorro = precio_con_cupon(1000, "NOEXISTE")
    assert ahorro == 0
    assert total == 1000


# ---------------------------------------------------------------
# Alta, baja, modificación (CRUD sobre el catálogo)
# ---------------------------------------------------------------

def prueba_reponer_stock_aumenta_correctamente():
    catalogo = crear_catalogo()
    producto = encontrar_producto(catalogo, "A01")
    stock_inicial = producto.stock
    reponer_stock(catalogo, "A01", 5)
    assert producto.stock == stock_inicial + 5


def prueba_reponer_stock_rechaza_cantidad_no_positiva():
    catalogo = crear_catalogo()
    try:
        reponer_stock(catalogo, "A01", 0)
        assert False, "Debía rechazar cantidad 0"
    except ValueError:
        pass


def prueba_cambiar_precio_rechaza_precio_invalido():
    catalogo = crear_catalogo()
    try:
        cambiar_precio(catalogo, "A01", 0)
        assert False, "Debía rechazar precio <= 0"
    except ValueError:
        pass


def prueba_agregar_producto_lo_suma_al_catalogo():
    catalogo = crear_catalogo()
    cantidad_inicial = len(catalogo)
    agregar_producto(catalogo, "Z01", "Producto nuevo", 500, 3, "Snacks")
    assert len(catalogo) == cantidad_inicial + 1
    assert encontrar_producto(catalogo, "Z01").nombre == "Producto nuevo"


def prueba_agregar_producto_rechaza_codigo_duplicado():
    catalogo = crear_catalogo()
    try:
        agregar_producto(catalogo, "A01", "Agua repetida", 500, 3, "Bebidas")
        assert False, "Debía rechazar el código repetido"
    except ValueError:
        pass


def prueba_eliminar_producto_desactiva_sin_borrar_del_catalogo():
    catalogo = crear_catalogo()
    cantidad_inicial = len(catalogo)
    eliminar_producto(catalogo, "A01")
    assert len(catalogo) == cantidad_inicial  # sigue en la lista
    assert encontrar_producto(catalogo, "A01").activo is False
    assert "A01" not in [p.codigo for p in buscar_productos(catalogo)]


def prueba_activar_producto_lo_reactiva():
    catalogo = crear_catalogo()
    eliminar_producto(catalogo, "A01")
    activar_producto(catalogo, "A01")
    assert encontrar_producto(catalogo, "A01").activo is True


def prueba_validar_producto_rechaza_datos_invalidos():
    try:
        validar_producto("", 100, 1, "Snacks")
        assert False, "Debía rechazar nombre vacío"
    except ValueError:
        pass
    try:
        validar_producto("Algo", -5, 1, "Snacks")
        assert False, "Debía rechazar precio negativo"
    except ValueError:
        pass
    try:
        validar_producto("Algo", 100, -1, "Snacks")
        assert False, "Debía rechazar stock negativo"
    except ValueError:
        pass
    assert validar_producto("Algo", 100, 1, "Snacks") is True


# ---------------------------------------------------------------
# Presupuesto: combinaciones
# ---------------------------------------------------------------

def prueba_combinaciones_posibles_descarta_productos_agotados():
    catalogo = [p for p in crear_catalogo() if p.codigo in ("A03", "A05", "A06")]
    encontrar_producto(catalogo, "A06").stock = 0  # lo deja agotado
    resultado = combinaciones_posibles(catalogo, 5000)
    nombres_en_resultado = {n for fila in resultado for n in (fila[0], fila[1])}
    assert "Caramelos" not in nombres_en_resultado


def prueba_combinaciones_avanzadas_respeta_cantidad_maxima():
    catalogo = crear_catalogo()
    resultado = combinaciones_avanzadas(catalogo, 3000, cantidad_maxima=3)
    assert all(len(opcion["productos"]) <= 3 for opcion in resultado)
    assert all(len(opcion["productos"]) >= 2 for opcion in resultado)


# ---------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------

def prueba_guardar_y_cargar_mantiene_stock_y_ventas():
    catalogo = crear_catalogo()
    encontrar_producto(catalogo, "A01").stock = 3
    ventas = [{"total": 1000, "productos": []}]
    guardar_datos(catalogo, ventas, "prueba_temporal.json")

    catalogo_nuevo = crear_catalogo()
    ventas_cargadas = cargar_datos(catalogo_nuevo, "prueba_temporal.json")

    assert encontrar_producto(catalogo_nuevo, "A01").stock == 3
    assert ventas_cargadas == ventas

    os.remove("prueba_temporal.json")


def prueba_cargar_datos_archivo_inexistente_devuelve_lista_vacia():
    catalogo = crear_catalogo()
    resultado = cargar_datos(catalogo, "no_existe_este_archivo.json")
    assert resultado == []


# ---------------------------------------------------------------
# Favoritos y estadísticas
# ---------------------------------------------------------------

def prueba_alternar_favorito_agrega_y_quita():
    favoritos = set()
    agregado = alternar_favorito(favoritos, "A01")
    assert agregado is True
    assert "A01" in favoritos
    quitado = alternar_favorito(favoritos, "A01")
    assert quitado is False
    assert "A01" not in favoritos


def prueba_estadisticas_ventas_cuenta_bien():
    ventas = [
        {"total": 1000, "productos": [{"cantidad": 2}]},
        {"total": 500, "productos": [{"cantidad": 1}]},
    ]
    resultado = estadisticas_ventas(ventas)
    assert resultado["ventas"] == 2
    assert resultado["ingresos"] == 1500
    assert resultado["unidades"] == 3


def prueba_producto_mas_barato_y_mas_caro():
    catalogo = crear_catalogo()
    barato = producto_mas_barato(catalogo)
    caro = producto_mas_caro(catalogo)
    assert all(p.precio >= barato.precio for p in catalogo if p.activo)
    assert all(p.precio <= caro.precio for p in catalogo if p.activo)


def prueba_ordenar_catalogo_por_precio_queda_ascendente():
    catalogo = crear_catalogo()
    ordenado = ordenar_catalogo(catalogo, criterio="precio")
    precios = [p.precio for p in ordenado]
    assert precios == sorted(precios)


def prueba_productos_agotados_solo_lista_stock_cero():
    catalogo = crear_catalogo()
    encontrar_producto(catalogo, "A01").stock = 0
    resultado = productos_agotados(catalogo)
    assert "A01" in [p.codigo for p in resultado]
    assert all(p.stock == 0 for p in resultado)


# ---------------------------------------------------------------
# Base de datos SQLite
# ---------------------------------------------------------------

def prueba_guardar_datos_crea_la_base_sqlite_con_el_mismo_stock():
    catalogo = crear_catalogo()
    encontrar_producto(catalogo, "A01").stock = 3
    ventas = []
    guardar_datos(catalogo, ventas, "prueba_temporal.json", "prueba_temporal.db")

    conexion = sqlite3.connect("prueba_temporal.db")
    fila = conexion.execute(
        "SELECT stock FROM productos WHERE codigo = ?", ("A01",)
    ).fetchone()
    cantidad = conexion.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    conexion.close()

    assert fila is not None, "El producto A01 no quedó en la base"
    assert fila[0] == 3, "El stock en la base no coincide con el del catálogo"
    assert cantidad == len(catalogo)

    os.remove("prueba_temporal.json")
    os.remove("prueba_temporal.db")


def prueba_base_de_datos_registra_ventas_con_su_detalle():
    catalogo = crear_catalogo()
    carrito = []
    sumar_al_carrito(catalogo, carrito, "A03", cantidad=2)
    ventas = []
    registrar_venta(carrito, ventas)
    guardar_en_base_datos(catalogo, ventas, "prueba_temporal.db")

    conexion = sqlite3.connect("prueba_temporal.db")
    total_ventas = conexion.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    detalle = conexion.execute(
        "SELECT producto_codigo, cantidad FROM detalle_venta"
    ).fetchall()
    conexion.close()

    assert total_ventas == 1
    assert ("A03", 2) in detalle

    os.remove("prueba_temporal.db")


def prueba_base_de_datos_reemplaza_datos_viejos_al_volver_a_guardar():
    catalogo = crear_catalogo()
    guardar_en_base_datos(catalogo, [], "prueba_temporal.db")

    # Sacamos un producto del catálogo en memoria y volvemos a guardar:
    # la base tiene que reflejar el catálogo actual, no acumular filas
    # de la vez anterior.
    catalogo_reducido = [p for p in catalogo if p.codigo != "A01"]
    guardar_en_base_datos(catalogo_reducido, [], "prueba_temporal.db")

    conexion = sqlite3.connect("prueba_temporal.db")
    cantidad = conexion.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    conexion.close()

    assert cantidad == len(catalogo_reducido)

    os.remove("prueba_temporal.db")


def prueba_top_productos_sql_devuelve_el_mas_vendido_primero():
    catalogo = crear_catalogo()
    ventas = []
    carrito = []
    sumar_al_carrito(catalogo, carrito, "A03", cantidad=3)  # Alfajor x3
    registrar_venta(carrito, ventas)
    sumar_al_carrito(catalogo, carrito, "A06", cantidad=1)  # Caramelos x1
    registrar_venta(carrito, ventas)
    guardar_en_base_datos(catalogo, ventas, "prueba_temporal.db")

    top = top_productos_sql("prueba_temporal.db", limite=5)

    assert top[0]["codigo"] == "A03"
    assert top[0]["unidades"] == 3

    os.remove("prueba_temporal.db")


# ---------------------------------------------------------------
# Runner
# ---------------------------------------------------------------

PRUEBAS = [
    prueba_crear_catalogo_devuelve_40_productos,
    prueba_encontrar_producto_por_codigo,
    prueba_encontrar_producto_inexistente_lanza_error,
    prueba_buscar_productos_por_texto,
    prueba_buscar_productos_por_categoria,
    prueba_buscar_productos_solo_disponibles_excluye_agotados,
    prueba_categorias_sin_repetidos,
    prueba_sumar_al_carrito_respeta_stock,
    prueba_sumar_al_carrito_rechaza_producto_desactivado,
    prueba_quitar_del_carrito,
    prueba_registrar_venta_descuenta_stock_y_guarda_registro,
    prueba_registrar_venta_rechaza_carrito_vacio,
    prueba_validar_cupon_codigos_validos_e_invalidos,
    prueba_precio_con_cupon_aplica_el_descuento_correcto,
    prueba_precio_con_cupon_invalido_no_descuenta,
    prueba_reponer_stock_aumenta_correctamente,
    prueba_reponer_stock_rechaza_cantidad_no_positiva,
    prueba_cambiar_precio_rechaza_precio_invalido,
    prueba_agregar_producto_lo_suma_al_catalogo,
    prueba_agregar_producto_rechaza_codigo_duplicado,
    prueba_eliminar_producto_desactiva_sin_borrar_del_catalogo,
    prueba_activar_producto_lo_reactiva,
    prueba_validar_producto_rechaza_datos_invalidos,
    prueba_combinaciones_posibles_descarta_productos_agotados,
    prueba_combinaciones_avanzadas_respeta_cantidad_maxima,
    prueba_guardar_y_cargar_mantiene_stock_y_ventas,
    prueba_cargar_datos_archivo_inexistente_devuelve_lista_vacia,
    prueba_alternar_favorito_agrega_y_quita,
    prueba_estadisticas_ventas_cuenta_bien,
    prueba_producto_mas_barato_y_mas_caro,
    prueba_ordenar_catalogo_por_precio_queda_ascendente,
    prueba_productos_agotados_solo_lista_stock_cero,
    prueba_guardar_datos_crea_la_base_sqlite_con_el_mismo_stock,
    prueba_base_de_datos_registra_ventas_con_su_detalle,
    prueba_base_de_datos_reemplaza_datos_viejos_al_volver_a_guardar,
    prueba_top_productos_sql_devuelve_el_mas_vendido_primero,
]


def main():
    fallidas = 0
    for prueba in PRUEBAS:
        nombre = prueba.__name__
        try:
            prueba()
            print(f"OK    · {nombre}")
        except AssertionError as error:
            fallidas += 1
            print(f"FALLÓ · {nombre} → {error}")
        except Exception as error:
            fallidas += 1
            print(f"ERROR · {nombre} → {type(error).__name__}: {error}")

    print()
    total = len(PRUEBAS)
    if fallidas == 0:
        print(f"Todas las pruebas pasaron ({total}/{total}).")
    else:
        print(f"{total - fallidas}/{total} pruebas pasaron, {fallidas} fallaron.")


if __name__ == "__main__":
    main()
