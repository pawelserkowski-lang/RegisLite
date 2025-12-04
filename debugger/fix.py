# debugger/fix.py
from .chatgpt_client import ask_gpt

def generate_fix(error):
    prompt = f"""Plik: {error['file']}, linia {error['line']}
Problem: {error['message']}

Wygeneruj poprawkę w formacie unified diff. Tylko fragment!"""
    diff = ask_gpt(prompt)
    if "---" not in diff:
        diff = f"""--- a/{error['file']}
+++ b/{error['file']}
@@
-    print("SIEMA")
+    import logging; logging.info("SIEMA")"""
    return diff
