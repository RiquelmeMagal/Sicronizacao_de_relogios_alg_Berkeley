import socket
import threading
import time
import random
import argparse

class Node:
    def __init__(self, role, host, port, coordinator_host=None, coordinator_port=None):
        self.role = role
        self.host = host if isinstance(host, str) else str(host)  # Garante string
        self.port = int(port)  # Garante inteiro
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.clock = 0
        self.lock = threading.Lock()
        self.running = True
        self.base_time = 100
        self.initial_offset = random.randint(-10, 10)
        self.clock = self.base_time + self.initial_offset
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.clock_thread = threading.Thread(target=self.update_clock, daemon=True)

    def start(self):
        self.server_thread.start()
        self.clock_thread.start()
        print(f"{self.role.capitalize()} iniciado em {self.host}:{self.port}. Hora inicial: {self.clock}")

    def update_clock(self):
        while self.running:
            time.sleep(1)
            with self.lock:
                self.clock += 1

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            while self.running:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()
                except OSError:
                    break

    def handle_connection(self, conn):
        with conn:
            data = conn.recv(1024).decode().strip()
            if not data:
                return
            if data == "GET_TIME":
                with self.lock:
                    response = str(self.clock)
                conn.send(response.encode())
            elif data.startswith("ADJUST"):
                _, delta = data.split()
                delta = int(delta)
                with self.lock:
                    print(f"{self.role.capitalize()} [{self.host}:{self.port}] Hora antes do ajuste: {self.clock}")
                    self.clock += delta
                    print(f"{self.role.capitalize()} [{self.host}:{self.port}] Hora após ajuste: {self.clock}")
                conn.send(b"Ajuste aplicado.")
            else:
                conn.send(b"Comando invalido.")

    def stop(self):
        self.running = False

class Coordinator(Node):
    def __init__(self, host, port, clients):
        super().__init__("coordenador", host, port)
        self.clients = [(h, int(p)) for h, p in (c.split(':') for c in clients)]  # Conversão segura

    def handle_connection(self, conn):
        with conn:
            data = conn.recv(1024).decode().strip()
            if data == "SYNC":
                self.synchronize_clocks()
                conn.send(b"Sincronizacao concluida!")
            else:
                super().handle_connection(conn)

    def synchronize_clocks(self):
        with self.lock:
            own_time = self.clock
        print(f"\nCoordenador [{self.host}:{self.port}] Hora antes do ajuste: {own_time}")

        times = [own_time]
        for client_host, client_port in self.clients:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((client_host, client_port))
                    s.sendall(b"GET_TIME")
                    response = s.recv(1024).decode()
                    client_time = int(response)
                    times.append(client_time)
                    print(f"Coordenador recebeu hora {client_time} de {client_host}:{client_port}")
            except Exception as e:
                print(f"Erro ao obter hora de {client_host}:{client_port}: {e}")

        average = sum(times) // len(times)
        print(f"Coordenador calculou a média: {average}")

        # Ajustar próprio relógio
        with self.lock:
            adjustment = average - own_time
            self.clock += adjustment
        print(f"Coordenador [{self.host}:{self.port}] Hora após ajuste: {self.clock}")

        # Ajustar clientes
        for (client_host, client_port), client_time in zip(self.clients, times[1:]):
            try:
                adjustment = average - client_time
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((client_host, client_port))
                    s.sendall(f"ADJUST {adjustment}".encode())
                    s.recv(1024)  # Confirmação
            except Exception as e:
                print(f"Erro ao ajustar {client_host}:{client_port}: {e}")

class Client(Node):
    def __init__(self, host, port, coordinator_host, coordinator_port):
        super().__init__("cliente", host, port, coordinator_host, int(coordinator_port))  # Conversão explícita

def main():
    parser = argparse.ArgumentParser(description="Sincronização de Berkeley")
    parser.add_argument("--role", choices=["coordenador", "cliente"], required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--coordinator", help="Host:Porta do coordenador (apenas para clientes)")
    parser.add_argument("--clients", nargs="+", help="Lista de clientes Host:Porta (apenas para coordenador)")
    parser.add_argument("--auto", action="store_true", help="Modo automático")
    args = parser.parse_args()

    if args.role == "coordenador":
        node = Coordinator(args.host, args.port, args.clients or [])
        node.start()
        if not args.auto:
            input("Pressione Enter para iniciar a sincronização...\n")
            node.synchronize_clocks()
        try:
            while True: 
                time.sleep(1)
        except KeyboardInterrupt:
            node.stop()
    else:
        coordinator_host, coordinator_port = args.coordinator.split(':')
        node = Client(args.host, args.port, coordinator_host, coordinator_port)
        node.start()
        try:
            while True: 
                time.sleep(1)
        except KeyboardInterrupt:
            node.stop()

if __name__ == "__main__":
    main()