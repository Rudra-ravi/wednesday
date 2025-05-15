#!/usr/bin/env python3
import os
import threading
import time
import json
import requests
import tkinter as tk
from tkinter import scrolledtext, PhotoImage, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import google.generativeai as genai
from dotenv import load_dotenv
import pyttsx3
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Import theme and logo
from themes import *
from ascii_logo import SMALL_LOGO, LOGO, DIVIDER

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Raspberry Pi server configuration
SERVER_IP = os.getenv("SERVER_IP", "localhost")
SERVER_PORT = os.getenv("SERVER_PORT", "8011")
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Configure CTk appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VoiceRecorder:
    def __init__(self, callback):
        self.callback = callback
        self.recording = False
        self.sample_rate = 44100
        self.channels = 1
        self.recording_thread = None
        
    def start_recording(self):
        if self.recording:
            return
        
        self.recording = True
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        
    def stop_recording(self):
        if not self.recording:
            return
        
        self.recording = False
        if self.recording_thread:
            self.recording_thread.join()
            
    def _record(self):
        recording = sd.rec(
            int(10 * self.sample_rate),  # 10 seconds max
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16'
        )
        
        # Wait for recording or stop
        while self.recording and sd.get_stream().active:
            sd.sleep(100)
        
        sd.stop()
        
        if not self.recording:  # Stopped early
            # Process the partial recording
            wav.write("temp_recording.wav", self.sample_rate, recording[:sd.get_stream().active_frames])
            self.callback("temp_recording.wav")

class MCPMessage:
    """Structure for MCP-compatible messages"""
    def __init__(self, content, role="user", content_type="text"):
        self.content = content
        self.role = role
        self.content_type = content_type
        
    def to_dict(self):
        return {
            "content": self.content,
            "role": self.role,
            "content_type": self.content_type
        }

class WednesdayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wednesday - AI Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set the theme colors for the window
        self.root.configure(bg=BG_COLOR_DARK)
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Create voice recorder
        self.recorder = VoiceRecorder(self.process_voice_recording)
        
        # Setup UI
        self.setup_ui()
        
        # Initialize server connection status
        self.check_server_connection()
    
    def setup_ui(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR_DARK)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR_LIGHT, corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Logo display
        logo_label = ctk.CTkLabel(
            header_frame,
            text=SMALL_LOGO,
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=PRIMARY_COLOR,
            justify="left"
        )
        logo_label.pack(side="left", padx=20, pady=10)
        
        # Server status
        self.server_status_label = ctk.CTkLabel(
            header_frame, 
            text="Server: Checking...", 
            font=ctk.CTkFont(size=12),
            text_color=TEXT_COLOR
        )
        self.server_status_label.pack(side="right", padx=20, pady=10)
        
        # Chat display frame
        chat_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR_LIGHT, corner_radius=10)
        chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chat display
        self.chat_display = ctk.CTkTextbox(
            chat_frame, 
            wrap="word", 
            font=ctk.CTkFont(size=14),
            fg_color=BG_COLOR_LIGHT,
            text_color=TEXT_COLOR,
            scrollbar_button_color=PRIMARY_COLOR,
            scrollbar_button_hover_color=HIGHLIGHT_COLOR
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.configure(state="disabled")
        
        # Configure tag styles
        self.chat_display.tag_config("user_tag", foreground=SECONDARY_COLOR)
        self.chat_display.tag_config("user_message", foreground=TEXT_COLOR)
        self.chat_display.tag_config("assistant_tag", foreground=PRIMARY_COLOR)
        self.chat_display.tag_config("assistant_message", foreground=HIGHLIGHT_COLOR)
        self.chat_display.tag_config("logo", foreground=PRIMARY_COLOR)
        self.chat_display.tag_config("divider", foreground=SECONDARY_COLOR)
        
        # Input frame
        input_frame = ctk.CTkFrame(self.main_frame, fg_color=BG_COLOR_DARK)
        input_frame.pack(fill="x", pady=(10, 0))
        
        # Text input
        self.text_input = ctk.CTkTextbox(
            input_frame, 
            height=80, 
            font=ctk.CTkFont(size=14),
            fg_color=BG_COLOR_LIGHT,
            text_color=TEXT_COLOR,
            corner_radius=10,
            border_width=1,
            border_color="#30363D"
        )
        self.text_input.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self.on_enter_press)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(input_frame, fg_color=BG_COLOR_DARK)
        buttons_frame.pack(side="right", fill="y")
        
        # Send button
        self.send_button = ctk.CTkButton(
            buttons_frame, 
            text="Send", 
            command=self.send_message,
            width=100,
            height=35,
            fg_color=PRIMARY_COLOR,
            hover_color=HIGHLIGHT_COLOR,
            text_color=TEXT_COLOR,
            corner_radius=6
        )
        self.send_button.pack(fill="x", pady=(0, 5))
        
        # Voice button
        self.voice_button = ctk.CTkButton(
            buttons_frame, 
            text="Voice", 
            command=self.toggle_voice_record,
            width=100,
            height=35,
            fg_color=SECONDARY_COLOR,
            hover_color="#FF7043",
            text_color=TEXT_COLOR,
            corner_radius=6
        )
        self.voice_button.pack(fill="x")
        
        # Recording status
        self.recording_status = False
        
        # Add a welcome message with logo
        self.display_welcome_message()
    
    def display_welcome_message(self):
        """Display a welcome message with the logo"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", LOGO + "\n", "logo")
        self.chat_display.insert("end", DIVIDER + "\n", "divider")
        self.chat_display.insert("end", "Wednesday: ", "assistant_tag")
        self.chat_display.insert("end", "Hello, I'm Wednesday. How can I help you today?\n\n", "assistant_message")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
        # Add to conversation history
        self.conversation_history.append(AIMessage(content="Hello, I'm Wednesday. How can I help you today?"))
    
    def check_server_connection(self):
        """Check if Raspberry Pi server is reachable"""
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=2)
            if response.status_code == 200:
                self.server_status_label.configure(text="Server: Connected", text_color=SUCCESS_COLOR)
            else:
                self.server_status_label.configure(text="Server: Error", text_color=WARNING_COLOR)
        except requests.exceptions.RequestException:
            self.server_status_label.configure(text="Server: Disconnected", text_color=WARNING_COLOR)
        
        # Schedule the next check
        self.root.after(8011, self.check_server_connection)
    
    def display_user_message(self, message):
        """Display a user message in the chat display"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "You: ", "user_tag")
        self.chat_display.insert("end", f"{message}\n\n", "user_message")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
        # Add to conversation history
        self.conversation_history.append(HumanMessage(content=message))
    
    def display_assistant_message(self, message):
        """Display an assistant message in the chat display"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "Wednesday: ", "assistant_tag")
        self.chat_display.insert("end", f"{message}\n\n", "assistant_message")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
        # Add to conversation history
        self.conversation_history.append(AIMessage(content=message))
    
    def on_enter_press(self, event):
        """Handle Enter key press to send message"""
        if not event.state & 0x1:  # Check if shift is not pressed
            self.send_message()
            return "break"  # Prevent default Enter behavior
    
    def send_message(self):
        """Send a text message to the AI assistant"""
        message = self.text_input.get("1.0", "end-1c").strip()
        if not message:
            return
        
        # Clear input
        self.text_input.delete("1.0", "end")
        
        # Display message
        self.display_user_message(message)
        
        # Process the message in a separate thread
        threading.Thread(target=self.process_message, args=(message,)).start()
    
    def process_message(self, message):
        """Process the user message and get AI response"""
        try:
            # Generate response from Gemini
            response = model.generate_content(message)
            response_text = response.text
            
            # Use Gemini to extract command intent if any
            command_prompt = f"""
            Analyze this user request and determine if it relates to controlling servo motors. 
            If yes, convert it to a structured command for a robotic system.
            User request: "{message}"
            
            If it's a servo control request, respond with a JSON object like:
            {{
                "is_command": true,
                "command_type": "servo_control",
                "servo_commands": [
                    {{
                        "servo_id": <integer 0-5>,
                        "position": <integer 0-180>,
                        "speed": <integer 1-100>
                    }}
                ],
                "description": "<plain language description of what's happening>"
            }}
            
            If it's not a servo control request, respond with:
            {{
                "is_command": false
            }}
            """
            
            command_response = model.generate_content(command_prompt)
            command_text = command_response.text.strip()
            
            try:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', command_text, re.DOTALL)
                if json_match:
                    command_data = json.loads(json_match.group(1))
                else:
                    command_data = json.loads(command_text)
                
                # If it's a command, send to server
                if command_data.get("is_command", False):
                    self.send_command_to_server(command_data)
                    # We'll still use the original response for display
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Error parsing command: {e}")
            
            # Display response
            self.display_assistant_message(response_text)
            
            # Text to speech
            self.speak_text(response_text)
            
        except Exception as e:
            print(f"Error processing message: {e}")
            self.display_assistant_message(f"I'm sorry, I encountered an error: {str(e)}")
    
    def send_command_to_server(self, command_data):
        """Send a command to the Raspberry Pi server"""
        try:
            response = requests.post(
                f"{SERVER_URL}/command", 
                json=command_data,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"Error sending command: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server: {e}")
            self.server_status_label.configure(text="Server: Connection Error", text_color=WARNING_COLOR)
    
    def toggle_voice_record(self):
        """Toggle voice recording on/off"""
        if self.recording_status:
            # Stop recording
            self.recording_status = False
            self.recorder.stop_recording()
            self.voice_button.configure(text="Voice", fg_color=SECONDARY_COLOR)
        else:
            # Start recording
            self.recording_status = True
            self.voice_button.configure(text="Recording...", fg_color=WARNING_COLOR)
            self.recorder.start_recording()
    
    def process_voice_recording(self, audio_file_path):
        """Process a voice recording file"""
        try:
            # Reset button state
            self.recording_status = False
            self.voice_button.configure(text="Voice", fg_color=SECONDARY_COLOR)
            
            # Perform speech-to-text
            # For this example, we'll use Gemini's audio capabilities
            audio_data = self.load_audio_file(audio_file_path)
            
            # For now, just showing a placeholder message
            # In a real implementation, you would use a speech-to-text API
            self.display_user_message("[Voice Message]")
            self.display_assistant_message("I heard you! However, speech recognition is not yet implemented in this demo.")
            
            # Clean up
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                
        except Exception as e:
            print(f"Error processing voice recording: {e}")
    
    def load_audio_file(self, file_path):
        """Load an audio file as bytes"""
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return None
    
    def speak_text(self, text):
        """Convert text to speech"""
        try:
            def speak():
                tts_engine.say(text)
                tts_engine.runAndWait()
            
            # Run in a separate thread to avoid blocking the UI
            threading.Thread(target=speak).start()
        except Exception as e:
            print(f"Error speaking text: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = WednesdayApp(root)
    root.mainloop() 