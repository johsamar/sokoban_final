from mesa import Agent
from helpers.constants import Constans
from queue import PriorityQueue


class RobotAgent(Agent):
    def __init__(self,unique_id, model, tag = ""):
        super().__init__(unique_id,model)
        self.image = "assets/robot.png"
        self.color = "grey"
        self.layer = 1
        self.tag = tag
        self.priority_queue_a = PriorityQueue()
        self.priority_queue_a.put((0, 0, "nodo0"))
        self.box_target = None        
        self.movement = []

    def define_path(self, target):
        pass

    def step(self):
        print("Robot step")
        print(f"id: {self.unique_id}")
        print("step", self.model.node_step)
        print("box target: ", self.box_target)
        print("posicion actual: ", self.pos)
        if self.pos == self.model.node_step["move"][1]:
            id_box = self.model.node_step["move"][0]
            box = self.model.get_agent_by_id(id_box)
            box_pos = box.pos
            box.new_pos = self.model.node_step[id_box]
            self.model.grid.move_agent(self, box_pos)
            self.model.counter += 1
        #verificar si el paso tiene movimeinto y si existe move en el diccionario                
        elif len(self.movement) > 0:
            print("movement", self.movement)
            next_step = self.movement.pop(0)
            print("next step", next_step)
            self.model.grid.move_agent(self, next_step)
        elif self.model.node_step["move"] is not None:
                box_id = self.model.node_step["move"][0]
                if box_id == self.box_target[0]:
                    target = self.model.node_step["move"][1]
                    print("target", target)
                    path = self.model.game_state.a_star(self, target, self.model)
                    self.movement = path
                    print("Path", path)
         