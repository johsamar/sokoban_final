from mesa import Agent
from utils.config import PROJECT_PATH
import os

class BoxAgent(Agent):
    
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.image = os.path.join(PROJECT_PATH, "assets/box.png")
        self.color = "yellow"
        self.layer = 1

    def step(self) -> None:
        return None


    def give_money(self):
        return None

    def move(self) -> None:
        return None
