
# LEXICON: Multi-Threaded Dictionary Server

Lexicon is a three-tier distributed dictionary service designed to demonstrate core principles of socket programming, multi-threading, and client-server architecture. It provides a seamless experience for looking up definitions via raw TCP, REST API, or a web-based frontend.

## 🏗 Architecture Overview

The system follows a three-tier distributed design to ensure separation of concerns:

1. __Tier 1: Socket Server (TCP:5000)__ - The core engine handling low-level communication and multi-threaded client management.
2. __Tier 2: REST API (HTTP:5001)__ - A Flask gateway that bridges the gap between web clients and the dictionary service.
3. __Tier 3: Web Frontend__ - A responsive UI with theme support, search history, and real-time server health monitoring.

## 🚀 Getting Started

### Prerequisites
- __Python 3.10+__
- Basic understanding of terminal/command prompt operations.

### Installation
1. Clone the repository or download the source files.
2. Navigate to the project directory:
   ```bash
   cd Library
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Stack
To operate the full system, start the components in this specific order:

1. __Start the Socket Server:__
   ```bash
   python dictionary_server.py
   ```
2. __Start the REST API:__
   ```bash
   python api_server.py
   ```
3. __Open the Frontend:__
   Launch `frontend/index.html` in your web browser.

## 🛠 Features

- __Tiered Lookup Strategy:__ Checks local `dictionary.json` first, then fetches from a remote API with a graceful fallback to typo suggestions.
- __Multi-Threading:__ Uses `ThreadPoolExecutor` to handle up to 10 concurrent clients without blocking.
- __Thread Safety:__ Implements shared immutable state for the dictionary service to prevent race conditions without complex locking.
- __Smart UX:__ Features Levenshtein Distance for "Did you mean?" suggestions and persistent dark/light mode.

## 📂 Project Structure
```text
.
├── api_server.py          # Flask REST API
├── client_handler.py      # TCP client logic
├── dictionary_server.py   # Multi-threaded TCP server
├── dictionary_service.py  # Core lookup & logic engine
├── dictionary.json        # Local word cache
├── frontend/              # Web assets (HTML, CSS, JS)
└── requirements.txt       # Python dependencies
```

---
__Computer Engineering • UENR 2026__
*Distributed Systems | Socket Programming | Concurrency*
```
