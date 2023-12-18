from mesa import Model
from agent.robot_agent import RobotAgent
from agent.rock_agent import RockAgent
from agent.path_agent import PathAgent
from agent.box_agent import BoxAgent
from agent.finish_agent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from utils.readfile import read_map
from queue import Queue, PriorityQueue
from helpers.load_agents import load_agents, calculate_all_heristic
from helpers.constants import Constans
import numpy as np
from utils.config import get_index
from helpers.game_state import GameState
class SokobanModel(Model):

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)

        # Los flags de finalización y éxito
        self.finished = False
        self.found = False

        self.filename = filename

        # Carga el mapa
        self.map, self.width, self.height = read_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        # Carga los agentes
        load_agents(self.map, self, self.grid, self.schedule, self.width, self.height)

        # Busca los caminos y los guarda en una lista
        self.game_state = GameState(self)
        self.boxes_path = self.game_state.path

        self.initial_node = self.boxes_path[0]
        self.current_node = self.initial_node
        self.node_step = self.initial_node
        self.counter = 0

    def step(self) -> None:
        try:        
            print("Model step")
            self.node_step = self.boxes_path[self.counter]
            print("node step", self.node_step)
            if self.what_box_move(self.node_step) is not None:            
                self.schedule.step()
            else:
                self.counter += 1
                self.node_step = self.boxes_path[self.counter]
        except IndexError:
            print("No hay más pasos")
            
    def what_box_move(self, step_box):
        box_moved = None
        for key, value in self.current_node.items():
            if value != step_box[key]:
                box_moved = key
        return box_moved
    
    def get_agent_by_id(self, id):
        for agent in self.schedule.agents:
            if agent.unique_id == id:
                return agent
        return None