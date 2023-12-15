from mesa import Agent

class FinishAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.image = "assets/finish.png"
        self.color = "green"
        self.layer = 1

    def step(self) -> None:
        return None


    def give_money(self):
        return None

    def move(self) -> None:
        return None
