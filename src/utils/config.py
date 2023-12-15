import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_index(array, element):
    for i in range(0, len(array)):
        if array[i] == element:
            return i
    return None