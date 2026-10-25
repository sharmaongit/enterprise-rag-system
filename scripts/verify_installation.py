import importlib.util, sys
from enterprise_rag.config import settings
from enterprise_rag.data.flight_data import load_flights

if __name__ == "__main__":
    print(f"Python: {sys.version.split()[0]}")
    for package in ("fastapi", "pandas", "pydantic", "sklearn", "pytest"):
        print(f"{package}: {'available' if importlib.util.find_spec(package) else 'MISSING'}")
    frame = load_flights(settings.data_path)
    print(f"Dataset loaded: {len(frame)} rows x {len(frame.columns)} columns")
    print("Optional Ollama enabled:", settings.enable_ollama)
