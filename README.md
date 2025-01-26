# AI-Powered Search Agent

An intelligent search agent that combines web search capabilities with AI-powered content processing using Ollama.

## Features

- Intelligent web searching based on user queries
- Content scraping and validation
- AI-powered response generation
- Colored logging output
- Interactive chat interface

## Prerequisites

Before running the search agent, you need to:

1. Install Ollama:
   - **macOS or Linux**:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```
   - **Windows**:
     - Download and install from [Ollama.com](https://ollama.com)

2. Have Python 3.8+ installed on your system

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ayepRahman/search-web-ai
   cd search-web-ai
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Activate on Windows
   .\venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Setting Up Ollama

1. After installing Ollama, pull the required model:
   ```bash
   ollama pull llama3.2
   ```

2. Verify Ollama is running:
   - On macOS/Linux, it should start automatically after installation
   - On Windows, launch the Ollama application
   - You can verify by opening a terminal and running:
     ```bash
     ollama list
     ```

## Running the Search Agent

1. Make sure Ollama is running in the background

2. Run the search agent:
   ```bash
   python search_agent.py
   ```

3. Start chatting! The agent will:
   - Analyze your query
   - Determine if web search is needed
   - Search and process relevant information
   - Provide AI-generated responses

## Example Usage

```bash
python search_agent.py
```

```bash
You: What is the weather in Tokyo?
```


```
Assistant: The weather in Tokyo is currently sunny with a temperature of 20°C.
```
