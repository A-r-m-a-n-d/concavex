################################################################################
#########|                                                            |#########
#########|   Fichier principal à exécuter se faire affronter les IA   |#########
#########|____________________________________________________________|#########
################################################################################



"""
Crédits :
Script réalisé par DE SAINT LEGER Térence en classe de Tle 7 Hélios

Prière de vous référer à READ_ME.txt pour plus d'informations
"""



#---------------------------< Imports des modules >----------------------------#


import multiprocessing as mp # Permet de faire tourner plusieurs fils de code
import pygame as pg # Moteur du jeu
from timeit import default_timer as timer # Utilisé pour ralentir manuellement les IA
import random as rd # Permet une génération aléatoire
import math # Utilisé 1 ou 2 fois pour des calculs
from os import listdir # Chargement automatique des images
from ressources.scripts.police import zoneTexte # Police faite maison :)



#------------------------------< Mise en place >-------------------------------#


pg.init() # Initialisation de pygame


# Participants (entrer le nom du fichier)
team_1 = "bob"
team_2 = "bob"


# Valeur par laquelle est divisée la vitesse d'exécution des IA
IA_SLOW_FACTOR = 5000 # Vitesse actuellement divisée par 4000
# Intervale minimum entre chaque exécution de l'IA : 50 ms


# Affichage d'éléments de débug et log d'informations dans la console
debug = True


"""
Explications rapides :

La surface "focus_screen" est l'écran d'affichage. A chaque frame, "screen" est dessinée, centrée et redimmensionnée sur "focus_screen". "focus_screen" est adaptée automatiquement à la taille de l'écran (plein écran).

La surface "screen" est la surface sur laquelle la simulation tourne. Sa taille ne varie que en fonction de la taille de la map.

Toutes les variables définies ci-dessous (sauf les constantes, la partie "focus_screen" et "gen_signature") sont définies temporairement, et voient leurs valeurs remplacées par la fonction "re_init()".

Si vous voullez créer votre propre génération de map, entrez clé et surface dans "GEN_SIGNATURES", allez dans "generate_carte" et créez votre propre générateur d'enfer sur Terre !
"""


# Si vous souhaitez signer vos attrocitées ($ = séparateur couleur-texte)
GEN_SIGNATURES = {
    # Générations par "La NSI"
    "Defaut": zoneTexte("(255,255,255)$Nom : $(180,180,180)$Labyrinthe classique  $(255,255,255)$-  Auteur : $(180,180,180)$La NSI", 2),
    "Blocks": zoneTexte("(255,255,255)$Nom : $(255,255,0)$Block-Land  $(255,255,255)$-  Auteur : $(180,180,180)$La NSI", 2),
    # Générations par "Térence"
    "PYRAT": zoneTexte("(255,255,255)$Nom : $(235,185,25)$Génération officielle de PYRAT édition Deluxe  $(255,255,255)$-  Auteur : $(235,185,25)$Térence", 2),
    "Ter1": zoneTexte("(255,255,255)$Nom : $(180,255,180)$Simplicité  $(255,255,255)$-  Auteur : $(235,185,25)$Térence", 2),
    "Ter2": zoneTexte("(255,255,255)$Nom : $(255,100,255)$Murs sans fins  $(255,255,255)$-  Auteur : $(235,185,25)$Térence", 2),
    "Ter3": zoneTexte("(255,255,255)$Nom : $(255,0,0)$Les couloirs de la douleur  $(255,255,255)$-  Auteur : $(235,185,25)$Térence", 2),
    "Vide": zoneTexte("(255,255,255)$Nom : $(255,120,0)$L'arène  $(255,255,255)$-  Auteur : $(170,15,0)$Le grand MANDIC", 2),
    "Points": zoneTexte("(255,255,255)$Nom : $(180,255,180)$Les petits points  $(200,100,255)$-  Auteur : $(235,185,25)$Térence", 2),
    }

SIZE = 64 # Taille d'une tuile avant zoom/dézoom

# Dictionnaire des mouvement (et donc outputs) possibles
MOVE = {
    "H": (0, -1),
    "B": (0, 1),
    "D": (1, 0),
    "G": (-1, 0)
}


# Surfaces représentants le nom des équipes (nom de fichier)
t1_name = zoneTexte(f"(255,0,0)$Equipe n°1 : {team_1.replace('_', ' ')}", 3)
t2_name = zoneTexte(f"(0,0,255)$Equipe n°2 : {team_2.replace('_', ' ')}", 3)

t1_victory = zoneTexte(f"(235,185,25)$L'équipe n°1 $(255,0,0)${team_1} $(235,185,25)$remporte la victoire !", 5)
t2_victory = zoneTexte(f"(235,185,25)$L'équipe n°2 $(0,0,255)${team_2} $(235,185,25)$remporte la victoire !", 5)

# Dimmensions de la carte (en tuiles) par défaut (pas en dessous de 19x19 svp)
dim_carte = (24, 24)
# Taille de la carte (en pixels)
size_carte = (dim_carte[0]*SIZE, dim_carte[1]*SIZE)
# Carte par défaut (sans les murs centraux) avec 2 de largeur en mur extérieurs
carte = [[" " if x not in [0, 1, dim_carte[0] - 1, dim_carte[0] - 2] and y not in [0, 1, dim_carte[1] - 1, dim_carte[1] - 2] else "#" for x in range(dim_carte[0])] for y in range(dim_carte[1])]
# Nombre total de fromage à rammasser
nb_cheese = 0
# Point d'apparition
spawnpoint = (0, 0)

# Nom du générateur + auteur :)
gen_signature = "Defaut"

# Taille de l'écran d'affichage
fs_width, fs_height = pg.display.Info().current_w, pg.display.Info().current_h
# fs_width, fs_height = 500, 500 # Si l'on veux déactiver le full-screen
# Ecran d'affichage
focus_screen = pg.display.set_mode((fs_width, fs_height))

# Ecran de simulation
screen = pg.surface.Surface(size_carte)
# Taille de l'écran de simulation lorsque redimmentionné
screen_zoom_size = (fs_width, int(size_carte[1]*fs_width/size_carte[0])) if fs_width/size_carte[0] < fs_width/size_carte[1] else (int(size_carte[0]*fs_height/size_carte[1]), fs_height)
# Position de l'écran de simulation lorsqu'affiché
screen_pos = ((fs_width - screen_zoom_size[0])//2, (fs_height - screen_zoom_size[1])//2)

# Bordure semi-transparante de l'écran s'affichage
fs_border_size = (fs_width, 51)
fs_border = pg.surface.Surface(fs_border_size)
fs_border.fill((255, 255, 255))
for y in range(fs_border_size[1]):
    for x in range(fs_border_size[0]):
        if (x + y)%3 != 0:
            pg.draw.rect(fs_border, (0, 0, 0), ((x, y), (1, 1)))
fs_border.set_colorkey((255, 255, 255))

# Affichage en HD (consomme BEAUCOUP de ressources)
HD_display = False

timer_start = 0


def load_img(path: str, size: tuple[int, int]=None) -> pg.Surface:
    """Charge une image et ajuste sa taille"""

    # CHargement de l'image
    img = pg.image.load(path)

    # Si l'image ne doit pas être redimmensionnée, alors retourne l'image
    if size is None:
        return img

    # smoothscale() nécessite une image en 24-bits ou 32-bits
    if img.get_bitsize() in (24, 32):
        return pg.transform.smoothscale(img, size)
    return pg.transform.scale(img, size)


# Set de tuile [<nom_set_tuiles>][<nom_tuile>] (seulement des png)
tiles_set = {folder: {file[:-4]: load_img(f"ressources\\images\\set_tuiles\\{folder}\\{file}", (SIZE, SIZE)) for file in listdir(f"ressources\\images\\set_tuiles\\{folder}") if file.endswith(".png")} for folder in listdir("ressources\\images\\set_tuiles")}
# Set de tuile utilisé ("none" = pas de textures)
used_tiles_set = "defaut"

# Sprites des IA (souris)
AI1_sprite = load_img(f"participants\\{team_1}\\custom\\souris.png", (SIZE, SIZE))
AI2_sprite = load_img(f"participants\\{team_2}\\custom\\souris.png", (SIZE, SIZE))

# Initialisation de variables pour les IA (afin qu'elles ne soit pas considérées comme des erreurs)
AI1_brain = None # Cerveau le l'IA n°1
AI2_brain = None # Cerveau le l'IA n°2

# Cerveau des IA
exec(f"from participants.{team_1}.main import main as AI1_brain")
exec(f"from participants.{team_2}.main import main as AI2_brain")

# Position des IA
AI1_pos = (0, 0)
AI2_pos = (0, 0)
# Score des IA
t1_score = 0
t2_score = 0

# Variables de debug
AI1_true_pos = (0, 0) # Position à laquelle l'IA n°1 pense être
AI2_true_pos = (0, 0) # Position à laquelle l'IA n°2 pense être



#--------------------------< Fonctions principales >---------------------------#


# Partie IA


def update_AI(send_data: bool=True) -> None:
    """Met à jour les données qu'ont les IA et gère leurs output"""

    # Réception et gestion des données (+ log des output)

    # Utilisé pour l'affichage du momment d'output
    time = pg.time.get_ticks() - timer_start
    time_txt = "00000" + str(time%60000)

    # Depuis l'IA n°1
    while not com_out_AI1.empty():
        output_AI1 = com_out_AI1.get()

        # Exécution de l'output
        if output_AI1 in MOVE and carte[AI1_pos[1] + MOVE[output_AI1][1]][AI1_pos[0] + MOVE[output_AI1][0]] != "#":
            globals()["AI1_pos"] = (AI1_pos[0] + MOVE[output_AI1][0], AI1_pos[1] + MOVE[output_AI1][1])
            # Si l'IA a atteint un fromage
            if carte[AI1_pos[1]][AI1_pos[0]] == "$":
                carte[AI1_pos[1]][AI1_pos[0]] = " "
                globals()["t1_score"] += 1

        # Log de l'output
        if debug:
            print(f"({time//60000}:{time_txt[-5:-3]}:{time_txt[-3:]})  IA n°1  ->  {output_AI1}\nPosition de l'IA n°1  :  x = {AI1_pos[0]} ; y = {AI1_pos[1]}")

    # Depuis l'IA n°2
    while not com_out_AI2.empty():
        output_AI2 = com_out_AI2.get()

        # Exécution de l'output
        if output_AI2 in MOVE and carte[AI2_pos[1] + MOVE[output_AI2][1]][AI2_pos[0] + MOVE[output_AI2][0]] != "#":
            globals()["AI2_pos"] = (AI2_pos[0] + MOVE[output_AI2][0], AI2_pos[1] + MOVE[output_AI2][1])
            # Si l'IA a atteint un fromage
            if carte[AI2_pos[1]][AI2_pos[0]] == "$":
                carte[AI2_pos[1]][AI2_pos[0]] = " "
                globals()["t2_score"] += 1

        # Log de l'output
        if debug:
            print(f"({time//60000}:{time_txt[-5:-3]}:{time_txt[-3:]})  IA n°2  ->  {output_AI2}\nPosition de l'IA n°2  :  x = {AI2_pos[0]} ; y = {AI2_pos[1]}")

    # Envoi des données aux IA (champ d'input commun)
    if send_data:
        # La carte
        com_in_AIs[0] = list(carte)
        # Position de l'IA n°1
        com_in_AIs[1] = tuple(AI1_pos)
        # Position de l'IA n°2
        com_in_AIs[2] = tuple(AI2_pos)
        # Autorisation à l'IA n°1 de continuer
        com_in_AIs[3] = True
        # Autorisation à l'IA n°2 de continuer
        com_in_AIs[4] = True
        # Si l'IA doit log
        com_in_AIs[7] = debug

    # Actualisation des variables de debug
    globals()["AI1_true_pos"] = com_in_AIs[5]
    globals()["AI2_true_pos"] = com_in_AIs[6]


def AI_controler(q_in: mp.Queue, q_out: mp.Queue, AI_brain: 'function', AI_nb: int=1) -> None:
    """Gestion des IA"""

    # Initialisation des variables
    maze: list[list[str]] = None
    pos_self: tuple[int, int] = None
    pos_enemy: tuple[int, int] = None

    # Variables utilisées pour le calcul du temps d'exécution
    end = start = 0

    # L'IA tourne jusqu'à ce que l'épreuve soit finie
    while True:

        # Doit attendre jusqu'à avoir reçu les dernières informations
        if not q_in[3 if AI_nb == 1 else 4]:
            continue
        q_in[3 if AI_nb == 1 else 4] = False

        # Délai de sécurité (risque de données erronnées si trop rapide)
        pg.time.wait(40)

        # Récupération des informations
        maze = list(q_in[0])
        pos_self = tuple(q_in[1 if AI_nb == 1 else 2])
        pos_enemy = tuple(q_in[2 if AI_nb == 1 else 1])

        # Si l'IA doit log des informations
        debug = q_in[7]

        # L'IA indique à quelle position elle pense être (débugging)
        q_in[5 if AI_nb == 1 else 6] = pos_self

        # Chronomètre : Début de l'exécution
        start = timer()

        # Exécution du cerveau de l'IA et obtention d'une output
        action = AI_brain(maze, pos_self, pos_enemy)

        # try:
        #     action = AI_brain(maze, pos_self, pos_enemy)
        # except:
        #     if debug:
        #         print(f"ERREUR FATALE chez l'IA n°{AI_nb}")
        #     action = None

        # Chronomètre : Fin de l'exécution
        end = timer()

        # Délai mineur entre chaque exécution (moins le délai de sécurité)
        pg.time.wait(int((end - start) * 1000 * IA_SLOW_FACTOR) - 40)

        if debug:
            print(f"Temps d'exécution de l'IA n°{AI_nb} : {round((end - start) * 1_000_000, 1)} micro-secondes\n")

        # Ajout de l'ouput
        if action is not None:
            q_out.put(action)
            action = None


def reboot_AI() -> None:
    """Relance les IA"""

    # Suppression des processus d'IA (de manière violente, car on a pas le temps)
    AI1_process.terminate()
    AI2_process.terminate()

    # Recréation des fils de code séparés pour les IA
    globals()["AI1_process"] = mp.Process(target=AI_controler, args=(com_in_AIs, com_out_AI1, AI1_brain, 1))
    globals()["AI2_process"] = mp.Process(target=AI_controler, args=(com_in_AIs, com_out_AI2, AI2_brain, 2))

    # Lancement des IA (posibilité de mettre ces lignes en commentaire pour ne pas lancer 1 des IA ou les 2)
    AI1_process.start()
    AI2_process.start()


# Partie génération de la carte


def re_init() -> None:
    """(Re)Initialise toutes les variables afin de générer une nouvelle carte"""

    # Partie carte
    dim_carte = (rd.randint(24, 34), rd.randint(19, 29))
    if dim_carte[0] < dim_carte[1]:
        dim_carte = (dim_carte[1], dim_carte[0])
    size_carte = (dim_carte[0]*SIZE, dim_carte[1]*SIZE)
    carte = [[" " if x not in [0, 1, dim_carte[0] - 1, dim_carte[0] - 2] and y not in [0, 1, dim_carte[1] - 1, dim_carte[1] - 2] else "#" for x in range(dim_carte[0])] for y in range(dim_carte[1])]
    used_tiles_set = rd.choice(list(tiles_set.keys()))

    # Partie écran de simulation
    screen = pg.surface.Surface(size_carte)
    screen_zoom_size = (fs_width, int(size_carte[1]*fs_width/size_carte[0])) if fs_width/size_carte[0] < fs_height/size_carte[1] else (int(size_carte[0]*fs_height/size_carte[1]), fs_height)
    screen_pos = ((fs_width - screen_zoom_size[0])//2, (fs_height - screen_zoom_size[1])//2)

    # Mise en global des variables locales ("C'est du terrorisme, et alors !?")
    for item in locals().items():
        globals()[item[0]] = item[1]


def find_AI_spawnpoint() -> tuple:
    """Trouve le point de spawn le plus adapté pour les IA"""

    # Le but est d'apparaitre le plus loin possible des fromages

    # Trouve la localisation de tous les fromages
    l_cheese = []
    for y in range(2, dim_carte[1] - 2):
        for x in range(2, dim_carte[0] - 2):
            if carte[y][x] == "$":
                l_cheese.append((x, y))

    # Trouve le point d'apparition le plus éloigné des fromages
    spawn_pos = (0, 0)
    spawn_dist = 10**10

    # On parcourt toute la carte sauf ses bordures
    for y in range(2, dim_carte[1] - 2):
        for x in range(2, dim_carte[0] - 2):

            # Le point d'apparition doit être un espace vide
            if carte[y][x] == " ":
                # Calcul de la proximité aux fromages
                dist = 0

                # Ajout de la proximité (distance ** -1)
                for cheese_x, cheese_y in l_cheese:
                    dist += ((x - cheese_x)**2 + (y - cheese_y)**2)**(-0.5)

                # Moyenne
                dist /= len(l_cheese)

                # Si la proximité est plus faible, alors on prend cette position
                if dist < spawn_dist:
                    spawn_pos = (x, y)
                    spawn_dist = dist

    # On retourne la position de spawn la plus adaptée
    return spawn_pos


def generate_block(size: tuple=(1, 1), invert: bool=False) -> None:
    """Génération de block de mur ou en vide"""

    # Position du curseur (centre du bloc)
    pos = [rd.randint(size[0]//2 + 2, dim_carte[0] - math.ceil(size[0]/2) - 2), rd.randint(size[1]//2 + 2, dim_carte[1] - math.ceil(size[1]/2) - 2)]

    # Methode de flemmard pour faire les contours du bloc en espaces vides
    if not invert:
        # Remplissage d'une zone 2x2 tuilles plus large que l'originale
        for dy in range(- (size[1]//2) - 1, math.ceil(size[1]/2) + 1):
            for dx in range(- (size[0]//2) - 1, math.ceil(size[0]/2) + 1):
                # On ne touche pas aux bordures de la map
                if 1 < pos[0] + dx < dim_carte[0] - 2 and 1 < pos[1] + dy < dim_carte[1] - 2:
                    carte[pos[1] + dy][pos[0] + dx] = " "

    # Remplissage de la zone où le block est situé
    for dy in range(- (size[1]//2), math.ceil(size[1]/2)):
        for dx in range(- (size[0]//2), math.ceil(size[0]/2)):
            carte[pos[1] + dy][pos[0] + dx] = " " if invert else "#"


def generate_wall(max_lenght: int=1000, from_sides: bool=False, expend_wall: bool=False) -> None:
    """Génération de mur sur la carte"""

    # Liste de mouvement possible (Haut, Bas, Droite, Gauche)
    moves = [(0, -1), (0, 1), (1, 0), (-1, 0)]

    # Position de départ du curseur (aléatoire)
    pos = [rd.randint(2, dim_carte[0] - 3), rd.randint(2, dim_carte[1] - 3)]

    # Déplacement vers une bordure
    if from_sides:
        # Choix de la bordure
        where = rd.choice(("N", "S", "E", "W"))

        # Bordure du haut
        if where == "N":
            pos[1] = 2
        # Bordure du bas
        elif where == "S":
            pos[1] = dim_carte[1] - 3
        # Bordure à droite
        elif where == "E":
            pos[0] = 2
        # Bordure à gauche
        else:
            pos[0] = dim_carte[0] - 3

    # Si True, alors le nouveau mur partira forcément d'un mur déjà existant
    elif expend_wall:
        for _ in range(100):
            if carte[pos[1]][pos[0]] != "#":
                pos = [rd.randint(2, dim_carte[0] - 3), rd.randint(2, dim_carte[1] - 3)]
            else:
                break

    # Si False, alors le nouveau mur ne partira pas d'un mur déjà existant
    else:
        # Limite de test, car il est fort probable d'obtenir une boucle infinie
        for _ in range(100):
            # Test des tuilles adjacentes
            for delta in ((0, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)):
                if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                    # Nouvelle position
                    pos = [rd.randint(3, dim_carte[0] - 4), rd.randint(3, dim_carte[1] - 4)]
                    break # Nouveau test
            else: # Test réussi
                carte[pos[1]][pos[0]] = "#"
                break # Fin des tests

    # Placement du premier mur si le curseur est situé sur le bord de la carte

    # Bordure à gauche
    if pos[0] == 2:
        for delta in ((2, -1), (2, 0), (2, 1), (1, -1), (1, 0), (1, 1)):
            if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                break # Echec du test
        else: # Si le nouveau mur peut être placé
            carte[pos[1]][pos[0]] = "#"

    # Bordure à droite
    elif pos[0] == dim_carte[0] - 3:
        for delta in ((-2, -1), (-2, 0), (-2, 1), (-1, -1), (-1, 0), (-1, 1)):
            if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                break # Echec du test
        else: # Si le nouveau mur peut être placé
            carte[pos[1]][pos[0]] = "#"

    # Bordure en haut
    elif pos[1] == 2:
        for delta in ((-1, 2), (0, 2), (1, 2), (-1, 1), (0, 1), (1, 1)):
            if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                break # Echec du test
        else: # Si le nouveau mur peut être placé
            carte[pos[1]][pos[0]] = "#"

    # Bordure en bas
    elif pos[1] == dim_carte[1] - 3:
        for delta in ((-1, -2), (0, -2), (1, -2), (-1, -1), (0, -1), (1, -1)):
            if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                break # Echec du test
        else: # Si le nouveau mur peut être placé
            carte[pos[1]][pos[0]] = "#"

    # Partie principale
    for _ in range(max_lenght):

        # Déplacement dans une direction aléatoire
        rd.shuffle(moves)
        for move in moves:
            # Le nouveau mur ne devra pas toucher d'autre mur (sauf celui dont il provient)

            # Test déplacement vers le haut
            if move == (0, -1):

                for delta in ((-1, -2), (0, -2), (1, -2), (-1, -1), (0, -1), (1, -1)):
                    if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                        break # Echec du test

                else: # Si le nouveau mur peut être placé
                    break # Fin des tests

            # Test déplacement vers le bas
            if move == (0, 1):

                for delta in ((-1, 2), (0, 2), (1, 2), (-1, 1), (0, 1), (1, 1)):
                    if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                        break # Echec du test

                else: # Si le nouveau mur peut être placé
                    break # Fin des tests

            # Test déplacement vers la droite
            if move == (1, 0):

                for delta in ((2, -1), (2, 0), (2, 1), (1, -1), (1, 0), (1, 1)):
                    if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                        break # Echec du test

                else: # Si le nouveau mur peut être placé
                    break # Fin des tests

            # Test déplacement vers la gauche
            if move == (-1, 0):

                for delta in ((-2, -1), (-2, 0), (-2, 1), (-1, -1), (-1, 0), (-1, 1)):
                    if carte[pos[1] + delta[1]][pos[0] + delta[0]] == "#":
                        break # Echec du test

                else: # Si le nouveau mur peut être placé
                    break # Fin des tests

        else: # Si aucun mouvement n'est possible
            break # Arret des déplacements

        # Déplacement du curseur
        pos[0] += move[0]
        pos[1] += move[1]
        # Placement du mur
        carte[pos[1]][pos[0]] = "#"


def place_cheese() -> None:
    """Place un fromage sur la carte"""

    # Tant que le fromage n'a pas été placé
    while True:

        # Position aléatoire (avec les bordures en mur exclues)
        pos = [rd.randint(2, dim_carte[0] - 3), rd.randint(2, dim_carte[1] - 3)]

        # Test pour placer le fromage
        if carte[pos[1]][pos[0]] == " ":
            carte[pos[1]][pos[0]] = "$"
            break # Fin


def generate_carte() -> None:
    """Permet de générer un nouveau labyrinthe"""

    # Réinitialisation de la carte
    for y in range(2, dim_carte[1] - 2):
        for x in range(2, dim_carte[0] - 2):
            carte[y][x] = " "

    globals()["gen_signature"] = rd.choice(list(GEN_SIGNATURES.keys()))

    # Génération de la carte de manière très random (c'est comme une soupe)

    # Génération par défaut (simple et efficace)
    if gen_signature == "Defaut":
        for _ in range(100):
            generate_wall(rd.randint(5, 10), rd.randint(0, 1), rd.randint(0, 1))

    # Génération de blocs (originale à sa manière)
    elif gen_signature == "Blocks":
        for _ in range(100):
            generate_block((rd.randint(3, 8), rd.randint(3, 8)))

    # Génération officielle
    elif gen_signature == "PYRAT":
        for _ in range(10):
            generate_wall(0)
        for _ in range(rd.randint(1, 5)):
            generate_block((rd.randint(1, 5), rd.randint(1, 5)))
        for _ in range(100):
            generate_wall(rd.randint(5, 10), rd.randint(0, 1))

    # Génération n°1 de Térence
    elif gen_signature == "Ter1":
        for _ in range(100):
            r = rd.random()
            if r < 0.01:
                generate_block((rd.randint(1, 6), rd.randint(1, 6)), rd.randint(0, 1))
            elif r < 0.08:
                generate_block((rd.randint(1, 4), rd.randint(1, 4)), rd.randint(0, 1))
            elif r < 0.22:
                generate_wall(rd.randint(0, 1))
            elif r < 0.45:
                generate_wall(rd.randint(0, 20), r < 0.26, r < 0.35)
            else:
                generate_wall(rd.randint(5, 15), r < 0.6, r < 0.8)

    # Génération n°2 de Térence
    elif gen_signature == "Ter2":
        for _ in range(10):
            generate_wall(0)
            generate_wall(from_sides=True)
        for _ in range(rd.randint(1, 5)):
            generate_block((rd.randint(1, 5), rd.randint(1, 5)), True)
        for _ in range(100):
            generate_wall(rd.randint(0, 20), rd.randint(0, 1), rd.randint(0, 1))

    # Génération n°3 de Térence
    elif gen_signature == "Ter3":
        for _ in range(100):
            generate_block((1, 10))
        for _ in range(100):
            generate_wall(from_sides=rd.randint(0, 1), expend_wall=rd.randint(0, 1))

    # Des petits points
    elif gen_signature == "Points":
        for _ in range(400):
            generate_block((1, 1))
            generate_wall(1, rd.randint(0, 1), False)

    # Placement des fromages (universel à tous les systèmes de génération)
    globals()["nb_cheese"] = (dim_carte[0] * dim_carte[1])//100 * 2 + 1
    for _ in range(nb_cheese):
        place_cheese()

    # Point d'apparition des IA
    globals()["spawnpoint"] = find_AI_spawnpoint()
    globals()["AI1_pos"] = tuple(spawnpoint)
    globals()["AI2_pos"] = tuple(spawnpoint)


# Partie interface et éléments cliquables


class Cursor:
    """Classe gérant toutes les interactions du curseur de la souris (pas celle dans le labyrinthe)"""

    def __init__(self) -> None:

        self.pos = pg.mouse.get_pos()
        self.m_pressed = pg.mouse.get_pressed(5)
        self.old_m_pressed = tuple(self.m_pressed)

    def update(self) -> None:
        """Met à jour les données de la souris"""

        self.pos = pg.mouse.get_pos()
        self.old_m_pressed = tuple(self.m_pressed)
        self.m_pressed = pg.mouse.get_pressed(5)

    def pressed(self, mouse_nb: int=0, reverse: bool=False) -> bool:
        """Retourne un booléan indiquant si le bouton testé vient d'être pressé ou relaché"""

        return (self.old_m_pressed[mouse_nb] and not self.m_pressed[mouse_nb]) if reverse else (self.m_pressed[mouse_nb] and not self.old_m_pressed[mouse_nb])


class Button:

    # Chargement de toutes les bases de bouton (commun à tous les objet Button)
    base_img = {name[:-4]: load_img(f"ressources\\images\\boutons\\bases\\{name}", (64, 64)) for name in listdir("ressources\\images\\boutons\\bases") if name.endswith(".png")}

    def __init__(self, pos: tuple, default_state: bool=None, icon_name: str=None) -> None:

        # Position du bouton
        self.pos = pos
        # Etat du bouton ("True" : activé ; "False" : désactivé ; "None" : désactivé + non-modifiable)
        self.state = default_state
        # Icone affichée sur le bouton
        self.icon = load_img(f"ressources\\images\\boutons\\icones\\{icon_name}.png", (64, 64)) if icon_name is not None else None

    def display(self) -> None:
        """Affichage du bouton sur l'écran d'affichage"""

        # Affichage du la base du bouton
        focus_screen.blit(self.base_img["on" if self.state else ("none" if self.state is None else "off")], self.pos)

        # Affichage de l'icone du bouton
        if self.icon is not None:
            focus_screen.blit(self.icon, self.pos)

    def update(self) -> None:
        """Détecte les cliques et met à jour le bouton en conséquence"""
        
        if mouse.pressed(0) and self.pos[0] <= mouse.pos[0] <= self.pos[0] + 64 and self.pos[1] <= mouse.pos[1] <= self.pos[1] + 64 and self.state is not None:
            self.state = not self.state
    
    def get_state(self) -> bool:
        """Retourne l'état du bouton"""

        return bool(self.state)


class Interface:
    """Classe principale de l'interface, barre d'interface"""

    def __init__(self, on_right_side: bool=False) -> None:

        # Coté sur lequel l'interface est affichée
        self.fliped = on_right_side

        # Si l'interface est ouverte et affichée ou non
        self.is_opened = False

        # Création du sprite pour la barre d'interface
        self.dim = (250, fs_height - 200)
        self.cz_dim = (40, 100)
        self.sprite = pg.surface.Surface(self.dim)
        self.sprite.fill((1, 1, 1))
        self.sprite.set_colorkey((1, 1, 1))

        # Outline (partie barre principale)
        pg.draw.rect(self.sprite, (0, 0, 0), ((-60, 0), (self.dim[0] + 30, self.dim[1])), border_radius=30)
        # Outline (partie zone cliquable)
        pg.draw.rect(self.sprite, (0, 0, 0), (((self.dim[0] - self.cz_dim[0] - 15), (self.dim[1] - self.cz_dim[1])//2 - 5), (self.cz_dim[0] + 10, self.cz_dim[1] + 10)), border_radius=15)

        # Petite barre cliquable pour cacher/montrer la barre d'interface
        pg.draw.rect(self.sprite, (50, 50, 50), (((self.dim[0] - self.cz_dim[0] - 10), (self.dim[1] - self.cz_dim[1])//2), self.cz_dim), border_radius=10)
        # Partie principale de la barre
        pg.draw.rect(self.sprite, (65, 65, 65), ((-50, 10), (self.dim[0] + 10, self.dim[1] - 20)), border_radius=20)

        # On flip le sprite si il doit être à droite de l'écran (au lieu d'à gauche)
        if self.fliped:
            self.sprite = pg.transform.rotate(self.sprite, 180)

        self.buttons = {} # Dictionnaire contenant tous les boutons

        if not self.fliped:
            # Définition des boutons
            self.buttons = {
                "debug": Button((10, (fs_height - self.dim[1])//2 + 20), debug, "debug")
            }

    def display(self) -> None:
        """
        Affichage de la barre d'interface et de son contenu\n
        Update également l'état de l'interface
        """

        # Affichage de la partie principale de l'interface
        focus_screen.blit(self.sprite, (((fs_width - self.dim[0]) if self.fliped else 0) if self.is_opened else ((fs_width - self.cz_dim[0]) if self.fliped else (self.cz_dim[0] - self.dim[0])), (fs_height - self.dim[1])//2))

        # Triangle affiché sur la zone cliquable
        if self.fliped:
            if self.is_opened:
                pg.draw.polygon(focus_screen, (255, 255, 255), ((fs_width - self.dim[0] + 20, fs_height//2 + 25), (fs_width - self.dim[0] + 20, fs_height//2 - 25), (fs_width - self.dim[0] + 30, fs_height//2)))
            else:
                pg.draw.polygon(focus_screen, (255, 255, 255), ((fs_width - 10, fs_height//2 + 25), (fs_width - 10, fs_height//2 - 25), (fs_width - 20, fs_height//2)))
        elif self.is_opened:
            pg.draw.polygon(focus_screen, (255, 255, 255), ((self.dim[0] - 20, fs_height//2 + 25), (self.dim[0] - 20, fs_height//2 - 25), (self.dim[0] - 30, fs_height//2)))
        else:
            pg.draw.polygon(focus_screen, (255, 255, 255), ((10, fs_height//2 + 25), (10, fs_height//2 - 25), (20, fs_height//2)))

        # Affiche les boutons
        if self.is_opened:
            for button in self.buttons.values():
                button.display()

    def update(self) -> None:
        """Met à jour l'interface en fonction des inputs"""

        # Ouverture/fermeture de l'interface
        # Lorsque LMB est pressé et est située dans cet intervale de hauteur
        if mouse.pressed(0) and (fs_height - self.cz_dim[1])//2 <= mouse.pos[1] <= (fs_height + self.cz_dim[1])//2:
            # Si l'interface se situe à droite de l'écran
            if self.fliped:
                # Si l'interface est ouverte
                if self.is_opened:
                    # Si la souris est située dans cet intervale de largeur
                    if fs_width - self.dim[0] <= mouse.pos[0] <= fs_width - self.dim[0] + self.cz_dim[0]:
                        # Ferme l'interface
                        self.is_opened = False
                # Si l'interface est fermée
                # Si la souris est située dans cet intervale de largeur
                elif fs_width - self.cz_dim[0] <= mouse.pos[0]:
                    # Ouvre l'interface
                    self.is_opened = True
            # Si l'interface se situe à gauche de l'écran
            # Si l'interface est ouverte
            elif self.is_opened:
                # Si la souris est située dans cet intervale de largeur
                if self.dim[0] - self.cz_dim[0] <= mouse.pos[0] <= self.dim[0]:
                    # Ferme l'interface
                    self.is_opened = False
            # Si l'interface est fermée
            # Si la souris est située dans cet intervale de largeur
            elif mouse.pos[0] <= self.cz_dim[0]:
                # Ouvre l'interface
                self.is_opened = True

        # Met à jour les boutons
        for button in self.buttons.values():
            button.update()

        # Met à jour le programme en fonction de l'état des boutons

        if self.fliped:
            pass

        else:
            # Bouton debug
            sb_debug = self.buttons["debug"].get_state()
            if debug and not sb_debug:
                globals()["debug"] = False
            elif sb_debug and not debug:
                globals()["debug"] = True


# Partie affichage


def display_carte() -> None:
    """Affichage de la carte"""

    # Affichage de toutes les tuiles
    for y in range(dim_carte[1]):
        for x in range(dim_carte[0]):

            # Affichage d'une case vide
            if carte[y][x] == " ":
                if "sol" in tiles_set[used_tiles_set]:
                    screen.blit(tiles_set[used_tiles_set]["sol"], (x*SIZE, y*SIZE))
                else:
                    pg.draw.rect(screen, (150, 150, 150), ((x*SIZE, y*SIZE), (SIZE, SIZE)))

            # Affichage d'une case avec un mur
            elif carte[y][x] == "#":
                if "mur" in tiles_set[used_tiles_set]:
                    screen.blit(tiles_set[used_tiles_set]["mur"], (x*SIZE, y*SIZE))
                else:
                    pg.draw.rect(screen, (50, 50, 50), ((x*SIZE, y*SIZE), (SIZE, SIZE)))

            # Affichage d'une case avec un fromage
            elif carte[y][x] == "$":
                if "sol" in tiles_set[used_tiles_set]:
                    screen.blit(tiles_set[used_tiles_set]["sol"], (x*SIZE, y*SIZE))
                else:
                    pg.draw.rect(screen, (150, 150, 150), ((x*SIZE, y*SIZE), (SIZE, SIZE)))
                if "fromage" in tiles_set[used_tiles_set]:
                    screen.blit(tiles_set[used_tiles_set]["fromage"], (x*SIZE, y*SIZE))
                else:
                    pg.draw.circle(screen, (200, 200, 50), (int(SIZE*(x + 0.5)), int(SIZE*(y + 0.5))), SIZE//4)

    # Affichage du point d'apparition
    if "spawn" in tiles_set[used_tiles_set]:
        screen.blit(tiles_set[used_tiles_set]["spawn"], (spawnpoint[0]*SIZE, spawnpoint[1]*SIZE))
    else:
        pg.draw.polygon(screen, (255, 0, 0), ((int((spawnpoint[0] + 0.5)*SIZE), int((spawnpoint[1] + 0.25)*SIZE)), (int((spawnpoint[0] + 0.75)*SIZE), int((spawnpoint[1] + 0.5)*SIZE)), (int((spawnpoint[0] + 0.5)*SIZE), int((spawnpoint[1] + 0.75)*SIZE)), (int((spawnpoint[0] + 0.25)*SIZE), int((spawnpoint[1] + 0.5)*SIZE))))


def display_AIs() -> None:
    """Affiche les IA (les souris)"""

    # IA n°1
    screen.blit(AI1_sprite, (AI1_pos[0]*SIZE, AI1_pos[1]*SIZE))
    # IA n°2
    screen.blit(AI2_sprite, (AI2_pos[0]*SIZE, AI2_pos[1]*SIZE))


def display_GUI() -> None:
    """Affichage du GUI directement sur l'écran d'affichage"""

    # Récupération du temps (avec technique de flemmard pour l'affichage)
    time = pg.time.get_ticks() - timer_start
    time_txt = "00000" + str(time%60000)

    # Affichage du GUI

    # Timer
    surf_time = zoneTexte(f"(255,255,255)${time//60000}:{time_txt[-5:-3]}:{time_txt[-3:]}", 3)
    focus_screen.blit(surf_time, ((fs_width - surf_time.get_size()[0])//2, 10))

    # Signatures de carte (pauvres fous !)
    focus_screen.blit(GEN_SIGNATURES[gen_signature], ((fs_width - GEN_SIGNATURES[gen_signature].get_size()[0])//2, fs_height -GEN_SIGNATURES[gen_signature].get_size()[1] - 10))

    # Nom des équipes
    focus_screen.blit(t1_name, (10, 10))
    focus_screen.blit(t2_name, (fs_width - t2_name.get_size()[0] - 10, 10))

    # Score de chaque équipe
    scores = zoneTexte(f"(255,255,255)$Score : $(255,0,0)${t1_score}$(255,255,255)$ point" + ("s" if t1_score > 1 else "") + " "*20 + f"$(255,255,255)$Score : $(0,0,255)${t2_score} $(255,255,255)$point" + ("s" if t2_score > 1 else ""), 2)
    focus_screen.blit(scores, ((fs_width - scores.get_size()[0])//2, 15))

    # Message de victoire
    if t1_score + t2_score == nb_cheese:
        focus_screen.blit(fs_border, (0, fs_height//2 - fs_border_size[1] - 5))
        focus_screen.blit(fs_border, (0, fs_height//2 - 5))
        if t1_score > t2_score:
            focus_screen.blit(t1_victory, ((fs_width - t1_victory.get_size()[0])//2, (fs_height - t1_victory.get_size()[1])//2))
        else:
            focus_screen.blit(t2_victory, ((fs_width - t2_victory.get_size()[0])//2, (fs_height - t2_victory.get_size()[1])//2))

    # Affichage de l'objet gui
    l_gui.display()
    r_gui.display()


def display() -> None:
    """Affichage de tous les éléments"""

    screen.fill((0, 0, 0))
    focus_screen.fill((0, 0, 0))

    # Affichage de la carte
    display_carte()
    
    # Affichage des éléments de débugging
    if debug:
        pg.draw.rect(screen, (255, 0, 0), ((AI1_true_pos[0]*SIZE, AI1_true_pos[1]*SIZE), (SIZE, SIZE)), 5)
        pg.draw.rect(screen, (0, 0, 255), ((AI2_true_pos[0]*SIZE, AI2_true_pos[1]*SIZE), (SIZE, SIZE)), 5)

    # Affichage des IA
    display_AIs()

    # Affichage de l'écran de simulation sur l'écran d'affichage
    focus_screen.blit(pg.transform.smoothscale(screen, screen_zoom_size) if HD_display else pg.transform.scale(screen, screen_zoom_size), screen_pos)

    # Bandes semi-transparantes affichées en haut et en bas de l'écran
    focus_screen.blit(fs_border, (0, 0))
    focus_screen.blit(fs_border, (0, fs_height - fs_border_size[1]))

    # Affichage des informations directement sur l'écran d'affichage
    display_GUI()

    # Affichage à l'écran
    pg.display.flip()


# Partie boucle principale


def main() -> None:
    """Boucle principale"""

    # Les IA commencent en pause
    do_update = True

    # Génartion initiale de la carte
    re_init()
    generate_carte()

    # Reset du timer
    globals()["timer_start"] = pg.time.get_ticks()

    # Boucle principale
    running = True
    while running:

        # Actualisation des données de la souris (du curseur)
        mouse.update()

        # Récupération de tous les évènements pygame
        for event in pg.event.get():

            # Quitter le script
            if event.type == pg.QUIT:
                running = False

            # Touche pressée
            elif event.type == pg.KEYDOWN:

                # Quitter le script
                if event.key == pg.K_ESCAPE:
                    running = False

                # Touche pour recréer une map
                elif event.key == pg.K_RETURN:
                    # Recharge la carte
                    re_init()
                    generate_carte()
                    # Reset les scores
                    globals()["t1_score"] = 0
                    globals()["t2_score"] = 0
                    # Relance les IA
                    reboot_AI()
                    # Reset du timer
                    globals()["timer_start"] = pg.time.get_ticks()

                # Touche pour activer/désactiver la HD
                elif event.key == pg.K_SPACE:
                    globals()["HD_display"] = not HD_display

                # Touche pour activer/désactiver les logs et les éléments de débug
                elif event.key == pg.K_ASTERISK:
                    globals()["debug"] = not debug

                # Touche pour activer/désactiver les IA
                elif event.key == pg.K_BACKSPACE:
                    do_update = not do_update

        # Mise à jour de l'interface
        l_gui.update()
        r_gui.update()

        # Gestion des IA (input/output)
        update_AI(do_update)

        # Affichage de tous les éléments
        display()



#----------------< Exécution automatique de la fonction main >-----------------#


# N'exécute le code que si ce script est exécuté
if __name__ == "__main__":

    # Définition du type de méthode utilisé pour le multi-processing
    mp.set_start_method('spawn')

    # Fils de communications avec les intéligences artificielles
    com_in_AIs = mp.Manager().list([None]*5 + [(0, 0)]*2 + [debug])
    com_out_AI1 = mp.Queue()
    com_out_AI2 = mp.Queue()

    # Création des fils de code séparés pour les IA
    AI1_process = mp.Process(target=AI_controler, args=(com_in_AIs, com_out_AI1, AI1_brain, 1))
    AI2_process = mp.Process(target=AI_controler, args=(com_in_AIs, com_out_AI2, AI2_brain, 2))

    # Lancement des IA (posibilité de mettre ces lignes en commentaire pour ne pas lancer 1 des IA ou les 2)
    AI1_process.start()
    AI2_process.start()

    # Création d'une instance de l'objet Curseur
    mouse = Cursor()

    # Création d'un objet Interface
    l_gui = Interface()
    r_gui = Interface(True)

    main() # Fonction principale

    # Arret de force des processus d'IA
    AI1_process.terminate()
    AI2_process.terminate()


pg.quit() # Arret de pygame