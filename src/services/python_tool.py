import asyncio
import subprocess
import sys

async def exec_python(code: str):
    """Executes a snippet of Python code safely (async)."""
    try:
        # Create a subprocess safely using asyncio
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Wait for the process to finish and get output with a timeout
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            return (stdout.decode() + stderr.decode())
        except asyncio.TimeoutError:
            proc.kill()
            return "Error: Timeout exceeded (10s)"
    except Exception as e:
        return str(e)
