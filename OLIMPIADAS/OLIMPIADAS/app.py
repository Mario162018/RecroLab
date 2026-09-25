import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image
from functools import partial
from datetime import datetime
from modelo import ( 
    crear_catalogo, sumar_al_carrito, registrar_venta, calcular_total,
    combinaciones_posibles, combinaciones_avanzadas, unidades_en_carrito,
    quitar_del_carrito, reponer_stock, guardar_datos, cargar_datos,
    buscar_productos, categorias, producto_mas_barato, producto_mas_caro,
    productos_agotados, productos_stock_bajo, valor_inventario,
    estadisticas_ventas, productos_mas_vendidos, exportar_resumen,
    generar_codigo, agregar_producto, eliminar_producto, activar_producto,
    cambiar_precio, precio_con_cupon, validar_cupon, recomendacion,
    resumen_inventario, producto_random, alternar_favorito, limpiar_favoritos,
    mensaje_stock
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ROJO = "#c8102e"
ROJO_OSCURO = "#9f0d24"
NEGRO = "#151515"
CREMA = "#f4f1ea"
BLANCO = "#ffffff"
VERDE = "#2e8b35"
GRIS = "#6d6d6d"
BORDE = "#ddd7cf"
DORADO = "#ffcc33"

def formatear_precio(numero):
    return "$" + f"{int(numero):,}".replace(",", ".")

class Aplicacion:
    def __init__(self):
        self.inventario = crear_catalogo()
        self.carrito = []
        self.ventas = cargar_datos(self.inventario)
        self.dinero = 0
        self.categoria = "Todos"
        self.orden = "nombre"
        self.favoritos = set()
        self.cupon = ""
        self.descuento = 0
        self.ultima_compra = None
        self.imagenes = {}
        self.cargar_imagenes()

        self.ventana = ctk.CTk(fg_color=CREMA)
        self.ventana.title("Olimpiadas • Kiosco Premium")
        self.ventana.geometry("1500x920")
        self.ventana.minsize(1200, 780)
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.construir_interfaz()
        self.pedir_dinero()
        self.actualizar_pantalla()

    def cargar_imagenes(self):
        carpeta = Path(__file__).parent / "imagenes"
        for producto in self.inventario:
            ruta = carpeta / f"{producto.codigo}.png"
            if ruta.exists():
                try:
                    imagen = Image.open(ruta)
                    self.imagenes[producto.codigo] = ctk.CTkImage(
                        light_image=imagen, dark_image=imagen, size=(185, 125)
                    )
                except Exception:
                    pass

    def construir_interfaz(self):
        self.ventana.grid_columnconfigure(1, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(
            self.ventana, width=245, corner_radius=0, fg_color=NEGRO
        )
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="🍔", font=("Arial", 48)).pack(pady=(25, 0))
        ctk.CTkLabel(
            sidebar, text="OLIMPIADAS", font=("Arial", 24, "bold"),
            text_color=DORADO
        ).pack()
        ctk.CTkLabel(
            sidebar, text="KIOSCO PREMIUM", font=("Arial", 11, "bold"),
            text_color="#bdbdbd"
        ).pack(pady=(0, 22))

        self.boton_inicio = self.boton_menu(sidebar, "🏠  Inicio", self.ir_inicio)
        self.boton_presupuesto = self.boton_menu(
            sidebar, "💰  Presupuesto", self.ir_presupuesto
        )
        self.boton_historial = self.boton_menu(
            sidebar, "🧾  Historial", self.ir_historial
        )
        self.boton_estadisticas = self.boton_menu(
            sidebar, "📊  Estadísticas", self.ir_estadisticas
        )
        self.boton_admin = self.boton_menu(
            sidebar, "⚙  Administración", self.ir_admin
        )

        ctk.CTkLabel(sidebar, text="────────────────",
                     text_color="#444").pack(pady=12)

        self.sidebar_dinero = ctk.CTkLabel(
            sidebar, text="", font=("Arial", 15, "bold"),
            text_color="#72e06f"
        )
        self.sidebar_dinero.pack(pady=6)

        self.sidebar_carrito = ctk.CTkLabel(
            sidebar, text="", font=("Arial", 13),
            text_color="#e8e8e8"
        )
        self.sidebar_carrito.pack(pady=3)

        self.sidebar_favoritos = ctk.CTkLabel(
            sidebar, text="", font=("Arial", 12),
            text_color="#ffb6b6"
        )
        self.sidebar_favoritos.pack(pady=3)

        ctk.CTkButton(
            sidebar, text="💵 Cambiar presupuesto",
            command=self.cambiar_presupuesto,
            height=38, fg_color="#242424", hover_color=ROJO
        ).pack(fill="x", padx=18, pady=(18, 5))

        ctk.CTkButton(
            sidebar, text="⭐ Mis favoritos",
            command=self.mostrar_favoritos,
            height=38, fg_color="#242424", hover_color=ROJO
        ).pack(fill="x", padx=18, pady=5)

        ctk.CTkButton(
            sidebar, text="🎲 Recomendarme algo",
            command=self.recomendar,
            height=38, fg_color="#242424", hover_color=ROJO
        ).pack(fill="x", padx=18, pady=5)

        ctk.CTkLabel(
            sidebar, text="RecreoLab v3.0\nSistema escolar de kiosco",
            font=("Arial", 10), text_color="#777"
        ).pack(side="bottom", pady=18)

        self.contenedor = ctk.CTkFrame(
            self.ventana, fg_color=CREMA, corner_radius=0
        )
        self.contenedor.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self.contenedor, fg_color=ROJO, corner_radius=0, height=105
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="¿Qué vas a comer hoy?",
            font=("Arial", 29, "bold"), text_color="white"
        ).grid(row=0, column=0, padx=28, pady=(18, 0), sticky="w")

        ctk.CTkLabel(
            header,
            text="Elegí tus favoritos • armá tu pedido • disfrutá tu recreo",
            font=("Arial", 13), text_color="#ffe5e5"
        ).grid(row=1, column=0, padx=30, pady=(0, 16), sticky="w")

        self.header_total = ctk.CTkLabel(
            header, text="TOTAL $0",
            font=("Arial", 19, "bold"), text_color="white"
        )
        self.header_total.grid(row=0, column=1, rowspan=2, padx=30)

        self.vistas = {}
        self.crear_inicio()
        self.crear_presupuesto()
        self.crear_historial()
        self.crear_estadisticas()
        self.crear_admin()
        self.mostrar_vista("inicio")

    def boton_menu(self, parent, texto, comando):
        return ctk.CTkButton(
            parent, text=texto, command=comando, height=45,
            corner_radius=10, fg_color="#242424",
            hover_color=ROJO, anchor="w",
            font=("Arial", 14, "bold")
        ).pack(fill="x", padx=18, pady=5)

    def crear_inicio(self):
        vista = ctk.CTkFrame(self.contenedor, fg_color=CREMA)
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_columnconfigure(1, weight=0)
        vista.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(vista, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=15)
        top.grid_columnconfigure(0, weight=1)

        self.campo_busqueda = ctk.CTkEntry(
            top, height=42, placeholder_text="🔎  Buscar por nombre, código o descripción..."
        )
        self.campo_busqueda.grid(row=0, column=0, sticky="ew")
        self.campo_busqueda.bind("<KeyRelease>", lambda e: self.actualizar_catalogo())

        ctk.CTkButton(
            top, text="Buscar", width=100, height=42,
            fg_color=NEGRO, hover_color="#333",
            command=self.actualizar_catalogo
        ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            top, text="↕ Ordenar", width=100, height=42,
            fg_color="#777", hover_color="#555",
            command=self.cambiar_orden
        ).grid(row=0, column=2, padx=(8, 0))

        categorias_menu = ["Todos"] + categorias(self.inventario)
        barra_cat = ctk.CTkFrame(vista, fg_color="transparent")
        barra_cat.grid(row=1, column=0, columnspan=2, sticky="ew", padx=24)

        for n, cat in enumerate(categorias_menu):
            ctk.CTkButton(
                barra_cat, text=cat, width=105, height=34,
                fg_color=ROJO if cat == "Todos" else "#d8d3cb",
                hover_color=ROJO_OSCURO,
                text_color="white" if cat == "Todos" else "#333",
                command=partial(self.seleccionar_categoria, cat)
            ).grid(row=0, column=n, padx=4, pady=(0, 8))

        opciones = ctk.CTkFrame(vista, fg_color="transparent")
        opciones.grid(row=2, column=0, columnspan=2, sticky="ew", padx=24)
        self.solo_stock = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            opciones, text="Mostrar solo disponibles",
            variable=self.solo_stock,
            command=self.actualizar_catalogo
        ).pack(side="left")

        self.solo_favoritos = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opciones, text="⭐ Solo favoritos",
            variable=self.solo_favoritos,
            command=self.actualizar_catalogo
        ).pack(side="left", padx=15)

        self.info_menu = ctk.CTkLabel(
            opciones, text="", text_color=GRIS
        )
        self.info_menu.pack(side="right")

        self.panel_catalogo = ctk.CTkScrollableFrame(
            vista, fg_color=CREMA, label_text="MENÚ"
        )
        self.panel_catalogo.grid(
            row=3, column=0, padx=(24, 10), pady=8, sticky="nsew"
        )
        for col in range(3):
            self.panel_catalogo.grid_columnconfigure(col, weight=1)

        self.panel_carrito = ctk.CTkFrame(
            vista, width=350, fg_color="white",
            corner_radius=18, border_width=1, border_color=BORDE
        )
        self.panel_carrito.grid(
            row=3, column=1, padx=(10, 24), pady=8, sticky="nsew"
        )
        self.panel_carrito.grid_propagate(False)
        self.panel_carrito.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.panel_carrito, text="🛒 TU PEDIDO",
            font=("Arial", 19, "bold"), text_color="#222"
        ).grid(row=0, column=0, pady=14)

        self.caja_carrito = ctk.CTkTextbox(
            self.panel_carrito, font=("Arial", 13),
            fg_color="#fafafa", text_color="#333"
        )
        self.caja_carrito.grid(row=1, column=0, padx=15, sticky="nsew")

        self.etiqueta_total = ctk.CTkLabel(
            self.panel_carrito, text="Total $0",
            font=("Arial", 24, "bold"), text_color=ROJO
        )
        self.etiqueta_total.grid(row=2, column=0, pady=8)

        self.etiqueta_descuento = ctk.CTkLabel(
            self.panel_carrito, text="Sin descuento",
            font=("Arial", 11), text_color=VERDE
        )
        self.etiqueta_descuento.grid(row=3, column=0)

        ctk.CTkButton(
            self.panel_carrito, text="↩ Quitar última",
            command=self.quitar_unidad,
            fg_color="#e7e3dd", text_color="#333",
            hover_color="#d5cfc6"
        ).grid(row=4, column=0, padx=15, pady=4, sticky="ew")

        ctk.CTkButton(
            self.panel_carrito, text="🗑 Vaciar",
            command=self.vaciar_carrito,
            fg_color="#e7e3dd", text_color="#333",
            hover_color="#d5cfc6"
        ).grid(row=5, column=0, padx=15, pady=4, sticky="ew")

        ctk.CTkButton(
            self.panel_carrito, text="🏷 Aplicar cupón",
            command=self.aplicar_cupon,
            fg_color="#777", hover_color="#555"
        ).grid(row=6, column=0, padx=15, pady=4, sticky="ew")

        ctk.CTkButton(
            self.panel_carrito, text="✔ CONFIRMAR PEDIDO",
            command=self.confirmar_venta, height=48,
            corner_radius=12, fg_color=VERDE,
            hover_color="#246f29",
            font=("Arial", 14, "bold")
        ).grid(row=7, column=0, padx=15, pady=(8, 15), sticky="ew")

        self.vistas["inicio"] = vista

    def crear_presupuesto(self):
        vista = ctk.CTkFrame(self.contenedor, fg_color=CREMA)
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            vista, text="💰 Calculadora de presupuesto",
            font=("Arial", 28, "bold"), text_color="#222"
        ).grid(row=0, column=0, pady=(30, 5))

        ctk.CTkLabel(
            vista,
            text="Buscá combinaciones de 2 o 3 productos que entren en tu dinero.",
            font=("Arial", 14), text_color="#666"
        ).grid(row=1, column=0, pady=8)

        caja = ctk.CTkFrame(vista, fg_color="white", corner_radius=18)
        caja.grid(row=2, column=0, padx=70, pady=25, sticky="nsew")
        caja.grid_columnconfigure(0, weight=1)
        caja.grid_rowconfigure(5, weight=1)

        self.campo_presupuesto = ctk.CTkEntry(
            caja, placeholder_text="Ejemplo: 5000", height=45
        )
        self.campo_presupuesto.grid(
            row=0, column=0, padx=30, pady=(25, 10), sticky="ew"
        )

        botones = ctk.CTkFrame(caja, fg_color="transparent")
        botones.grid(row=1, column=0, padx=30, sticky="ew")
        ctk.CTkButton(
            botones, text="🔎 Pares", height=42,
            fg_color=ROJO, hover_color=ROJO_OSCURO,
            command=self.buscar_combinaciones
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            botones, text="✨ Combos 2-3", height=42,
            fg_color=NEGRO, hover_color="#333",
            command=self.buscar_combinaciones_avanzadas
        ).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(
            botones, text="🎯 Recomendar", height=42,
            fg_color=VERDE, hover_color="#246f29",
            command=self.recomendar_por_presupuesto
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.caja_resultados = ctk.CTkTextbox(
            caja, font=("Arial", 14),
            fg_color="#fafafa", text_color="#333"
        )
        self.caja_resultados.grid(
            row=5, column=0, padx=30, pady=20, sticky="nsew"
        )
        self.vistas["presupuesto"] = vista

    def crear_historial(self):
        vista = ctk.CTkFrame(self.contenedor, fg_color=CREMA)
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            vista, text="🧾 Historial de pedidos",
            font=("Arial", 28, "bold"), text_color="#222"
        ).grid(row=0, column=0, pady=(30, 5))

        ctk.CTkLabel(
            vista, text="Acá quedan registrados tus pedidos confirmados.",
            font=("Arial", 14), text_color="#666"
        ).grid(row=1, column=0)

        self.caja_historial = ctk.CTkTextbox(
            vista, font=("Consolas", 13),
            fg_color="white", text_color="#333"
        )
        self.caja_historial.grid(
            row=2, column=0, padx=60, pady=25, sticky="nsew"
        )

        botones = ctk.CTkFrame(vista, fg_color="transparent")
        botones.grid(row=3, column=0, pady=(0, 20))
        ctk.CTkButton(
            botones, text="🔄 Actualizar",
            command=self.actualizar_historial,
            fg_color=ROJO
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            botones, text="📄 Exportar reporte",
            command=self.exportar_reporte,
            fg_color=NEGRO
        ).pack(side="left", padx=5)
        self.vistas["historial"] = vista

    def crear_estadisticas(self):
        vista = ctk.CTkFrame(self.contenedor, fg_color=CREMA)
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            vista, text="📊 Panel de estadísticas",
            font=("Arial", 28, "bold"), text_color="#222"
        ).grid(row=0, column=0, pady=(30, 5))

        self.caja_estadisticas = ctk.CTkTextbox(
            vista, font=("Consolas", 14),
            fg_color="white", text_color="#333"
        )
        self.caja_estadisticas.grid(
            row=2, column=0, padx=60, pady=25, sticky="nsew"
        )

        ctk.CTkButton(
            vista, text="🔄 Actualizar estadísticas",
            command=self.actualizar_estadisticas,
            fg_color=ROJO
        ).grid(row=3, column=0, pady=(0, 20))

        self.vistas["estadisticas"] = vista

    def crear_admin(self):
        vista = ctk.CTkFrame(self.contenedor, fg_color=CREMA)
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_columnconfigure(1, weight=1)
        vista.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            vista, text="⚙ Administración del kiosco",
            font=("Arial", 28, "bold"), text_color="#222"
        ).grid(row=0, column=0, columnspan=2, pady=20)

        self.panel_stock = ctk.CTkScrollableFrame(
            vista, label_text="STOCK ACTUAL", fg_color="white"
        )
        self.panel_stock.grid(
            row=1, column=0, padx=20, pady=10, sticky="nsew"
        )

        derecha = ctk.CTkScrollableFrame(
            vista, fg_color=CREMA
        )
        derecha.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        form = ctk.CTkFrame(derecha, fg_color="white", corner_radius=18)
        form.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            form, text="📦 Reponer stock",
            font=("Arial", 20, "bold"), text_color="#222"
        ).pack(pady=(20, 12))

        self.campo_codigo_reponer = ctk.CTkEntry(
            form, placeholder_text="Código: A01", height=40
        )
        self.campo_codigo_reponer.pack(fill="x", padx=20, pady=6)

        self.campo_cantidad_reponer = ctk.CTkEntry(
            form, placeholder_text="Cantidad", height=40
        )
        self.campo_cantidad_reponer.pack(fill="x", padx=20, pady=6)

        ctk.CTkButton(
            form, text="➕ Reponer", command=self.reponer,
            height=42, fg_color=NEGRO, hover_color="#333"
        ).pack(fill="x", padx=20, pady=12)

        precio = ctk.CTkFrame(derecha, fg_color="white", corner_radius=18)
        precio.pack(fill="x", pady=12)

        ctk.CTkLabel(
            precio, text="💲 Cambiar precio",
            font=("Arial", 18, "bold"), text_color="#222"
        ).pack(pady=(18, 10))

        self.campo_codigo_precio = ctk.CTkEntry(
            precio, placeholder_text="Código"
        )
        self.campo_codigo_precio.pack(fill="x", padx=20, pady=5)

        self.campo_nuevo_precio = ctk.CTkEntry(
            precio, placeholder_text="Nuevo precio"
        )
        self.campo_nuevo_precio.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            precio, text="Guardar precio",
            command=self.cambiar_precio_admin,
            fg_color=ROJO
        ).pack(fill="x", padx=20, pady=12)

        nuevo = ctk.CTkFrame(derecha, fg_color="white", corner_radius=18)
        nuevo.pack(fill="x", pady=12)

        ctk.CTkLabel(
            nuevo, text="➕ Crear producto",
            font=("Arial", 18, "bold"), text_color="#222"
        ).pack(pady=(18, 10))

        self.admin_entries = {}
        campos = [
            ("codigo", "Código opcional"),
            ("nombre", "Nombre"),
            ("precio", "Precio"),
            ("stock", "Stock inicial"),
            ("categoria", "Categoría"),
            ("emoji", "Emoji"),
            ("descripcion", "Descripción")
        ]
        for clave, texto in campos:
            entrada = ctk.CTkEntry(nuevo, placeholder_text=texto)
            entrada.pack(fill="x", padx=20, pady=4)
            self.admin_entries[clave] = entrada

        ctk.CTkButton(
            nuevo, text="Crear producto",
            command=self.crear_producto_admin,
            fg_color=VERDE, hover_color="#246f29"
        ).pack(fill="x", padx=20, pady=12)

        acciones = ctk.CTkFrame(derecha, fg_color="white", corner_radius=18)
        acciones.pack(fill="x", pady=12)

        ctk.CTkLabel(
            acciones, text="🗃 Gestión rápida",
            font=("Arial", 18, "bold"), text_color="#222"
        ).pack(pady=(18, 8))

        self.campo_codigo_accion = ctk.CTkEntry(
            acciones, placeholder_text="Código del producto"
        )
        self.campo_codigo_accion.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            acciones, text="Desactivar producto",
            command=self.desactivar_producto_admin,
            fg_color="#777", hover_color="#555"
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            acciones, text="Activar producto",
            command=self.activar_producto_admin,
            fg_color=VERDE, hover_color="#246f29"
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            acciones, text="🎲 Generar código",
            command=self.generar_codigo_admin,
            fg_color=NEGRO
        ).pack(fill="x", padx=20, pady=5)

        self.info_admin = ctk.CTkLabel(
            derecha, text="", font=("Arial", 12), text_color="#666"
        )
        self.info_admin.pack(padx=20, pady=15)

        self.vistas["admin"] = vista

    def mostrar_vista(self, nombre):
        for vista in self.vistas.values():
            vista.grid_forget()
        self.vistas[nombre].grid(row=1, column=0, sticky="nsew")
        if nombre == "inicio":
            self.actualizar_catalogo()
        elif nombre == "admin":
            self.actualizar_stock()
        elif nombre == "historial":
            self.actualizar_historial()
        elif nombre == "estadisticas":
            self.actualizar_estadisticas()

    def ir_inicio(self):
        self.mostrar_vista("inicio")

    def ir_presupuesto(self):
        self.mostrar_vista("presupuesto")

    def ir_historial(self):
        self.mostrar_vista("historial")

    def ir_estadisticas(self):
        self.mostrar_vista("estadisticas")

    def ir_admin(self):
        self.mostrar_vista("admin")

    def pedir_dinero(self):
        dialogo = ctk.CTkInputDialog(
            text="¿Cuánto dinero tenés para gastar?\nIngresá un número entero.",
            title="💰 Presupuesto"
        )
        texto = dialogo.get_input()
        try:
            self.dinero = int(texto.strip()) if texto else 0
            if self.dinero < 0:
                raise ValueError
        except ValueError:
            self.dinero = 0
            self.mostrar_alerta(
                "Dinero inválido",
                "El presupuesto quedó en $0.",
                "warning"
            )

    def cambiar_presupuesto(self):
        dialogo = ctk.CTkInputDialog(
            text="Nuevo presupuesto disponible:",
            title="💵 Cambiar presupuesto"
        )
        texto = dialogo.get_input()
        try:
            nuevo = int(texto)
            if nuevo < 0:
                raise ValueError
            self.dinero = nuevo
            self.actualizar_pantalla()
        except (ValueError, TypeError):
            self.mostrar_alerta(
                "Presupuesto inválido",
                "Ingresá un número entero mayor o igual a 0.",
                "warning"
            )

    def seleccionar_categoria(self, cat):
        self.categoria = cat
        self.actualizar_catalogo()

    def cambiar_orden(self):
        opciones = ["nombre", "precio", "precio_desc", "stock"]
        posicion = opciones.index(self.orden)
        self.orden = opciones[(posicion + 1) % len(opciones)]
        self.actualizar_catalogo()
        self.mostrar_alerta(
            "Orden actualizado",
            f"Orden actual: {self.orden}",
            "info"
        )

    def actualizar_catalogo(self):
        for w in self.panel_catalogo.winfo_children():
            w.destroy()

        busqueda = self.campo_busqueda.get().strip()
        productos = buscar_productos(
            self.inventario, busqueda, self.categoria,
            self.solo_stock.get()
        )

        if self.solo_favoritos.get():
            productos = [p for p in productos if p.codigo in self.favoritos]

        if self.orden == "precio":
            productos.sort(key=lambda p: p.precio)
        elif self.orden == "precio_desc":
            productos.sort(key=lambda p: p.precio, reverse=True)
        elif self.orden == "stock":
            productos.sort(key=lambda p: p.stock, reverse=True)
        else:
            productos.sort(key=lambda p: p.nombre.lower())

        self.info_menu.configure(
            text=f"{len(productos)} producto(s) • Orden: {self.orden}"
        )

        for i, producto in enumerate(productos):
            self.crear_tarjeta(producto, i // 3, i % 3)

        if not productos:
            ctk.CTkLabel(
                self.panel_catalogo,
                text="😕 No encontramos productos con esos filtros.",
                font=("Arial", 18, "bold"), text_color="#555"
            ).grid(row=0, column=0, columnspan=3, pady=60)

    def crear_tarjeta(self, p, fila, columna):
        disponible = p.disponible()

        tarjeta = ctk.CTkFrame(
            self.panel_catalogo, fg_color="white",
            corner_radius=16, border_width=1,
            border_color=BORDE
        )
        tarjeta.grid(
            row=fila, column=columna,
            padx=8, pady=8, sticky="nsew"
        )

        if p.codigo in self.imagenes:
            ctk.CTkLabel(
                tarjeta, text="", image=self.imagenes[p.codigo]
            ).pack(padx=10, pady=(10, 0))
        else:
            ctk.CTkLabel(
                tarjeta, text=p.emoji,
                font=("Arial", 58)
            ).pack(pady=(14, 3))

        titulo = p.nombre
        if p.codigo in self.favoritos:
            titulo = "⭐ " + titulo

        ctk.CTkLabel(
            tarjeta, text=titulo,
            font=("Arial", 17, "bold"), text_color="#222"
        ).pack(pady=(6, 0))

        ctk.CTkLabel(
            tarjeta, text=p.categoria,
            font=("Arial", 10), text_color="#999"
        ).pack()

        ctk.CTkLabel(
            tarjeta, text=formatear_precio(p.precio),
            font=("Arial", 19, "bold"), text_color=ROJO
        ).pack(pady=4)

        ctk.CTkLabel(
            tarjeta, text=mensaje_stock(p),
            font=("Arial", 11, "bold"),
            text_color="#999" if not disponible else VERDE
        ).pack()

        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.pack(fill="x", padx=12, pady=10)

        ctk.CTkButton(
            botones, text="⭐", width=40,
            command=partial(self.alternar_favorito_ui, p.codigo),
            fg_color="#eee" if p.codigo not in self.favoritos else DORADO,
            text_color="#222", hover_color="#ffdf70"
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            botones,
            text="AGREGAR" if disponible else "AGOTADO",
            command=partial(self.agregar_producto, p.codigo),
            height=38, state="normal" if disponible else "disabled",
            fg_color=ROJO if disponible else "#aaa",
            hover_color=ROJO_OSCURO
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            tarjeta, text="ℹ Ver detalle",
            command=partial(self.ver_detalle, p.codigo),
            fg_color="#e7e3dd", text_color="#333",
            hover_color="#d5cfc6", height=30
        ).pack(fill="x", padx=12, pady=(0, 12))

    def ver_detalle(self, codigo):
        try:
            p = next(x for x in self.inventario if x.codigo == codigo)
        except StopIteration:
            return

        ventana = ctk.CTkToplevel(self.ventana)
        ventana.title(p.nombre)
        ventana.geometry("440x520")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text=p.emoji, font=("Arial", 75)
        ).pack(pady=(25, 5))
        ctk.CTkLabel(
            ventana, text=p.nombre,
            font=("Arial", 26, "bold"), text_color="#222"
        ).pack()
        ctk.CTkLabel(
            ventana, text=p.categoria,
            font=("Arial", 12), text_color=GRIS
        ).pack(pady=5)
        ctk.CTkLabel(
            ventana, text=formatear_precio(p.precio),
            font=("Arial", 25, "bold"), text_color=ROJO
        ).pack(pady=10)
        ctk.CTkLabel(
            ventana, text=p.descripcion,
            wraplength=360, font=("Arial", 14),
            text_color="#444"
        ).pack(pady=15)
        ctk.CTkLabel(
            ventana, text=mensaje_stock(p),
            font=("Arial", 13, "bold"),
            text_color=VERDE if p.disponible() else "#999"
        ).pack(pady=5)

        ctk.CTkButton(
            ventana, text="AGREGAR AL PEDIDO",
            command=lambda: [ventana.destroy(), self.agregar_producto(codigo)],
            fg_color=ROJO, hover_color=ROJO_OSCURO,
            height=45
        ).pack(fill="x", padx=40, pady=25)

    def agregar_producto(self, codigo):
        producto = next(
            (p for p in self.inventario if p.codigo == codigo), None
        )
        if not producto:
            return

        total_actual = calcular_total(self.carrito)
        if total_actual + producto.precio > self.dinero:
            falta = total_actual + producto.precio - self.dinero
            self.mostrar_alerta(
                "💰 Presupuesto insuficiente",
                f"Te faltan {formatear_precio(falta)} para agregar {producto.nombre}.",
                "warning"
            )
            return

        try:
            sumar_al_carrito(self.inventario, self.carrito, codigo)
        except ValueError as e:
            self.mostrar_alerta("Revisá la compra", str(e), "warning")
            return

        self.actualizar_pantalla()

    def alternar_favorito_ui(self, codigo):
        estado = alternar_favorito(self.favoritos, codigo)
        limpiar_favoritos(self.favoritos, self.inventario)
        self.actualizar_catalogo()
        self.sidebar_favoritos.configure(
            text=f"⭐ {len(self.favoritos)} favorito(s)"
        )

    def mostrar_favoritos(self):
        self.ir_inicio()
        self.solo_favoritos.set(True)
        self.actualizar_catalogo()

    def recomendar(self):
        producto = producto_random(self.inventario)
        if not producto:
            self.mostrar_alerta(
                "Sin productos", "No hay productos disponibles.", "warning"
            )
            return
        self.ver_detalle(producto.codigo)

    def quitar_unidad(self):
        if self.carrito:
            self.carrito.pop()
        self.actualizar_pantalla()

    def quitar_codigo(self, codigo):
        quitar_del_carrito(self.carrito, codigo, 1)
        self.actualizar_pantalla()

    def vaciar_carrito(self):
        self.carrito.clear()
        self.cupon = ""
        self.descuento = 0
        self.actualizar_pantalla()

    def aplicar_cupon(self):
        if not self.carrito:
            self.mostrar_alerta(
                "Carrito vacío", "Agregá productos antes de usar un cupón.", "warning"
            )
            return

        dialogo = ctk.CTkInputDialog(
            text="Cupones válidos:\nRECREO10 • PREMIUM15 • KIOSCO20 • VUELTA5",
            title="🏷 Cupón"
        )
        codigo = dialogo.get_input()
        porcentaje = validar_cupon(codigo or "")

        if porcentaje == 0:
            self.mostrar_alerta(
                "Cupón inválido",
                "Ese código no existe.",
                "warning"
            )
            return

        self.cupon = codigo.upper()
        self.descuento = porcentaje
        self.actualizar_pantalla()

    def actualizar_pantalla(self):
        if hasattr(self, "caja_carrito"):
            self.caja_carrito.configure(state="normal")
            self.caja_carrito.delete("1.0", "end")

            if not self.carrito:
                texto = "Tu pedido está vacío.\n\nElegí algo rico del menú."
            else:
                resumen = {}
                for p in self.carrito:
                    if p.codigo not in resumen:
                        resumen[p.codigo] = [p, 0]
                    resumen[p.codigo][1] += 1

                partes = []
                for codigo, datos in resumen.items():
                    p, cantidad = datos
                    subtotal = p.precio * cantidad
                    partes.append(
                        f"{cantidad}x {p.nombre}\n"
                        f"   {formatear_precio(subtotal)}   "
                        f"[quitar 1 con botón inferior]\n"
                    )
                texto = "\n".join(partes)

            self.caja_carrito.insert("1.0", texto)
            self.caja_carrito.configure(state="disabled")

            subtotal = calcular_total(self.carrito)
            total, ahorro = precio_con_cupon(subtotal, self.cupon)

            self.etiqueta_total.configure(
                text=f"Total {formatear_precio(total)}"
            )

            if ahorro:
                self.etiqueta_descuento.configure(
                    text=f"🏷 {self.cupon}: -{formatear_precio(ahorro)}"
                )
            else:
                self.etiqueta_descuento.configure(
                    text="Sin descuento"
                )

            self.header_total.configure(
                text=f"TOTAL {formatear_precio(total)}"
            )

        cantidad = len(self.carrito)
        self.sidebar_dinero.configure(
            text=f"💰 {formatear_precio(self.dinero)} disponibles"
        )
        self.sidebar_carrito.configure(
            text=f"🛒 {cantidad} unidad(es)"
        )
        self.sidebar_favoritos.configure(
            text=f"⭐ {len(self.favoritos)} favorito(s)"
        )

        if "inicio" in self.vistas:
            self.actualizar_catalogo()

        if "admin" in self.vistas:
            self.actualizar_stock()

    def confirmar_venta(self):
        if not self.carrito:
            self.mostrar_alerta(
                "Pedido vacío",
                "Agregá productos antes de confirmar.",
                "warning"
            )
            return

        subtotal = calcular_total(self.carrito)
        total, ahorro = precio_con_cupon(subtotal, self.cupon)

        if total > self.dinero:
            falta = total - self.dinero
            self.mostrar_alerta(
                "Presupuesto insuficiente",
                f"Te faltan {formatear_precio(falta)}.",
                "warning"
            )
            return

        if not messagebox.askyesno(
            "Confirmar pedido",
            f"Subtotal: {formatear_precio(subtotal)}\n"
            f"Descuento: {formatear_precio(ahorro)}\n"
            f"Total: {formatear_precio(total)}\n\n"
            "¿Querés confirmar este pedido?",
            parent=self.ventana
        ):
            return

        try:
            total_real = registrar_venta(
                self.carrito, self.ventas,
                self.descuento, self.cupon
            )
        except ValueError as e:
            self.mostrar_alerta(
                "No se registró",
                str(e),
                "error"
            )
            return

        self.dinero -= total_real
        self.ultima_compra = datetime.now()
        self.cupon = ""
        self.descuento = 0

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()

        self.mostrar_alerta(
            "✅ ¡Pedido confirmado!",
            f"Total: {formatear_precio(total_real)}\n"
            f"Te quedan {formatear_precio(self.dinero)}.",
            "info"
        )

    def buscar_combinaciones(self):
        try:
            presupuesto = int(self.campo_presupuesto.get().strip())
            opciones = combinaciones_posibles(
                self.inventario, presupuesto
            )
        except ValueError:
            self.mostrar_alerta(
                "Presupuesto inválido",
                "Ingresá un número entero mayor que 0.",
                "warning"
            )
            return

        if not opciones:
            self.mostrar_texto(
                self.caja_resultados,
                "No hay pares disponibles con ese presupuesto."
            )
            return

        texto = "COMBINACIONES DE 2 PRODUCTOS\n\n"
        for a, b, total, sobra in opciones[:30]:
            texto += (
                f"🍔 {a} + {b}\n"
                f"   Total: {formatear_precio(total)}\n"
                f"   Sobran: {formatear_precio(sobra)}\n\n"
            )
        self.mostrar_texto(self.caja_resultados, texto)

    def buscar_combinaciones_avanzadas(self):
        try:
            presupuesto = int(self.campo_presupuesto.get().strip())
            opciones = combinaciones_avanzadas(
                self.inventario, presupuesto, 3
            )
        except ValueError:
            self.mostrar_alerta(
                "Presupuesto inválido",
                "Ingresá un número entero mayor que 0.",
                "warning"
            )
            return

        if not opciones:
            self.mostrar_texto(
                self.caja_resultados,
                "No encontramos combos de 2 o 3 productos."
            )
            return

        texto = "✨ COMBOS DE 2 Y 3 PRODUCTOS\n\n"
        for opcion in opciones[:40]:
            nombres = " + ".join(opcion["productos"])
            texto += (
                f"🍱 {nombres}\n"
                f"   Total: {formatear_precio(opcion['total'])}\n"
                f"   Sobra: {formatear_precio(opcion['sobra'])}\n\n"
            )
        self.mostrar_texto(self.caja_resultados, texto)

    def recomendar_por_presupuesto(self):
        try:
            presupuesto = int(self.campo_presupuesto.get().strip())
            producto = recomendacion(self.inventario, presupuesto)
        except ValueError:
            self.mostrar_alerta(
                "Presupuesto inválido",
                "Ingresá un número entero.",
                "warning"
            )
            return

        if not producto:
            self.mostrar_texto(
                self.caja_resultados,
                "No hay un producto que entre en ese presupuesto."
            )
            return

        self.mostrar_texto(
            self.caja_resultados,
            "🎯 RECOMENDACIÓN\n\n"
            f"{producto.emoji} {producto.nombre}\n"
            f"Precio: {formatear_precio(producto.precio)}\n"
            f"Te sobran: {formatear_precio(presupuesto - producto.precio)}"
        )

    def actualizar_stock(self):
        for w in self.panel_stock.winfo_children():
            w.destroy()

        for p in self.inventario:
            if not p.activo:
                continue

            fila = ctk.CTkFrame(
                self.panel_stock, fg_color="#fafafa",
                corner_radius=10
            )
            fila.pack(fill="x", padx=5, pady=4)

            estado = (
                "🔴 Agotado" if p.stock == 0
                else ("🟠 Bajo" if p.stock <= 2 else "🟢 Disponible")
            )

            ctk.CTkLabel(
                fila, text=f"{p.emoji} {p.codigo} • {p.nombre}",
                font=("Arial", 13, "bold"),
                text_color="#333"
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                fila, text=f"{p.stock}  {estado}",
                font=("Arial", 12), text_color="#555"
            ).pack(side="right", padx=12)

        resumen = resumen_inventario(self.inventario)
        self.info_admin.configure(
            text=f"{resumen['productos']} productos activos\n"
                 f"{resumen['stock']} unidades en stock\n"
                 f"Valor del inventario: {formatear_precio(resumen['valor'])}\n"
                 f"Agotados: {resumen['agotados']} • Stock bajo: {resumen['bajo_stock']}"
        )

    def reponer(self):
        codigo = self.campo_codigo_reponer.get().strip().upper()

        try:
            cantidad = int(self.campo_cantidad_reponer.get().strip())
        except ValueError:
            self.mostrar_alerta(
                "Cantidad inválida",
                "Usá un número entero positivo.",
                "warning"
            )
            return

        try:
            producto = reponer_stock(
                self.inventario, codigo, cantidad
            )
        except ValueError as e:
            self.mostrar_alerta(
                "No se pudo reponer",
                str(e),
                "warning"
            )
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_alerta(
            "📦 Stock actualizado",
            f"{producto.nombre}: ahora tiene {producto.stock} unidad(es).",
            "info"
        )

    def cambiar_precio_admin(self):
        codigo = self.campo_codigo_precio.get().strip().upper()

        try:
            precio = int(self.campo_nuevo_precio.get().strip())
            producto = cambiar_precio(
                self.inventario, codigo, precio
            )
        except ValueError as e:
            self.mostrar_alerta(
                "Precio inválido",
                str(e),
                "warning"
            )
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_alerta(
            "💲 Precio actualizado",
            f"{producto.nombre}: {formatear_precio(producto.precio)}.",
            "info"
        )

    def crear_producto_admin(self):
        datos = {
            clave: entrada.get().strip()
            for clave, entrada in self.admin_entries.items()
        }

        try:
            codigo = datos["codigo"] or generar_codigo(self.inventario)
            precio = int(datos["precio"])
            stock = int(datos["stock"])

            producto = agregar_producto(
                self.inventario,
                codigo,
                datos["nombre"],
                precio,
                stock,
                datos["categoria"] or "Otros",
                datos["descripcion"],
                datos["emoji"] or "🍴"
            )
        except (ValueError, TypeError) as e:
            self.mostrar_alerta(
                "No se creó el producto",
                str(e),
                "warning"
            )
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()

        for entrada in self.admin_entries.values():
            entrada.delete(0, "end")

        self.mostrar_alerta(
            "✅ Producto creado",
            f"{producto.codigo} • {producto.nombre}",
            "info"
        )

    def desactivar_producto_admin(self):
        codigo = self.campo_codigo_accion.get().strip().upper()
        try:
            producto = eliminar_producto(self.inventario, codigo)
        except ValueError as e:
            self.mostrar_alerta(
                "Código inválido", str(e), "warning"
            )
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_alerta(
            "Producto desactivado",
            f"{producto.nombre} ya no aparece en el menú.",
            "info"
        )

    def activar_producto_admin(self):
        codigo = self.campo_codigo_accion.get().strip().upper()
        try:
            producto = activar_producto(self.inventario, codigo)
        except ValueError as e:
            self.mostrar_alerta(
                "Código inválido", str(e), "warning"
            )
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_alerta(
            "Producto activado",
            f"{producto.nombre} volvió al menú.",
            "info"
        )

    def generar_codigo_admin(self):
        codigo = generar_codigo(self.inventario)
        self.admin_entries["codigo"].delete(0, "end")
        self.admin_entries["codigo"].insert(0, codigo)

    def actualizar_historial(self):
        texto = ""

        if not self.ventas:
            texto = "Todavía no hay pedidos registrados."
        else:
            for numero, venta in enumerate(reversed(self.ventas), 1):
                if isinstance(venta, dict):
                    texto += (
                        f"PEDIDO #{len(self.ventas) - numero + 1}\n"
                        f"Fecha: {venta.get('fecha', '-')}\n"
                        f"Subtotal: {formatear_precio(venta.get('subtotal', 0))}\n"
                        f"Descuento: {formatear_precio(venta.get('descuento', 0))}\n"
                        f"Total: {formatear_precio(venta.get('total', 0))}\n"
                    )
                    if venta.get("cupon"):
                        texto += f"Cupón: {venta.get('cupon')}\n"
                    texto += "Productos:\n"
                    for p in venta.get("productos", []):
                        texto += (
                            f"  • {p.get('cantidad', 0)}x "
                            f"{p.get('nombre', 'Producto')} "
                            f"= {formatear_precio(p.get('subtotal', 0))}\n"
                        )
                    texto += "\n" + ("-" * 55) + "\n\n"
                else:
                    texto += (
                        f"PEDIDO #{len(self.ventas) - numero + 1}\n"
                        f"Total: {formatear_precio(venta)}\n\n"
                    )

        self.mostrar_texto(self.caja_historial, texto)

    def actualizar_estadisticas(self):
        datos = estadisticas_ventas(self.ventas)
        ranking = productos_mas_vendidos(self.ventas)
        agotados = productos_agotados(self.inventario)
        bajos = productos_stock_bajo(self.inventario)
        barato = producto_mas_barato(self.inventario)
        caro = producto_mas_caro(self.inventario)

        texto = (
            "RECREOLAB • ESTADÍSTICAS\n"
            + "=" * 55 + "\n\n"
            f"Pedidos registrados: {datos['ventas']}\n"
            f"Unidades vendidas: {datos['unidades']}\n"
            f"Ingresos acumulados: {formatear_precio(datos['ingresos'])}\n\n"
            "INVENTARIO\n"
            + "-" * 55 + "\n"
            f"Productos activos: {resumen_inventario(self.inventario)['productos']}\n"
            f"Unidades en stock: {resumen_inventario(self.inventario)['stock']}\n"
            f"Valor del inventario: {formatear_precio(valor_inventario(self.inventario))}\n"
            f"Agotados: {len(agotados)}\n"
            f"Stock bajo: {len(bajos)}\n"
        )

        if barato:
            texto += (
                f"\nProducto más barato: {barato.nombre} "
                f"({formatear_precio(barato.precio)})\n"
            )
        if caro:
            texto += (
                f"Producto más caro: {caro.nombre} "
                f"({formatear_precio(caro.precio)})\n"
            )

        texto += "\nTOP DE VENTAS\n" + "-" * 55 + "\n"
        if ranking:
            for posicion, (nombre, cantidad) in enumerate(ranking[:10], 1):
                texto += f"{posicion:02d}. {nombre}: {cantidad} unidad(es)\n"
        else:
            texto += "Todavía no hay suficientes datos de ventas.\n"

        self.mostrar_texto(self.caja_estadisticas, texto)

    def exportar_reporte(self):
        try:
            ruta = exportar_resumen(self.ventas)
            self.mostrar_alerta(
                "📄 Reporte creado",
                f"Se guardó en:\n{ruta.resolve()}",
                "info"
            )
        except OSError as e:
            self.mostrar_alerta(
                "Error al exportar", str(e), "error"
            )

    def mostrar_texto(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def mostrar_alerta(self, titulo, mensaje, tipo="info"):
        colores = {
            "error": "#c8102e",
            "warning": "#e08b00",
            "info": "#2e8b35"
        }
        iconos = {
            "error": "❌",
            "warning": "⚠️",
            "info": "✅"
        }

        ventana = ctk.CTkToplevel(self.ventana)
        ventana.title(titulo)
        ventana.geometry("450x250")
        ventana.resizable(False, False)
        ventana.grab_set()

        color = colores.get(tipo, VERDE)

        ctk.CTkFrame(
            ventana, fg_color=color,
            height=85, corner_radius=0
        ).pack(fill="x")

        ctk.CTkLabel(
            ventana,
            text=f"{iconos.get(tipo, '✅')}  {titulo}",
            font=("Arial", 18, "bold"),
            text_color="white", fg_color=color
        ).place(relx=.5, rely=.17, anchor="center")

        ctk.CTkLabel(
            ventana, text=mensaje,
            font=("Arial", 14),
            wraplength=390, text_color="#333"
        ).pack(pady=25)

        ctk.CTkButton(
            ventana, text="Aceptar",
            command=ventana.destroy,
            width=120, fg_color=NEGRO
        ).pack()

    def cerrar(self):
        try:
            guardar_datos(self.inventario, self.ventas)
        except OSError:
            pass
        self.ventana.destroy()

    def ejecutar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    Aplicacion().ejecutar()
