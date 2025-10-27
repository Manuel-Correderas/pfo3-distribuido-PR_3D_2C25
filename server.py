import os
import socket
import threading
import json
import queue
import time
from concurrent.futures import ThreadPoolExecutor

# Opcional: integración RabbitMQ (si está disponible y USE_RABBIT=1)
USE_RABBIT = os.getenv("USE_RABBIT", "0") == "1"
RABBIT_PARAMS = {
    "host": os.getenv("RABBIT_HOST", "localhost"),
    "port": int(os.getenv("RABBIT_PORT", "5672")),
    "queue": os.getenv("RABBIT_QUEUE", "tasks"),
}

try:
    import pika  # type: ignore
except Exception:
    pika = None
    USE_RABBIT = False

HOST = os.getenv("SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("SERVER_PORT", "9001"))
MAX_CLIENTS = 100
WORKERS = int(os.getenv("WORKERS", "4"))

inproc_queue = queue.Queue()

def do_work(task: dict) -> dict:
    # Simula procesamiento de una tarea.
    # Acciones soportadas: echo, fib, upper, sleep
    action = task.get("action")
    payload = task.get("payload")
    if action == "echo":
        return {"ok": True, "data": payload}
    elif action == "upper":
        return {"ok": True, "data": str(payload).upper()}
    elif action == "sleep":
        sec = float(payload or 0.5)
        time.sleep(sec)
        return {"ok": True, "slept": sec}
    elif action == "fib":
        n = int(payload or 20)
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return {"ok": True, "fib": a}
    else:
        return {"ok": False, "error": f"unknown action {action}"}

def worker_loop():
    while True:
        task, client_sock = inproc_queue.get()
        if task is None:
            break
        task_id = task.get("id")
        print(f"[Server] Task {task_id}: iniciando")   # ← comenzó a procesar
        result = do_work(task)
        print(f"[Server] Task {task_id}: finalizó")    # ← terminó
        response = {"id": task_id, "status": "done", "result": result}
        try:
            msg = (json.dumps(response) + "\n").encode("utf-8")
            client_sock.sendall(msg)
        except Exception:
            pass
        finally:
            inproc_queue.task_done()

def handle_client(conn, addr):
    conn_file = conn.makefile("r")
    for line in conn_file:
        line = line.strip()
        if not line:
            continue
        print(f"[Server] Task recibida: {line}")      # ← llegó la solicitud
        try:
            task = json.loads(line)
        except json.JSONDecodeError:
            conn.sendall(b'{"error":"invalid json"}\n')
            continue

        # Enviar a RabbitMQ si está habilitado, de lo contrario usar in-proc queue
        if USE_RABBIT and pika is not None:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBIT_PARAMS["host"], port=RABBIT_PARAMS["port"])
                )
                channel = connection.channel()
                channel.queue_declare(queue=RABBIT_PARAMS["queue"], durable=False)
                # Publish
                channel.basic_publish(exchange="", routing_key=RABBIT_PARAMS["queue"], body=json.dumps(task))
                connection.close()
                # Para demo, respondemos ack inmediato
                ack = {"id": task.get("id"), "status": "queued"}
                conn.sendall((json.dumps(ack) + "\n").encode("utf-8"))
            except Exception as e:
                err = {"id": task.get("id"), "status": "error", "error": str(e)}
                conn.sendall((json.dumps(err) + "\n").encode("utf-8"))
        else:
            # Encolar localmente para ser consumido por pool de workers
            inproc_queue.put((task, conn))

def start_server():
    # Pool de workers locales
    executor = ThreadPoolExecutor(max_workers=WORKERS)
    for _ in range(WORKERS):
        executor.submit(worker_loop)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(MAX_CLIENTS)
        print(f"[Server] Escuchando en {HOST}:{PORT} con {WORKERS} workers (Rabbit={USE_RABBIT})")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    start_server()