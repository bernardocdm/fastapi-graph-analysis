import os
from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar arquivo .env manualmente (sem dependência de python-dotenv)
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _val = _line.split("=", 1)
                os.environ.setdefault(_key.strip(), _val.strip().strip('"').strip("'"))

# Diretórios de dados
DATA_DIR           = BASE_DIR / "data"
RAW_DATA_DIR       = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR    = DATA_DIR / "outputs"

_tokens_csv = os.getenv("GITHUB_TOKENS", "")
if _tokens_csv:
    GITHUB_TOKENS = [t.strip() for t in _tokens_csv.split(",") if t.strip()]
else:
    GITHUB_TOKENS = [
        t for t in [
            os.getenv("GITHUB_TOKEN_1", ""),
            os.getenv("GITHUB_TOKEN_2", ""),
            os.getenv("GITHUB_TOKEN_3", ""),
            os.getenv("GITHUB_TOKEN",   ""),   # fallback legado
        ] if t
    ]
    # Remove duplicatas mantendo a ordem
    seen = set()
    GITHUB_TOKENS = [t for t in GITHUB_TOKENS if not (t in seen or seen.add(t))]

# Mantido por compatibilidade com código que ainda importe GITHUB_TOKEN diretamente
GITHUB_TOKEN = GITHUB_TOKENS[0] if GITHUB_TOKENS else ""

# Repositório padrão
DEFAULT_REPO = "makeplane/plane"


def init_directories():
    """Garante que todas as pastas de dados necessárias existam no disco."""
    for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR]:
        path.mkdir(parents=True, exist_ok=True)

# Inicializar pastas na importação do módulo
init_directories()
