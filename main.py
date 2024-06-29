"""-----------------------------------------------------------------------Bali-dator-------------------------------------------------------------"""

# Importar las bibliotecas necesarias
import tkinter as tk  # Importar la biblioteca tkinter para la interfaz gráfica
from tkinter import messagebox  # Importar el módulo messagebox de tkinter para mostrar mensajes
import ttkbootstrap as ttk  # Importar ttkbootstrap para estilos de widgets

# Definir la clase de la aplicación MaterialPerformanceApp
class MaterialPerformanceApp:
    def __init__(self, root):
        self.root = root  # Asignar la ventana principal a self.root
        self.root.title("Bali-dator")  # Establecer el título de la ventana
        self.root.iconbitmap('C:/Users/mfern/OneDrive/Escritorio/Balidator/icon.ico')  # Establecer el icono de la ventana
        self.create_widgets()  # Llamar al método para crear los widgets

    def create_widgets(self):
        # Crear un marco dentro de la ventana principal
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, padx=10, pady=10)  # Ajustar el marco en la cuadrícula
        
        # Etiquetas y campos de entrada para ingresar datos
        ttk.Label(frame, text="Cantidad de Granel Ingresado:").grid(row=0, column=0, padx=10, pady=10)
        self.material_ingresado = ttk.Entry(frame)
        self.material_ingresado.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Cantidad de Granel Devuelto:").grid(row=1, column=0, padx=10, pady=10)
        self.material_devuelto = ttk.Entry(frame)
        self.material_devuelto.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Cantidad de blisters Producida:").grid(row=2, column=0, padx=10, pady=10)
        self.cantidad_producida = ttk.Entry(frame)
        self.cantidad_producida.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(frame, text="Dosis X Blister:").grid(row=3, column=0, padx=10, pady=10)
        self.dosis = ttk.Entry(frame)
        self.dosis.grid(row=3, column=1, padx=10, pady=10)

        # Botón para calcular el rendimiento con su correspondiente comando y estilo
        ttk.Button(frame, text="Calcular Rendimiento", command=self.calcular_rendimiento, style="success.TButton").grid(row=4, columnspan=2, pady=20)

    def calcular_rendimiento(self):
        try:
            # Obtener los valores de los campos de entrada o establecerlos a 0 si están vacíos
            material_ingresado = float(self.material_ingresado.get()) if self.material_ingresado.get() else 0
            material_devuelto = float(self.material_devuelto.get()) if self.material_devuelto.get() else 0
            cantidad_producida = float(self.cantidad_producida.get()) if self.cantidad_producida.get() else 0
            dosis = float(self.dosis.get()) if self.dosis.get() else 0
            
            # Validaciones de los valores ingresados
            if material_ingresado <= 0 or material_devuelto < 0 or dosis < 0:
                raise ValueError("No se permiten valores negativos, y el granel ingresado no puede ser 0(cero)")
            if material_devuelto >= material_ingresado:
                raise ValueError("La cantidad de Granel devuelto no puede ser mayor o igual a la cantidad ingresada")
            
            # Calcular el material utilizado y el rendimiento
            material_utilizado = material_ingresado - material_devuelto
            rendimiento = ((cantidad_producida * dosis) / material_utilizado) * 100
            
            # Validar que el rendimiento esté dentro del rango permitido
            if rendimiento > 100 or rendimiento <= 0:
                raise ValueError("El rendimiento no puede ser mayor a 100 o menor a 0(cero)")
            
            # Mostrar el resultado del rendimiento en un cuadro de mensaje
            messagebox.showinfo("Rendimiento de Utilización", f"Rendimiento: {rendimiento:.2f}%")
        except ValueError as e:
            # Capturar errores de valor y mostrar un cuadro de mensaje de error
            messagebox.showerror("Error", str(e))

# Punto de entrada principal del programa
if __name__ == "__main__":
    # Crear la ventana principal utilizando ttkbootstrap con un tema específico
    root = ttk.Window(themename="minty")
    
    root.config(bg='#004d33')  # Establecer el color de fondo de la ventana
    
    app = MaterialPerformanceApp(root)  # Crear una instancia de la aplicación MaterialPerformanceApp
    root.mainloop()  # Iniciar el bucle principal de la interfaz gráfica
