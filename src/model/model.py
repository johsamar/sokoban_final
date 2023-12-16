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

        # Estructuras de datos para la búsqueda
        self.queue = Queue()        
        self.stack = []
        self.priority_queue = PriorityQueue()
        self.priority_queue_a = PriorityQueue()
        self.visited = set()
        self.vsited_list = []
        self.final_path = {}

        self.visited_dic = {}

        # Los flags de finalización y éxito
        self.finished = False
        self.found = False

        # Inicializa los parámetros del modelo
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.filename = filename

        # Carga el mapa
        self.map, self.width, self.height = read_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        # Carga los agentes
        load_agents(self.map, self, self.grid, self.schedule, self.width, self.height)

        # Obtener la posición de la meta, y el robot
        robot_agent = next(agent for agent in self.schedule.agents if isinstance(agent, RobotAgent))
        goal_agent = next(agent for agent in self.schedule.agents if isinstance(agent, FinishAgent))
        # Obtener todos los agentes necesarios
        all_robots = [agent for agent in self.schedule.agents if isinstance(agent, RobotAgent)]
        all_goals = [agent for agent in self.schedule.agents if isinstance(agent, FinishAgent)]
        all_boxes = [agent for agent in self.schedule.agents if isinstance(agent, BoxAgent)]

        # Busquedas de cajas


        #Define la posición de la meta
        self.goal_position = goal_agent.pos

        calculate_all_heristic(self.heuristic, self.schedule, goal_agent)

        # Obtener la posición actual del robot
        self.start_position = robot_agent.pos

        # Lista para la sumar los nodos en la columna
        self.suma_nodos = np.zeros(self.width)

        # Agregar la posición inicial del robot a las estructuras de datos
        self.queue.put((self.start_position, 0))
        self.priority_queue.put((0, "nodo0"))
        self.priority_queue_a.put((0, 0, "nodo0"))
        self.stack.append((self.start_position, 0))
        self.visited_dic["nodo0"] = self.start_position

        self.bfs_search()

    def set_filename(self, new_filename):
        self.filename = new_filename
     
    def print_grid(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if len(cell) > 0:
                    for item in cell:
                        print(f'{item.__class__.__name__} en ({x}, {y})', end='')
                else:
                    print(f'Camino en ({x}, {y})', end='')
            print()

    def step(self) -> None:        
        # Realizar la búsqueda en anchura
        if self.algorithm == Constans.BFS and not self.finished:
            self.bfs()
        if self.algorithm == Constans.UNIFORM_COST and not self.finished:
            self.costo_uniforme()
        elif self.algorithm == Constans.DFS and not self.finished:
            # self.dfs()
            self.dfs2()
        elif self.algorithm == Constans.BEAM_SEARCH and not self.finished:
            self.beam_search(beam_width=4)
        elif self.algorithm == Constans.A_STAR and not self.finished:
            self.a_star()
        if not self.finished:
            self.schedule.step()
        if self.finished:
            if self.found:
                # maximo = self.suma_nodos.max()
                # index = get_index(self.suma_nodos, maximo)
                # print("La columna con mas nodos es: " + str(index) + " con "+ str(maximo))
                print("Se encontró la meta")
                print("orden de visitados: ", self.vsited_list)
                print("Cantidad de nodos visitados: ", len(self.visited))
                path = list(reversed(self.get_final_path(self.start_position, self.goal_position)))
                print("path", path )
            else:
                print("No se encontró la meta")

    def bfs(self):        
        if not self.queue.empty():
            current, step = self.queue.get()
            print(f"Current: {current}")
            if current == self.goal_position:
                self.finished = True
                self.found = True
            if current not in self.visited:
                self.visited.add(current)
                
                # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                # print(f"Vecinos: {neighbors_sort} del {current}" )
                for neighbor in neighbors_sort:
                    # Obtener el agente que se encuentra en la posición vecina y verificar que no sea una roca 
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                    
                    if neighbor not in self.visited:
                        if(size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent)):
                            # print("Vecino roca: ", neighbor)
                            pass
                        else:
                            self.queue.put((neighbor, step + 1))
                            self.final_path[neighbor] = current
            print(f"Cola: {self.queue.queue}")
        else:
            self.finished = True
    
    def dfs(self):
        if len(self.stack) > 0:
            current, step = self.stack.pop()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True
                
            if current not in self.visited:
                self.visited.add(current)
                self.suma_nodos[current[0]] += 1
                print(f"Visitado: {self.visited}")
                print("suma: " + str(self.suma_nodos))
                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False )
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")

                for neighbor in neighbors_sort:
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))

                    if neighbor not in self.visited:
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                            print("Vecino roca: ", neighbor)
                        else:
                            self.stack.append((neighbor, step + 1))
                            self.final_path[neighbor] = current

            print(f"Pila: {self.stack}")
        else:
            self.finished = True

    def dfs2(self):
        if len(self.stack) > 0:
            current, step = self.stack.pop()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True
                
            if current not in self.visited:
                self.visited.add(current)
                # self.suma_nodos[current[0]] += 1
                # print(f"Visitado: {self.visited}")
                # print("suma: " + str(self.suma_nodos))
                
                # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False )
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")
                neighbors_inv = list(reversed(neighbors_sort))
                for neighbor in neighbors_inv:
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))

                    if neighbor not in self.visited:
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                            print("Vecino roca: ", neighbor)
                        else:
                            self.stack.append((neighbor, step + 1))
                            self.final_path[neighbor] = current

            print(f"Pila: {self.stack}")
        else:
            self.finished = True
            
    def costo_uniforme(self):
        if not self.finished:
            if not self.priority_queue.empty():
                step, id_current = self.priority_queue.get()
                current = self.visited_dic[id_current]
                print(f"Current: {current}")
                # Si el nodo actual es la meta, establece los indicadores y finaliza
                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                # print(f"Paso actual: {current}")
                # print(f"Vecinos: {self.grid.get_neighborhood(current, moore=False, include_center=False)}")
                
                if current not in self.visited:
                    self.visited.add(current)
                    
                    # añadir el orden de visitados
                    self.increase_node(current)

                    # Obtén los vecinos del nodo actual
                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    
                    neighbors_sort = list(neighbors)
                    neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                    neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                    print(f"Vecinos: {neighbors_sort} del {current}")
                    # neighbors_inv = list(reversed(neighbors_sort))
                    # print(f"Vecinos inv: {neighbors_inv} del {current}")

                    for neighbor in neighbors_sort:
                        # Verificar si el vecino es un camino libre
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            # Calcular el costo de moverse al vecino
                            cost = self.calculate_cost(neighbor)
                            print(f"Costo: {cost}")
                            # Actualizar el costo total

                            total_cost = step + cost

                            print(f"Costo total: {total_cost}")
                            # id randome
                            id_nodo = "nodo" + str(np.random.randint(1000000))                            
                            self.visited_dic[id_nodo] = neighbor
                            self.priority_queue.put((total_cost, id_nodo))
                            self.final_path[neighbor] = current
                    print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True

    def calculate_cost(self, position):
        # En este ejemplo, el costo de movimiento es 10 para cualquier dirección
        return 10
        

    def beam_search(self, beam_width):
        if not self.priority_queue.empty():
            _, id_current = self.priority_queue.get()
            current = self.visited_dic[id_current]

            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True

            if current not in self.visited:
                self.visited.add(current)
                print(f"Visitado: {self.visited}")
                 # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")
                neighbors_inv = list(reversed(neighbors_sort))
                print(f"Vecinos inv: {neighbors_inv} del {current}")
                for neighbor in neighbors_inv:
                    if neighbor not in self.visited:
                        size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                                print("Vecino roca: ", neighbor)
                        else:           
                            heuristica = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                            id_nodo = "nodo" + str(np.random.randint(1000000))                            
                            self.visited_dic[id_nodo] = neighbor
                            self.priority_queue.put((heuristica, id_nodo))
                            self.final_path[neighbor] = current
                        
            print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True

    def a_star(self):
        if not self.finished:
            if not self.priority_queue_a.empty():
                t_cost, cost, id_current = self.priority_queue_a.get()
                current = self.visited_dic[id_current]

                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                if current not in self.visited:
                    self.visited.add(current)
                    # añadir el orden de visitados
                    self.increase_node(current)

                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    for neighbor in neighbors:
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            movement_cost = self.calculate_cost(neighbor)
                            heuristic = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                            total_cost = t_cost + heuristic
                            id_nodo = "nodo" + str(np.random.randint(1000000))                            
                            self.visited_dic[id_nodo] = neighbor
                            self.priority_queue_a.put((total_cost, t_cost + movement_cost, id_nodo ))
                            self.final_path[neighbor] = current

            else:
                self.finished = True

    def get_final_path(self, initial, goal):
        finish = True
        path = [goal]
        parent = goal
        while finish:
            parent = self.final_path[parent]
            path.append((parent[0]-1, parent[1]-1))
            if parent == initial:
                finish = False
        return path
    
    def increase_node(self, current):
        self.vsited_list.append((current[0]-1, current[1]-1))
        # print(f"VIsitados: {self.visited}")
        # Obtener agentes en la posición actual
        floorAgent = self.grid.get_cell_list_contents([current])[0]
        #obtener el floorAgent de la posición actual
        floorAgent.set_state(len(self.visited))

    # ------------------------------------------------- busquedas de cajas ----------------------------------------------
    # def is_goal_state(self):
    #     # Verifica si todas las cajas están en la meta
    #     return all(agent in self.grid_state and 'M' in self.grid_state[agent] for agent in self.agent_positions)

    # def generate_next_states(self):
    #     # Genera todos los posibles estados hijos aplicando movimientos válidos
    #     next_states = []

    #     for agent_id, position in self.agent_positions.items():
    #         x, y = position

    #         # Prioridad de mover primero a la caja más a la izquierda
    #         cajas_izquierda = sorted(
    #             [(box_id, box_position) for box_id, box_position in self.agent_positions.items() if 'C-b' in self.grid_state[box_id]],
    #             key=lambda box: box[1][0]
    #         )

    #         for box_id, box_position in cajas_izquierda:
    #             box_x, box_y = box_position

    #             # Prioridad de mover abajo, arriba, izquierda y derecha
    #             for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
    #                 new_agent_positions = self.agent_positions.copy()
    #                 new_box_position = (box_x + dx, box_y + dy)

    #                 if self.is_valid_move(new_box_position):
    #                     new_agent_positions[agent_id] = new_box_position

    #                     new_state = copy.deepcopy(self)
    #                     new_state.agent_positions = new_agent_positions
    #                     new_state.grid_state[agent_id] = ''
    #                     new_state.grid_state[box_id] = 'C-b'

    #                     next_states.append(new_state)

    #     return next_states
    
    # def is_valid_move(self, new_position):
    #     # Verifica si el movimiento es válido, por ejemplo, no chocar con rocas o salir de la grilla
    #     x, y = new_position
    #     return 0 <= x < self.model.width and 0 <= y < self.model.height and self.grid_state[x][y] != 'R'

    # Función BFS modificada para trabajar con múltiples cajas
    def bfs_search(self):
        initial_state = GameState(self)
        # visited_states = set()

        # queue = Queue()
        # queue.put(initial_state)
        # visited_states.add(tuple(tuple(row) for row in initial_state.grid_state))  # Usamos una tupla para que sea hashable

        # while not queue.empty():
        #     current_state = queue.get()
        #     print("current_state: " + str(current_state))

        #     if current_state.is_goal_state():
        #         return current_state

        #     for next_state in current_state.generate_next_states():
        #         next_state_tuple = tuple(tuple(row) for row in next_state.grid_state)
        #         if next_state_tuple not in visited_states:
        #             visited_states.add(next_state_tuple)
        #             queue.put(next_state)

        # return None  # No se encontró una solución