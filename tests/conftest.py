import sys
from pathlib import Path

# Добавляем корень репозитория в sys.path, чтобы тесты могли импортировать пакет `app`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
