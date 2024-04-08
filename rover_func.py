from pydantic import BaseModel
import random
import string
import hashlib as h
import json
from typing import Optional
from fastapi import HTTPException

class Mine(BaseModel):
    serial: str = None
    x: int = None
    y: int = None

class Rover(BaseModel):
    rover_id: str
    commands: str
    status: str          # survival status of the rover

class RoverReq(BaseModel):
    commands:str

def read_map(filename):

    # open file to get the map
    with open(filename, 'r') as f:
        mineMap = [line.split() for line in f]

    return mineMap

def write_map(path_map: list[list[str]], file_name: str):
    with open(file_name, "w") as file:
        for row in path_map:
            file.write(' '.join(map(str, row)) + '\n')

def write_rovers_to_file(rovers: list[Rover], filename: str) -> None:
  # Convert the list of rovers to a JSON serializable list
    rover_data = [rover.model_dump() for rover in rovers]

    with open(filename, "w") as f:
        json.dump(rover_data, f, indent=4)  # indeatation for better presentation

def read_rovers_from_file(filename: str) -> list[Rover]:
    try:
        with open(filename, "r") as f:
            rover_data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Returning an empty list.")
        return []

    # Convert the list of dictionaries back to Rover objects
    rovers = [Rover(**data) for data in rover_data]  # Unpack data into Rover objects
    return rovers


def deriveSerialNumber():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generatePIN():
    return ''.join(random.choices(string.digits + string.digits, k=10))


def hash_key(key: str):
    return h.sha256(key.encode('utf-8')).hexdigest()

def identify_mines_in_array(array):
    detected_mines = []

    # Traversing through row and col using enumerate
    for i, row in enumerate(array):
        for j, location in enumerate(row):
            # If 'location' contains 'mine1 / mine2' its a mine --> len is 5
            if type(location) == str and len(location) == 5:  
                mine = Mine(serial=location, x=i, y=j)
                # Add the new Mine model to the list
                detected_mines.append(mine)

    return detected_mines


def findMine_usingID(array, serial_id):
    # Iterating through the array
    for i, row in enumerate(array):
        try:
            # Find the index of the serial_id in the current row
            j = row.index(serial_id)
            # If found, return the Mine object with serial and coordinates
            return Mine(serial=serial_id, x=i, y=j)
        except ValueError:
            pass  # Serial ID not found in this row
    
    return None  # Serial ID not found in the array


def deleteMine_usingID(array, serial_id):
    # Load the mineMap from the file
    mineMap = read_map("map.txt")

    # Iterate over each row and column in the array
    for i, row in enumerate(array):
        try:
            # Find the index of the serial_id in the current row
            j = row.index(serial_id)
            # If found, delete the mine by setting the value to 0
            array[i][j] = 0
            mineMap[i][j] = 0
            # We will have to update both the txt files
            write_map(array, "mines.txt")   
            write_map(mineMap, "map.txt")
            # Return the response
            return "Mine successfully deleted"
        except ValueError:
            pass  # Serial ID not found in this row
    
    # If the serial ID is not found in the array
    return "Not found"


def add_new_mine(serial_id, x, y):
    # Read map files
    mineMap = read_map("map.txt")
    mineSerialMap = read_map("mines.txt")
    
    # Update mine in the map
    mineMap[x][y] = "1"
    # Update mine in the serial map
    mineSerialMap[x][y] = serial_id
    
    # Write maps back to files
    write_map(mineMap, "map.txt")
    write_map(mineSerialMap, "mines.txt")

    return serial_id


def update_mine_information(serial: str, new_serial: str = None, x: int = None, y: int = None):
    mineSerialMap = read_map("mines.txt")
    mineMap = read_map("map.txt")
    new_mine = Mine()  # creating new instance of mine class
    
    # Helper function to check if coordinates are within the range
    def is_valid_coordinate(x, y):
        return 0 <= x < len(mineSerialMap[0]) and 0 <= y < len(mineSerialMap)

    # Find the mine with the given serial and update it
    for i in range(len(mineSerialMap)):
        for j in range(len(mineSerialMap[i])):
            if mineSerialMap[i][j] == serial:
                # Update serial if provided
                if new_serial is not None:
                    mineSerialMap[i][j] = new_serial
                    new_mine.serial = new_serial

                # Update coordinates if provided
                if x is not None and is_valid_coordinate(x, j):
                    mineSerialMap[i][j] = (new_serial if new_serial else mineSerialMap[i][j], x)
                    mineMap[i][j] = 1
                    new_mine.x = x
                else:
                    print(f"Error: Invalid X-coordinate '{x}' provided. Mine remains at position ({i}, {j}).")

                if y is not None and is_valid_coordinate(i, y):
                    mineSerialMap[i][j] = (new_serial if new_serial else mineSerialMap[i][j], y)
                    mineMap[i][j] = 1
                    new_mine.y = y
                else:
                    print(f"Error: Invalid Y-coordinate '{y}' provided. Mine remains at position ({i}, {j}).")
                
                # Write updated maps to files and return new_mine
                write_map(mineSerialMap, "mines.txt")
                write_map(mineMap, "map.txt")
                return new_mine

    print(f"Error: Serial '{serial}' not found in the map.")
    return False


# --------------------------------------- ROVER FUNCTIONS ---------------------------------------      
    
def find_rover(rover_id: str):
    my_rovers = read_rovers_from_file("rovers.json")
    matching_rovers = [rover for rover in my_rovers if rover.rover_id == rover_id]
    
    return matching_rovers[0] if matching_rovers else None


def addNewRover(commands:str):
    my_rovers = read_rovers_from_file("rovers.json")
    
    new_id = int(my_rovers[-1].rover_id)+1      # current number of rovers + 1
    new_rover = Rover(rover_id=str(new_id),commands=commands,status="Traversal has not begun yet")
    
    my_rovers.append(new_rover)
    write_rovers_to_file(rovers=my_rovers,filename="rovers.json")
    return int(new_rover.rover_id)

def delete_rover(rover_id:str):
    my_rovers = read_rovers_from_file("rovers.json")
    
    for rover in my_rovers:
        if rover.rover_id == rover_id:
            my_rovers.remove(rover)
            write_rovers_to_file(rovers=my_rovers,filename="rovers.json")
            return "Rover has been deleted"
        
    return "Rover does not exist in the list"


def new_commands(rover_id: str, commands: str):
    my_rovers = read_rovers_from_file("rovers.json")

    # Find the rover with the specified ID
    for rover in my_rovers:
        if rover.rover_id == rover_id:
            # Check if rover status allows new commands
            if rover.status == "Traversal has not begun yet" or rover.status == "Finished":
                # Update rover commands
                rover.commands = commands
                # Write updated rover list to file
                write_rovers_to_file(my_rovers, "rovers.json")
                return "New Commands given"
            else:
                # Rover status does not allow new commands
                return "Rover status does not allow new commands"
    
    # Rover with specified ID not found
    return "Rover not found"

# ------------------------------------------------------------------------------

# Rover methods to ensure safe traversal.
def check_boundary(roverPointerDir, x, y, x_border, y_border):
    # Check boundary condition based on the rover's direction
    if roverPointerDir == 'S':
        return y + 1 < y_border
    elif roverPointerDir == 'N':
        return y - 1 >= 0
    elif roverPointerDir == 'E':
        return x + 1 < x_border
    elif roverPointerDir == 'W':
        return x - 1 >= 0
    else:
        return False  # Default to False if direction is invalid



def deactivateMine(mineSerialMap: list[list[str]], y: int, x: int):
    key = generatePIN() + mineSerialMap[y][x]
    hashedKey = hash_key(key)
    while hashedKey[:2] != '00': # zeros in the start
        hashedKey = hash_key(key)
        print(f"Attempting with deactivate using {hashedKey}")
        key = generatePIN() + mineSerialMap[y][x]


def changeRoverDir(current_direction: str, turn: str):
    directions = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
    
    # Calculate the new direction index
    if turn == 'R':
        new_direction_index = (directions[current_direction] + 1) % 4
    else:
        new_direction_index = (directions[current_direction] - 1) % 4
    
    # Return the new direction
    return list(directions.keys())[list(directions.values()).index(new_direction_index)]


def update_rover_list(rover:Rover):
    my_rovers = read_rovers_from_file("rovers.json")
    
    for r in my_rovers:
        if r.rover_id == rover.rover_id:
            r.status = rover.status
            write_rovers_to_file(rovers=my_rovers,filename="rovers.json")
            return 
    
    

                
def beginTraversal(rover_id: str):
    # Read the maps
    mineMap = read_map("map.txt")
    mineSerialMap = read_map("mines.txt")
    
    rover = find_rover(rover_id)
    if rover is None:
        return "Failure to find the Rover"
    
    # Update rover status
    rover.status = "--Traversing--"
    update_rover_list(rover=rover)
    
    # rover location and direction at the start of the map
    y, x = 0, 0
    roverPointerDir = 'S'

    # Traverse the commands
    for m in rover.commands:
        if m == 'D':
            # Disarm the mine
            if mineMap[y][x] == '1':
                deactivateMine(mineSerialMap, y, x)
                mineMap[y][x] = "#"
        elif m == 'M':
            # Move
            if check_boundary(roverPointerDir, x, y, len(mineMap[y]), len(mineMap)):
                if mineMap[y][x] == '1':
                    mineMap[y][x] = "-_-"  
                    rover.status = "Died"
                    update_rover_list(rover=rover)
                    break
                else:
                    
                    if mineMap[y][x] != '#':
                        mineMap[y][x] = "*"
                    dx, dy = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[roverPointerDir]
                    x = min(max(x + dx, 0), len(mineMap[0]) - 1)
                    y = min(max(y + dy, 0), len(mineMap) - 1)
        elif m == 'R' or m == 'L':
            # Change direction
            roverPointerDir = changeRoverDir(roverPointerDir, m)
    
    # final rover status
    rover.status = "Finished"
    update_rover_list(rover=rover)
    
    # Print mine map
    for row in mineMap:
        print(f"Row: {row}")
    
    return mineMap
