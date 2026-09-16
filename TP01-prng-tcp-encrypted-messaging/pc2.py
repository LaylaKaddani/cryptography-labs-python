import socket
import threading
import base64



# Classe PRNG

class PRNG:

    def __init__(self, a, c, n):
        # Mise en place des paramètres a,c,n
        self.a = a
        self.c = c
        self.n = n

        # État interne
        self.x = 0

    def gen_key(self, k):
        # La clé = le premier état interne
        self.x = k

    def update(self):
        # Met jour l'état :
    
        self.x = (self.a * self.x + self.c) % self.n

        return self.x



# Classe Chiffrement


class Chiffrement:

    def __init__(self, k):

        # Paramètres du PRNG
    
        a = 8
        c = 6
        n = 256

        # PRNG pour les messages envoyé
        self.prng_envoi = PRNG(a, c, n)

        # PRNG pour les messages reçus
        self.prng_reception = PRNG(a, c, n)

        # Même clé secrète
        self.prng_envoi.gen_key(k)
        self.prng_reception.gen_key(k)

    def chiffrer(self, m):
        """
        Transforme le message clair en message chiffré Base64.
        """

        # Encodage de la chaîne en binaire
        message_binaire = m.encode("utf-8")

        # Résultat du chiffrement
        chiffre_binaire = bytearray()

        # XOR entre le message et le masque du PRNG
        for octet in message_binaire:

            masque = self.prng_envoi.update()

            octet_chiffre = octet ^ masque

            chiffre_binaire.append(octet_chiffre)

        # Encodage Base64
        chiffre_base64 = base64.b64encode(chiffre_binaire)

        return chiffre_base64.decode("ascii")

    def dechiffrer(self, c):
        """
        Transforme un message Base64 chiffré
        en message clair.
        """

        # Décodage Base64
        chiffre_binaire = base64.b64decode(c)

        message_binaire = bytearray()

        # XOR avec le PRNG de réception
        for octet_chiffre in chiffre_binaire:

            masque = self.prng_reception.update()

            octet_clair = octet_chiffre ^ masque

            message_binaire.append(octet_clair)

        # Retourne le message clair
        return message_binaire.decode("utf-8")



# CONFIGURATION (Connexion au PC1)




HOST = "10.94.136.101"

PORT = 5000

# Même clé que le PC 1
CLE = 42



# Objet de chiffrement


chiffrement = Chiffrement(CLE)

connexion = None



# Réception


def recevoir_messages():

    buffer = b""

    while True:

        try:
            donnees = connexion.recv(4096)

            if not donnees:
                print("\n[INFO] L'autre PC a fermé la connexion.")
                break

            buffer += donnees

            # On traite chaque message terminé par '\n'
            while b"\n" in buffer:

                ligne, buffer = buffer.split(b"\n", 1)

                if ligne:

                    chiffre = ligne.decode("ascii")

                    try:
                        message = chiffrement.dechiffrer(chiffre)

                        print(f"\n[REÇU] {message}")
                        print("> ", end="", flush=True)

                    except Exception as erreur:

                        print(
                            f"\n[ERREUR DE DÉCHIFFREMENT] {erreur}"
                        )

                        print("> ", end="", flush=True)

        except Exception as erreur:

            print(f"\n[ERREUR DE RÉCEPTION] {erreur}")
            break



# Connexion au PC1


def se_connecter():

    global connexion

    connexion = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    print("========================================")
    print(" PC 2 - CLIENT")
    print("========================================")
    print(f"Connexion à {HOST}:{PORT}...")

    connexion.connect((HOST, PORT))

    print("[CONNECTÉ] Connexion établie.")



# Programme principal


se_connecter()


# Le thread de réception fonctionne en parallèle
thread_reception = threading.Thread(
    target=recevoir_messages,
    daemon=True
)

thread_reception.start()


print("\nVous pouvez maintenant discuter.")
print("Tapez un message puis appuyez sur Entrée.")
print("Tapez /quit pour quitter.\n")



# ENVOI


while True:

    try:

        message = input("> ")

        if message == "/quit":
            break

        if message == "":
            continue

        # Chiffrement
        message_chiffre = chiffrement.chiffrer(message)

        # Envoi
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