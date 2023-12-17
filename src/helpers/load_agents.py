from agent.robot_agent import RobotAgent
from agent.rock_agent import RockAgent
from agent.box_agent import BoxAgent
from agent.finish_agent import FinishAgent
from agent.path_agent import PathAgent
from helpers.constants import Constans
def load_agents(map, model, grid, schedule, width, height):
    agent_id = 0
    for y in range(height - 1, -1, -1):
        for x in range(width):
            grid_content = map[height - 1 - y][x]
            
            path = PathAgent(agent_id, model, "C")
            grid.place_agent(path, (x, y))
            schedule.add(path)
            agent_id += 1

            if 'C-a' in grid_content:
                robot = RobotAgent(agent_id, model, "C-a")
                grid.place_agent(robot, (x, y))
                schedule.add(robot)
                agent_id += 1
            elif 'C-b' in grid_content:
                box = BoxAgent(agent_id, model, "C-b")
                grid.place_agent(box, (x, y))
                schedule.add(box)
                agent_id += 1
            elif 'R' in grid_content:
                rock = RockAgent(agent_id, model, "R")
                grid.place_agent(rock, (x, y))
                schedule.add(rock)
                agent_id += 1
            elif 'M' in grid_content:
                finish = FinishAgent(agent_id, model, "M")
                grid.place_agent(finish, (x, y))
                schedule.add(finish)
                agent_id += 1

def calculate_heuristic(heuristic, initial_position, finish_position):
    if heuristic == Constans.MANHATTAN:
        # Cálculo de la distancia de Manhattan entre la caja y la meta
        distance = abs(initial_position[0] - finish_position[0]) + abs(initial_position[1] - finish_position[1])
        return distance
    elif heuristic == Constans.EUCLIDEAN:
        # Cálculo de la distancia euclidiana entre la caja y la meta
        distance = ((initial_position[0] - finish_position[0])**2 + (initial_position[1] - finish_position[1])**2)**0.5
        return distance
    
def calculate_all_heristic(selected_heuristic, schedule, goal_agent):
    for agent in schedule.agents: 
        if isinstance(agent, PathAgent):
            heuristic = calculate_heuristic(selected_heuristic, agent.pos, goal_agent.pos)
            print("Heuristica de", agent.pos, ":", heuristic)
            agent.heuristic = heuristic

def get_all_heristics(schedule, goal_agents):
    heuristic_dict = {}
    for agent in schedule.agents: 
        if isinstance(agent, PathAgent):
            heuristic = 0
            for goal_agent in goal_agents:
                agent_heuristic = calculate_heuristic(Constans.MANHATTAN, agent.pos, goal_agent.pos)
                heuristic += agent_heuristic
            # print("Heuristica de", agent.pos, ":", heuristic)
            heuristic_dict[agent.pos] = heuristic
    return heuristic_dict

def get_heristics_for_goals(schedule, goal_agents):
    heuristic_dict = {}
    for goal_agent in goal_agents:
        heuristic = {}
        for agent in schedule.agents: 
            if isinstance(agent, PathAgent):
                agent_heuristic = calculate_heuristic(Constans.MANHATTAN, agent.pos, goal_agent.pos)
                heuristic[agent.pos] = agent_heuristic
                # print("Heuristica de", agent.pos, ":", agent_heuristic)
        # print("Heuristica de", goal_agent.pos, ":", heuristic)
        heuristic_dict[goal_agent.pos] = heuristic
    return heuristic_dict
