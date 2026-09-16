import socket
import threading
import base64


# Classe PRNG
# Générateur pseudo-aléatoire 
# La formule utilisée est :
#       x(n+1) = (a * x(n) + c) mod n

class PRNG:

    def __init__(self, a, c, n):

        self.a = a
        self.c = c
        self.n = n

        # x représente l'état interne du PRNG
        self.x = 0

    def gen_key(self, k):
        # La clé k devient le premier état interne
        self.x = k

    def update(self):
        # Mise à jour de l'état interne
        self.x = (self.a * self.x + self.c) % self.n

        # On retourne le nouvel état interne
        return self.x


# Classe Chiffrement
# On utilise deux PRNG :

# - PRNG_envoi      : pour chiffrer les messages envoyés
# - PRNG_reception  : pour déchiffrer les messages reçus

# Cela permet d'envoyer ET recevoir simultanément.

class Chiffrement:

    def __init__(self, k):
        # Paramètres du PRNG

        a = 8
        c = 6
        n = 256

        # PRNG utilisé pour chiffrer ce que l'on envoie
        self.prng_envoi = PRNG(a, c, n)

        # PRNG utilisé pour déchiffrer ce que l'on reçoit
        self.prng_reception = PRNG(a, c, n)

        # Même clé de départ pour les deux PRNG
        self.prng_envoi.gen_key(k)
        self.prng_reception.gen_key(k)

    def chiffrer(self, m):
        """
        Prend une chaîne de caractères et renvoie
        une chaîne encodée en Base64.
        """

        # La chaîne de caractères devient une suite d'octets
        message_binaire = m.encode("utf-8")

        # Tableau qui contiendra le message chiffré
        chiffre_binaire = bytearray()

        # Pour chaque octet du message,
        # on récupère une valeur du PRNG et on fait XOR.
        for octet in message_binaire:

            masque = self.prng_envoi.update()

            octet_chiffre = octet ^ masque

            chiffre_binaire.append(octet_chiffre)

        # Transformation du binaire en Base64
        chiffre_base64 = base64.b64encode(chiffre_binaire)

        # On renvoie une chaîne de caractères
        return chiffre_base64.decode("ascii")

    def dechiffrer(self, c):
        """
        Prend une chaîne Base64 et renvoie
        la chaîne de caractères originale.
        """

        # On décode la Base64 pour retrouver les octets chiffrés
        chiffre_binaire = base64.b64decode(c)

        # Tableau pour reconstruire le message original
        message_binaire = bytearray()

        # Même opération XOR avec le PRNG de réception
        for octet_chiffre in chiffre_binaire:

            masque = self.prng_reception.update()

            octet_clair = octet_chiffre ^ masque

            message_binaire.append(octet_clair)

        # Conversion des octets en chaîne de caractères
        return message_binaire.decode("utf-8")


# CONFIGURATION

# Adresse IP du PC 1
HOST = "0.0.0.0"

# Port utilisé pour la communication
PORT = 5000

# Clé secrète commune 
CLE = 42


# Création de l'objet de chiffrement

chiffrement = Chiffrement(CLE)


# Variable globale pour la connexion
connexion = None


# Réception des messages

def recevoir_messages():
    """
    Cette fonction tourne dans un thread séparé.
    Elle peut donc recevoir pendant que l'utilisateur tape
    un message à envoyer.
    """

    buffer = b""

    while True:

        try:
            donnees = connexion.recv(4096)

            # Si recv() renvoie vide, la connexion est fermée
            if not donnees:
                print("\n[INFO] L'autre PC a fermé la connexion.")
                break

            buffer += donnees

            # Les messages sont séparés par '\n'
            while b"\n" in buffer:

                ligne, buffer = buffer.split(b"\n", 1)

                if ligne:
                    # Conversion des bytes en texte
                    chiffre = ligne.decode("ascii")

                    try:
                        # Déchiffrement
                        message = chiffrement.dechiffrer(chiffre)

                        print(f"\n[REÇU] {message}")
                        print("> ", end="", flush=True)

                    except Exception as erreur:
                        print(f"\n[ERREUR DE DÉCHIFFREMENT] {erreur}")
                        print("> ", end="", flush=True)

        except Exception as erreur:
            print(f"\n[ERREUR DE RÉCEPTION] {erreur}")
            break


# Serveur : attente du PC 2

def demarrer_serveur():

    global connexion

    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permet de réutiliser le port plus facilement
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # On associe le socket à notre adresse et à notre port
    serveur.bind((HOST, PORT))

    # Le serveur attend une connexion
    serveur.listen(1)

    print("========================================")
    print(" PC 1 - SERVEUR")
    print("========================================")
    print(f"En attente d'une connexion sur le port {PORT}...")

    connexion, adresse = serveur.accept()

    print(f"[CONNECTÉ] Connexion reçue depuis : {adresse}")

    serveur.close()


# Programme principal

demarrer_serveur()

# Création du thread de réception
thread_reception = threading.Thread(
    target=recevoir_messages,
    daemon=True
)

thread_reception.start()


print("\nVous pouvez maintenant discuter.")
print("Tapez un message puis appuyez sur Entrée.")
print("Tapez /quit pour quitter.\n")


# ENVOI DES MESSAGES

while True:

    try:
        message = input("> ")

        if message == "/quit":
            break

        # On ne chiffre pas une chaîne vide
        if message == "":
            continue

        # Chiffrement
        message_chiffre = chiffrement.chiffrer(message)

        # Envoi du Base64.

        connexion.sendall(
            (message_chiffre + "\n").encode("ascii")
        )

        print(f"[ENVOYÉ] {message}")

    except KeyboardInterrupt:
        break

    except Exception as erreur:
        print(f"[ERREUR D'ENVOI] {erreur}")
        break


# Fermeture 
try:
    connexion.close()
except Exception:
    pass

print("Connexion fermée.")