import os
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # When running as a bundled app, sys._MEIPASS is the temp directory
    # This is where PyInstaller unpacks files for one-file mode, or the root of one-dir mode.
    customtkinter_assets_path_in_bundle = os.path.join(sys._MEIPASS, 'customtkinter', 'assets')
    # Set environment variable for customtkinter to find its assets
    # customtkinter checks for this env var or tries to find assets relative to its own path
    os.environ["CUSTOMTKINTER_PATH"] = customtkinter_assets_path_in_bundle
    
    # print(f"[hook-customtkinter.py] CUSTOMTKINTER_PATH set to: {customtkinter_assets_path_in_bundle}") # Optional: for debugging the hook
