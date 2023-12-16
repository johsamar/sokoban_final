from agent.robot_agent import RobotAgent
from agent.rock_agent import RockAgent
from agent.path_agent import PathAgent
from agent.box_agent import BoxAgent
from agent.finish_agent import FinishAgent
from mesa import Model
from utils.write_file import write_files
from helpers.constants import Constans

class GameState:
    def __init__(self, model: Model):
        print("GameState: Inicializando")
        self.model = model
        self.all_goals = [agent for agent in self.model.schedule.agents if isinstance(agent, FinishAgent)]
        self.all_boxes = [agent for agent in self.model.schedule.agents if isinstance(agent, BoxAgent)]
        self.visited = {
            box.unique_id: [] for box in self.all_boxes
        }
        self.save_game_state("states/node_1.txt")
        next_states = self.generate_next_states()
        print("Estados hijos:", next_states)

    # Verifica si todas las cajas están en la meta
    def is_goal_state(self):
        grids_goal = [self.model.grid.get_cell_list_contents([goal.pos]) for goal in self.goals]        
        count = 0
        for grid in grids_goal:
            if len(grid) == 0 or len(grid) == 1 or len(grid) == 2:
                return False            
            if any(isinstance(x, BoxAgent) for x in grid):
                count += 1
        return count == len(grids_goal)        


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
            
            if neighbor not in self.visited[box_id]:
                if(size_agents > 1 and (isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], RockAgent) or isinstance(self.model.grid.get_cell_list_contents([neighbor])[1], BoxAgent))):
                    # print("Vecino roca: ", neighbor)
                    pass
                else:
                    movements.append(neighbor)
        return movements, ortogonal_movs

