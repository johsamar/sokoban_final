from mesa import Agent
from PIL import Image
import numpy as np
import os

class RockAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.image = "assets/wall.jpg"
        self.color = "black"
        self.layer = 1

    def step(self) -> None:
        return None


    def give_money(self):
        return None

    def move(self) -> None:
        return None
