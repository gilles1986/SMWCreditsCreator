import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class CallistoHandler:
    @staticmethod
    def get_executable_path(project_path, version):
        # Tuple version comparison
        if version >= (5, 13):
            return os.path.join(project_path, "tools", "Callisto", "callisto.exe")
        else:
            # v5.00 - v5.12
            return os.path.join(project_path, "buildtool", "callisto.exe")

    @staticmethod
    def run_command(project_path, version, command):
        exe_path = CallistoHandler.get_executable_path(project_path, version)
        if not os.path.exists(exe_path):
            return False, f"Executable not found at {exe_path}"
        
        try:
            # Run in project root? Or exe dir? usually project root is CWD for these tools or they take args.
            # Assuming run from project root.
            # Command is "callisto.exe save" or "callisto.exe update"
            
            # Note: subprocess.run needs the list of args
            cmd_args = [exe_path, command]
            
            # Hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(
                cmd_args, 
                cwd=project_path, 
                capture_output=True, 
                text=True, 
                startupinfo=startupinfo
            )
            
            if result.returncode == 0:
                return True, f"Successfully ran '{command}'."
            else:
                return False, f"Error running '{command}': {result.stderr}"
                
        except Exception as e:
            logger.error(f"Failed to run callisto: {e}")
            return False, f"Exception running callisto: {e}"

    @staticmethod
    def save(project_path, version):
        return CallistoHandler.run_command(project_path, version, "save")

    @staticmethod
    def update(project_path, version):
        return CallistoHandler.run_command(project_path, version, "update")
