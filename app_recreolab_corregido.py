import customtkinter as ctk
from tkinter import messagebox
from functools import partial

from modelo_recreolab_corregido import (crear_catalogo, sumar_al_carrito, registrar_venta,
                     calcular_total, combinaciones_posibles,
                     unidades_en_carrito, reponer_stock,
                     guardar_datos, cargar_datos)


def formatear_precio(monto):
    """Formatea un monto entero como '$1.500' (separador de miles ·
    solo afecta cómo se muestra, no cómo se valida ni se calcula)."""
    return f"${monto:,}".replace(",", ".")


class Aplicacion:
    def __init__(self):
        self.inventario = crear_catalogo()
        self.carrito = []
        self.ventas = cargar_datos(self.inventario)
        self.dinero = 0

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk(fg_color="#271944")
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.ventana.title("RecreoLab | Demostración escolar")
        self.ventana.geometry("1080x740")
        self.ventana.minsize(960, 660)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(2, weight=1)

        # Al entrar al programa se pide el dinero disponible para gastar.
        self.pedir_dinero()

        titulo = ctk.CTkLabel(self.ventana, text="🏪 RecreoLab",
            font=("Arial", 30, "bold"))
        titulo.grid(row=0, column=0, padx=16, pady=(18, 0))

        subtitulo = ctk.CTkLabel(self.ventana,
            text="¿Qué comprás con tu presupuesto?",
            font=("Arial", 15), text_color="#9aa0a6")
        subtitulo.grid(row=1, column=0, padx=16, pady=(0, 12))

        self.tabs = ctk.CTkTabview(self.ventana,fg_color="#271944", corner_radius=12)
        self.tabs.grid(row=2, column=0, padx=16, pady=8,
                        sticky="nsew")
        self.tabs.add("🏪 Kiosco")
        self.tabs.add("💰 Presupuesto")
        self.tabs.add("🛠 Administración")

        self.armar_pestania_kiosco()
        self.armar_pestania_presupuesto()
        self.armar_pestania_administracion()

        barra_resumen = ctk.CTkFrame(self.ventana, fg_color="#1b2230",
            corner_radius=12)
        barra_resumen.grid(row=3, column=0, padx=16, pady=(0, 16),
                            sticky="ew")
        barra_resumen.grid_columnconfigure(0, weight=1)

        self.resumen = ctk.CTkLabel(barra_resumen, text="",
            font=("Arial", 13, "bold"), text_color="#64b5f6")
        self.resumen.grid(row=0, column=0, pady=10)

        self.actualizar_pantalla()

    def pedir_dinero(self):
        dialogo = ctk.CTkInputDialog(
            text="¿Cuánto dinero tenés para gastar?\nIngresá un número entero.",
            title="💰 Dinero disponible"
        )
        texto = dialogo.get_input()

        if texto is None or texto.strip() == "":
            self.dinero = 0
            return

        try:
            dinero = int(texto.strip())
            if dinero < 0:
                raise ValueError
            self.dinero = dinero
        except ValueError:
            self.dinero = 0
            self.ventana.after(200, lambda: self.mostrar_alerta(
                "Dinero inválido",
                "No se pudo usar ese monto. El dinero disponible quedó en $0.",
                "warning"
            ))

    def armar_pestania_kiosco(self):
        panel = self.tabs.tab("🏪 Kiosco")
        panel.grid_columnconfigure((0, 1), weight=1)
        panel.grid_rowconfigure(2, weight=1)

        subtitulo_catalogo = ctk.CTkLabel(panel,
            text="Elegí un producto para agregarlo al carrito",
            font=("Arial", 14), text_color="#a0a0a0")
        subtitulo_catalogo.grid(row=0, column=0, padx=8,
                                 pady=(4, 0), sticky="w")

        subtitulo_carrito = ctk.CTkLabel(panel,
            text="🛒 Tu carrito",
            font=("Arial", 14, "bold"))
        subtitulo_carrito.grid(row=0, column=1, padx=8,
                                pady=(4, 0), sticky="w")

        # Actividad A: buscador por nombre, encima del catálogo.
        buscador = ctk.CTkFrame(panel, fg_color="transparent")
        buscador.grid(row=1, column=0, padx=8, pady=(4, 0), sticky="ew")
        buscador.grid_columnconfigure(0, weight=1)

        self.campo_busqueda = ctk.CTkEntry(buscador,
            placeholder_text="Buscar por nombre (vacío = mostrar todo)")
        self.campo_busqueda.grid(row=0, column=0, padx=(0, 8),
                                  sticky="ew")
        self.campo_busqueda.bind("<KeyRelease>",
                                 lambda evento: self.actualizar_pantalla())

        boton_buscar = ctk.CTkButton(buscador, text="🔎 Buscar",
            command=self.actualizar_pantalla, width=100)
        boton_buscar.grid(row=0, column=1)

        self.panel_catalogo = ctk.CTkScrollableFrame(panel,
            label_text="Productos")
        self.panel_catalogo.grid(row=2, column=0, padx=8, pady=8,
                                  sticky="nsew")
        self.panel_catalogo.grid_columnconfigure(0, weight=1)

        compra = ctk.CTkFrame(panel)
        compra.grid(row=2, column=1, padx=8, pady=8, sticky="nsew")
        compra.grid_columnconfigure(0, weight=1)
        compra.grid_rowconfigure(0, weight=1)

        self.caja_carrito = ctk.CTkTextbox(compra, font=("Arial", 16))
        self.caja_carrito.grid(row=0, column=0, padx=12, pady=12,
                                sticky="nsew")

        self.etiqueta_total = ctk.CTkLabel(compra, text="",
            font=("Arial", 26, "bold"), text_color="#4caf50")
        self.etiqueta_total.grid(row=1, column=0, pady=(4, 10))

        separador = ctk.CTkFrame(compra, height=2, fg_color="#3a3a3a")
        separador.grid(row=2, column=0, padx=12, pady=(0, 8),
                        sticky="ew")

        boton_quitar = ctk.CTkButton(compra,
            text="↩ Quitar última unidad",
            command=self.quitar_unidad, height=36,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"))
        boton_quitar.grid(row=3, column=0, padx=12, pady=5, sticky="ew")

        boton_vaciar = ctk.CTkButton(compra, text="🗑 Vaciar carrito",
            command=self.vaciar_carrito, height=36,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"))
        boton_vaciar.grid(row=4, column=0, padx=12, pady=5, sticky="ew")

        boton_vender = ctk.CTkButton(compra,
            text="✔ Confirmar venta simulada",
            command=self.confirmar_venta, height=40,
            fg_color="#2e7d32", hover_color="#1b5e20")
        boton_vender.grid(row=5, column=0, padx=12, pady=(10, 5),
                           sticky="ew")

    def armar_pestania_presupuesto(self):
        panel = self.tabs.tab("💰 Presupuesto")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(4, weight=1)

        titulo = ctk.CTkLabel(panel,
            text="💰 ¿Qué dos productos comprás con tu presupuesto?",
            font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, padx=12, pady=(8, 0))

        aviso = ctk.CTkLabel(panel,
            text="Pares distintos: una unidad de cada producto.\n"
                 "Consulta independiente; no reserva stock.",
            font=("Arial", 13), text_color="#a0a0a0")
        aviso.grid(row=1, column=0, padx=12, pady=6)

        self.campo_presupuesto = ctk.CTkEntry(panel,
            placeholder_text="Pesos enteros, sin puntos: ej. 3000",
            height=36)
        self.campo_presupuesto.grid(row=2, column=0, padx=12, pady=8,
                                     sticky="ew")

        boton = ctk.CTkButton(panel, text="🔎 Buscar combinaciones",
            command=self.buscar_combinaciones, height=36)
        boton.grid(row=3, column=0, padx=12, pady=8)

        self.caja_resultados = ctk.CTkTextbox(panel, font=("Arial", 16))
        self.caja_resultados.grid(row=4, column=0, padx=12, pady=8,
                                   sticky="nsew")
        self.mostrar_texto(self.caja_resultados, "Ingresá un presupuesto.")

    def armar_pestania_administracion(self):
        panel = self.tabs.tab("🛠 Administración")
        panel.grid_columnconfigure(0, weight=2)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        subtitulo_stock = ctk.CTkLabel(panel,
            text="📋 Stock actual de los 6 productos",
            font=("Arial", 14, "bold"))
        subtitulo_stock.grid(row=0, column=0, padx=8, pady=(4, 0),
                              sticky="w")

        subtitulo_form = ctk.CTkLabel(panel,
            text="📦 Reponer stock",
            font=("Arial", 14, "bold"))
        subtitulo_form.grid(row=0, column=1, padx=8, pady=(4, 0),
                             sticky="w")

        self.panel_stock = ctk.CTkScrollableFrame(panel,
            label_text="Código · Producto · Stock · Estado")
        self.panel_stock.grid(row=1, column=0, padx=8, pady=8,
                               sticky="nsew")
        self.panel_stock.grid_columnconfigure(1, weight=1)

        formulario = ctk.CTkFrame(panel, fg_color="#20242e",
            border_width=1, border_color="#3a3f4b", corner_radius=10)
        formulario.grid(row=1, column=1, padx=8, pady=8, sticky="new")
        formulario.grid_columnconfigure(0, weight=1)

        aviso_admin = ctk.CTkLabel(formulario,
            text="Uso interno / docente.\nNo lo ve el público en el stand.",
            font=("Arial", 12), text_color="#8fa3bf",
            justify="left")
        aviso_admin.grid(row=0, column=0, padx=14, pady=(14, 10),
                          sticky="w")

        self.campo_codigo_reponer = ctk.CTkEntry(formulario,
            placeholder_text="Código (ej: A06)", height=34)
        self.campo_codigo_reponer.grid(row=1, column=0, padx=14,
                                        pady=(0, 8), sticky="ew")

        self.campo_cantidad_reponer = ctk.CTkEntry(formulario,
            placeholder_text="Cantidad (entero positivo)", height=34)
        self.campo_cantidad_reponer.grid(row=2, column=0, padx=14,
                                          pady=(0, 8), sticky="ew")

        boton_reponer = ctk.CTkButton(formulario, text="➕ Reponer stock",
            command=self.reponer, height=38,
            fg_color="#455a75", hover_color="#374863")
        boton_reponer.grid(row=3, column=0, padx=14, pady=(4, 14),
                            sticky="ew")

    def mostrar_alerta(self, titulo, mensaje, tipo="info"):
        ventana = ctk.CTkToplevel(self.ventana)
        ventana.title(titulo)
        ventana.geometry("420x220")
        ventana.resizable(False, False)
        ventana.grab_set()

        if tipo == "error":
            icono = "❌"
            color = "#b3261e"
        elif tipo == "warning":
            icono = "⚠️"
            color = "#b5651d"
        else:
            icono = "✅"
            color = "#2e7d32"

        encabezado = ctk.CTkFrame(ventana, fg_color=color, corner_radius=0)
        encabezado.pack(fill="x")

        ctk.CTkLabel(encabezado, text=icono,
                     font=("Arial", 30)).pack(pady=(10, 0))
        ctk.CTkLabel(encabezado, text=titulo,
                     font=("Arial", 17, "bold"),
                     text_color="white").pack(pady=(0, 10))

        ctk.CTkLabel(ventana, text=mensaje,
                     font=("Arial", 14),
                     wraplength=370).pack(pady=18)

        ctk.CTkButton(ventana, text="Aceptar",
                      command=ventana.destroy,
                      width=120).pack(pady=(0, 15))

    def mostrar_texto(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def actualizar_pantalla(self):
        for widget in self.panel_catalogo.winfo_children():
            widget.destroy()

        # Ampliación · semáforo con colores: el estado (y su color)
        # depende de producto.stock, que solo cambia al confirmar
        # una venta simulada (sumar_al_carrito no lo modifica).
        # Actividad A: filtro por nombre, sin tocar self.inventario.
        texto_busqueda = self.campo_busqueda.get().strip().lower()

        fila = 0
        coincidencias = 0
        for producto in self.inventario:
            if texto_busqueda and texto_busqueda not in producto.nombre.lower():
                continue
            coincidencias += 1

            if producto.stock == 0:
                estado, icono, color, color_hover = (
                    "Agotado", "❌", "#5c5c5c", "#5c5c5c")
            elif producto.stock <= 2:
                estado, icono, color, color_hover = (
                    "Reponer", "⚠️", "#b5651d", "#8a4d15")
            else:
                estado, icono, color, color_hover = (
                    "Disponible", "✅", "#2e7d32", "#1b5e20")

            tarjeta = ctk.CTkFrame(self.panel_catalogo, fg_color=color,
                corner_radius=10)
            tarjeta.grid(row=fila, column=0, padx=8, pady=6,
                         sticky="ew")
            tarjeta.grid_columnconfigure(0, weight=1)

            etiqueta_nombre = ctk.CTkLabel(tarjeta,
                text=f"{producto.nombre} · {formatear_precio(producto.precio)}",
                font=("Arial", 16, "bold"), anchor="w",
                text_color="white")
            etiqueta_nombre.grid(row=0, column=0, padx=14, pady=(10, 2),
                                  sticky="ew")

            etiqueta_estado = ctk.CTkLabel(tarjeta,
                text=f"Stock: {producto.stock}  {icono} {estado}",
                font=("Arial", 11), anchor="w",
                text_color="#e8e8e8")
            etiqueta_estado.grid(row=1, column=0, padx=14, pady=(0, 10),
                                  sticky="ew")

            if estado == "Agotado":
                etiqueta_nombre.configure(text_color="#bbbbbb")
                etiqueta_estado.configure(text_color="#bbbbbb")
            else:
                for widget in (tarjeta, etiqueta_nombre, etiqueta_estado):
                    widget.configure(cursor="hand2")
                    widget.bind("<Button-1>",
                        partial(self.al_tocar_producto, producto.codigo))
                    widget.bind("<Enter>",
                        partial(self.resaltar_tarjeta, tarjeta, color_hover))
                    widget.bind("<Leave>",
                        partial(self.resaltar_tarjeta, tarjeta, color))

            fila += 1

        if texto_busqueda and coincidencias == 0:
            aviso_busqueda = ctk.CTkLabel(self.panel_catalogo,
                text=f"No hay productos que coincidan con «{texto_busqueda}».")
            aviso_busqueda.grid(row=0, column=0, padx=8, pady=12)

        # Administración: lista de solo lectura con el stock real de
        # los 6 productos, con estilo propio (filas alternadas), bien
        # distinto de las tarjetas grandes y clickeables del Kiosco.
        for widget in self.panel_stock.winfo_children():
            widget.destroy()

        for fila_stock, producto in enumerate(self.inventario):
            if producto.stock == 0:
                estado_admin, icono_admin = "Agotado", "❌"
            elif producto.stock <= 2:
                estado_admin, icono_admin = "Reponer", "⚠️"
            else:
                estado_admin, icono_admin = "Disponible", "✅"

            color_fila = "#1c1f27" if fila_stock % 2 == 0 else "#242832"
            renglon = ctk.CTkFrame(self.panel_stock, fg_color=color_fila,
                corner_radius=6)
            renglon.grid(row=fila_stock, column=0, padx=2, pady=2,
                         sticky="ew")
            renglon.grid_columnconfigure(1, weight=1)

            etiqueta_codigo = ctk.CTkLabel(renglon, text=producto.codigo,
                font=("Consolas", 12, "bold"), text_color="#7f8ea3",
                width=48, anchor="w")
            etiqueta_codigo.grid(row=0, column=0, padx=(10, 6), pady=8,
                                  sticky="w")

            etiqueta_producto = ctk.CTkLabel(renglon,
                text=f"{producto.nombre} · {formatear_precio(producto.precio)}",
                font=("Arial", 13), anchor="w")
            etiqueta_producto.grid(row=0, column=1, padx=6, pady=8,
                                    sticky="w")

            etiqueta_stock_admin = ctk.CTkLabel(renglon,
                text=f"Stock: {producto.stock}  {icono_admin} {estado_admin}",
                font=("Arial", 12, "bold"), anchor="e")
            etiqueta_stock_admin.grid(row=0, column=2, padx=(6, 10),
                                       pady=8, sticky="e")

        # Ampliación · carrito agrupado por producto, con la cantidad
        # y el subtotal, en vez de repetir una línea por unidad.
        renglones = []
        for producto in self.inventario:
            cantidad = unidades_en_carrito(self.carrito, producto.codigo)
            if cantidad == 0:
                continue
            subtotal = producto.precio * cantidad
            if cantidad == 1:
                renglones.append(
                    f"{producto.nombre}: {formatear_precio(producto.precio)}")
            else:
                renglones.append(
                    f"{producto.nombre} × {cantidad} = "
                    f"{formatear_precio(subtotal)}")

        texto_carrito = ("\n".join(renglones) if renglones else
            "El carrito está vacío.\nElegí un producto de la izquierda.")
        self.mostrar_texto(self.caja_carrito, texto_carrito)

        self.etiqueta_total.configure(
            text=f"Total: {formatear_precio(calcular_total(self.carrito))}")

        importe_total = sum(self.ventas)
        self.resumen.configure(
            text=f"💰 Dinero disponible: {formatear_precio(self.dinero)}  |  "
                 f"🧾 Ventas: {len(self.ventas)}  |  "
                 f"Importe vendido: {formatear_precio(importe_total)}")

    def al_tocar_producto(self, codigo, event=None):
        self.agregar_producto(codigo)

    def resaltar_tarjeta(self, tarjeta, color, event=None):
        tarjeta.configure(fg_color=color)

    def agregar_producto(self, codigo):
        producto = None
        for articulo in self.inventario:
            if articulo.codigo == codigo:
                producto = articulo
                break

        if producto is None:
            return

        total_actual = calcular_total(self.carrito)
        if total_actual + producto.precio > self.dinero:
            falta = total_actual + producto.precio - self.dinero
            self.mostrar_alerta(
                "💰 Dinero insuficiente",
                f"No podés agregar {producto.nombre}.\n"
                f"Te faltan {formatear_precio(falta)} para comprarlo.",
                "warning"
            )
            return

        try:
            sumar_al_carrito(self.inventario, self.carrito, codigo)
        except ValueError as error:
            self.mostrar_alerta("Revisá la compra", str(error), "warning")
        self.actualizar_pantalla()

    def quitar_unidad(self):
        if self.carrito:
            self.carrito.pop()
        self.actualizar_pantalla()

    def vaciar_carrito(self):
        self.carrito.clear()
        self.actualizar_pantalla()

    def confirmar_venta(self):
        if not self.carrito:
            self.mostrar_alerta("Carrito vacío", "Agregá un producto.", "warning")
            return

        total = calcular_total(self.carrito)
        if total > self.dinero:
            self.mostrar_alerta(
                "💰 Dinero insuficiente",
                f"El carrito cuesta {formatear_precio(total)} y solo tenés "
                f"{formatear_precio(self.dinero)} disponibles.",
                "warning"
            )
            return

        acepta = messagebox.askyesno("Confirmar",
            "¿Registrar esta venta simulada?", parent=self.ventana)
        if not acepta:
            return

        try:
            total = registrar_venta(self.carrito, self.ventas)
        except ValueError as error:
            self.mostrar_alerta("No se registró", str(error), "error")
            return

        self.dinero -= total
        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_texto(self.caja_resultados,
            "Cambió el stock. Volvé a buscar combinaciones.")

        if self.dinero == 0:
            self.mostrar_alerta(
                "🎉 Dinero agotado",
                "Ya no te queda dinero para gastar.\n"
                "¡Terminaste tu presupuesto!",
                "info"
            )
        else:
            self.mostrar_alerta(
                "✅ Venta registrada",
                f"Total: {formatear_precio(total)}\n"
                f"Te quedan {formatear_precio(self.dinero)} para gastar.",
                "info"
            )

    def reponer(self):
        codigo = self.campo_codigo_reponer.get().strip().upper()
        texto_cantidad = self.campo_cantidad_reponer.get().strip()

        try:
            cantidad = int(texto_cantidad)
        except ValueError:
            self.mostrar_alerta(
                "Reposición inválida",
                "La cantidad debe ser un número entero positivo.",
                "warning"
            )
            return

        try:
            reponer_stock(self.inventario, codigo, cantidad)
        except ValueError as error:
            self.mostrar_alerta("Reposición inválida", str(error), "warning")
            return

        guardar_datos(self.inventario, self.ventas)
        self.actualizar_pantalla()
        self.mostrar_texto(self.caja_resultados,
            "Cambió el stock. Volvé a buscar combinaciones.")
        self.mostrar_alerta(
            "Stock actualizado",
            f"Se repusieron {cantidad} unidades de {codigo}.",
            "info"
        )

    def buscar_combinaciones(self):
        try:
            texto = self.campo_presupuesto.get().strip()
            presupuesto = int(texto)
            opciones = combinaciones_posibles(self.inventario, presupuesto)
        except ValueError:
            self.mostrar_alerta(
                "Presupuesto inválido",
                "Ingresá un número entero mayor que 0, sin puntos ni decimales.",
                "warning"
            )
            return

        if not opciones:
            self.mostrar_texto(self.caja_resultados,
                "No hay pares disponibles.")
            return

        # Actividad E: combinaciones_posibles ya las devuelve ordenadas
        # de menor a mayor sobrante; acá solo aclaramos qué significa
        # ese orden, para no sugerir que es "la mejor compra posible".
        renglones = [
            f"{primero} + {segundo}: {formatear_precio(total)} | "
            f"Sobran {formatear_precio(sobra)}"
            for primero, segundo, total, sobra in opciones
        ]
        resultado = ("Menor sobrante entre estos pares (no es "
                      "necesariamente la mejor compra para cualquier "
                      "necesidad):\n\n" + "\n".join(renglones))
        self.mostrar_texto(self.caja_resultados, resultado)

    def cerrar(self):
        guardar_datos(self.inventario, self.ventas)
        self.ventana.destroy()

    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    Aplicacion().ejecutar()
