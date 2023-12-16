

def write_files(filename, lines):
    with open(filename, 'w') as file:
        for line in lines:
            file.write(line + '\n')
        