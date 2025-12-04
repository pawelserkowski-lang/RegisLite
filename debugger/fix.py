# debugger/fix.py
from .chatgpt_client import ask_gpt

def generate_fake_fix(error):
    prompt = f"""Plik: {error['file']}, linia {error['line']}
Problem: {error['message']}
    
Wygeneruj poprawkę w formacie unified diff (tylko fragment!)."""
    diff = ask_gpt(prompt)
    return diff if "diff" in diff.lower() or "---" in diff else """--- a/{0}
+++ b/{0}
@@
-    print("DEBUG")
+    import logging; logging.debug("DEBUG")""".format(error['file'])
