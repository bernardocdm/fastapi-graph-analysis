import os
from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretórios de dados
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR = DATA_DIR / "outputs"

# Configurações do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DEFAULT_REPO = "encode/fastapi"

def init_directories():
    """Garante que todas as pastas de dados necessárias existam no disco."""
    for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR]:
        path.mkdir(parents=True, exist_ok=True)

# Inicializar pastas na importação do módulo
init_directories()
