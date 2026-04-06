import socket
import struct
from annuaire_cles import KeyDirectoryServer

# ==========================================
# Fonctions de transport TCP (cadrage)
# ==========================================

def send_seq_binaire(sock: socket.socket, data: bytes) -> None:
    """Envoie la taille du paquet (4 octets) puis les données."""
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)

def recv_seq_binaire(sock: socket.socket) -> bytes:
    """Lit la taille du paquet puis lit exactement ce nombre d'octets."""
    header = _recv_exactly(sock, 4)
    if not header:
        return b""
    length = struct.unpack(">I", header)[0]
    return _recv_exactly(sock, length)

def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    buffer = b""
    while len(buffer) < n:
        chunk = sock.recv(min(4096, n - len(buffer)))
        if not chunk:
            break
        buffer += chunk
    return buffer

def send_recv(host: str, port: int, data: bytes) -> bytes:
    """Ouvre une connexion, envoie le paquet, attend la réponse et ferme."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        send_seq_binaire(sock, data)
        return recv_seq_binaire(sock)

# ==========================================
# Fabrique de réseau Tor
# ==========================================

class FabriqueReseau:
    def __init__(self):
        self.annuaire = KeyDirectoryServer()
        self.noeuds = {}

    def creer_noeud(self, nom: str, port: int):
        # Import local pour éviter l'import circulaire avec oignon_noeud.py
        from oignon_noeud import OignonNoeud
        
        noeud = OignonNoeud(nom, port)
        self.noeuds[nom] = noeud
        # On publie la clé publique dans l'annuaire
        self.annuaire.register(nom, noeud.cles.public_key_pem())
        return noeud

    def demarrer_tout(self):
        for noeud in self.noeuds.values():
            noeud.demarrer()