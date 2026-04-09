import socket
import json
import threading

class ClientHandler:
    def __init__(self, client_socket: socket.socket, address: tuple, dictionary_service):
        self.client_socket = client_socket
        self.address = address
        self.dictionary_service = dictionary_service
        self.thread_name = threading.current_thread().name
        # Wrap socket in file-like object for reliable line reading
        self.rfile = client_socket.makefile('rb')

    def _recv_line(self):
        """Read one complete line using makefile — reliable, no buffer issues."""
        try:
            line = self.rfile.readline()
            if not line:
                return None
            return line.decode('utf-8').strip()
        except Exception:
            return None

    def handle(self):
        print(f"[{self.thread_name}] Client connected: {self.address}")
        try:
            while True:
                raw_data = self._recv_line()

                if not raw_data:
                    break

                try:
                    request = json.loads(raw_data)
                    word = request.get("word", "").strip()
                except json.JSONDecodeError:
                    self._send_response("error", None, "Invalid JSON format.", None)
                    continue

                if not word:
                    self._send_response("error", None, "Empty word received.", None)
                    continue

                print(f"[{self.thread_name}] Query received: '{word}'")
                lookup_result = self.dictionary_service.lookup(word)

                if lookup_result:
                    self._send_response(
                        "success",
                        lookup_result["definition"],
                        None,
                        lookup_result["source"]
                    )
                else:
                    self._send_response(
                        "not_found", None,
                        f"'{word}' not found.", None
                    )

        except (ConnectionResetError, BrokenPipeError):
            print(f"[{self.thread_name}] Client disconnected abruptly: {self.address}")
        finally:
            self.rfile.close()
            self.client_socket.close()
            print(f"[{self.thread_name}] Connection closed: {self.address}")

    def _send_response(self, status: str, definition: str, error: str, source: str = None):
        response = {
            "status": status,
            "definition": definition,
            "error": error,
            "source": source
        }
        raw = json.dumps(response) + "\n"
        self.client_socket.sendall(raw.encode("utf-8"))