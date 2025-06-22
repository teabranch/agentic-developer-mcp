import os
import socket
import sys

# Get starting port from environment or default to 8180
start_port = int(os.environ.get("MCP_PORT", 8180))
max_port = 8200  # Arbitrary upper limit to avoid infinite loop

for port in range(start_port, max_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            s.close()
            print(port)
            sys.exit(0)
        except OSError:
            continue

print(f"No available port found in range {start_port}-{max_port-1}", file=sys.stderr)
sys.exit(1)
