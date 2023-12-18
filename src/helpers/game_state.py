from agent.robot_agent import RobotAgent
from agent.rock_agent import RockAgent
from agent.path_agent import PathAgent
from agent.box_agent import BoxAgent
from agent.finish_agent import FinishAgent
from mesa import Model
from utils.write_file import write_files
from utils.delete_files import delete_files
from helpers.constants import Constans
from queue import Queue, PriorityQueue
from helpers.load_agents import get_all_heristics, get_heristics_for_goals, calculate_heristic

class GameState:
    def __init__(self, model: Model):
        print("GameState: Inicializando")
        delete_files()
        self.model = model
        self.all_goals = [agent for agent in self.model.schedule.agents if isinstance(agent, FinishAgent)]
        self.all_boxes = [agent for agent in self.model.schedule.agents if isinstance(agent, BoxAgent)]
        self.all_robots = [agent for agent in self.model.schedule.agents if isinstance(agent, RobotAgent)]
        self.box_goal = {}
        self.robot_box = {}
        self.heuristic_general = get_all_heristics(self.model.schedule, self.all_goals)
        self.heuristic = get_heristics_for_goals(self.model.schedule, self.all_goals)
        self.heuristic_boxes = get_heristics_for_goals(self.model.schedule, self.all_boxes)
        # print("Heuristica:", self.heurictics2)
        self.assign_goal_box_less_heuristic()
        self.assign_box_robot_less_heuristic()
        self.visited = []
        self.number_child = 0
        # self.path = self.bfs_search()
        self.path = self.beam_search()
        # self.path = []
        print("Camino:", self.path)
        #Reinicia las cajas a su posición inicial
        self.move_boxes(self.initial_state)

    def assign_goal_box_less_heuristic(self):
        # Asigna la caja con menor heurística a la meta más cercana
        assigned_goal = []
        used_goals = []
        used_boxes = []
        for box in self.all_boxes:       
            heuristics_goals_box = []
            for goal in self.all_goals:
                    heuristic = self.heuristic[goal.pos][box.pos]
                    heuristics_goals_box.append((goal.pos, heuristic))
                    assigned_goal.append((heuristic, goal.pos, box.unique_id))
            # heuristics_goals_box.sort(key=lambda x: x[1])
            # self.box_goal[box.unique_id] = calculte
        assigned_goal.sort(key=lambda x: x[0])
        print("Asignación de robots a cajas:", assigned_goal)
        for goal in assigned_goal:
            if goal[1] not in used_goals and goal[2] not in used_boxes:
                self.box_goal[goal[2]] = goal[1]
                used_boxes.append(goal[2])
                used_goals.append(goal[1])
        print("Asignación de robots a cajas:", self.box_goal)
        
    def assign_box_robot_less_heuristic(self):
        # Asigna la caja con menor heurística a la meta más cercana
        if len(self.all_robots) > 1:
            assigned_box = []
            used_boxes = []
            used_robots = []
            for robot in self.all_robots:       
                heuristics_box_robot = []
                for box in self.all_boxes:
                        heuristic = self.heuristic_boxes[box.pos][robot.pos]
                        heuristics_box_robot.append((box.pos, heuristic))
                        assigned_box.append((heuristic, {box.unique_id: box.pos}, robot.unique_id))
                # heuristics_goals_box.sort(key=lambda x: x[1])
                # self.box_goal[box.unique_id] = calculte
            assigned_box.sort(key=lambda x: x[0])
            print("Asignación de cajas a metas:", assigned_box)
            for box in assigned_box:
                if box[1] not in used_boxes and box[2] not in used_robots:
                    self.robot_box[box[2]] = box[1]
                    used_robots.append(box[2])
                    used_boxes.append(box[1])

            for robot in self.all_robots:
                # robot.box_target = self.robot_box[robot.unique_id]
                key, value = self.robot_box[robot.unique_id].popitem()
                robot.box_target = (key, value)
            print("Asignación de cajas a metas:", self.robot_box)
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
                elif len(content) == 3:
                    tags.append(content[2].tag)
                else:
                    tags.append("C")                
            line = ', '.join(tags)
            lines.append(line)
        
        write_files(filename, lines)

    """
    Retorna una lista de tuplas con la siguiente estructura:
    (id_caja, movimiento, donde_se_ejerce_movimiento, (heurística, heurística_general))
    """
    def generate_next_states(self):
        # Genera todos los posibles estados hijos aplicando movimientos válidos
        next_states = []

        # Ordenar las cajas mas a la izquierda
        boxes_izquierda = sorted(self.all_boxes, key=lambda box: box.pos[0])

        for box in boxes_izquierda:
            # Obtener los movimientos válidos para la caja
            if self.box_goal[box.unique_id] != box.pos:
                valid_moves, moves = self.get_possible_moves(box.pos, box.unique_id)
                print("Movimientos posibles:", valid_moves)
                if len(valid_moves) > 0:
                    if moves[Constans.BOTTOM] in valid_moves and moves[Constans.TOP] in valid_moves:
                        next_states.append((box.unique_id, moves[Constans.BOTTOM], moves[Constans.TOP], (self.heuristic[self.box_goal[box.unique_id]][moves[Constans.BOTTOM]], self.heuristic_general[moves[Constans.BOTTOM]]),))
                    if moves[Constans.TOP] in valid_moves and moves[Constans.BOTTOM] in valid_moves:
                        next_states.append((box.unique_id, moves[Constans.TOP], moves[Constans.BOTTOM], (self.heuristic[self.box_goal[box.unique_id]][moves[Constans.TOP]], self.heuristic_general[moves[Constans.TOP]]),))
                    if moves[Constans.LEFT] in valid_moves and moves[Constans.RIGHT] in valid_moves:
                        next_states.append((box.unique_id, moves[Constans.LEFT], moves[Constans.RIGHT], (self.heuristic[self.box_goal[box.unique_id]][moves[Constans.LEFT]], self.heuristic_general[moves[Constans.LEFT]]),))
                    if moves[Constans.RIGHT] in valid_moves and moves[Constans.LEFT] in valid_moves:
                        next_states.append((box.unique_id, moves[Constans.RIGHT], moves[Constans.LEFT], (self.heuristic[self.box_goal[box.unique_id]][moves[Constans.RIGHT]], self.heuristic_general[moves[Constans.RIGHT]]),))

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
            
            if(size_agents == 2 and (isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], RockAgent) or isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], BoxAgent))):
                pass
            elif(size_agents == 3 and isinstance(self.model.grid.get_cell_list_contents([neighbor])[2], BoxAgent)):
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
        # print("Estados visitados:", self.visited)
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
                new_state["move"] = (next_state[0], next_state[2])
                if new_state not in self.visited:
                    queue.put((new_state, (current_state, parent_state)))
                    # print("Estados visitados:", self.visited)
                
        return None
    
    def move_boxes(self, state):
        print("Moviendo cajas...")
        print("Estado:", state)
        for key, value in state.items():
            if key != "move" and key != "nodo":
                box = self.model.schedule.agents[key]
                self.model.grid.move_agent(box, value)          

    def beam_search(self, beam_width=4):
        self.number_child += 1

        self.initial_state = {
            box.unique_id: box.pos for box in self.all_boxes
        }
        self.initial_state["nodo"] = self.number_child
        self.initial_state["move"] = None
        queue = PriorityQueue()

        node_zero = f"nodo_{self.number_child}"
        queue.put((0, node_zero))
        queue_data = {
            node_zero: (self.initial_state, None)
        }
        # self.visited.append(self.initial_state)
        counter = 0
        while not queue.empty():
            print("-----------------------------------")
            # print("queue_data: ", queue_data)
            # print("-----------------------------------")
            _, current_state_id = queue.get()
            current_state, parent_state = queue_data[current_state_id]
            # quitar move y nodo del estado en copia, si existe
            copy = current_state.copy()
            if "move" in copy:
                del copy["move"]
            if "nodo" in copy:
                del copy["nodo"]
            
            self.move_boxes(current_state)
            self.visited.append(copy)
            self.save_game_state(f"states/node_{current_state['nodo']}.txt")
            
            if self.is_goal_state(current_state):
                path = [current_state]
                while parent_state is not None:
                    path.append(parent_state[0])
                    parent_state = parent_state[1]
                return path[::-1]

            next_states = self.generate_next_states()
            # print("Estados hijos:", next_states)
            # la heuristica es una tupla (heuristica de la caja, heuristica general)
            # Ordena por la heurística
            next_states.sort(key=lambda x: x[3][1])
            
            for i in range(min(beam_width, len(next_states))):
                self.number_child += 1
                next_state = next_states[i]
                new_state = current_state.copy()
                new_state[next_state[0]] = next_state[1]
               
                print("Nuevo: ", new_state)
                # print("Visitados:", self.visited)                

                if new_state not in self.visited:
                    new_state["move"] = (next_state[0], next_state[2])
                    new_state["nodo"] = self.number_child
                    node_id = f"nodo_{self.number_child}"
                    queue_data[node_id] = (new_state, (current_state, parent_state))
                    heuristic_1, _ = next_state[3]
                    # queue.put((heuristic_1, heuristic_2, node_id))
                    queue.put((heuristic_1, node_id))
                    # queue.put((next_state[3], node_id))
                    # self.visited.append(new_state)
            # print("Cola:", queue.queue)
            # counter += 1
            # if counter == 5:
            #     break
        return None


    def a_star(self, agent, target, model):
        number_child = 1

        agent.initial_state = agent.pos
        

        heuristics_for_target = calculate_heristic(model.schedule, target)
        
        queue = PriorityQueue()

        node_zero = f"nodo_{number_child}"
        queue.put((0, 0, node_zero))
        
        visited_dic = {
            node_zero: (agent.initial_state, None)
        }
        visited = []
        path = None
        while not queue.empty():        
            t_cost, _, id_current = queue.get()
            current = visited_dic[id_current]

            if current[0] == target:
                path = [current[0]]
                parent_state = current[1]
                while parent_state is not None:
                    state = visited_dic[parent_state]
                    path.append(state[0])
                    parent_state = state[1]
                return path[::-1]
                

            if current not in visited:
                print("current:", current)
                visited.append(current)
                # añadir el orden de visitados
                # self.increase_node(current)

                neighbors = model.grid.get_neighborhood(current[0], moore=False, include_center=False)
                for neighbor in neighbors:
                    contents = model.grid.get_cell_list_contents([neighbor])
                    is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                    is_box = any(isinstance(obj, BoxAgent) for obj in contents)
                    is_robot = any(isinstance(obj, RobotAgent) for obj in contents)

                    if not is_rock and not is_box and not is_robot and neighbor not in visited:
                        number_child += 1
                        movement_cost = self.calculate_cost(neighbor)
                        heuristic = heuristics_for_target[neighbor]
                        total_cost = t_cost + heuristic
                        id_nodo = f"nodo_{number_child}"
                        visited_dic[id_nodo] = (neighbor, id_current)
                        queue.put((total_cost, t_cost + movement_cost, id_nodo ))
        
    
    def calculate_cost(self, position):
        # En este ejemplo, el costo de movimiento es 10 para cualquier dirección
        return 10