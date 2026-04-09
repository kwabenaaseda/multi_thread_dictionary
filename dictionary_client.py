import socket
import json

HOST = "127.0.0.1"
PORT = 5000

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    # Wrap in file-like object — same fix as server side
    rfile = client_socket.makefile('rb')
    
    print(f"Connected to Dictionary Server at {HOST}:{PORT}")
    print("Type a word to look it up. Type 'quit' to exit.\n")

    try:
        while True:
            word = input("Enter word: ").strip()
            if word.lower() == "quit":
                break
            if not word:
                continue

            # Send request
            request = json.dumps({"word": word}) + "\n"
            client_socket.sendall(request.encode("utf-8"))

            # Read exactly one complete line — blocks until \n arrives
            raw_response = rfile.readline()
            if not raw_response:
                print("Server closed connection.")
                break

            response = json.loads(raw_response.decode('utf-8').strip())

            if response["status"] == "success":
                source = response.get("source", "unknown")
                print(f"Definition [{source}]: {response['definition']}\n")
            elif response["status"] == "not_found":
                print(f"Not found: {response['error']}\n")
            else:
                print(f"Error: {response['error']}\n")

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        rfile.close()
        client_socket.close()
        print("Disconnected.")

if __name__ == "__main__":
    start_client()