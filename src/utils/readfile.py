# read_map es una función que lee un fichero de texto y devuelve una lista de listas con el contenido del fichero.
# En este caso nuestro mapa del juego de Sokoban 
def read_map(filename):
    with open(filename, 'r') as file:
        map_string = file.read()
    map_list = [line.split(', ') for line in map_string.splitlines()]
    width = len(map_list[0]) 
    height = len(map_list)
    return map_list, width, height