# services/python_tool.py
import ast
import sys
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

async def exec_python(code: str):
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Eval, ast.Exec, ast.Delete, ast.Global, ast.Nonlocal)):
                return "[ERROR] Dangerous code blocked!"
        f = StringIO()
        e = StringIO()
        with redirect_stdout(f), redirect_stderr(e):
            exec(code, {"__builtins__": {}}, {})
        out = f.getvalue() + e.getvalue()
        return out or "OK – kod wykonany bez błędów"
    except Exception as err:
        return f"[ERROR] {str(err)}"
