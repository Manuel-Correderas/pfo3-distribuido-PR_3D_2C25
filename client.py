# client.py
import socket
import sys
import json
from typing import Iterable, Tuple, Optional

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9001
READ_TIMEOUT = 3.0  # segundos

def parse_host_port(argv: list) -> Tuple[str, int]:
    """
    Permite:
      python client.py
      python client.py 127.0.0.1 9001
      python client.py 127.0.0.1:9001
    """
    host, port = DEFAULT_HOST, DEFAULT_PORT
    if len(argv) >= 2:
        a1 = argv[1]
        if ":" in a1:
            h, p = a1.split(":", 1)
            host, port = h.strip(), int(p)
        else:
            host = a1.strip()
            if len(argv) >= 3:
                port = int(argv[2])
    return host, port

def send_tasks(tasks: Iterable[dict], host: str, port: int) -> None:
    print(f"[Client] Conectando a {host}:{port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0)
        s.connect((host, port))
        # Envío: una tarea por línea
        for t in tasks:
            line = json.dumps(t) + "\n"
            s.sendall(line.encode("utf-8"))
            print(f"[Client] Enviada task id={t.get('id')} action={t.get('action')}")
        # Lectura de respuestas línea por línea
        s.settimeout(READ_TIMEOUT)
        buf = b""
        print("[Client] Esperando respuestas...")
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                # Procesar líneas completas
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line.decode("utf-8"))
                    except Exception:
                        print(f"[Client] Respuesta no JSON: {line!r}")
                        continue
                    # Mostrar estado claro
                    tid = data.get("id")
                    status = data.get("status")
                    print(f"[Client] Respuesta task id={tid} status={status}: {data}")
            except socket.timeout:
                # No llegaron más datos en el tiempo definido
                break
    print("[Client] Finalizado.")

def main(argv: list) -> None:
    host, port = parse_host_port(argv)
    # Tareas de ejemplo;
    demo_tasks = [
        {"id": 1, "action": "echo",  "payload": "hola"},
        {"id": 2, "action": "upper", "payload": "texto de prueba"},
        {"id": 3, "action": "sleep", "payload": 0.5},
        {"id": 4, "action": "fib",   "payload": 25},
    ]
    send_tasks(demo_tasks, host, port)

if __name__ == "__main__":
    main(sys.argv)
