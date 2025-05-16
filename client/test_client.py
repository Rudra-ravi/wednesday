import asyncio
import sys
import json
import subprocess
import time

async def run_test_client():
    """
    A simplified test client that launches the server as a subprocess and communicates via stdio.
    """
    print("Starting test client for simulated servo server...")
    
    # Launch the server as a subprocess
    server_process = subprocess.Popen(
        ["python3", "../server/mcp_server_sim.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Give the server a moment to initialize
    await asyncio.sleep(1)
    
    # Example commands to move various servos
    test_commands = [
        # Wave motion with the arm
        {"pin": 17, "angle": 45, "duration_ms": 1000},  # Base
        {"pin": 22, "angle": 30, "duration_ms": 800},   # Elbow
        {"pin": 24, "angle": 120, "duration_ms": 500},  # Wrist pitch
        
        # Return to neutral position
        {"pin": 24, "angle": 90, "duration_ms": 500},   # Wrist pitch
        {"pin": 22, "angle": 90, "duration_ms": 800},   # Elbow
        {"pin": 17, "angle": 90, "duration_ms": 1000},  # Base
        
        # Open and close gripper
        {"pin": 25, "angle": 180, "duration_ms": 1000}, # Open gripper
        {"pin": 25, "angle": 0, "duration_ms": 1000},   # Close gripper
    ]
    
    # Create an MCP message to call the execute_servo_commands tool
    mcp_message = {
        "type": "call_tool",
        "tool_name": "execute_servo_commands",
        "tool_args": {"commands": test_commands}
    }
    
    print(f"Sending command to server: {mcp_message}")
    
    # Convert the message to JSON and send it to the server
    json_message = json.dumps(mcp_message) + "\n"
    server_process.stdin.write(json_message)
    server_process.stdin.flush()
    
    # Read the response from the server
    response_line = server_process.stdout.readline()
    
    try:
        response = json.loads(response_line)
        print(f"Response from server: {response}")
    except json.JSONDecodeError:
        print(f"Error parsing server response: {response_line}")
    
    # Terminate the server process
    print("Shutting down server process...")
    server_process.terminate()
    server_process.wait(timeout=5)
    
    print("Test client completed.")

if __name__ == "__main__":
    asyncio.run(run_test_client()) 