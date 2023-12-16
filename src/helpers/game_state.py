from agent.robot_agent import RobotAgent
from agent.rock_agent import RockAgent
from agent.path_agent import PathAgent
from agent.box_agent import BoxAgent
from agent.finish_agent import FinishAgent
from mesa import Model
from utils.write_file import write_files
from helpers.constants import Constans
from queue import Queue
import copy

class GameState:
    def __init__(self, model: Model):
        print("GameState: Inicializando")
        self.model = model
        self.all_goals = [agent for agent in self.model.schedule.agents if isinstance(agent, FinishAgent)]
        self.all_boxes = [agent for agent in self.model.schedule.agents if isinstance(agent, BoxAgent)]
        # self.visited = {
        #     box.unique_id: [] for box in self.all_boxes
        # }
        self.visited = []
        self.number_child = 0
        path = self.bfs_search()
        print("Camino:", path)
        #Reinicia las cajas a su posición inicial
        self.move_boxes(self.initial_state)
        

    # Verifica si todas las cajas están en la meta
    def is_goal_state(self, current_state):
        count = 0
        for goal in self.all_goals:
            for key, value in current_state.items():
                if goal.pos == value:
                    count += 1
        if count == len(self.all_goals):
            return True
        return False


    def save_game_state(self, filename):
        # Guardar el estado actual del juego en un archivo de texto plano
        lines = []
        for y in range(self.model.height - 1, -1, -1):
            tags = []
            for x in range(self.model.width):
                content = self.model.grid.get_cell_list_contents([(x, y)])
                if len(content) == 2:
                    tags.append(content[1].tag)
                elif len(content) == 1:
                    tags.append(content[0].tag)
                else:
                    tags.append("C")                
            line = ', '.join(tags)
            lines.append(line)
        
        write_files(filename, lines)

    def generate_next_states(self):
        # Genera todos los posibles estados hijos aplicando movimientos válidos
        next_states = []

        # Ordenar las cajas mas a la izquierda
        boxes_izquierda = sorted(self.all_boxes, key=lambda box: box.pos[0])

        for box in boxes_izquierda:
            # Obtener los movimientos válidos para la caja
            valid_moves, moves = self.get_possible_moves(box.pos, box.unique_id)
            print("Movimientos posibles:", valid_moves)
            if len(valid_moves) > 0:
                if moves[Constans.BOTTOM] in valid_moves and moves[Constans.TOP] in valid_moves:
                    next_states.append((box.unique_id, moves[Constans.BOTTOM]))
                if moves[Constans.TOP] in valid_moves and moves[Constans.BOTTOM] in valid_moves:
                    next_states.append((box.unique_id, moves[Constans.TOP]))
                if moves[Constans.LEFT] in valid_moves and moves[Constans.RIGHT] in valid_moves:
                    next_states.append((box.unique_id, moves[Constans.LEFT]))
                if moves[Constans.RIGHT] in valid_moves and moves[Constans.LEFT] in valid_moves:
                    next_states.append((box.unique_id, moves[Constans.RIGHT]))

        return next_states


    def get_possible_moves(self, box_pos, box_id):
        neighbors = self.model.grid.get_neighborhood(box_pos, moore=False, include_center=False)
        neighbors = list(neighbors)
        neighbors[0], neighbors[1], neighbors[2], neighbors[3] = neighbors[1], neighbors[2], neighbors[0], neighbors[3]
        movements = []
        print("Vecinos de la caja:", neighbors)
        ortogonal_movs = {
            Constans.BOTTOM: neighbors[0],
            Constans.TOP: neighbors[1],
            Constans.LEFT: neighbors[2],
            Constans.RIGHT: neighbors[3]
        }
        for neighbor in neighbors:
            # Obtener el agente que se encuentra en la posición vecina y verificar que no sea una roca 
            size_agents = len(self.model.grid.get_cell_list_contents([neighbor]))            
            
            if(size_agents > 1 and (isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], RockAgent) or isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], BoxAgent))):
                # print("Vecino roca: ", neighbor)
                pass
            else:
                movements.append(neighbor)
        return movements, ortogonal_movs

    def bfs_search(self):     
        self.initial_state = {
            box.unique_id: box.pos for box in self.all_boxes
        }
        queue = Queue()
        queue.put((self.initial_state, None))
        print("Estados visitados:", self.visited)
        while not queue.empty():            
            print("-----------------------------------")
            current_state, parent_state = queue.get()
            print("Estado actual:", current_state)
            self.move_boxes(current_state)
            self.visited.append(current_state)
            
            self.number_child += 1
            self.save_game_state(f"states/node_{self.number_child}.txt")
            
            if self.is_goal_state(current_state):
                print("Estado meta encontrado:", current_state)
                path = [current_state]
                while parent_state is not None:
                    path.append(parent_state[0])
                    parent_state = parent_state[1]
                return path[::-1]

            for next_state in self.generate_next_states():
                print("Estado hijo:", next_state)
                new_state = current_state.copy()
                new_state[next_state[0]] = next_state[1]
                if new_state not in self.visited:
                    queue.put((new_state, (current_state, parent_state)))
                    print("Estados visitados:", self.visited)
                
        return None
    
    def move_boxes(self, state):
        print("Moviendo cajas...")
        for key, value in state.items():
            box = self.model.schedule.agents[key]
            self.model.grid.move_agent(box, value)          

