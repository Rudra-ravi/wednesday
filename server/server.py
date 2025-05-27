import asyncio
import pigpio
from fastmcp import FastMCP

# Initialize pigpio
try:
    pi = pigpio.pi()
except Exception as e:
    print(f"Failed to connect to pigpio daemon: {e}")
    print("Please ensure pigpiod is running (e.g., sudo systemctl start pigpiod)")
    # In a real application, you might want to exit or handle this more gracefully
    # For now, we'll let it proceed, but tool calls will likely fail.
    pi = None


mcp = FastMCP("ServoController")

ALLOWED_PINS = {17, 27, 22, 23, 24, 25}
PINS_WITH_ANGLE_CAP = {17, 27, 22}
MAX_ANGLE_FOR_CAPPED_PINS = 45.0
MIN_PULSE_WIDTH = 500
MAX_PULSE_WIDTH = 2500
MIN_ANGLE = 0.0
MAX_ANGLE = 180.0

def angle_to_pulsewidth(angle: float) -> int:
    """Converts an angle in degrees to a servo pulse width in microseconds."""
    return int(MIN_PULSE_WIDTH + (angle / MAX_ANGLE) * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH))

@mcp.tool()
async def execute_servo_commands(commands: list[dict]) -> list[dict]:
    """
    Execute a batch of servo moves. Each command dict should have:
      - pin (int): BCM GPIO pin (17,27,22,23,24,25)
      - angle (float):  Desired angle in degrees (0–180, but 17/27/22 capped at 45)
      - duration_ms (int, optional): How long to hold this position (default 500ms)
    Returns a list of status dicts for each command.
    """
    results = []
    if not pi:
        # pigpio not initialized, return error for all commands
        for cmd_idx, cmd in enumerate(commands):
            pin = cmd.get("pin")
            results.append({
                "pin": pin,
                "status": "error",
                "message": "pigpio daemon not connected. Cannot control servos."
            })
        return results

    for cmd in commands:
        pin = cmd.get("pin")
        angle = cmd.get("angle")
        duration_ms = cmd.get("duration_ms", 500) # Default duration 500ms
        status = {"pin": pin}

        # Validate pin
        if pin not in ALLOWED_PINS:
            status.update(status="error", message=f"Invalid pin {pin}. Allowed pins are {ALLOWED_PINS}.")
            results.append(status)
            continue

        # Validate angle type
        if not isinstance(angle, (int, float)):
            status.update(status="error", message=f"Invalid angle type for pin {pin}. Angle must be a number.")
            results.append(status)
            continue
            
        # Validate angle range
        if not (MIN_ANGLE <= angle <= MAX_ANGLE):
            status.update(status="error", message=f"Invalid angle {angle} for pin {pin}. Angle must be between {MIN_ANGLE} and {MAX_ANGLE} degrees.")
            results.append(status)
            continue

        # Cap angle for specific pins
        original_angle = angle
        if pin in PINS_WITH_ANGLE_CAP and angle > MAX_ANGLE_FOR_CAPPED_PINS:
            angle = MAX_ANGLE_FOR_CAPPED_PINS
            status["message"] = f"Angle {original_angle}° for pin {pin} was capped to {MAX_ANGLE_FOR_CAPPED_PINS}°."
        
        pulse_width = angle_to_pulsewidth(angle)
        
        try:
            pi.set_servo_pulsewidth(pin, pulse_width)
            await asyncio.sleep(duration_ms / 1000.0)
            pi.set_servo_pulsewidth(pin, 0)  # Stop sending pulses to the servo
            status["status"] = "ok"
            if "message" not in status: # If no capping message, confirm original angle
                 status["message"] = f"Servo on pin {pin} moved to {angle}°."
        except pigpio.error as e:
            status.update(status="error", message=f"pigpio error for pin {pin}: {str(e)}")
        except Exception as e:
            status.update(status="error", message=f"Unexpected error for pin {pin}: {str(e)}")
        
        results.append(status)

    return results

if __name__ == "__main__":
    print("Starting Servo MCP Server on port 8011...")
    # Ensure pigpio is available before trying to run the server reliant on it.
    if pi is None:
        print("Cannot start server: pigpio is not initialized.")
        print("Make sure the pigpio daemon (pigpiod) is running and accessible.")
    else:
        print(f"Connected to pigpio daemon (version {pi.get_pigpio_version()}).")
        print(f"Hardware revision: {pi.get_hardware_revision()}")
        print(f"Controlling servos on BCM pins: {ALLOWED_PINS}")
        print(f"Pins {PINS_WITH_ANGLE_CAP} have their angles capped at {MAX_ANGLE_FOR_CAPPED_PINS} degrees.")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8011) 