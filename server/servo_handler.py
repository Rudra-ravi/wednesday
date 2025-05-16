import RPi.GPIO as GPIO
import time
import asyncio

class ServoController:
    def __init__(self, servo_pins_map: dict): # e.g., {17: "servo1", 23: "servo2"}
        self.servo_pins = list(servo_pins_map.keys())
        self.pwm_objects = {}
        self.is_initialized = False
        # Store the map if you need to refer to servos by name, otherwise just pins is fine
        self.servo_pins_map = servo_pins_map 

    async def initialize_gpio(self):
        if self.is_initialized:
            print("GPIO already initialized.")
            return
        try:
            GPIO.setmode(GPIO.BCM) # Use Broadcom pin numbering
            GPIO.setwarnings(False) # Disable warnings
            for pin in self.servo_pins:
                GPIO.setup(pin, GPIO.OUT)
                self.pwm_objects[pin] = GPIO.PWM(pin, 50) # 50Hz frequency
                self.pwm_objects[pin].start(0) # Start with 0 duty cycle
                print(f"Initialized GPIO pin {pin} for PWM.")
            self.is_initialized = True
            print("Servo controller initialized successfully.")
        except Exception as e:
            print(f"Error initializing GPIO: {e}")
            self.is_initialized = False
            # Consider how to handle this error in the MCP server - maybe prevent tool calls

    def _angle_to_duty_cycle(self, angle: int) -> float:
        angle = max(0, min(180, angle))
        # This formula (angle / 18 + 2) generally works for 0-180 degrees.
        # It gives a range from 2% (for 0 deg) to 12% (for 180 deg).
        # (0 / 18) + 2 = 2
        # (90 / 18) + 2 = 5 + 2 = 7
        # (180 / 18) + 2 = 10 + 2 = 12
        duty_cycle = (float(angle) / 18.0) + 2.0
        return round(duty_cycle, 2)

    async def set_angle(self, pin: int, angle: int, duration_ms: int = 500):
        if not self.is_initialized:
            msg = "GPIO not initialized. Call initialize_gpio first."
            print(msg)
            # In a real scenario, you might raise an exception or return a specific error status
            return False, msg 
        
        if pin not in self.pwm_objects:
            msg = f"Pin {pin} not configured for servo control."
            print(msg)
            return False, msg

        duty = self._angle_to_duty_cycle(angle)
        try:
            self.pwm_objects[pin].ChangeDutyCycle(duty)
            print(f"Set servo on pin {pin} to angle {angle} (duty: {duty}%)")
            if duration_ms > 0:
                await asyncio.sleep(duration_ms / 1000.0) # Hold position or allow time for movement
            # Optional: Set duty cycle to 0 after movement to stop signal and potential jitter
            # self.pwm_objects[pin].ChangeDutyCycle(0) 
            return True, f"Servo on pin {pin} set to {angle} degrees."
        except Exception as e:
            msg = f"Error setting angle for pin {pin}: {e}"
            print(msg)
            return False, msg

    async def process_commands(self, commands: list[dict]) -> str:
        if not self.is_initialized:
            return "Error: Servo controller not initialized. Cannot process commands."
        
        results_log = []
        all_successful = True
        for command_idx, command_data in enumerate(commands):
            pin = command_data.get("pin")
            angle = command_data.get("angle")
            duration = command_data.get("duration_ms", 500) # Default duration if not specified

            if pin is None or angle is None:
                msg = f"Command {command_idx}: Invalid - missing 'pin' or 'angle'. Data: {command_data}"
                print(msg)
                results_log.append(msg)
                all_successful = False
                continue
            
            if pin not in self.servo_pins:
                msg = f"Command {command_idx}: Pin {pin} not configured for servo control. Data: {command_data}"
                print(msg)
                results_log.append(msg)
                all_successful = False
                continue
            
            try:
                angle = int(angle)
                if not (0 <= angle <= 180):
                    msg = f"Command {command_idx}: Angle {angle} for pin {pin} is out of range (0-180). Data: {command_data}"
                    print(msg)
                    results_log.append(msg)
                    all_successful = False
                    continue
            except ValueError:
                msg = f"Command {command_idx}: Angle '{angle}' for pin {pin} is not a valid integer. Data: {command_data}"
                print(msg)
                results_log.append(msg)
                all_successful = False
                continue

            success, message = await self.set_angle(pin, angle, duration)
            results_log.append(f"Command {command_idx} (pin {pin}, angle {angle}): {message}")
            if not success:
                all_successful = False
        
        final_status = "All commands processed successfully." if all_successful else "Some commands failed or had issues."
        return f"{final_status}\nLog:\n" + "\n".join(results_log)

    async def cleanup_gpio(self):
        if not self.is_initialized:
            # print("GPIO not initialized or already cleaned up, no explicit cleanup action taken.")
            return # Idempotent: if not initialized, nothing to clean.
        
        print("Cleaning up GPIO...")
        try:
            for pin in self.pwm_objects:
                self.pwm_objects[pin].stop()
            GPIO.cleanup()
            self.is_initialized = False # Mark as not initialized
            print("GPIO cleanup complete.")
        except Exception as e:
            print(f"Error during GPIO cleanup: {e}")
            # Even if cleanup fails, mark as not initialized to prevent reuse without re-init
            self.is_initialized = False


# Example usage (for testing servo_handler.py directly on RPi)
# Ensure this part is commented out or removed when mcp_server.py uses this module.
# async def main_test():
#     # GPIO pins for servos: 17, 27, 22, 23, 24, 25
#     servo_pins_config = {
#         17: "servo_1_base", 
#         27: "servo_2_shoulder", 
#         22: "servo_3_elbow",
#         23: "servo_4_wrist_rotate", 
#         24: "servo_5_wrist_pitch", 
#         25: "servo_6_gripper"
#     }
#     controller = ServoController(servo_pins_config)
    
#     # It's crucial to use await for async methods
#     await controller.initialize_gpio() 
    
#     if not controller.is_initialized:
#         print("Failed to initialize servo controller. Exiting test.")
#         return

#     try:
#         print("Testing servo movements...")
#         # Test servo on pin 17
#         test_commands_s1 = [
#             {"pin": 17, "angle": 0, "duration_ms": 1000},
#             {"pin": 17, "angle": 90, "duration_ms": 1000},
#             {"pin": 17, "angle": 180, "duration_ms": 1000},
#             {"pin": 17, "angle": 90, "duration_ms": 1000},
#         ]
#         print("\\nProcessing commands for servo on pin 17:")
#         print(await controller.process_commands(test_commands_s1))
        
#         # Test servo on pin 27 (if connected and safe)
#         # print("\\nTesting servo on pin 27 to 45 degrees for 2 seconds...")
#         # success_s2, msg_s2 = await controller.set_angle(27, 45, 2000)
#         # print(f"Pin 27 to 45 deg: Success: {success_s2}, Msg: {msg_s2}")
#         # await asyncio.sleep(1)
#         # success_s2_neutral, msg_s2_neutral = await controller.set_angle(27, 90, 500) # return to neutral
#         # print(f"Pin 27 to 90 deg: Success: {success_s2_neutral}, Msg: {msg_s2_neutral}")

#         # Example of a sequence for multiple servos
#         # complex_sequence = [
#         #     {"pin": 17, "angle": 45, "duration_ms": 700},
#         #     {"pin": 27, "angle": 120, "duration_ms": 700},
#         #     {"pin": 22, "angle": 90, "duration_ms": 700},
#         #     {"pin": 17, "angle": 90, "duration_ms": 500}, # return base to center
#         # ]
#         # print("\\nProcessing complex sequence:")
#         # print(await controller.process_commands(complex_sequence))


#     except Exception as e:
#         print(f"An error occurred during testing: {e}")
#     finally:
#         print("Ensuring GPIO cleanup in test...")
#         await controller.cleanup_gpio()

# if __name__ == "__main__":
#     # This check prevents RPi.GPIO errors if not run on a Pi
#     # For real testing, this script should be run on the Raspberry Pi.
#     try:
#         # Check if running on RPi by trying to import RPi.GPIO
#         # This is a bit of a hack for dev, real RPi environment is assumed for execution
#         import RPi.GPIO 
#         print("RPi.GPIO available. Running test sequence.")
#         asyncio.run(main_test())
#     except (RuntimeError, ModuleNotFoundError) as e:
#         print(f"Not running on a Raspberry Pi or RPi.GPIO not available. Skipping main_test. Error: {e}")
#         print("ServoController class defined. To test, run this script on a Raspberry Pi.") 