import sys
from pathlib import Path

# Add 'backend' and 'backend/src' to sys.path so 'src' and root modules can be imported
backend_dir = Path(__file__).resolve().parent.parent
src_dir = backend_dir / "src"

for directory in [str(backend_dir), str(src_dir)]:
    if directory not in sys.path:
        sys.path.insert(0, directory)
