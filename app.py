import customtkinter as ctk
from tkinter import messagebox
from functools import partial

from modelo import (catalogo_inicial, agregar, confirmar,
                     total_carrito, sugerir_pares, cantidad_en_carrito)


class Aplicacion:
    def __init__(self):
        self.productos = catalogo_inicial()
        self.carrito = []
        self.ventas = []

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.title("RecreoLab | Demostración escolar")
        self.ventana.geometry("1050x700")
        self.ventana.minsize(950, 640)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)

        titulo = ctk.CTkLabel(self.ventana,
            text="🏪 RecreoLab · ¿Qué comprás con tu presupuesto?",
            font=("Arial", 24, "bold"))
        titulo.grid(row=0, column=0, padx=16, pady=12)

        self.tabs = ctk.CTkTabview(self.ventana)
        self.tabs.grid(row=1, column=0, padx=16, pady=8,
                        sticky="nsew")
        self.tabs.add("Kiosco")
        self.tabs.add("Presupuesto")

        self.crear_kiosco()
        self.crear_presupuesto()

        self.resumen = ctk.CTkLabel(self.ventana, text="",
            font=("Arial", 13, "bold"), text_color="#64b5f6")
        self.resumen.grid(row=2, column=0, pady=10)

        self.refrescar()

    def crear_kiosco(self):
        panel = self.tabs.tab("Kiosco")
        panel.grid_columnconfigure((0, 1), weight=1)
        panel.grid_rowconfigure(1, weight=1)

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

        self.catalogo = ctk.CTkScrollableFrame(panel,
            label_text="Productos")
        self.catalogo.grid(row=1, column=0, padx=8, pady=8,
                            sticky="nsew")
        self.catalogo.grid_columnconfigure(0, weight=1)

        compra = ctk.CTkFrame(panel)
        compra.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        compra.grid_columnconfigure(0, weight=1)
        compra.grid_rowconfigure(0, weight=1)

        self.detalle = ctk.CTkTextbox(compra, font=("Arial", 16))
        self.detalle.grid(row=0, column=0, padx=12, pady=12,
                           sticky="nsew")

        self.total = ctk.CTkLabel(compra, text="",
            font=("Arial", 26, "bold"), text_color="#4caf50")
        self.total.grid(row=1, column=0, pady=(4, 10))

        separador = ctk.CTkFrame(compra, height=2, fg_color="#3a3a3a")
        separador.grid(row=2, column=0, padx=12, pady=(0, 8),
                        sticky="ew")

        boton_quitar = ctk.CTkButton(compra,
            text="↩ Quitar última unidad",
            command=self.quitar, height=36,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"))
        boton_quitar.grid(row=3, column=0, padx=12, pady=5, sticky="ew")

        boton_vaciar = ctk.CTkButton(compra, text="🗑 Vaciar carrito",
            command=self.vaciar, height=36,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"))
        boton_vaciar.grid(row=4, column=0, padx=12, pady=5, sticky="ew")

        boton_vender = ctk.CTkButton(compra,
            text="✔ Confirmar venta simulada",
            command=self.vender, height=40,
            fg_color="#2e7d32", hover_color="#1b5e20")
        boton_vender.grid(row=5, column=0, padx=12, pady=(10, 5),
                           sticky="ew")

    def crear_presupuesto(self):
        panel = self.tabs.tab("Presupuesto")
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

        self.presupuesto = ctk.CTkEntry(panel,
            placeholder_text="Pesos enteros, sin puntos: 2000",
            height=36)
        self.presupuesto.grid(row=2, column=0, padx=12, pady=8,
                               sticky="ew")

        boton = ctk.CTkButton(panel, text="🔎 Buscar combinaciones",
            command=self.sugerir, height=36)
        boton.grid(row=3, column=0, padx=12, pady=8)

        self.opciones = ctk.CTkTextbox(panel, font=("Arial", 16))
        self.opciones.grid(row=4, column=0, padx=12, pady=8,
                            sticky="nsew")
        self.escribir(self.opciones, "Ingresá un presupuesto.")

    def escribir(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def refrescar(self):
        for widget in self.catalogo.winfo_children():
            widget.destroy()

        # Actividad B: semáforo con colores. El estado (y su color)
        # depende de producto.stock, que solo cambia al confirmar
        # una venta simulada (agregar() no lo modifica).
        for fila, producto in enumerate(self.productos):
            estado = "Disponible"
            if producto.stock == 0:
                estado = "Agotado"
            elif producto.stock <= 2:
                estado = "Reponer"

            icono = {"Disponible": "✅", "Reponer": "⚠️",
                      "Agotado": "❌"}[estado]

            if estado == "Agotado":
                color_fondo = "#5c5c5c"
            elif estado == "Reponer":
                color_fondo = "#b5651d"
            else:
                color_fondo = "#2e7d32"

            tarjeta = ctk.CTkFrame(self.catalogo, fg_color=color_fondo,
                corner_radius=8)
            tarjeta.grid(row=fila, column=0, padx=8, pady=5,
                         sticky="ew")
            tarjeta.grid_columnconfigure(0, weight=1)

            nombre = ctk.CTkLabel(tarjeta,
                text=f"{producto.nombre} · ${producto.precio}",
                font=("Arial", 16, "bold"), anchor="w",
                text_color="white")
            nombre.grid(row=0, column=0, padx=14, pady=(10, 2),
                        sticky="ew")

            estado_label = ctk.CTkLabel(tarjeta,
                text=f"Stock: {producto.stock}  {icono} {estado}",
                font=("Arial", 11), anchor="w",
                text_color="#e8e8e8")
            estado_label.grid(row=1, column=0, padx=14, pady=(0, 10),
                              sticky="ew")

            if estado == "Agotado":
                nombre.configure(text_color="#bbbbbb")
                estado_label.configure(text_color="#bbbbbb")
            else:
                for widget in (tarjeta, nombre, estado_label):
                    widget.configure(cursor="hand2")
                    widget.bind("<Button-1>",
                        partial(self.click_producto, producto.codigo))

        # Actividad C: agrupar el carrito por producto en vez de
        # repetir una línea por unidad.
        lineas = []
        for producto in self.productos:
            cantidad = cantidad_en_carrito(self.carrito, producto.codigo)
            if cantidad == 0:
                continue
            subtotal = producto.precio * cantidad
            if cantidad == 1:
                lineas.append(f"{producto.nombre}: ${producto.precio}")
            else:
                lineas.append(
                    f"{producto.nombre} × {cantidad} = ${subtotal}")
        self.escribir(self.detalle, "\n".join(lineas) if lineas
            else "El carrito está vacío.\nElegí un producto de la izquierda.")

        self.total.configure(text=f"Total: ${total_carrito(self.carrito)}")

        importe = sum(self.ventas)
        self.resumen.configure(text=f"Ventas de esta sesión: "
            f"{len(self.ventas)} | Importe vendido: ${importe}")

    def click_producto(self, codigo, event=None):
        self.agregar_uno(codigo)

    def agregar_uno(self, codigo):
        try:
            agregar(self.productos, self.carrito, codigo)
        except ValueError as error:
            messagebox.showwarning("Revisá la compra", str(error),
                parent=self.ventana)
        self.refrescar()

    def quitar(self):
        if self.carrito:
            self.carrito.pop()
        self.refrescar()

    def vaciar(self):
        self.carrito.clear()
        self.refrescar()

    def vender(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío",
                "Agregá un producto.", parent=self.ventana)
            return

        acepta = messagebox.askyesno("Confirmar",
            "¿Registrar esta venta simulada?", parent=self.ventana)
        if not acepta:
            return

        try:
            total = confirmar(self.carrito, self.ventas)
        except ValueError as error:
            messagebox.showerror("No se registró", str(error),
                parent=self.ventana)
            return

        self.refrescar()
        self.escribir(self.opciones,
            "Cambió el stock. Volvé a buscar combinaciones.")
        messagebox.showinfo("Venta simulada registrada",
            f"Total: ${total}\nComprobante sin validez fiscal.",
            parent=self.ventana)

    def sugerir(self):
        try:
            texto = self.presupuesto.get().strip()
            presupuesto = int(texto)
            if presupuesto > 1000000:
                raise ValueError("Usá hasta 1000000 pesos.")
            opciones = sugerir_pares(self.productos, presupuesto)
        except ValueError:
            messagebox.showwarning("Presupuesto inválido",
                "Ingresá entre 1 y 1000000, sin puntos ni decimales.",
                parent=self.ventana)
            return

        lineas = []
        for primero, segundo, total, sobra in opciones:
            lineas.append(f"{primero} + {segundo}: ${total} "
                f"| Sobran ${sobra}")
        resultado = "\n".join(lineas) or "No hay pares disponibles."
        self.escribir(self.opciones, resultado)

    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    Aplicacion().ejecutar()
