# wednesday_client.spec

import os
import sys
import site

# SPECPATH is a global variable provided by PyInstaller, representing the directory of the .spec file.
main_script_dir = SPECPATH
if main_script_dir not in sys.path:
    sys.path.append(main_script_dir)

# --- Hook directories ---
pyi_build_hooks_dir = os.path.join(main_script_dir, "pyi_hooks")
pyi_runtime_hooks_dir = os.path.join(main_script_dir, "pyi_runtime_hooks")
# Ensure they exist (the hook file itself is now permanent)
if not os.path.exists(pyi_build_hooks_dir):
    os.makedirs(pyi_build_hooks_dir)
if not os.path.exists(pyi_runtime_hooks_dir):
    os.makedirs(pyi_runtime_hooks_dir)

# Define the absolute path to the runtime hook
# This hook file (hook-customtkinter.py) must exist at this location.
# It was created in the previous step by an edit_file call.
customtkinter_runtime_hook_abs_path = os.path.join(pyi_runtime_hooks_dir, 'hook-customtkinter.py')

customtkinter_path = None
try:
    import customtkinter
    customtkinter_path = os.path.dirname(customtkinter.__file__)
except ImportError:
    for sp_path in site.getsitepackages():
        potential_path = os.path.join(sp_path, "customtkinter")
        if os.path.isdir(potential_path):
            customtkinter_path = potential_path
            break
    if not customtkinter_path:
        print("WARNING: CustomTkinter path could not be automatically determined for .spec file evaluation stage.")

block_cipher = None

added_files = [
    ("dot_env_example", "."),
]

if customtkinter_path and os.path.isdir(os.path.join(customtkinter_path, "assets")):
    added_files.append((os.path.join(customtkinter_path, "assets"), "customtkinter/assets"))
    print(f"CustomTkinter assets added from: {os.path.join(customtkinter_path, 'assets')}")
elif customtkinter_path:
    print(f"WARNING: Found customtkinter at {customtkinter_path}, but assets subdirectory not found directly within it.")
else:
    print("WARNING: CustomTkinter path not found during spec parsing. Relying on runtime hook and PyInstaller's analysis of main script.")

hidden_imports = [
    'dotenv',
    'requests',
    'sounddevice',
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'pyttsx3.drivers.nsss',
    'pyttsx3.drivers.espeak',
    'PIL._tkinter_finder',
    'google.generativeai',
    'google.ai.generativelanguage',
    'google.api_core',
    'google.auth',
    'google.oauth2',
    'scipy._lib.messagestream',
    'langchain.schema',
    'langchain_core.messages',
    'langchain_core.utils.function_calling',
    'numpy',
    'customtkinter',
]

a = Analysis(
    ['wednesday_client.py'],
    pathex=[main_script_dir],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[pyi_build_hooks_dir], # Can remove pyi_runtime_hooks_dir if we use absolute path for the runtime hook
    hooksconfig={},
    runtime_hooks=[customtkinter_runtime_hook_abs_path], # Use the absolute path here
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_common_options = {
    'name': 'WednesdayClient',
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'console': False,
    'disable_windowed_traceback': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

win_icon_path = os.path.join(main_script_dir, 'assets', 'wednesday_icon.ico')
if sys.platform == "win32" and os.path.exists(win_icon_path):
    exe_common_options['icon'] = win_icon_path
elif sys.platform == "win32":
    print(f"Warning: Windows icon not found at {win_icon_path}")

mac_icon_path = os.path.join(main_script_dir, 'assets', 'wednesday_icon.icns')
if sys.platform == "darwin" and os.path.exists(mac_icon_path):
    exe_common_options['icon'] = mac_icon_path
elif sys.platform == "darwin":
    print(f"Warning: macOS icon not found at {mac_icon_path}")

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, **exe_common_options)

if sys.platform == "darwin":
    if os.path.exists(mac_icon_path):
        app = BUNDLE(exe, name='WednesdayClient.app', icon=mac_icon_path, bundle_identifier=None)
    else:
        app = BUNDLE(exe, name='WednesdayClient.app', bundle_identifier=None)
        print(f"Warning: macOS .app bundle created without icon as it was not found at {mac_icon_path}")

print(f"Spec file processing complete. Ensure all dependencies are available to PyInstaller. Current 'added_files': {added_files}") 