import socket
from concurrent.futures import ThreadPoolExecutor
from dictionary_service import DictionaryService
from client_handler import ClientHandler

HOST = "0.0.0.0"   # Listen on all network interfaces
PORT = 5000
MAX_THREADS = 10   # Thread pool size — handles up to 10 clients simultaneously

def start_server():
    # Load the dictionary once — shared across all threads
    dictionary_service = DictionaryService("dictionary.json")

    # Create the thread pool
    executor = ThreadPoolExecutor(max_workers=MAX_THREADS)

    # Create the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # This line lets us restart the server quickly without "Address already in use" error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Queue up to 5 pending connections
    
    print(f"[Server] Dictionary Server running on {HOST}:{PORT}")
    print(f"[Server] Thread pool size: {MAX_THREADS}")

    try:
        while True:
            # Block here until a client connects
            client_socket, address = server_socket.accept()
            
            # Create a handler for this client
            handler = ClientHandler(client_socket, address, dictionary_service)
            
            # Submit to thread pool — non-blocking, returns immediately
            executor.submit(handler.handle)
            
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        server_socket.close()
        executor.shutdown(wait=True)

if __name__ == "__main__":
    start_server()