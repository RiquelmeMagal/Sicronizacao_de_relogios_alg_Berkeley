import argparse
import subprocess
import sys
import time
import socket
import os
from colorama import init, Fore

init(autoreset=True)

def kill_ports(ports):
    for port in ports:
        os.system(f"fuser -k {port}/tcp > /dev/null 2>&1")

def wait_for_port(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket() as s:
                s.connect(("localhost", port))
                return True
        except ConnectionRefusedError:
            time.sleep(0.5)
    return False

def auto_start():
    ports = [5000, 5001, 5002, 5003, 5004]
    kill_ports(ports)

    print(Fore.CYAN + "🚀 Iniciando todos os nós...")

    # Iniciar coordenador
    coordinator = subprocess.Popen([
        sys.executable, "node.py",
        "--role", "coordenador",
        "--port", "5000",
        "--clients", "localhost:5001", "localhost:5002", "localhost:5003", "localhost:5004",
        "--auto"
    ], cwd="src")

    # Iniciar clientes
    clients = []
    for port in ports[1:]:
        clients.append(subprocess.Popen([
            sys.executable, "node.py",
            "--role", "cliente",
            "--port", str(port),
            "--coordinator", "localhost:5000"
        ], cwd="src"))

    if not wait_for_port(5000):
        print(Fore.RED + "⛔ Coordenador não iniciou a tempo")
        return

    print(Fore.YELLOW + "\n🔁 Sincronizando...")
    try:
        with socket.socket() as s:
            s.connect(("localhost", 5000))
            s.sendall(b"SYNC")
            print(Fore.GREEN + "Resposta:", s.recv(1024).decode())
    except Exception as e:
        print(Fore.RED + f"Erro na sincronização: {e}")

    input(Fore.CYAN + "\n⏹ Pressione Enter para finalizar...")
    coordinator.terminate()
    for c in clients:
        c.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Modo automático completo")
    args = parser.parse_args()

    if args.auto:
        auto_start()
    else:
        from node import main
        main()
