import uvicorn
import os
import sys

# Dodajemy katalog src do ścieżki systemowej
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    # Uruchamiamy aplikację wskazując na moduł w src
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)