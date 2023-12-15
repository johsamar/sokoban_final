import tkinter as tk
from tkinter import filedialog
from utils.config import PROJECT_PATH
import random
from helpers.constants import Constans

class SeleccionAlgoritmoApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Selección de Algoritmo")

        # Lista de opciones tipos de algoritmos
        self.opciones = ["Seleccione un algoritmo", Constans.NO_INFORMADO, Constans.INFORMADO]
        self.variable = tk.StringVar(root)
        self.variable.set(self.opciones[0])

        # Lista de opciones de algoritmos no informados
        self.opciones_no_informados = ["Seleccione un algoritmo no informado", Constans.DFS, Constans.BFS, Constans.UNIFORM_COST]
        self.variable_no_informados = tk.StringVar(root)
        self.variable_no_informados.set(self.opciones[0])

         # Lista de opciones de algoritmos no informados
        self.opciones_informados = ["Seleccione un algoritmo informado", Constans.BEAM_SEARCH, Constans.A_STAR, Constans.HILL_CLIMBING]
        self.variable_informados = tk.StringVar(root)
        self.variable_informados.set(self.opciones[0])

        # Lista de opciones de heurísticas
        self.opciones_heuristica = ["Seleccione una heurística", Constans.MANHATTAN, Constans.EUCLIDEAN]
        self.variable_heuristica = tk.StringVar(root)
        self.variable_heuristica.set(self.opciones_heuristica[0])

        # Crear menú desplegable algoritmos
        self.menu = tk.OptionMenu(root, self.variable, *self.opciones)
        self.menu.pack()

        # Crear menú desplegable algoritmos no informados (inicialmente deshabilitado)
        self.menu_no_informados = tk.OptionMenu(root, self.variable_no_informados, *self.opciones_no_informados)
        self.menu_no_informados.pack()
        self.menu_no_informados.config(state=tk.DISABLED)

        # Crear menú desplegable algoritmos informados (inicialmente deshabilitado)
        self.menu_informados = tk.OptionMenu(root, self.variable_informados, *self.opciones_informados)
        self.menu_informados.pack()
        self.menu_informados.config(state=tk.DISABLED)
        
        # Crear menú desplegable heurísticas (inicialmente deshabilitado)
        self.menu_heuristica = tk.OptionMenu(root, self.variable_heuristica, *self.opciones_heuristica)
        self.menu_heuristica.pack()
        self.menu_heuristica.config(state=tk.DISABLED)

        # Vincular la función de habilitar_heuristica a los cambios en el menú de algoritmos
        self.variable.trace_add("write", self.habilitar_heuristica)

        # Botón para confirmar selección de algoritmo
        self.boton_seleccionar = tk.Button(root, text="Seleccionar", command=self.seleccionar_algoritmo)
        self.boton_seleccionar.pack()
        
       

        # Crear menú desplegable para elegir entre cargar archivo o escribir mapa
        opciones_opcion = ["Cargar Archivo", "Escribir Mapa"]
        self.variable_opcion = tk.StringVar(root)
        self.variable_opcion.set(opciones_opcion[0])
        menu_opcion = tk.OptionMenu(root, self.variable_opcion, *opciones_opcion, command=self.seleccionar_opcion)
        menu_opcion.pack()

        # Etiqueta para mostrar la ruta del archivo seleccionado
        self.label_ruta = tk.Label(root, text="")
        self.label_ruta.pack()

        # Cuadro de texto para ingresar el mapa manualmente (inicialmente deshabilitado)
        self.textbox_mapa = tk.Text(root, height=10, width=50)
        self.textbox_mapa.pack_forget()

        # Botón para continuar
        self.boton_continuar = tk.Button(root, text="Continuar", command=self.continuar_sokoban)
        self.boton_continuar.pack()

        # Variable para almacenar la instancia de la ventana de datos
        self.ventana_datos = None
        # Inicializar heuristica_seleccionada
        self.heuristica_seleccionada = None
        # Inicializar variable_algoritmo
        self.variable_algoritmo = tk.StringVar()

    def habilitar_heuristica(self, *args):
        if self.variable.get() == Constans.INFORMADO:
            self.menu_heuristica.config(state=tk.NORMAL)
            self.menu_no_informados.config(state=tk.DISABLED)
            self.menu_informados.config(state=tk.NORMAL)
            self.heuristica_seleccionada = self.variable_heuristica.get()  # Actualizar el valor de heuristica_seleccionada

        else:
            self.menu_heuristica.config(state=tk.DISABLED)
            self.menu_no_informados.config(state=tk.NORMAL)
            self.menu_informados.config(state=tk.DISABLED)

    def seleccionar_opcion(self,_):
        opcion = self.variable_opcion.get()

        if opcion == "Cargar Archivo":
            ruta_archivo = self.cargar_mapa_desde_archivo()
            self.label_ruta.config(text="Ruta del Archivo: " + ruta_archivo)
            self.textbox_mapa.pack_forget()  # Olvidar el cuadro de texto
        elif opcion == "Escribir Mapa":
            self.label_ruta.config(text="")
            self.textbox_mapa.pack()  # Mostrar el cuadro de texto
        

    def cargar_mapa_desde_archivo(self):
        # Seleccionar un archivo utilizando un cuadro de diálogo
        filename = filedialog.askopenfilename(initialdir=PROJECT_PATH, title="Seleccionar archivo de mapa")
        return filename

    def guardar_mapa_en_archivo(self, contenido):
        # Guardar el contenido en un archivo .txt con un número aleatorio como nombre
        filename = "mapa_" + str(random.randint(0, 1000000)) + ".txt"
        with open(filename, 'w') as file:
            file.write(contenido)
        return filename


    def continuar_sokoban(self):
        # Si se seleccionó una ruta de archivo, se carga el mapa desde el archivo
        if self.label_ruta.cget("text") != "":
            self.filename = self.label_ruta.cget("text").split(": ")[1]
        # Si se seleccionó escribir el mapa, se guarda el mapa en un archivo y se carga desde el archivo
        else:
            self.filename = self.guardar_mapa_en_archivo(self.textbox_mapa.get("1.0", tk.END))
        
        if self.variable.get() == "Algoritmo Informado":
            self.algoritmo_seleccionado = self.variable_informados.get()
        else:
            self.algoritmo_seleccionado = self.variable_no_informados.get()

        #cerrar ventana
        self.root.destroy()
        
    def seleccionar_algoritmo(self):
        self.algoritmo_seleccionado = self.variable_algoritmo.get()  # Obtener la opción seleccionada del algoritmo
        self.heuristica_seleccionada = self.variable_heuristica.get()  # Obtener la opción seleccionada de la heurística

    def getValores(self):
        return self.algoritmo_seleccionado, self.filename, self.heuristica_seleccionada

    def run(self):
        self.root.geometry("600x400")
        self.root.mainloop()

    