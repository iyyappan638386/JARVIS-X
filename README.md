# JARVIS-X

A local AI-powered desktop and voice assistant built with Python.

## Features

- Local AI chat using Ollama
- Offline speech recognition using Faster-Whisper
- Windows text-to-speech
- Conversation memory and long-term facts
- Desktop application automation
- System information
- Volume control
- Conversation backup and restore

## Requirements

- Windows 10 or later
- Python 3.13
- Ollama
- Microphone and speakers for voice mode

## Installation

1. Create a virtual environment:
   `python -m venv .venv`

2. Activate the environment:
   `.venv\Scripts\Activate.ps1`

3. Install dependencies:
   `python -m pip install -r requirements.txt`


## Ollama Setup

Install Ollama, then download the configured model:

```powershell
ollama pull qwen2.5:3b
```

Make sure Ollama is running before starting AI chat.

## Run JARVIS-X

### Text Chat
```powershell
python -m app.chat
```

### Voice Assistant
```powershell
python -m app.voice_chat
```

### Basic Application
```powershell
python -m app.main
```


## Run Tests

Run the complete test suite:

```powershell
python -m pytest -v
```


## Configuration

Default settings are defined in `app/config.py`.

See `.env.example` for the configuration reference.

Environment variables must be available to the Python process.

## Project Structure

```text
jarvis-x/
|-- app/
|   |-- ai/
|   |   |-- __init__.py
|   |   |-- provider.py
|   |   |-- ollama_provider.py
|   |-- __init__.py
|   |-- backup.py
|   |-- chat.py
|   |-- command_router.py
|   |-- config.py
|   |-- desktop_automation.py
|   |-- logging_config.py
|   |-- long_term_memory.py
|   |-- main.py
|   |-- memory.py
|   |-- system_info.py
|   |-- voice_chat.py
|   |-- voice_test.py
|   |-- volume_control.py
|-- tests/
|-- data/
|-- docs/
|-- logs/
|-- models/
|-- screenshots/
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- README.md
```
## Development Status

JARVIS-X is under active development. Some features may have limitations or require additional testing.
