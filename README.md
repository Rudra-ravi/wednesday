# Wednesday - AI Servo Control System

A Python-based project that utilizes the Gemini 2.5 Flash AI model to control servo motors through natural language processing. The system consists of a GUI client and a Raspberry Pi server that communicate through a Model Context Protocol (MCP) compatible interface.

## Overview

Wednesday is a voice-enabled AI assistant that can interpret natural language commands and control a robotic arm with 6 servo motors. The project features:

- 🧠 **Gemini 2.5 Flash** AI model for natural language understanding and response generation
- 💬 **Voice input and output** capabilities for hands-free operation
- 🔧 **Servo motor control** via a Raspberry Pi server
- 🖥️ **Modern GUI** with a JARVIS-inspired interface
- 🔄 **MCP-compatible** API for standardized communication between client and server

## Project Structure

```
wednesday/
├── client/                  # GUI client application
│   ├── wednesday_client.py  # Main client application
│   ├── themes.py            # UI theme configuration
│   ├── requirements.txt     # Python dependencies for client
│   └── dot_env_example      # Example environment variables
├── server/                  # Raspberry Pi server
│   ├── mcp_server.py        # MCP-compatible server
│   ├── requirements.txt     # Python dependencies for server
│   └── dot_env_example      # Example environment variables
└── README.md                # This file
```

## Setup Instructions

### Client Setup (Computer)

1. Install the required dependencies:
   ```bash
   cd client
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the client directory with your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   SERVER_IP=192.168.1.100  # Replace with your Raspberry Pi's IP
   SERVER_PORT=8011
   ```

3. Run the client application:
   ```bash
   python wednesday_client.py
   ```

### Server Setup (Raspberry Pi)

1. Install the required dependencies on your Raspberry Pi:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. Connect the 6 servo motors to your Raspberry Pi using the PCA9685 controller.

3. Create a `.env` file in the server directory:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   SERVER_PORT=8011
   DEBUG=False
   ```

4. Run the server application:
   ```bash
   python mcp_server.py
   ```

## Hardware Configuration

### Servo Motors

The system is configured to control 6 servo motors with the following functions:

- **Servo 0**: Base rotation (0° to 180°)
- **Servo 1**: Shoulder joint (0° to 180°)
- **Servo 2**: Elbow joint (0° to 180°)
- **Servo 3**: Wrist pitch (0° to 180°)
- **Servo 4**: Wrist roll (0° to 180°)
- **Servo 5**: Gripper (0° = open, 180° = closed)

### Wiring Diagram

Connect your PCA9685 servo controller to the Raspberry Pi:

- VCC: 5V power supply
- GND: Ground
- SDA: GPIO 2 (I2C Data)
- SCL: GPIO 3 (I2C Clock)

Then connect each servo motor to channels 0-5 on the PCA9685 controller.

## Usage

1. Launch the client application on your computer.
2. Ensure the server is running on your Raspberry Pi.
3. The client will attempt to connect to the server automatically.
4. You can use either text or voice commands to control the robot.

### Example Commands

- "Move the base servo to 45 degrees"
- "Turn the wrist 90 degrees"
- "Open the gripper"
- "Move the robotic arm to a resting position"
- "Wave hello with the arm"

## Model Context Protocol (MCP)

Wednesday implements a simplified version of the Model Context Protocol (MCP) for client-server communication. The MCP allows the AI model to convert natural language into structured commands that can be executed by the server.

Commands sent to the server follow this format:
```json
{
    "is_command": true,
    "command_type": "servo_control",
    "servo_commands": [
        {
            "servo_id": 0,
            "position": 90,
            "speed": 50
        }
    ],
    "description": "Rotating the base to the center position"
}
```

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Google Gemini for the AI language model
- The Model Context Protocol (MCP) community for inspiration
- Iron Man's JARVIS for the UI design inspiration 