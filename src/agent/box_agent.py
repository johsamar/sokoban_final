from mesa import Agent
from utils.config import PROJECT_PATH
import os

class BoxAgent(Agent):
    
    def __init__(self,unique_id, model, tag = ""):
        super().__init__(unique_id,model)
        self.image = "assets/box.png"
        self.color = "yellow"
        self.layer = 1
        self.tag = tag
        self.new_pos = None

    def step(self) -> None:
        if self.new_pos is not None:
            self.model.grid.move_agent(self, self.new_pos)
            self.new_pos = None
