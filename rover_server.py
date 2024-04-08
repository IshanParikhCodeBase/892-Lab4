from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rover_func import read_map,Mine, write_map
from rover_func import findMine_usingID,deleteMine_usingID,add_new_mine,update_mine_information
from rover_func import read_rovers_from_file,find_rover,addNewRover,delete_rover,new_commands,beginTraversal,RoverReq
from rover_func import addNewRover 
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

# fast api instantiation
app = FastAPI()

cors_allowed_origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost",
    "null",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creation of the methods
rover_list = []

# Map Requests
@app.get("/map", response_class=HTMLResponse)
async def get_map():
    field_map = read_map("map.txt")
    html_content = "<h1>Map for rover traversal</h1><table border='2'>"
    for row in field_map:
        html_content += "<tr>"
        for item in row:
            html_content += "<td>{}</td>".format(item)
        html_content += "</tr>"
    html_content += "</table>"
    return html_content


@app.put("/updatemap", response_class=HTMLResponse)
@app.post("/updatemap", response_class=HTMLResponse)
async def update_map(h: int = Form(...), w: int = Form(...)):
    # To update the height and width of the field
    array = read_map("map.txt")
    old_height = len(array)
    old_width = len(array[0]) if old_height > 0 else 0

    # Initialize new array with None
    new_array = [["0" for _ in range(w)] for _ in range(h)]

    # Copy old data into new array
    for i in range(min(old_height, h)):
        for j in range(min(old_width, w)):
            new_array[i][j] = array[i][j]
    
    # Write updated map to file
    write_map("map.txt", new_array)

    # Generate HTML response with updated map
    html_content = "<h1>Updated Field Map</h1><table border='1'>"
    for row in new_array:
        html_content += "<tr>"
        for item in row:
            html_content += "<td>{}</td>".format(item)
        html_content += "</tr>"
    html_content += "</table>"
    
    return html_content

@app.get("/updatemap", response_class=HTMLResponse)
async def get_map_form():
    # Return HTML form to input new height and width
    return """
        <h1>Update Field Map</h1>
        <form method='post'>
            <label for='height'>Height:</label>
            <input type='number' id='height' name='h'><br>
            <label for='width'>Width:</label>
            <input type='number' id='width' name='w'><br>
            <input type='submit' value='Update Map'>
        </form>
    """

# Mines Requests -----------------------------------------------------------------

@app.get("/mines", response_class=HTMLResponse)
async def get_map():
    serial_map = read_map("mines.txt")
    html_content = "<h1>Map with the mines</h1><table border='2'>"
    for row in serial_map:
        html_content += "<tr>"
        for item in row:
            html_content += "<td>{}</td>".format(item)
        html_content += "</tr>"
    html_content += "</table>"
    return html_content

@app.get("/mines/{id}")
def mine_related(id:str):
    return findMine_usingID(read_map("mines.txt"),id)

@app.delete("/deletemines/{id}")
def mine_related(id:str):
    return deleteMine_usingID(read_map("mines.txt"),id)

def write_mine_to_file(mine: Mine):
    # Write mine information to the mines.txt file
    with open("mines.txt", "a") as f:
        f.write(f"{mine.serial} {mine.x} {mine.y}\n")

@app.get("/createmines", response_class=HTMLResponse)
async def get_mine_form():
    # Return HTML form to input mine information
    return """
        <h1>Create Mine</h1>
<form method='post'>
    <label for='serial'>Serial:</label>
    <input type='text' id='serial' name='serial'><br>
    <label for='x'>X-coordinate:</label>
    <input type='number' id='x' name='x'><br>
    <label for='y'>Y-coordinate:</label>
    <input type='number' id='y' name='y'><br>
    <input type='submit' value='Create Mine'>
</form>

    """

@app.post("/createmines")
async def create_mine(serial: str, x: int, y: int):
    # Write mine information to the file
    with open("mines.txt", "a") as f:
        f.write(f"{serial} {x} {y}\n")
    
    # Return success message
    return {"message": "Mine created successfully"}

@app.get("/updatemines/{id}", response_class=HTMLResponse)
async def get_mine_form(id: str):
    # Return HTML form to input new serial for the mine
    return f"""
        <h1>Update Mine Information for ID: {id}</h1>
        <form method='put'>
            <label for='new_serial'>New Serial:</label>
            <input type='text' id='new_serial' name='new_serial'><br>
            <label for='x'>X Coordinate:</label>
            <input type='number' id='x' name='x'><br>
            <label for='y'>Y Coordinate:</label>
            <input type='number' id='y' name='y'><br>
            <input type='submit' value='Update Mine'>
        </form>
    """

# Rover Requests -----------------------------------------------------------------

@app.get("/rovers", response_class=HTMLResponse)
def get_rovers():
    rovers = read_rovers_from_file("rovers.json")
    
    # Generate HTML content for the rovers table
    html_content = "<h1>Rovers Information</h1>"
    html_content += "<table border='1'>"
    html_content += "<tr><th>Rover ID</th><th>Commands</th><th>Status</th></tr>"
    for rover in rovers:
        html_content += f"<tr><td>{rover.rover_id}</td><td>{rover.commands}</td><td>{rover.status}</td></tr>"
    html_content += "</table>"
    
    return html_content


@app.get("/rovers/{rover_id}", response_class=HTMLResponse)
def get_rover(rover_id: str):
    rover = find_rover(rover_id)
    if rover:
        html_content = f"""
            <h1>Rover Information</h1>
            <p><strong>Rover ID:</strong> {rover.rover_id}</p>
            <p><strong>Commands:</strong> {rover.commands}</p>
            <p><strong>Status:</strong> {rover.status}</p>
        """
        return html_content
    else:
        return HTMLResponse(content="<h1>Rover not found</h1>", status_code=404)

@app.post("/addrovers", response_class=HTMLResponse)
async def create_rvr(request: Request, commands: str = Form(...)):
    # Logic to create a new rover with commands
    addNewRover(commands)
    
    # Return HTML response indicating the rover has been added
    return HTMLResponse(content="<h1>Rover added successfully! Check JSON</h1>", status_code=200)

@app.get("/addrovers", response_class=HTMLResponse)
async def get_rvr_form():
    # Return HTML form to input rover commands
    return HTMLResponse(content="<h1>Enter Rover Commands:</h1><form method='post'><input type='text' name='commands'><input type='submit' value='Confirm'></form>", status_code=200)

# Endpoint to delete a rover --- enter rover ID on text field
@app.get("/deleterover", response_class=HTMLResponse)
async def get_delete_rvr_form():
    # Return HTML form to input rover ID for deletion
    return HTMLResponse(content="<h1>Delete Rover</h1><form method='post'><input type='text' name='rover_id'><input type='submit' value='Delete'></form>", status_code=200)

# POST endpoint to handle form submission for deleting a rover
@app.post("/deleterover", response_class=HTMLResponse)
async def delete_rvr(request: Request, rover_id: str = Form(...)):
    # Call the delete_rover function to delete the rover with the specified ID
    result = delete_rover(rover_id)
    
    # Check if rover deletion was successful
    if result == "Rover has been deleted":
        # Return HTML response indicating the rover has been deleted
        return HTMLResponse(content=f"<h1>Rover {rover_id} has been deleted successfully!</h1>", status_code=200)
    else:
        # If rover was not found, return HTML response with error message
        return HTMLResponse(content="<h1>Error: Rover not found</h1>", status_code=404)

# updating commands for a rover, enter rover ID in url as well!
@app.get("/newcmds/{rover_id}", response_class=HTMLResponse)
async def get_commands_form(rover_id: str):
    # Return HTML form to input rover commands
    return HTMLResponse(
        content=f"<h1>Enter Commands for Rover {rover_id}:</h1>"
                f"<form method='post'><input type='text' name='commands'>"
                f"<input type='submit' value='Update'></form>",
        status_code=200
    )

# Endpoint to handle updating commands when form is submitted
@app.post("/newcmds/{rover_id}", response_class=HTMLResponse)
async def send_commands(rover_id: str, commands: str = Form(...)):
    # Logic to send commands to the specified rover
    result = new_commands(rover_id, commands)
    
    # Construct HTML response message
    if result == "New Commands given":
        message = "<h1>Commands updated successfully, check JSON</h1>"
    else:
        message = "<h1>Failed to update commands, Rover does not exist!</h1>"

    # Return HTML response
    return HTMLResponse(content=message, status_code=200)

@app.route("/rovers/{rover_id}/dispatch", methods=["GET", "POST"])
def dispatch_rover(rover_id: str, commands: str = None):
    if commands is not None:  # POST request
        # Logic to dispatch a rover with its ID, status, latest position, and executed commands
        mineMap = beginTraversal(rover_id=rover_id)
        
        # Convert mineMap to HTML format for visualization
        html_content = "<h1>Rover Traversal Map</h1>"
        for row in mineMap:
            html_content += "<h1>" + " ".join(row) + "</h1>"
        
        # Add dispatch success message
        html_content += "<h1>Dispatch successful</h1>"
        
        return HTMLResponse(content=html_content, status_code=200)
    else:  # GET request
        # Return HTML form to input rover ID for dispatch
        form_content = f"<h1>Enter Commands for Rover ID: {rover_id}</h1><form method='post'><input type='text' name='commands'><input type='submit' value='Dispatch'></form>"
        return HTMLResponse(content=form_content, status_code=200)