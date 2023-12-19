import tkinter as tk
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model.model import SokobanModel
from mesa.visualization.UserParam import UserParam
from mesa.visualization.modules import TextElement
from helpers.window import SeleccionAlgoritmoApp
import os 
from utils.config import PROJECT_PATH
from helpers.constants import Constans

class ViewElement(TextElement):
    
    def __init__(self):
        pass

    def algoritmo_render(self, model):
        return "Algoritmo seleccionado: " + model.algorithm
    
    def heuristic_render(self, model):
        return "Heuristica seleccionada: " + model.heuristic

def agent_portrayal(agent):
    portrayal = {
        "Shape": agent.image if hasattr(agent, 'image') else "circle",
        "Filled": "true",
        "r": 0.9,
        "Color": agent.color,
        "Layer": agent.layer,
        "text": agent.text if hasattr(agent, 'text') else ""
    }
    return portrayal

# Ventana para seleccionar el algoritmo y la heuristica
# root = tk.Tk()
# vantana = SeleccionAlgoritmoApp(root)
# vantana.run()
# algoritmo_seleccionado, filename, heuristica_seleccionada =  vantana.getValores()
# ----------------------------------------------

filename = os.path.join(PROJECT_PATH, "maps/map3.txt") #MAP 3 ES EL DELPROFESOR, MAPA 4 SUSTENTACION
algoritmo_seleccionado = Constans.HILL_CLIMBING
heuristica_seleccionada = Constans.MANHATTAN

model = SokobanModel(filename=filename)
grid = CanvasGrid(agent_portrayal, model.grid.width, model.grid.height, 500, 500)

#grid = CanvasGrid(agent_portrayal, width, height, 500, 500) 

# Crear el servidor con el modelo Sokoban y la cuadrícula
server = ModularServer(
    SokobanModel,
    [grid, ViewElement()],
    "Sokoban Model",
    {       
        "algorithm": algoritmo_seleccionado,
        "heuristic": heuristica_seleccionada,
        "filename": filename  # Nombre del archivo del mapa
    }
)
server.port = 8521
server.launch()


    
