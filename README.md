# Necrom - a 2.5D shooter demo
Welcome to Necrom, a demo 2.5D first-person-shooter written in [Python 3](https://www.python.org). Expect skeletons, rats and endless waves of enemies. Survive as long as you can!

# Requirements
- [Python 3.9.2](https://www.python.org/downloads/release/python-392/)
- Packages listed in [`requirements.txt`](requirements.txt)

Python 3.9.2 can be downloaded [here](https://www.python.org/downloads/release/python-392/).

It is recommended (and just good practice) to set up a Python virtual environment using Python's builtin `venv` module.

The packages can be installed manually or automatically using pip in the project root:
`pip install -r requirements.txt`

Launch the game with `python main.py` (make sure you have activated the venv if you created one).

# Gameplay
Move with WASD. Turn with mouse. Shoot with left mouse button.

Survive as long as you can.

# Additional information
## Logging
Logs are generated in `log.txt` at the project root.
## Config
Config is available in `config.ini` at the project root. Configurable options include controls, mouse sensitivity, log level, and video settings (e.g. fullscreen, resolution, etc.).
## Debugging
Activate debugging mode by launching `main.py` with the flag `--debug`.
- `lshift+f3` to toggle debug info
- `lshift+g` to toggle god mode
- `lshift+n` to toggle noclip