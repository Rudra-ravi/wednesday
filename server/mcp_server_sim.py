from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Import our simulated servo handler
from servo_handler_sim import ServoController 

# Configuration for servo pins
# User specified: 17, 27, 22, 23, 24, 25
SERVO_PINS_CONFIG = {
    17: "servo_1_base", 
    27: "servo_2_shoulder", 
    22: "servo_3_elbow",
    23: "servo_4_wrist_rotate", 
    24: "servo_5_wrist_pitch", 
    25: "servo_6_gripper"
}

# Instantiate the MCP application
# Using stateless_http=True can simplify things if session state across calls isn't strictly needed by MCP itself
# For just calling a tool, stateless is often fine.
mcp_app = FastMCP(name="RaspberryPiServoControlServer_Simulation", stateless_http=True)

# Instantiate the servo controller globally within the server module
# Its lifecycle (init/cleanup) will be managed by the MCP app's lifespan
servo_controller_instance = ServoController(servo_pins_map=SERVO_PINS_CONFIG)

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage application lifecycle: initialize and cleanup servo controller."""
    print("MCP Server Lifespan: Initializing Servo Controller (SIMULATION)...")
    await servo_controller_instance.initialize_gpio()
    if not servo_controller_instance.is_initialized:
        print("Error: Servo controller failed to initialize. Server may not function correctly.")
        # You might want to raise an error here to prevent the server from starting
        # or handle this state in the tool itself.
    try:
        yield {"servo_controller": servo_controller_instance} # Pass controller if needed in context (not typical for FastMCP tools)
    finally:
        print("MCP Server Lifespan: Cleaning up Servo Controller (SIMULATION)...")
        await servo_controller_instance.cleanup_gpio()

# Assign the lifespan manager to the MCP application
mcp_app.lifespan = app_lifespan

@mcp_app.tool(description="Executes a list of servo movement commands on the Raspberry Pi (SIMULATION).")
async def execute_servo_commands(commands: list[dict]) -> str:
    """
    Receives a list of command objects, where each object should have:
    - "pin": integer (BCM GPIO pin number)
    - "angle": integer (0-180 degrees)
    - "duration_ms": optional integer (time for movement/hold in milliseconds, defaults to 500)
    Returns a string indicating the status of command processing.
    """
    print(f"MCP Tool 'execute_servo_commands' called with: {commands}")
    if not servo_controller_instance.is_initialized:
        error_msg = "Error: Servo controller is not initialized. Cannot execute commands."
        print(error_msg)
        # The MCP SDK handles returning errors from tools. 
        # Raising an exception here would also work and be potentially clearer for the client.
        # For now, returning an error string.
        return error_msg 

    try:
        # The process_commands method in ServoController is already async
        result_message = await servo_controller_instance.process_commands(commands)
        print(f"Servo command processing result: {result_message}")
        return result_message
    except Exception as e:
        # Catch-all for unexpected errors during command processing
        error_msg = f"An unexpected error occurred in execute_servo_commands: {str(e)}"
        print(error_msg)
        # Again, consider raising an exception that MCP can serialize, 
        # or ensure your string clearly indicates an error.
        return error_msg

if __name__ == "__main__":
    server_host = "127.0.0.1" # Listen on localhost for simulation
    server_port = 8011
    print(f"Starting SIMULATED Raspberry Pi Servo Control MCP Server on {server_host}:{server_port}...")
    
    # According to newer MCP SDK, we should use transport parameter without host/port
    # We'll use a simpler call that works with the current version
    mcp_app.run(transport="stdio") 