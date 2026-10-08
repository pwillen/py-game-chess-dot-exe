# py-game-chess-dot-exe
Downloadable Chess App

## Build a Windows `.exe` (one-folder)

### Prerequisites
- Windows
- Python 3.12+
- `uv`
- `just`

Install project dependencies (including PyInstaller in the dev group):

```powershell
uv sync --dev
```

### Build command
From the repository root:

```powershell
just build-exe
```

### Output
PyInstaller produces the app in:

`dist\chess\`

Run:

`dist\chess\chess.exe`
