# Wednesday: AI-Powered Robotic Arm Controller

This project enables controlling a servo-driven robotic arm (or similar device) connected to a Raspberry Pi using natural language commands processed by Google's Gemini AI. It leverages the **Model Context Protocol (MCP)** for standardized communication between the client application and the server running on the Raspberry Pi.

## Project Overview

The system consists of two main components:

1.  **Client (`client/`)**:
    *   A Tkinter-based GUI application.
    *   Takes user input in natural language (e.g., "Wave the arm").
    *   Uses the Google Gemini API to translate these commands into a structured JSON list of servo motor actions (pin, angle, duration).
    *   Communicates with the Raspberry Pi server via HTTP using the **Model Context Protocol (MCP)** client libraries. Specifically, it uses MCP to discover and call the `execute_servo_commands` tool exposed by the server.
    *   Requires a `GEMINI_API_KEY` in a `.env` file within the `client` directory.

2.  **Server (`server/`)**:
    *   A Python application designed to run on a Raspberry Pi.
    *   Requires `pigpiod` service to be running.
    *   Exposes an MCP tool named `execute_servo_commands` over HTTP. This tool accepts servo commands and uses the `pigpio` library to control servo motors connected to the Raspberry Pi's GPIO pins.
    *   The use of MCP allows the server to define its capabilities (i.e., the servo control tool) in a standardized way that any MCP-compliant client can interact with.
    *   Currently configured for specific GPIO pins (17, 27, 22, 23, 24, 25) with some pins having angle caps.


## 🚀 Working

### Demonstration Video
[![Working Demo](https://github.com/user-attachments/assets/52ea6d9a-40a0-485d-badb-8fbba3c78d12)](https://github.com/user-attachments/assets/52ea6d9a-40a0-485d-badb-8fbba3c78d12)

### System in Operation
![System Connected and Running](https://github.com/user-attachments/assets/81b0b9e8-7ffd-45a9-a0ed-b2cd4de480a4)

### System Architecture
![Block Diagram](https://github.com/user-attachments/assets/6d5ca818-dda1-4e8b-9120-64d6825ca72a)

### Hardware Implementation
<div align="center">
  <img src="https://github.com/user-attachments/assets/11ca076c-a456-4f72-97af-7fbbc5abbbed" alt="3D Printed Components" width="45%" />
  <img src="https://github.com/user-attachments/assets/dcb6a9c0-7cc7-44ed-9b91-29f5a90eafde" alt="Hardware Assembly" width="45%" />
</div>







## What is MCP (Model Context Protocol)?

MCP is an open protocol designed to standardize how AI models and applications (like our client) interact with external tools and services (like our Raspberry Pi server). Key benefits in this project include:

*   **Standardized Tool Usage**: The server exposes its servo control functionality as an MCP "tool". The client can discover and call this tool using a standard MCP mechanism, rather than custom API calls.
*   **Decoupling**: The client doesn't need to know the fine-grained details of how the server implements servo control. It only needs to understand the MCP tool's interface (name, arguments, expected output).
*   **Interoperability (Potential)**: While this project uses a custom client and server, MCP aims to allow different AI agents and tools to work together more easily.

In this project, the `mcp` Python library (specifically `mcp[cli]`) is used on both the client and server to implement this protocol.

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
4.  The client application, using its MCP client capabilities, sends this JSON payload as arguments to the `execute_servo_commands` tool on the Raspberry Pi server. This is done via an HTTP request structured according to MCP specifications.
5.  The MCP server on the Raspberry Pi receives the tool call, parses the JSON, and its `execute_servo_commands` function uses `pigpio` to move the specified servo(s).
6.  The server sends back a response (e.g., status of each servo command), again structured as an MCP tool result, which is displayed in the client's log.

## Project Structure

```
├── client
│   ├── dot_env_example
│   ├── requirements.txt
│   └── wednesday_app.py
├── README.md
├── server
│   ├── requirements.txt
│   └── server.py

```
