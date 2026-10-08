set shell := ["powershell.exe", "-c"]

build-exe:
    uv run pyinstaller --windowed --noconfirm --clean chess.spec