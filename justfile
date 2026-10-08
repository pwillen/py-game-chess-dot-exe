set shell := ["powershell.exe", "-c"]

build-exe:
    uv run pyinstaller --noconfirm --clean chess.spec