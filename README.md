# Wednesday: AI-Powered Robotic Arm Controller

This project enables controlling a servo-driven robotic arm (or similar device) connected to a Raspberry Pi using natural language commands processed by Google's Gemini AI.

## Project Overview

The system consists of two main components:

1.  **Client (`client/`)**:
    *   A Tkinter-based GUI application.
    *   Takes user input in natural language (e.g., "Wave the arm").
    *   Uses the Google Gemini API to translate these commands into a structured JSON list of servo motor actions (pin, angle, duration).
    *   Communicates with the Raspberry Pi server via HTTP (using the MCP library) to send the servo commands.
    *   Requires a `GEMINI_API_KEY` in a `.env` file within the `client` directory.

2.  **Server (`server/`)**:
    *   A Python application designed to run on a Raspberry Pi.
    *   Requires `pigpiod` service to be running.
    *   Exposes an MCP tool (`execute_servo_commands`) over HTTP.
    *   Receives JSON commands from the client and controls servo motors connected to the Raspberry Pi's GPIO pins using the `pigpio` library.
    *   Currently configured for specific GPIO pins (17, 27, 22, 23, 24, 25) with some pins having angle caps.

## Setup

### Server (Raspberry Pi)

1.  **Clone the repository (or copy the `server/` directory) to your Raspberry Pi.**
2.  **Install dependencies:**
    ```bash
    cd server
    pip install -r requirements.txt
    ```
3.  **Ensure `pigpiod` daemon is running:**
    ```bash
    sudo systemctl start pigpiod
    ```
4.  **Run the server:**
    ```bash
    python server.py
    ```
    The server will start by default on port 8011.

### Client (Your Computer)

1.  **Clone the repository (or copy the `client/` directory).**
2.  **Install dependencies:**
    ```bash
    cd client
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file in the `client/` directory:**
    Copy `dot_env_example` to `.env` and add your Google Gemini API Key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
4.  **Run the client application:**
    ```bash
    python wednesday_app.py
    ```
5.  In the application, enter the IP address and port of your Raspberry Pi server and then type your commands.

## How it Works

1.  User types a command like "Lift arm 1 to 30 degrees" into the client GUI.
2.  The client sends this text to the Google Gemini AI, along with a prompt instructing it to convert the command into JSON-formatted servo instructions.
3.  Gemini responds with a JSON list, e.g., `[{"pin": 17, "angle": 30, "duration_ms": 500}]`.
4.  The client application sends this JSON payload to the `/mcp` endpoint on the Raspberry Pi server.
5.  The server parses the JSON and uses the `execute_servo_commands` tool to move the specified servo(s) via `pigpio`.
6.  The server sends back a response, which is displayed in the client's log.

## Project Structure

```
wednesday/
├── client/
│   ├── wednesday_app.py    # Main client GUI application
│   ├── requirements.txt    # Client dependencies
│   └── dot_env_example     # Example for .env file
└── server/
    ├── server.py           # Raspberry Pi server application
    └── requirements.txt    # Server dependencies
``` 