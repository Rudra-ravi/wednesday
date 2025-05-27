import tkinter as tk
from tkinter import ttk, scrolledtext, font, simpledialog, messagebox
import asyncio
import threading
import json
import time
from dotenv import load_dotenv
import os
import anyio # Added import
import socket # Added import

# For MCP Client
from mcp import ClientSession, types as mcp_types
from mcp.client.streamable_http import streamablehttp_client # Added import

# For Gemini
import google.generativeai as genai

class AsyncTkinterLoop:
    """
    Manages an asyncio event loop in a separate thread, allowing asyncio code
    to run alongside Tkinter's main loop.
    """
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        asyncio.set_event_loop(self._loop)

    def run_coroutine(self, coro):
        """Schedules a coroutine to be run in the asyncio event loop."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self):
        """Stops the asyncio event loop."""
        self._loop.call_soon_threadsafe(self._loop.stop)
        # self._thread.join() # Optional: wait for thread to finish

class WednesdayApp:
    def __init__(self, root, async_loop_manager):
        self.root = root
        self.async_loop_manager = async_loop_manager
        self.root.title("Wednesday - MCP Client")
        self.root.geometry("750x650") # Increased size

        # Load Gemini API Key
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            messagebox.showwarning("API Key Missing", "GEMINI_API_KEY not found in .env file. Gemini features will not work.")
        else:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # or 'gemini-pro'
                print("Gemini Model Initialized.")
            except Exception as e:
                messagebox.showerror("Gemini Init Error", f"Failed to initialize Gemini: {e}")
                self.gemini_model = None


        self.bg_color = "#1E1E1E"
        self.fg_color = "#00A0D2" # Light blue
        self.text_area_bg = "#2B2B2B"
        self.button_fg = "#FFFFFF"
        self.status_error_fg = "#FF6347" # Tomato red
        self.status_success_fg = "#32CD32" # Lime green
        self.label_fg = "#CCCCCC" # Lighter grey for labels

        self.root.configure(bg=self.bg_color)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("TLabel", background=self.bg_color, foreground=self.label_fg, font=("Segoe UI", 10))
        self.style.configure("Accent.TLabel", foreground=self.fg_color, font=("Segoe UI", 11, "bold"))
        self.style.configure("TButton", background="#007ACC", foreground=self.button_fg, font=("Segoe UI", 11, "bold"), borderwidth=1, padding=5)
        self.style.map("TButton",
                       background=[('active', '#005f99')],
                       relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        self.style.configure("TEntry", fieldbackground=self.text_area_bg, foreground=self.fg_color, insertcolor=self.fg_color, borderwidth=1, relief=tk.FLAT)


        # --- UI Elements ---
        # Server Configuration Frame
        config_frame = ttk.Frame(root, style="TFrame", padding=(10, 5))
        config_frame.pack(fill="x", padx=20, pady=(10,0))
        config_frame.columnconfigure(1, weight=1)

        ttk.Label(config_frame, text="Raspberry Pi IP:", style="TLabel").grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
        self.rpi_ip_var = tk.StringVar(value="192.168.197.168") # Default IP for local server
        self.rpi_ip_entry = ttk.Entry(config_frame, textvariable=self.rpi_ip_var, width=30, font=("Segoe UI", 10))
        self.rpi_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(config_frame, text="Port:", style="TLabel").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.rpi_port_var = tk.StringVar(value="8011") # Default port to match server
        self.rpi_port_entry = ttk.Entry(config_frame, textvariable=self.rpi_port_var, width=8, font=("Segoe UI", 10))
        self.rpi_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")


        # Main Input Area
        main_input_label = ttk.Label(root, text="Enter your command for Wednesday:", style="Accent.TLabel")
        main_input_label.pack(pady=(10,2), padx=20, anchor="w")
        
        text_font = font.Font(family="Segoe UI", size=12)
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=8,
                                                   font=text_font,
                                                   bg=self.text_area_bg, fg=self.fg_color,
                                                   insertbackground=self.fg_color,
                                                   relief=tk.FLAT, borderwidth=2, bd=2, highlightthickness=1, highlightbackground=self.fg_color)
        self.text_area.pack(pady=5, padx=20, fill="both", expand=True)

        # Submit Button
        self.submit_button = ttk.Button(root, text="Send Command to Pi", command=self.on_submit_action_async, style="TButton")
        self.submit_button.pack(pady=(5,10))

        # Status and Log Area Frame
        status_log_frame = ttk.Frame(root, style="TFrame")
        status_log_frame.pack(fill="both", expand=True, padx=20, pady=(0,10))
        
        # Status Label
        self.status_label = ttk.Label(status_log_frame, text="Ready. Enter command and Raspberry Pi IP.", style="TLabel", wraplength=700)
        self.status_label.pack(pady=(0,5), anchor="w")

        # Log Text Area (read-only)
        log_label = ttk.Label(status_log_frame, text="Log / Server Response:", style="Accent.TLabel")
        log_label.pack(pady=(5,2), anchor="w")
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10,
                                                 font=("Courier New", 10), # Monospaced for logs
                                                 bg="#252526", fg="#D4D4D4", # Slightly different log bg
                                                 relief=tk.FLAT, borderwidth=1, state=tk.DISABLED)
        self.log_area.pack(pady=5, padx=20, fill="both", expand=True)


        print("App Initialized with Async Loop and MCP/Gemini components.")
        self.log_message("Application initialized. Configure RPi IP and enter command.")

    def log_message(self, message, level="INFO"):
        self.log_area.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_area.insert(tk.END, f"[{timestamp} {level}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        print(f"LOG: {message}") # Also print to console for easier debugging

    def update_status(self, message, is_error=False, is_success=False):
        self.status_label.config(text=message)
        if is_error:
            self.status_label.config(foreground=self.status_error_fg)
        elif is_success:
            self.status_label.config(foreground=self.status_success_fg)
        else:
            self.status_label.config(foreground=self.label_fg) # Default status color
        self.root.update_idletasks()

    def on_submit_action_async(self):
        """Wraps the async submit action to be called from Tkinter button."""
        # Disable button to prevent multiple submissions
        self.submit_button.config(state=tk.DISABLED, text="Processing...")
        self.update_status("Processing command...")
        self.log_message("Submit button clicked.")

        # Schedule the async task
        future = self.async_loop_manager.run_coroutine(self.submit_text_action_async())
        
        # Define a callback to re-enable the button and handle results/exceptions
        def on_done_callback(fut):
            try:
                # If the coroutine returned something, it would be in fut.result()
                fut.result() 
            except Exception as e:
                self.update_status(f"An error occurred: {e}", is_error=True)
                self.log_message(f"Error in async submission: {e}", level="ERROR")
            finally:
                self.submit_button.config(state=tk.NORMAL, text="Send Command to Pi")
                if not self.status_label.cget("text").startswith("Error:") and not self.status_label.cget("text").startswith("Success:"):
                     self.update_status("Ready for next command.")


        future.add_done_callback(on_done_callback)

    async def submit_text_action_async(self):
        user_command = self.text_area.get("1.0", tk.END).strip()
        rpi_ip = self.rpi_ip_var.get().strip()
        rpi_port_str = self.rpi_port_var.get().strip()

        if not rpi_ip:
            self.update_status("Raspberry Pi IP address is required.", is_error=True)
            self.log_message("Validation Error: RPi IP missing.", level="ERROR")
            return
        if not rpi_port_str.isdigit():
            self.update_status("Raspberry Pi Port must be a number.", is_error=True)
            self.log_message("Validation Error: RPi Port invalid.", level="ERROR")
            return
        rpi_port = int(rpi_port_str)

        if not user_command:
            self.update_status("Please enter a command.", is_error=True)
            self.log_message("Validation Error: User command missing.", level="ERROR")
            return

        self.log_message(f"User command: '{user_command}' for RPi at {rpi_ip}:{rpi_port}")

        if not self.gemini_model:
            self.update_status("Gemini model not initialized. Check API Key.", is_error=True)
            self.log_message("Gemini Error: Model not initialized.", level="ERROR")
            return

        # Step 1: Get instructions from Gemini
        self.update_status("Getting instructions from Gemini...")
        self.log_message("Contacting Gemini...")
        gemini_instructions_json = await self.get_gemini_instructions(user_command)

        if gemini_instructions_json is None:
            # Error already logged and status updated by get_gemini_instructions
            return

        self.log_message(f"Gemini raw response: {json.dumps(gemini_instructions_json, indent=2)}")

        # Step 2: Send instructions to Raspberry Pi via MCP
        self.update_status(f"Sending {len(gemini_instructions_json)} command(s) to Raspberry Pi...")
        self.log_message(f"Sending commands to RPi: {rpi_ip}:{rpi_port}")
        
        pi_response = await self.send_commands_to_pi_mcp(rpi_ip, rpi_port, gemini_instructions_json)

        if pi_response:
            self.update_status(f"Response from Pi: {pi_response.splitlines()[0]}", is_success=True) # Show first line in status
            self.log_message(f"Full response from Pi:\n{pi_response}", level="INFO" if "Error" not in pi_response else "ERROR")
        else:
            # Error handled by send_commands_to_pi_mcp
            pass
            
    def _get_gemini_prompt(self, user_text_input: str) -> str:
        return f"""
You are a precise robot arm controller. Your task is to convert the user's textual command into a sequence of servo motor movements.
You are controlling a robot arm with 6 servo motors. These servos are identified by names and are connected to the following Raspberry Pi GPIO pins:
- servo_0: pin 17
- servo_1: pin 27
- servo_2: pin 22
- servo_3: pin 23
- servo_4: pin 24
- servo_5: pin 25
    
Servos 0-2 can move between 0 and 45 degrees. Servos 3-5 can move between 0 and 180 degrees.

Output your response as a JSON list of objects. Each object in the list represents a single servo command and must have the following fields:
- "pin": An integer representing the BCM GPIO pin number for the servo.
- "angle": An integer representing the target angle for the servo (0-180).
- "duration_ms": An optional integer for how long the movement/hold should take in milliseconds (e.g., 500). If not critical, you can omit it or use a default like 500.

For example, if the user says "Move servo_0 to 90 degrees and servo_2 to 30 degrees, each for 1 second", you should output:
[
    {{"pin": 17, "angle": 45, "duration_ms": 500}},
    {{"pin": 22, "angle": 30, "duration_ms": 1000}}
]

If the user says "Wave the arm connected to servo_0", a possible output could be:
[
    {{"pin": 23, "angle": 45, "duration_ms": 500}},
    {{"pin": 23, "angle": 10, "duration_ms": 700}},
    {{"pin": 23, "angle": 45, "duration_ms": 500}}
]

Ensure the output is ONLY the JSON list, with no other text, markdown formatting, or explanations.
User command: "{user_text_input}"
JSON output:
"""

    async def get_gemini_instructions(self, user_input: str) -> list[dict] | None:
        if not self.gemini_model:
            self.update_status("Gemini model not available.", is_error=True)
            self.log_message("Gemini call skipped: model not initialized.", level="ERROR")
            return None
        
        prompt = self._get_gemini_prompt(user_input)
        self.log_message(f"Sending prompt to Gemini:\n{prompt}")

        try:
            response = await self.gemini_model.generate_content_async(prompt)
            raw_response_text = response.text.strip()
            self.log_message(f"Gemini raw text response:\n{raw_response_text}")

            # Clean the response: remove potential markdown ```json ... ```
            if raw_response_text.startswith("```json"):
                raw_response_text = raw_response_text[7:] # Remove ```json
            if raw_response_text.endswith("```"):
                raw_response_text = raw_response_text[:-3] # Remove ```
            raw_response_text = raw_response_text.strip()

            parsed_json = json.loads(raw_response_text)
            if not isinstance(parsed_json, list):
                raise ValueError("Gemini response is not a JSON list.")
            for item in parsed_json:
                if not isinstance(item, dict) or "pin" not in item or "angle" not in item:
                    raise ValueError("Invalid item in Gemini JSON list response.")
            
            self.update_status("Successfully received and parsed instructions from Gemini.", is_success=True)
            return parsed_json
        except json.JSONDecodeError as e:
            self.update_status(f"Gemini Error: Failed to parse JSON response: {e}. Raw: {raw_response_text}", is_error=True)
            self.log_message(f"JSONDecodeError from Gemini response: {e}. Raw response: '{raw_response_text}'", level="ERROR")
            return None
        except ValueError as e: # For custom validation errors
            self.update_status(f"Gemini Error: Invalid data format from Gemini: {e}. Raw: {raw_response_text}", is_error=True)
            self.log_message(f"ValueError (Invalid format) from Gemini response: {e}. Raw response: '{raw_response_text}'", level="ERROR")
            return None
        except Exception as e:
            self.update_status(f"Gemini API Error: {e}", is_error=True)
            self.log_message(f"Error calling Gemini API: {e}", level="ERROR")
            return None

    async def send_commands_to_pi_mcp(self, rpi_ip: str, port: int, commands: list[dict]) -> str | None:
        mcp_server_url_for_context = f"http://{rpi_ip}:{port}/mcp" # For logging and context
        self.log_message(f"Attempting to establish MCP connection to {rpi_ip}:{port}")

        try:
            mcp_http_url = f"http://{rpi_ip}:{port}/mcp"
            self.log_message(f"Opening MCP HTTP connection to {mcp_http_url}...")
            
            async with streamablehttp_client(mcp_http_url) as (read_stream, write_stream, _response_future):
                self.log_message(f"MCP HTTP transport established to {mcp_http_url}.")

                # Ensure commands is a dictionary for the tool call as per MCP spec for arguments
                tool_arguments = {"commands": commands}

                async with ClientSession(read_stream, write_stream) as session:
                    self.log_message("MCP Client: Initializing session...")
                    init_response = await session.initialize()
                    self.log_message(f"MCP Client: Session initialized. Server capabilities: {init_response.capabilities if init_response else 'N/A'}")

                    self.log_message(f"MCP Client: Calling tool 'execute_servo_commands' with args: {tool_arguments}")
                    tool_result = await session.call_tool(
                        name="execute_servo_commands",
                        arguments=tool_arguments
                    )
                    self.log_message(f"MCP Client: Tool call successful. Raw result content type: {type(tool_result.content)}")
                    self.log_message(f"MCP Client: Tool call result content (full): {str(tool_result.content)}") # Log the full content for inspection

                    content = tool_result.content
                    if isinstance(content, list) and len(content) > 0:
                        first_item = content[0]
                        # Check if the first item is an MCP content type (like TextContent)
                        # and has a 'text' attribute which holds the actual string data.
                        if hasattr(first_item, 'text') and isinstance(first_item.text, str):
                            self.log_message(f"Extracted text from MCP content object: {first_item.text}")
                            return first_item.text
                        else:
                            # If the list contains something else, or .text is not a string
                            self.log_message(f"Tool result is a list, but first item is not a recognized MCP text content object or .text is not a string: {str(first_item)}", level="WARNING")
                            # Fallback to stringifying the whole list, though this might not be the desired JSON.
                            return str(content)
                    elif isinstance(content, str):
                        # If the content is already a string, return it directly.
                        return content
                    elif isinstance(content, dict):
                        # If server directly returns a dict (e.g. FastMCP might auto-serialize some Pydantic models to dicts)
                        # and the calling code expects a JSON string of that dict.
                        self.log_message(f"Tool result is a dict, returning its JSON string representation: {str(content)}", level="INFO")
                        return json.dumps(content) # Convert dict to JSON string
                    else:
                        # Fallback for any other unexpected types.
                        self.log_message(f"Unexpected tool result content structure. Type: {type(content)}, Value: {str(content)}", level="WARNING")
                        return str(content)

        except socket.gaierror: # Specific error for DNS/address lookup issues
            self.update_status(f"MCP Error: Could not resolve hostname {rpi_ip}. Check IP address.", is_error=True)
            self.log_message(f"DNS or address lookup error for MCP server at {rpi_ip}:{port}.", level="ERROR")
            return None
        except anyio.BrokenResourceError as e: 
             self.update_status(f"MCP Error: Connection to {rpi_ip}:{port} broken.", is_error=True)
             self.log_message(f"AnyIO BrokenResourceError for MCP server at {rpi_ip}:{port}: {e}", level="ERROR")
             import traceback
             self.log_message(traceback.format_exc(), level="DEBUG")
             return None
        except OSError as e: # Catch generic OS errors like ConnectionRefusedError
            # Check if it's a ConnectionRefusedError (covers different OSes)
            if isinstance(e, ConnectionRefusedError) or \
               (hasattr(e, 'errno') and e.errno in [111, 61]) or \
               ('Connection refused' in str(e)): # 111 for Linux, 61 for macOS/Windows
                 self.update_status(f"MCP Error: Connection refused by {rpi_ip}:{port}. Server running?", is_error=True)
                 self.log_message(f"ConnectionRefusedError for MCP server at {rpi_ip}:{port}. Is the server running and accessible?", level="ERROR")
            else:
                 self.update_status(f"MCP Network Error: {type(e).__name__} - {e}", is_error=True)
                 self.log_message(f"Network/OS error in MCP communication to {rpi_ip}:{port}: {e}", level="ERROR")
                 import traceback
                 self.log_message(traceback.format_exc(), level="DEBUG")
            return None
        except asyncio.TimeoutError: 
            self.update_status(f"MCP Error: Operation to {rpi_ip}:{port} timed out.", is_error=True)
            self.log_message(f"TimeoutError during MCP operation with {rpi_ip}:{port}.", level="ERROR")
            return None
        except Exception as e: # General MCP or other errors
            # Check if the error message indicates an HTTP error status (e.g. 404, 500)
            # This is a basic check; mcp library might have more specific HTTP error types
            str_e = str(e).lower()
            if "status_code=404" in str_e or "404 not found" in str_e:
                 self.update_status(f"MCP HTTP Error: Server not found at {mcp_http_url} (404). Check URL and server path.", is_error=True)
                 self.log_message(f"HTTP 404 Not Found for MCP server at {mcp_http_url}. Ensure server is running and path is correct.", level="ERROR")
            elif "status_code=5" in str_e: # Catches 5xx errors
                 self.update_status(f"MCP HTTP Error: Server error at {mcp_http_url} ({e}). Check server logs.", is_error=True)
                 self.log_message(f"HTTP Server Error ({e}) for MCP server at {mcp_http_url}.", level="ERROR")
            else:
                self.update_status(f"MCP Client Error: {type(e).__name__} - {e}", is_error=True)
                self.log_message(f"General error in MCP communication to {mcp_http_url}: {e}", level="ERROR")
            
            import traceback
            self.log_message(traceback.format_exc(), level="DEBUG")
            return None
        # The 'finally' block for closing client_stream is removed as 
        # streamablehttp_client and ClientSession are async context managers and handle their own cleanup.
        # No explicit close needed for streams obtained from streamablehttp_client within its context.

if __name__ == "__main__":
    # Create and manage the asyncio event loop
    async_loop_mgr = AsyncTkinterLoop()
    
    root = tk.Tk()
    app = WednesdayApp(root, async_loop_mgr)
    
    def on_closing():
        print("Closing application...")
        async_loop_mgr.stop() # Stop the asyncio loop
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted by user.")
        on_closing() 