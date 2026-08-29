import customtkinter as ctk
from tkinter import messagebox
from functools import partial

from modelo import (catalogo_inicial, agregar, total_carrito,
                     sugerir_pares, cantidad_en_carrito)


class Aplicacion:
    def __init__(self):
        self.productos = catalogo_inicial()
        self.carrito = []

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.title("RecreoLab | Primera etapa")
        self.ventana.geometry("1050x680")
        self.ventana.minsize(950, 620)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkLabel(self.ventana,
            text="🏪 RecreoLab",
            font=("Arial", 26, "bold"))
        encabezado.grid(row=0, column=0, padx=20, pady=(16, 0),
                         sticky="w")

        self.tabs = ctk.CTkTabview(self.ventana)
        self.tabs.grid(row=1, column=0, padx=16, pady=16,
                        sticky="nsew")
        self.tabs.add("Kiosco")
        self.tabs.add("Presupuesto")

        self.crear_kiosco()
        self.crear_presupuesto()

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

        acciones = [("↩ Quitar última unidad", self.quitar),
                    ("🗑 Vaciar carrito", self.vaciar)]
        for fila, (texto, accion) in enumerate(acciones, start=3):
            boton = ctk.CTkButton(compra, text=texto,
                command=accion, height=36,
                fg_color="transparent", border_width=1,
                text_color=("gray10", "gray90"))
            boton.grid(row=fila, column=0, padx=12, pady=5,
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
            placeholder_text="Pesos enteros, sin puntos: 1500",
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

        for fila, producto in enumerate(self.productos):
            estado = "Disponible"
            if producto.stock == 0:
                estado = "Agotado"
            elif producto.stock <= 2:
                estado = "Reponer"

            icono = {"Disponible": "✅", "Reponer": "⚠️",
                      "Agotado": "❌"}[estado]
            texto = (f"{producto.nombre} · ${producto.precio}\n"
                     f"Stock: {producto.stock}  {icono} {estado}")
            boton = ctk.CTkButton(self.catalogo, text=texto,
                height=64, anchor="w",
                command=partial(self.agregar_uno, producto.codigo))
            boton.grid(row=fila, column=0, padx=8, pady=5,
                       sticky="ew")

            if estado == "Agotado":
                boton.configure(state="disabled",
                    fg_color="#5c5c5c", hover_color="#5c5c5c")
            elif estado == "Reponer":
                boton.configure(fg_color="#b5651d",
                    hover_color="#8a4d15")
            else:
                boton.configure(fg_color="#2e7d32",
                    hover_color="#1b5e20")

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
        texto_carrito = ("\n".join(lineas) if lineas
                          else "El carrito está vacío.\n"
                               "Elegí un producto de la izquierda.")
        self.escribir(self.detalle, texto_carrito)

        self.total.configure(text=f"Total: ${total_carrito(self.carrito)}")

    def agregar_uno(self, codigo):
        try:
            agregar(self.productos, self.carrito, codigo)
        except ValueError as error:
            messagebox.showwarning("Revisá la compra", str(error),
                parent=self.ventana)
        self.refrescar()

    def quitar(self):
        if self.carrito:
            producto = self.carrito.pop()
            producto.stock += 1
        self.refrescar()

    def vaciar(self):
        for producto in self.carrito:
            producto.stock += 1
        self.carrito.clear()
        self.refrescar()

    def sugerir(self):
        try:
            texto = self.presupuesto.get().strip()
            presupuesto = int(texto)
            if presupuesto > 1500:
                raise ValueError("Usá hasta 1500 pesos.")
            opciones = sugerir_pares(self.productos, presupuesto)
        except ValueError:
            messagebox.showwarning("Presupuesto inválido",
                "Ingresá entre 1 y 1500, sin puntos ni decimales.",
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
