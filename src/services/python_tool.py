import subprocess
import sys


def exec_python(code: str):
    """Executes a snippet of Python code safely."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)
