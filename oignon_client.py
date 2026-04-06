from crypto_suites_utiles import generate_aes_key, rsa_encrypt, aes_encrypt, aes_decrypt, load_public_key
from oignon_reseau import send_recv

class OignonClient:
    def __init__(self, annuaire):
        self.annuaire = annuaire

    def envoyer_message(self, chemin, message: str, ip_port_final: str):
        print(f"\n[Client] Construction de l'oignon pour : '{message}'")
        payload = message.encode('utf-8')
        cles_aes_sauvegardees = []

        # Construction de l'intérieur vers l'extérieur
        # Le premier next_hop est le serveur final
        next_hop = f"FINAL:{ip_port_final}"

        # On parcourt le chemin à l'envers (Sortie -> Inter -> Entrée)
        for nom_noeud, ip_port in reversed(chemin):
            cle_pub_pem = self.annuaire.get_public_key_pem(nom_noeud)
            cle_aes = generate_aes_key()
            
            # On garde les clés pour pouvoir déchiffrer la réponse plus tard
            cles_aes_sauvegardees.append(cle_aes)

            # On formatte le next_hop sur 64 octets exacts pour faciliter le découpage
            next_hop_bytes = next_hop.encode('utf-8').ljust(64, b'\x00')
            data_a_chiffrer = next_hop_bytes + payload

            # Chiffrement de la donnée (AES) puis de la clé (RSA)
            aes_chiffre = aes_encrypt(cle_aes, data_a_chiffrer)
            rsa_chiffre = rsa_encrypt(load_public_key(cle_pub_pem), cle_aes)

            payload = rsa_chiffre + aes_chiffre
            
            # Le next_hop pour la couche du dessus devient l'IP du noeud actuel
            next_hop = ip_port 

        # Envoi au noeud d'entrée (le premier de la liste)
        entree_ip, entree_port = chemin[0][1].split(":")
        print(f"[Client] Envoi du paquet ({len(payload)} octets) au noeud d'entrée...")
        reponse_chiffree = send_recv(entree_ip, int(entree_port), payload)

        # Déchiffrement de la réponse au retour
        # L'ordre dans 'cles_aes_sauvegardees' est : [Clé Sortie, Clé Inter, Clé Entrée]
        # La réponse a été chiffrée par Sortie, puis Inter, puis Entrée. On déchiffre donc à l'envers !
        print("[Client] Déchiffrement de la réponse de retour...")
        for cle in reversed(cles_aes_sauvegardees):
            reponse_chiffree = aes_decrypt(cle, reponse_chiffree)

        return reponse_chiffree.decode('utf-8')