import socket
import threading
from oignon_reseau import recv_seq_binaire, send_seq_binaire

class ServeurEcho:
    def __init__(self, port: int):
        self.port = port

    def demarrer(self):
        threading.Thread(target=self._serve, daemon=True, name="ServeurEcho").start()

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", self.port))
            srv.listen(5)
            print(f"[ServeurEcho] Écoute sur le port {self.port}")
            
            while True:
                conn, _ = srv.accept()
                paquet = recv_seq_binaire(conn)
                if paquet:
                    msg_str = paquet.decode('utf-8')
                    print(f"[ServeurEcho] Reçu : {msg_str}")
                    
                    reponse = f"ECHO : {msg_str}".encode('utf-8')
                    send_seq_binaire(conn, reponse)
                conn.close()