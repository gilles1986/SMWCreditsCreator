import PyInstaller.__main__
import shutil
import os
import customtkinter

# Get CustomTkinter path for data bundling
ctk_path = os.path.dirname(customtkinter.__file__)

print("Building SMW Credits Creator...")

args = [
    'main.py',
    '--name=SMWCreditsCreator',
    '--onefile',
    '--windowed',
    '--noconfirm',
    f'--add-data={ctk_path};customtkinter',
]

if os.path.exists('icon.ico'):
    args.append('--icon=icon.ico')
    args.append('--add-data=icon.ico;.')
    print("Using icon.ico")
else:
    print("Warning: icon.ico not found, building with default icon.")

PyInstaller.__main__.run(args)

print("Build complete. Copying external files...")

# With --onefile, the exe is directly in dist/
dest_dir = 'dist' 

# Files to copy
files_to_copy = ['config.template.json', 'mapping.json', 'user_manual.html']

for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, dest_dir)
        print(f"Copied {f}")
    else:
        print(f"Warning: {f} not found!")

print(f"Done! Executable is in {dest_dir}")
