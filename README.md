# Raspberry Pi Servo Control with MCP

This project demonstrates controlling servo motors on a Raspberry Pi using the Model Context Protocol (MCP). It consists of a server component that runs on the Raspberry Pi and controls the servos, and a client component that sends commands to the server.

## Project Structure

- **server/**: Contains the MCP server that runs on the Raspberry Pi
  - `mcp_server.py`: The main server for actual Raspberry Pi hardware
  - `mcp_server_sim.py`: A simulated version for testing without hardware
  - `servo_handler.py`: Controls the servo motors using RPi.GPIO
  - `servo_handler_sim.py`: A simulated version for testing without hardware
  - `requirements.txt`: Python dependencies for the server

- **client/**: Contains the client application
  - `wednesday_app.py`: A Tkinter GUI application that uses Gemini to interpret commands
  - `test_client.py`: A simple test client for the server
  - `requirements.txt`: Python dependencies for the client

## Setup

### Server Setup (Raspberry Pi)

1. Install the required dependencies:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python mcp_server.py
   ```

### Client Setup

1. Install the required dependencies:
   ```bash
   cd client
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the client directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Run the client:
   ```bash
   python wednesday_app.py
   ```

## Testing Without Hardware

For testing without a Raspberry Pi, you can use the simulated versions:

1. Run the simulated server:
   ```bash
   cd server
   python mcp_server_sim.py
   ```

2. Run the test client:
   ```bash
   cd client
   python test_client.py
   ```

## Servo Configuration

The server is configured to control 6 servo motors connected to the following GPIO pins:

- Pin 17: Base servo
- Pin 27: Shoulder servo
- Pin 22: Elbow servo
- Pin 23: Wrist rotation servo
- Pin 24: Wrist pitch servo
- Pin 25: Gripper servo

## Protocol

The server exposes a tool called `execute_servo_commands` that accepts a list of commands. Each command is a dictionary with the following fields:

- `pin`: The GPIO pin number the servo is connected to
- `angle`: The target angle in degrees (0-180)
- `duration_ms`: (Optional) Time to take for the movement in milliseconds (defaults to 500ms)

Example command:
```json
{
  "commands": [
    {"pin": 17, "angle": 45, "duration_ms": 1000},
    {"pin": 22, "angle": 30, "duration_ms": 800}
  ]
}
```

## License

This project is open source and available under the MIT License. 