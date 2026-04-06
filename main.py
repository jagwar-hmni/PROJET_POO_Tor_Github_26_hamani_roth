import time
from oignon_reseau import FabriqueReseau
from serveur_echo import ServeurEcho
from oignon_client import OignonClient

def main():
    print("=== Démarrage du Projet Tor ===\n")

    # 1. Initialiser le réseau (Annuaire)
    reseau = FabriqueReseau()

    # 2. Création et enregistrement des relais
    reseau.creer_noeud("Noeud_Entree", 8001)
    reseau.creer_noeud("Noeud_Intermediaire", 8002)
    reseau.creer_noeud("Noeud_Sortie", 8003)

    reseau.demarrer_tout()

    # 3. Démarrer le serveur final
    serveur = ServeurEcho(9000)
    serveur.demarrer()

    # On laisse une seconde pour que tous les threads sockets écoutent bien
    time.sleep(1)

    # 4. Simuler le client
    client = OignonClient(reseau.annuaire)

    # Définition du circuit de routage voulu
    chemin = [
        ("Noeud_Entree", "127.0.0.1:8001"),
        ("Noeud_Intermediaire", "127.0.0.1:8002"),
        ("Noeud_Sortie", "127.0.0.1:8003")
    ]

    print("\n" + "-"*40)
    reponse = client.envoyer_message(chemin, "Bonjour depuis Annecy !", "127.0.0.1:9000")
    print("-"*40)
    
    print(f"\n[Succès] Le client a reçu la réponse finale : {reponse}")

if __name__ == "__main__":
    main()