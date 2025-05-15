#!/usr/bin/env python3
import os
import sys
import json
import time
from flask import Flask, request, jsonify
from adafruit_servokit import ServoKit
import google.generativeai as genai
from dotenv import load_dotenv
import threading
import logging
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Wednesday-Server")

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Initialize the Flask app
app = Flask(__name__)

# Initialize the servo controller
try:
    # Initialize ServoKit for PCA9685 controller with 16 channels
    logger.info("Initializing servo controller...")
    kit = ServoKit(channels=16)
    
    # Configure the 6 servos we'll be using (adjust as needed)
    for i in range(6):
        # Set initial angle to 90 degrees (center position)
        kit.servo[i].angle = 90
        logger.info(f"Initialized servo {i} to center position (90°)")
    
    servo_initialized = True
except Exception as e:
    logger.error(f"Failed to initialize servo controller: {e}")
    logger.warning("Running in simulation mode - no actual servos will be controlled")
    servo_initialized = False

class MCPServer:
    def __init__(self):
        """Initialize the Model Context Protocol server"""
        self.conversation_history = []
        
        # Add a system prompt to guide the model
        system_message = """
        You are Wednesday, an AI assistant capable of controlling 6 servo motors on a robotic arm.
        The servo IDs range from 0 to 5, where:
        - Servo 0: Base rotation (0° to 180°)
        - Servo 1: Shoulder joint (0° to 180°)
        - Servo 2: Elbow joint (0° to 180°)
        - Servo 3: Wrist pitch (0° to 180°)
        - Servo 4: Wrist roll (0° to 180°)
        - Servo 5: Gripper (0° = open, 180° = closed)
        
        Convert natural language commands into specific servo movements.
        """
        self.conversation_history.append(SystemMessage(content=system_message))
    
    def process_command(self, command_data):
        """Process a command received from the client"""
        if not command_data.get("is_command", False):
            return {"status": "error", "message": "Not a valid command"}
        
        if command_data.get("command_type") == "servo_control":
            return self.handle_servo_command(command_data)
        
        return {"status": "error", "message": "Unknown command type"}
    
    def handle_servo_command(self, command_data):
        """Handle a servo control command"""
        try:
            servo_commands = command_data.get("servo_commands", [])
            results = []
            
            for cmd in servo_commands:
                servo_id = cmd.get("servo_id")
                position = cmd.get("position")
                speed = cmd.get("speed", 50)
                
                # Validate parameters
                if not (0 <= servo_id <= 5):
                    results.append({
                        "servo_id": servo_id,
                        "status": "error",
                        "message": "Invalid servo ID (must be 0-5)"
                    })
                    continue
                
                if not (0 <= position <= 180):
                    results.append({
                        "servo_id": servo_id,
                        "status": "error",
                        "message": "Invalid position (must be 0-180)"
                    })
                    continue
                
                # Move servo
                if servo_initialized:
                    # Get current position
                    current_position = kit.servo[servo_id].angle
                    
                    # Calculate step size based on speed (1-100)
                    step_size = max(1, min(10, speed / 10))
                    
                    # Move servo gradually in a separate thread
                    threading.Thread(
                        target=self._move_servo_gradually,
                        args=(servo_id, current_position, position, step_size)
                    ).start()
                    
                    results.append({
                        "servo_id": servo_id,
                        "status": "success",
                        "message": f"Moving servo {servo_id} to position {position}"
                    })
                else:
                    # Simulation mode
                    results.append({
                        "servo_id": servo_id,
                        "status": "simulated",
                        "message": f"Simulated: Moving servo {servo_id} to position {position}"
                    })
            
            return {
                "status": "success",
                "results": results,
                "description": command_data.get("description", "Command executed")
            }
        
        except Exception as e:
            logger.error(f"Error handling servo command: {e}")
            return {"status": "error", "message": str(e)}
    
    def _move_servo_gradually(self, servo_id, start_pos, end_pos, step_size):
        """Move a servo gradually from start to end position"""
        try:
            # Determine direction
            step = step_size if start_pos < end_pos else -step_size
            
            # Move in steps
            current_pos = start_pos
            while (step > 0 and current_pos < end_pos) or (step < 0 and current_pos > end_pos):
                current_pos += step
                # Ensure we don't overshoot
                if (step > 0 and current_pos > end_pos) or (step < 0 and current_pos < end_pos):
                    current_pos = end_pos
                
                # Move servo
                kit.servo[servo_id].angle = current_pos
                logger.debug(f"Servo {servo_id} moved to {current_pos}°")
                
                # Small delay for smooth movement
                time.sleep(0.015)
            
            # Ensure final position is set
            kit.servo[servo_id].angle = end_pos
            logger.info(f"Servo {servo_id} reached target position: {end_pos}°")
        
        except Exception as e:
            logger.error(f"Error moving servo {servo_id} gradually: {e}")

# Create MCP server instance
mcp_server = MCPServer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "servo_controller": "active" if servo_initialized else "simulated"
    })

@app.route('/command', methods=['POST'])
def receive_command():
    """Endpoint to receive commands from the client"""
    try:
        command_data = request.json
        logger.info(f"Received command: {json.dumps(command_data)}")
        
        result = mcp_server.process_command(command_data)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate_content():
    """Generate content using the Gemini model"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Generate content
        response = model.generate_content(prompt)
        
        return jsonify({
            "response": response.text
        })
    
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Default port is 8011
    port = int(os.getenv("SERVER_PORT", 8011))
    
    # Run the app
    logger.info(f"Starting Wednesday MCP Server on port {port}")
    logger.info(f"Servo controller status: {'Active' if servo_initialized else 'Simulated'}")
    
    app.run(host='0.0.0.0', port=port, debug=False) 