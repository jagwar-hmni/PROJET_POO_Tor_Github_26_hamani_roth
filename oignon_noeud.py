import socket
import threading
from crypto_suites_utiles import RSAKeyPair, aes_decrypt, aes_encrypt
from oignon_reseau import send_recv, recv_seq_binaire, send_seq_binaire

class OignonNoeud:
    def __init__(self, nom: str, port: int):
        self.nom = nom
        self.port = port
        self.cles = RSAKeyPair()

    def demarrer(self):
        threading.Thread(target=self._serve, daemon=True, name=self.nom).start()

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", self.port))
            srv.listen(5)
            print(f"[{self.nom}] Écoute sur le port {self.port}")
            
            while True:
                conn, _ = srv.accept()
                threading.Thread(target=self._traitement, args=(conn,), daemon=True).start()

    def _traitement(self, conn: socket.socket):
        paquet = recv_seq_binaire(conn)
        if not paquet:
            return

        try:
            # 1. Peler l'oignon (Décapsuler)
            # RSA-2048 donne toujours un chiffré de 256 octets
            rsa_chiffre = paquet[:256]
            aes_chiffre = paquet[256:]

            cle_aes = self.cles.decrypt(rsa_chiffre)
            payload_clair = aes_decrypt(cle_aes, aes_chiffre)

            # 2. Extraire la destination (64 premiers octets) et la donnée interne
            next_hop_str = payload_clair[:64].rstrip(b'\x00').decode('utf-8')
            data_interne = payload_clair[64:]

            print(f"[{self.nom}] Relais vers -> {next_hop_str}")

            # 3. Routage vers le prochain saut
            if next_hop_str.startswith("FINAL:"):
                ip, port_str = next_hop_str.replace("FINAL:", "").split(":")
            else:
                ip, port_str = next_hop_str.split(":")

            reponse_claire = send_recv(ip, int(port_str), data_interne)

            # 4. Rechiffrer la réponse avec la même clé AES pour le retour
            reponse_chiffree = aes_encrypt(cle_aes, reponse_claire)
            send_seq_binaire(conn, reponse_chiffree)

        except Exception as e:
            print(f"[{self.nom}] Erreur de traitement : {e}")
        finally:
            conn.close()