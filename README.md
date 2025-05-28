# Wednesday: AI-Powered Robotic Arm Controller

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%2B-red.svg)](https://www.raspberrypi.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://github.com/modelcontextprotocol)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This project enables controlling a servo-driven robotic arm (or similar device) connected to a Raspberry Pi using natural language commands processed by Google's Gemini AI. It leverages the **Model Context Protocol (MCP)** for standardized communication between the client application and the server running on the Raspberry Pi.

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Hardware Setup](#-hardware-setup)
- [Software Installation](#-software-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Functionality
- **Natural Language Control**: Issue commands in plain English (e.g., "Wave the arm", "Move servo 1 to 45 degrees")
- **AI-Powered Translation**: Google Gemini AI converts natural language to precise servo commands
- **Real-time Control**: Direct servo motor control with customizable timing and positioning
- **Multi-Servo Support**: Control up to 6 servos simultaneously on GPIO pins 17, 27, 22, 23, 24, 25
- **Safety Features**: Built-in angle limits and validation for specific servo configurations

### Technical Features
- **MCP Protocol**: Standardized communication protocol for AI-tool interaction
- **Cross-Platform Client**: Tkinter-based GUI that runs on Windows, macOS, and Linux
- **Async Architecture**: Non-blocking operations for responsive user interface
- **Error Handling**: Comprehensive error reporting and status monitoring
- **Logging System**: Detailed operation logs for debugging and monitoring

### User Interface
- **Modern GUI**: Dark-themed interface with intuitive controls
- **Real-time Status**: Live status updates and command execution feedback
- **Command History**: Log of all commands and responses
- **Connection Management**: Easy server IP and port configuration


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

## 🔧 System Requirements

### Hardware Requirements

#### Raspberry Pi (Server)
- **Model**: Raspberry Pi 4B (recommended) or Raspberry Pi 3B+
- **RAM**: Minimum 2GB, 4GB recommended
- **Storage**: MicroSD card (16GB+, Class 10)
- **GPIO**: Access to GPIO pins for servo connections
- **Power**: 5V 3A power supply (official Raspberry Pi power supply recommended)

#### Servo Motors
- **Type**: Standard hobby servos (SG90, MG996R, or similar)
- **Voltage**: 4.8V-6V operation
- **Signal**: PWM control (50Hz, 1-2ms pulse width)
- **Quantity**: Up to 6 servos supported

#### Additional Hardware
- **Breadboard/PCB**: For connections and power distribution
- **Jumper Wires**: Male-to-male and male-to-female
- **External Power Supply**: 5V-6V for servos (separate from Pi power)
- **Capacitors**: 1000µF capacitors for servo power stabilization (recommended)

### Software Requirements

#### Client Computer
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.11 or higher
- **Internet**: Required for Gemini AI API access
- **Network**: Local network access to Raspberry Pi

#### Raspberry Pi
- **OS**: Raspberry Pi OS (Bullseye or newer)
- **Python**: Version 3.11 (typically pre-installed)
- **pigpio**: Daemon for precise GPIO control
- **Network**: WiFi or Ethernet connection

## 🏗 Architecture Overview

### System Components

The system consists of two main components communicating via the Model Context Protocol:

```
┌─────────────────┐    HTTP/MCP     ┌─────────────────┐
│                 │ ──────────────► │                 │
│  Client App     │                 │  Raspberry Pi   │
│  (Your PC)      │ ◄────────────── │  Server         │
│                 │    JSON/MCP     │                 │
└─────────────────┘                 └─────────────────┘
        │                                     │
        │                                     │
        ▼                                     ▼
┌─────────────────┐                 ┌─────────────────┐
│  Gemini AI      │                 │  Servo Motors   │
│  (Google)       │                 │  (Hardware)     │
└─────────────────┘                 └─────────────────┘
```

### Data Flow

1. **User Input**: Natural language command entered in GUI
2. **AI Processing**: Gemini AI converts text to structured servo commands
3. **MCP Communication**: Client sends commands to Pi server via MCP protocol
4. **Hardware Control**: Server executes commands using pigpio library
5. **Feedback**: Status and results returned to client

### MCP Integration

The Model Context Protocol provides:
- **Standardized Tool Definition**: Server exposes `execute_servo_commands` tool
- **Type Safety**: Structured JSON schema for command validation
- **Error Handling**: Standardized error reporting and status codes
- **Discoverability**: Client can query available tools and their schemas

## 📁 Project Structure

```
wednesday/
├── client/                          # Client application
│   ├── wednesday_app.py            # Main GUI application (429 lines)
│   ├── requirements.txt            # Python dependencies
│   ├── dot_env_example             # Environment file template
│   └── .env                        # API keys (create from template)
├── server/                          # Raspberry Pi server
│   ├── server.py                   # MCP server implementation (110 lines)
│   └── requirements.txt            # Python dependencies
├── README.md                       # This documentation
├── LICENSE                         # MIT License
└── docs/                           # Additional documentation (optional)
    ├── hardware_setup.md           # Detailed hardware instructions
    ├── api_reference.md            # API documentation
    └── troubleshooting.md          # Common issues and solutions
```

### Key Files Description

#### Client Files
- **`wednesday_app.py`**: Main application with Tkinter GUI, Gemini integration, and MCP client
- **`requirements.txt`**: Dependencies including `google-generativeai`, `mcp[cli]`, `python-dotenv`
- **`.env`**: Configuration file containing Gemini API key

#### Server Files
- **`server.py`**: FastMCP server with servo control logic and safety features
- **`requirements.txt`**: Dependencies including `mcp[cli]`, `pigpio`, `fastmcp`

## 🔌 Hardware Setup

### GPIO Pin Configuration

The server is configured to control servos on the following GPIO pins:

| GPIO Pin | Description | Angle Limit | Typical Use |
|----------|-------------|-------------|-------------|
| 17       | Servo 1     | 0-45°       | Base rotation (limited) |
| 27       | Servo 2     | 0-45°       | Shoulder joint (limited) |
| 22       | Servo 3     | 0-45°       | Elbow joint (limited) |
| 23       | Servo 4     | 0-180°      | Wrist rotation |
| 24       | Servo 5     | 0-180°      | Wrist tilt |
| 25       | Servo 6     | 0-180°      | Gripper/end effector |

### Wiring Diagram

```
Raspberry Pi                    Servo Motors
┌─────────────┐                ┌─────────────┐
│ GPIO 17 ────┼────────────────┼─── Signal   │ Servo 1
│ GPIO 27 ────┼────────────────┼─── Signal   │ Servo 2
│ GPIO 22 ────┼────────────────┼─── Signal   │ Servo 3
│ GPIO 23 ────┼────────────────┼─── Signal   │ Servo 4
│ GPIO 24 ────┼────────────────┼─── Signal   │ Servo 5
│ GPIO 25 ────┼────────────────┼─── Signal   │ Servo 6
│ 5V ─────────┼────────────────┼─── VCC      │ (All servos)
│ GND ────────┼────────────────┼─── GND      │ (All servos)
└─────────────┘                └─────────────┘
```

### Assembly Instructions

1. **Power Distribution**:
   - Use a separate 5V-6V power supply for servos
   - Connect servo VCC to external power supply positive
   - Connect servo GND to both external power supply negative AND Raspberry Pi GND
   - This prevents power draw issues on the Pi

2. **Signal Connections**:
   - Connect each servo signal wire to its designated GPIO pin
   - Use jumper wires or a custom PCB for clean connections
   - Ensure solid connections to prevent signal interference

3. **Mechanical Assembly**:
   - Mount servos according to your robotic arm design
   - Ensure servo horns are properly aligned
   - Test mechanical range of motion before applying power

## 💾 Software Installation

### Server Setup (Raspberry Pi)

1. **Update System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install pigpio**:
   ```bash
   sudo apt install pigpio python3-pigpio -y
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```

3. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/wednesday.git
   cd wednesday/server
   ```

4. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Test pigpio Installation**:
   ```bash
   python3 -c "import pigpio; pi = pigpio.pi(); print(f'pigpio version: {pi.get_pigpio_version()}')"
   ```

6. **Run Server**:
   ```bash
   python3 server.py
   ```

### Client Setup (Your Computer)

1. **Prerequisites**:
   - Python 3.11 installed
   - pip package manager
   - Internet connection

2. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/wednesday.git
   cd wednesday/client
   ```

3. **Create Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**:
   ```bash
   cp dot_env_example .env
   # Edit .env file and add your Gemini API key
   ```

6. **Run Client**:
   ```bash
   python wednesday_app.py
   ```

## ⚙️ Configuration

### Gemini API Setup

1. **Get API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key for configuration

2. **Configure Client**:
   ```bash
   # Edit client/.env file
   GEMINI_API_KEY="your_actual_api_key_here"
   ```

### Server Configuration

The server configuration is defined in `server/server.py`:

```python
# Pin Configuration
ALLOWED_PINS = {17, 27, 22, 23, 24, 25}
PINS_WITH_ANGLE_CAP = {17, 27, 22}
MAX_ANGLE_FOR_CAPPED_PINS = 45.0

# Servo Parameters
MIN_PULSE_WIDTH = 500    # microseconds
MAX_PULSE_WIDTH = 2500   # microseconds
MIN_ANGLE = 0.0          # degrees
MAX_ANGLE = 180.0        # degrees
```

### Network Configuration

1. **Find Raspberry Pi IP**:
   ```bash
   # On Raspberry Pi:
   hostname -I
   # Or check router's admin panel
   ```

2. **Configure Client**:
   - Open client application
   - Enter Raspberry Pi IP address
   - Default port: 8011

### Firewall Configuration

```bash
# On Raspberry Pi (if firewall is enabled):
sudo ufw allow 8011/tcp
```

## 📖 Usage Guide

### Basic Commands

The system understands natural language commands. Here are examples:

#### Simple Movements
- `"Move servo 1 to 30 degrees"`
- `"Set arm position to 45 degrees"`
- `"Rotate base to 90 degrees"`

#### Complex Movements
- `"Wave the arm"` → Multiple servos moving in sequence
- `"Open and close gripper"` → Servo 6 movement pattern
- `"Move to home position"` → All servos to 0 degrees

#### Multi-Servo Commands
- `"Move servo 1 to 30 and servo 2 to 45 degrees"`
- `"Set all servos to 90 degrees"`
- `"Move servos 1, 2, and 3 to 30, 45, and 60 degrees"`

### GUI Operation

1. **Connect to Server**:
   - Enter Raspberry Pi IP address
   - Verify port (default: 8011)
   - Check connection status

2. **Send Commands**:
   - Type natural language command
   - Click "Send Command to Pi"
   - Monitor status and log output

3. **Monitor Results**:
   - Watch status updates
   - Review command execution logs
   - Check for error messages

### Command Examples

#### JSON Command Format

The Gemini AI converts natural language to JSON commands:

```json
[
  {
    "pin": 17,
    "angle": 30.0,
    "duration_ms": 500
  },
  {
    "pin": 23,
    "angle": 90.0,
    "duration_ms": 1000
  }
]
```

#### Command Parameters

- **pin**: GPIO pin number (17, 27, 22, 23, 24, 25)
- **angle**: Target angle in degrees (0-180, some pins limited to 0-45)
- **duration_ms**: Hold time in milliseconds (default: 500)

## 📚 API Documentation

### MCP Server Tools

#### `execute_servo_commands`

Executes a batch of servo movements.

**Parameters**:
- `commands` (list[dict]): Array of servo command objects

**Command Object**:
```python
{
    "pin": int,          # GPIO pin (17,27,22,23,24,25)
    "angle": float,      # Angle in degrees (0-180)
    "duration_ms": int   # Optional: hold duration (default 500ms)
}
```

**Response**:
```python
[
    {
        "pin": int,
        "status": str,      # "ok" or "error"
        "message": str      # Status description
    }
]
```

### Client API

#### `WednesdayApp` Class

Main application class managing GUI and MCP communication.

**Key Methods**:
- `submit_text_action_async()`: Process user commands
- `get_gemini_instructions()`: Convert text to servo commands
- `send_commands_to_pi_mcp()`: Execute commands on Pi

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `invalid_pin` | Invalid GPIO pin | Use pins 17,27,22,23,24,25 |
| `invalid_angle` | Angle out of range | Use 0-180° (0-45° for pins 17,27,22) |
| `pigpio_error` | Hardware communication error | Check pigpiod service |
| `connection_error` | Network communication failed | Verify IP address and network |

## 🛠 Troubleshooting

### Common Issues

#### Server Issues

**Problem**: "Failed to connect to pigpio daemon"
```bash
# Solution:
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```

**Problem**: "Port 8011 already in use"
```bash
# Solution:
sudo netstat -tlnp | grep 8011
sudo kill <process_id>
```

**Problem**: Servos not responding
- Check wiring connections
- Verify servo power supply
- Test individual servos
- Check GPIO pin assignments

#### Client Issues

**Problem**: "GEMINI_API_KEY not found"
- Verify `.env` file exists in client directory
- Check API key format and validity
- Ensure no extra spaces or quotes

**Problem**: "Connection refused"
- Verify Raspberry Pi IP address
- Check if server is running
- Test network connectivity: `ping <pi_ip>`
- Verify firewall settings

**Problem**: GUI freezes
- Check async loop functionality
- Restart application
- Verify Python version compatibility

### Debug Mode

Enable debug logging in server:

```python
# Add to server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Enable verbose client logging:

```python
# In wednesday_app.py, modify log_message calls
self.log_message(f"DEBUG: {debug_info}", level="DEBUG")
```

### Performance Tuning

#### Server Optimization
- Increase pigpio sampling rate
- Optimize servo update frequency
- Use hardware PWM for critical servos

#### Network Optimization
- Use wired connection for Pi
- Optimize MCP message size
- Implement command queuing



## 🔍 What is MCP (Model Context Protocol)?

MCP is an open protocol designed to standardize how AI models and applications (like our client) interact with external tools and services (like our Raspberry Pi server). 

### Key Benefits in This Project

- **Standardized Tool Usage**: The server exposes its servo control functionality as an MCP "tool". The client can discover and call this tool using a standard MCP mechanism, rather than custom API calls.

- **Type Safety**: MCP provides structured schemas for tool definitions, ensuring type safety and validation of commands.

- **Decoupling**: The client doesn't need to know the fine-grained details of how the server implements servo control. It only needs to understand the MCP tool's interface (name, arguments, expected output).

- **Interoperability**: While this project uses a custom client and server, MCP enables different AI agents and tools to work together more easily.

- **Error Handling**: Standardized error reporting and status codes across the protocol.

### MCP Implementation Details

In this project, the `mcp` Python library (specifically `mcp[cli]`) is used on both the client and server to implement this protocol:

- **Server**: Uses `FastMCP` to expose servo control tools
- **Client**: Uses `streamablehttp_client` to communicate with MCP servers
- **Protocol**: HTTP transport layer for communication
- **Format**: JSON-structured messages with defined schemas

## 🎯 Development

### Adding New Features

#### New Servo Commands

1. **Extend Command Schema**:
   ```python
   # Add new command types to Gemini prompt
   NEW_COMMANDS = {
       "sequence": "Execute predefined movement sequence",
       "calibrate": "Calibrate servo positions",
       "speed": "Control movement speed"
   }
   ```

2. **Update Server Logic**:
   ```python
   # In server.py, extend execute_servo_commands
   if cmd.get("type") == "sequence":
       await execute_sequence(cmd.get("sequence_name"))
   ```

#### New Hardware Support

1. **Extend Pin Configuration**:
   ```python
   ALLOWED_PINS = {17, 27, 22, 23, 24, 25, 26, 19}  # Add new pins
   ```

2. **Add Hardware-Specific Limits**:
   ```python
   PIN_LIMITS = {
       17: (0, 45),    # Base rotation
       26: (30, 150),  # New servo with custom range
   }
   ```

### Testing

#### Unit Tests

Create test files for core functionality:

```python
# tests/test_servo_commands.py
import pytest
from server import execute_servo_commands

@pytest.mark.asyncio
async def test_valid_servo_command():
    commands = [{"pin": 17, "angle": 30, "duration_ms": 500}]
    results = await execute_servo_commands(commands)
    assert results[0]["status"] == "ok"
```

#### Integration Tests

Test MCP communication:

```python
# tests/test_mcp_integration.py
async def test_mcp_tool_execution():
    # Test MCP client-server communication
    pass
```

### Code Style

Follow PEP 8 guidelines:

```bash
# Install development tools
pip install black flake8 mypy

# Format code
black *.py

# Check style
flake8 *.py

# Type checking
mypy *.py
```

## 🤝 Contributing

### Getting Started

1. **Fork the Repository**
2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make Changes** following code style guidelines
4. **Add Tests** for new functionality
5. **Submit Pull Request**

### Areas for Contribution

- **Hardware Support**: Add support for different servo types
- **UI Improvements**: Enhance the client interface
- **Command Extensions**: Add new natural language commands
- **Documentation**: Improve guides and tutorials
- **Testing**: Expand test coverage
- **Performance**: Optimize servo control timing

### Development Environment

```bash
# Setup development environment
git clone https://github.com/yourusername/wednesday.git
cd wednesday

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 client/ server/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: For natural language processing capabilities
- **Model Context Protocol**: For standardized AI-tool communication
- **pigpio Library**: For precise Raspberry Pi GPIO control
- **Tkinter**: For cross-platform GUI framework
- **Open Source Community**: For tools and libraries that made this project possible

---

**Happy Robotics! 🤖**

*Built with ❤️ by the Wednesday Team*
