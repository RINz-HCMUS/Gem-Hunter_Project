from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import combinations

def convert_to_flatten(pos, size):
    """
    Converts 2D coordinates to flattened index.

    Args:
        pos (tuple): The 2D coordinates.
        size (tuple): The size of the grid.

    Returns:
        int: The flattened index.
    """
    num_r, num_c = size
    r, c = pos
    return (r*num_c + c + 1)

def convert_to_2D(flat, size):
    """
    Converts flattened index to 2D coordinates.

    Args:
        flat (int): The flattened index.
        size (tuple): The size of the grid.

    Returns:
        tuple: The 2D coordinates.
    """
    num_r, num_c = size
    c = (flat-1) % num_c
    r = (flat-1) // num_c
    return r,c

def generate_around(pos, size):
    """
    Generates valid neighboring cells around the given position.

    Args:
        pos (tuple): The 2D coordinates.
        size (tuple): The size of the grid.

    Yields:
        tuple: The coordinates of valid neighboring cells.
    """
    r, c = pos
    num_r, num_c = size
    for i in range(-1, 2):
        for j in range(-1, 2):
            new_r, new_c = r + i, c + j
            if 0 <= new_r < num_r and 0 <= new_c < num_c:
                yield new_r, new_c

def is_valid(pos, grid, size):
    """
    Checks if a position is valid in the grid.

    Args:
        pos (tuple): The 2D coordinates.
        grid (list of lists): The grid representing the Minesweeper game.
        size (tuple): The size of the grid.

    Returns:
        bool: True if the position is valid, False otherwise.
    """
    num_r, num_c = size
    r, c = pos 
    return 0 <= r < num_r and 0 <= c < num_c and grid[r][c] == '_'  

def list_combination(n, k):
    """
    Generates combinations of k elements from a list of n elements.

    Args:
        n (int): The total number of elements.
        k (int): The size of combinations.

    Returns:
        list: A list of combinations.
    """
    if k > n:
        return []
    comb_list = list(combinations(range(1, n + 1), k))
    return comb_list


def generate_CNF(pos, grid, size):
    """
    Generates CNF clauses for the given position in the grid.

    Args:
        pos (tuple): The 2D coordinates.
        grid (list of lists): The grid representing the Minesweeper game.
        size (tuple): The size of the grid.

    Returns:
        list of lists: The CNF clauses.
    """
    if grid[pos[0]][pos[1]] == '_':
        return []
    
    list_cells = []
    for new_pos in generate_around(pos, size):
        if is_valid(new_pos, grid, size):
            list_cells.append(convert_to_flatten(new_pos, size))
    
    
    number = int(grid[pos[0]][pos[1]])

    num_valid = len(list_cells)
    clauses = []
    
    first_comb = list_combination(num_valid, number + 1)
    
    for comb in first_comb:
        clause = []
        for index in comb:
            clause.append(-list_cells[index - 1])
        clauses.append(clause)
    
    second_comb = list_combination(num_valid, num_valid - number + 1)
    for comb in second_comb:
        clause = []
        for index in comb:
            clause.append(list_cells[index - 1])
        clauses.append(clause)
    
    return clauses

def solve_by_pysat(grid, size):
    """
    Solves the Minesweeper game using the PYSAT library.

    Args:
        grid (list of lists): The grid representing the Minesweeper game.
        size (tuple): The size of the grid.

    Returns:
        list or None: The satisfying assignment if found, None otherwise.
    """
    num_r, num_c = size
    clauses = [generate_CNF((r, c), grid, size) for r in range(num_r) for c in range(num_c)]

    cnf = CNF()
    for clause in clauses:
        cnf.extend(clause)

    with Solver(bootstrap_with=cnf) as solver:
        # Solve the SAT problem
        if solver.solve():
            # If satisfiable, get the satisfying assignment
            satisfying_assignment = solver.get_model()
            print('Formula is satisfiable')
            return satisfying_assignment
        else:
            # If unsatisfiable
            print('Formula is unsatisfiable')
            return None  # Or handle the unsatisfiable case accordingly

def ouput_for_pysat(list_result, grid, size):
    """
    Converts the satisfying assignment to the solution grid.

    Args:
        list_result (list): The satisfying assignment.
        grid (list of lists): The grid representing the Minesweeper game.
        size (tuple): The size of the grid.

    Returns:
        list of lists: The solution grid.
    """
    output = grid.copy()
    num_r, num_c = size
    for r in range(num_r):
        for c in range(num_c):
            if output[r][c] != '_':
                continue
            index = r * num_c + c
            if index < len(list_result) and list_result[index] > 0:
                output[r][c] = 'T'
            else:
                output[r][c] = 'G'
    return output

def read_input_file(file_path):
    """
    Reads the input file containing the Minesweeper grid.

    Args:
        file_path (str): The path to the input file.

    Returns:
        tuple or None: A tuple containing the size and grid if successful, None otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            size = tuple(map(int, lines[0].strip().split()))
            grid = []
            for line in lines[1:]:
                row = line.strip().split(',')
                row = [int(cell) if cell != '_' else '_' for cell in row]
                grid.append(row)
            return size, grid
    except FileNotFoundError:
        print("File not found.")
        return None

# Solves the Minesweeper game using the PYSAT library
def Pysat_Solution(grid, size):
    """
    Solves the Minesweeper game using the PYSAT library.

    Args:
        grid (list of lists): The grid representing the Minesweeper game.
        size (tuple): The size of the grid.

    Returns:
        list of lists or None: The solution grid if found, None otherwise.
    """
    result = solve_by_pysat(grid, size)
    if result is not None:
        return ouput_for_pysat(result, grid, size)
    else:
        print("No solution found.")
        return None
