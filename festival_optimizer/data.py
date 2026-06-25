"""
Modèles de données et jeu de données fictif du Festival Optimizer.

Conventions de nommage :
    L01–L05  → Lieux (venues)
    E01–E07  → Exposition
    CH01–CH21 → Créneaux horaires (time slots)
    P01–P04    → Profils visiteurs

"""

from dataclasses import dataclass
from typing import List, Tuple


# ─── Constantes budget ────────────────────────────────────────────────────────
# Chaque clé correspond à une fourchette (min €, max €)

BUDGET_RANGES: dict = {
    "pb": (7,  10),   # petit budget
    "mb": (12, 15),   # moyen budget
    "gb": (18, 20),   # gros budget
}

BUDGET_LABELS: dict = {
    "pb": "Petit budget (7–10 €)",
    "mb": "Moyen budget (12–15 €)",
    "gb": "Gros budget (18–20 €)",
}

# ─── Constantes tolérance à la foule ─────────────────────────────────────────

TOLERANCE_FOULE_LABELS: dict = {
    "tf": "Très forte — aime l'affluence (80–99 %)",
    "fo": "Forte — à l'aise dans la foule (60–79 %)",
    "m":  "Moyenne (40–59 %)",
    "fa": "Faible — préfère le calme (20–39 %)",
    "ff": "Très faible — évite la foule à tout prix (0–19 %)",
}

# ─── Styles d'exposition disponibles ─────────────────────────────────────────

STYLES = [
    "Photographie ambulante",
    "Photographie de rue",
    "Photographie de mode",
    "Photographie conceptuelle",
    "Portrait photographique",
    "Photographie abstraite",
    "Photographie d'architecture",
    "Photographie animalière",
    "Photographie culinaire",
    "Photographie de nuit",
    "Photographie sous-marine",
    "Photographie aérienne",
    "Photographie panoramique",
    "Photographie n&b",
]


# ─── Modèles ──────────────────────────────────────────────────────────────────

@dataclass
class Lieu:
    lieu_id: str
    name: str
    address: str
    district: str


@dataclass
class Exposition:
    exposition_id: str
    name: str
    lieu_id: str
    style: str              # l'un des STYLES ci-dessus
    themes: List[str]       # mots-clés de matching avec les intérêts visiteurs
    duration_minutes: int
    max_capacity: int       # capacité totale du lieu pour cette expo
    price: int              # tarif en € : 7, 10, 12, 15, 18 ou 20
    description: str


@dataclass
class Creneau:
    creneau_id: str
    exposition_id: str
    start_hour: int
    end_hour: int
    max_capacity: int       # 50–95 % de Exhibition.max_capacity
    reservation: int     # 0–100 % de max_capacity

    @property
    def remaining(self) -> int:
        return self.max_capacity - self.reservation

    @property
    def occupancy_pct(self) -> float:
        """Retourne un float entre 0.0 et 1.0."""
        return self.reservation / self.max_capacity


@dataclass
class Visiteur:
    visiteur_id: str
    name: str
    interet: List[str]                    # 3–4 thèmes parmi ceux des expos
    disponibilites: List[Tuple[int, int]]     # fenêtres horaires disponibles (1–2 max)
    budget: str                             # "pb" | "mb" | "gb"
    tolerance_foule: str                    # "ff" | "fa" | "m" | "fo" | "tf"


# ─── Lieux (adresses réelles, Paris) ─────────────────────────────────────────

LIEUX: List[Lieu] = [
    Lieu(
        lieu_id="L01",
        name="Musée d'Art Moderne de Paris",
        address="11 avenue du Président Wilson, 75016 Paris",
        district="16ème",
    ),
    Lieu(
        lieu_id="L02",
        name="Jeu de Paume",
        address="1 place de la Concorde, 75001 Paris",
        district="1er",
    ),
    Lieu(
        lieu_id="L03",
        name="Bibliothèque historique de la Ville de Paris",
        address="24 rue Pavée, 75004 Paris",
        district="4ème",
    ),
    Lieu(
        lieu_id="L04",
        name="Fondation Henri Cartier-Bresson",
        address="79 Rue des Archives, 75003 Paris",
        district="3ème",
    ),
    Lieu(
        lieu_id="L05",
        name="Musée de l'Homme",
        address="17 Place du Trocadéro, 75016 Paris",
        district="16ème",
    ),
    Lieu(
        lieu_id="L06",
        name="Musée du Louvre",
        address="Rue de Rivoli, 75001 Paris",
        district="1er",
    ),
    Lieu(
        lieu_id="L07",
        name="Petit Palais",
        address="Avenue Winston Churchill, 75008 Paris",
        district="8ème",
    ),
    Lieu(
        lieu_id="L08",
        name="Musée du Quai Branly - Jacques Chirac",
        address="37 Quai Jacques Chirac, 75007 Paris",
        district="7ème",
    ),
    Lieu(
        lieu_id="L09",
        name="Musée Carnavalet",
        address="23 Rue de Sévigné, 75003 Paris",
        district="3ème",
    ),
    Lieu(
        lieu_id="L10",
        name="Galerie Perrotin",
        address="76 Rue de Turenne, 75003 Paris",
        district="3ème",
    ),
]
# ─── Exhibition ──────────────────────────────────────────────────────────────

EXPOSITIONS: List[Exposition] = [
    Exposition(
        exposition_id="E01",
        name="Visages du Monde",
        lieu_id="L01",
        style="Portrait photographique",
        themes=["portrait", "humanisme"],
        duration_minutes=45,
        max_capacity=100,
        price=10,
        description="Portraits de 30 nations réunis en 120 clichés argentiques",
    ),
    Exposition(
        exposition_id="E02",
        name="Paris la Nuit",
        lieu_id="L02",
        style="Photographie de nuit",
        themes=["nuit", "urbain", "n&b"],
        duration_minutes=60,
        max_capacity=150,
        price=15,
        description="La capitale vue après minuit par 15 photographes contemporains",
    ),
    Exposition(
        exposition_id="E03",
        name="Nature Intime",
        lieu_id="L03",
        style="Photographie animalière",
        themes=["nature", "macro", "couleur"],
        duration_minutes=30,
        max_capacity=60,
        price=12,
        description="Gros plans botaniques et animaliers en tirage grand format",
    ),
    Exposition(
        exposition_id="E04",
        name="Architecture & Lumière",
        lieu_id="L04",
        style="Photographie d'architecture",
        themes=["architecture", "urbain"],
        duration_minutes=50,
        max_capacity=200,
        price=18,
        description="Bâtiments iconiques du monde entier sous la lumière naturelle",
    ),
    Exposition(
        exposition_id="E05",
        name="Mémoires d'Enfance",
        lieu_id="L05",
        style="Photographie n&b",
        themes=["portrait", "humanisme", "n&b"],
        duration_minutes=40,
        max_capacity=50,
        price=7,
        description="Photos argentiques de familles parisiennes de 1950 à 1980",
    ),
    Exposition(
        exposition_id="E06",
        name="Déserts du Monde",
        lieu_id="L02",
        style="Photographie panoramique",
        themes=["paysage", "nature", "couleur"],
        duration_minutes=55,
        max_capacity=150,
        price=15,
        description="Étendues arides des 6 continents en tirage XXL",
    ),
    Exposition(
        exposition_id="E07",
        name="Scènes de Rue",
        lieu_id="L01",
        style="Photographie de rue",
        themes=["urbain", "humanisme", "couleur"],
        duration_minutes=35,
        max_capacity=80,
        price=10,
        description="Instants volés dans les rues de Paris, New York et Tokyo",
    ),

    # ── Expositions calibrées pour chaque profil visiteur ────────────────────

    Exposition(
        exposition_id="E08",
        name="Saveurs & Objectifs",
        lieu_id="L10",
        style="Photographie culinaire",
        themes=["culinaire", "rue", "nuit"],
        duration_minutes=40,
        max_capacity=60,
        price=18,
        description="Portraits culinaires de street food parisienne signés par 8 photographes de nuit",
    ),
    Exposition(
        exposition_id="E09",
        name="Entre Ciel et Terre",
        lieu_id="L07",
        style="Photographie aérienne",
        themes=["aérienne", "animalière", "mode"],
        duration_minutes=50,
        max_capacity=50,
        price=8,
        description="Faune sauvage et silhouettes de mode vues du ciel par drones et hélicoptères",
    ),
    Exposition(
        exposition_id="E10",
        name="Architectures Nocturnes",
        lieu_id="L08",
        style="Photographie d'architecture",
        themes=["architecture", "conceptuelle", "urbain"],
        duration_minutes=55,
        max_capacity=120,
        price=15,
        description="Structures urbaines réinterprétées à la tombée de la nuit par 12 architectes-photographes",
    ),
    Exposition(
        exposition_id="E11",
        name="Paysages au Crépuscule",
        lieu_id="L09",
        style="Photographie panoramique",
        themes=["paysage", "n&b", "portrait"],
        duration_minutes=45,
        max_capacity=80,
        price=20,
        description="Portraits de visages devant des paysages français en noir et blanc grand format",
    ),
    Exposition(
        exposition_id="E12",
        name="Néons de la Ville",
        lieu_id="L06",
        style="Photographie de nuit",
        themes=["nuit", "urbain", "couleur"],
        duration_minutes=60,
        max_capacity=100,
        price=10,
        description="Rues de Tokyo, Las Vegas et Bangkok saisies en longue exposition sous les lumières néon",
    ),
    Exposition(
        exposition_id="E13",
        name="Visions Conceptuelles",
        lieu_id="L04",
        style="Photographie conceptuelle",
        themes=["conceptuelle", "urbain"],
        duration_minutes=45,
        max_capacity=80,
        price=12,
        description="Installations photographiques abstraites interrogeant la ville et ses habitants",
    ),
    Exposition(
        exposition_id="E14",
        name="Plumes & Parures",
        lieu_id="L03",
        style="Photographie de mode",
        themes=["mode", "animalière", "aérienne"],
        duration_minutes=40,
        max_capacity=50,
        price=9,
        description="Créations de haute couture inspirées du plumage des oiseaux exotiques",
    ),
    Exposition(
        exposition_id="E15",
        name="Nuit Argentique",
        lieu_id="L05",
        style="Photographie n&b",
        themes=["paysage", "n&b", "portrait"],
        duration_minutes=50,
        max_capacity=70,
        price=20,
        description="Paysages français et portraits intimes tirés sur film argentique en chambre noire",
    ),
]

# ─── Créneaux horaires ────────────────────────────────────────────────────────
# max_capacity = 50–95 % de Exhibition.max_capacity
# reservation = 0–100 % de max_capacity
# Plusieurs créneaux volontairement saturés pour illustrer les scénarios limites.

CRENEAUX: List[Creneau] = [
    # ── Visages du Monde (E01) — portrait / humanisme — prix: 10 € ───────────
    Creneau(creneau_id="CH01", exposition_id="E01", start_hour=9,  end_hour=10, max_capacity=70, reservation=14),  # 20 %
    Creneau(creneau_id="CH02", exposition_id="E01", start_hour=10, end_hour=11, max_capacity=80, reservation=32),  # 40 %
    Creneau(creneau_id="CH03", exposition_id="E01", start_hour=13, end_hour=14, max_capacity=75, reservation=68),  # 91 % SATURÉ
    Creneau(creneau_id="CH04", exposition_id="E01", start_hour=15, end_hour=16, max_capacity=70, reservation=35),  # 50 %

    # ── Paris la Nuit (E02) — nuit / urbain / n&b — prix: 15 € ─────
    Creneau(creneau_id="CH05", exposition_id="E02", start_hour=9,  end_hour=10, max_capacity=100, reservation=20), # 20 %
    Creneau(creneau_id="CH06", exposition_id="E02", start_hour=11, end_hour=12, max_capacity=120, reservation=48), # 40 %
    Creneau(creneau_id="CH07", exposition_id="E02", start_hour=13, end_hour=14, max_capacity=110, reservation=102),# 93 % SATURÉ
    Creneau(creneau_id="CH08", exposition_id="E02", start_hour=15, end_hour=16, max_capacity=100, reservation=30), # 30 %

    # ── Nature Intime (E03) — nature / macro / couleur — prix: 12 € ──────────
    Creneau(creneau_id="CH09", exposition_id="E03", start_hour=11, end_hour=12, max_capacity=40, reservation=8),   # 20 %
    Creneau(creneau_id="CH10", exposition_id="E03", start_hour=14, end_hour=15, max_capacity=35, reservation=33),  # 94 % SATURÉ 

    # ── Architecture & Lumière (E04) — architecture / urbain — prix: 18 € ────
    Creneau(creneau_id="CH11", exposition_id="E04", start_hour=10, end_hour=12, max_capacity=140, reservation=42), # 30 %
    Creneau(creneau_id="CH12", exposition_id="E04", start_hour=14, end_hour=16, max_capacity=160, reservation=147),# 92 % SATURÉ

    # ── Mémoires d'Enfance (E05) — portrait / humanisme / n&b — prix: 7 € ───
    Creneau(creneau_id="CH13", exposition_id="E05", start_hour=11, end_hour=12, max_capacity=30, reservation=5),   # 17 %
    Creneau(creneau_id="CH14", exposition_id="E05", start_hour=13, end_hour=14, max_capacity=35, reservation=15),  # 43 %
    Creneau(creneau_id="CH15", exposition_id="E05", start_hour=15, end_hour=16, max_capacity=28, reservation=26),  # 93 % SATURÉ

    # ── Déserts du Monde (E06) — paysage / nature / couleur — prix: 15 € ────
    Creneau(creneau_id="CH16", exposition_id="E06", start_hour=11, end_hour=13, max_capacity=100, reservation=27), # 27 %
    Creneau(creneau_id="CH17", exposition_id="E06", start_hour=12, end_hour=14, max_capacity=100, reservation=33), # 33 %
    Creneau(creneau_id="CH18", exposition_id="E06", start_hour=14, end_hour=16, max_capacity=90,  reservation=30), # 33 %

    # ── Scènes de Rue (E07) — urbain / humanisme / couleur — prix: 10 € ─────
    Creneau(creneau_id="CH19", exposition_id="E07", start_hour=9,  end_hour=10, max_capacity=55, reservation=11),  # 20 %
    Creneau(creneau_id="CH20", exposition_id="E07", start_hour=12, end_hour=13, max_capacity=50, reservation=45),  # 90 % SATURÉ
    Creneau(creneau_id="CH21", exposition_id="E07", start_hour=14, end_hour=15, max_capacity=55, reservation=28),  # 51 %

    # ── Saveurs & Objectifs (E08) — culinaire / rue / nuit — prix: 18 € ─────
    # Calme (10%) → ff=+30 | Cible : Amaury (P01, gb, ff, 9h–11h)
    Creneau(creneau_id="CH22", exposition_id="E08", start_hour=9,  end_hour=10, max_capacity=40, reservation=4),   # 10 % Calme
    Creneau(creneau_id="CH23", exposition_id="E08", start_hour=10, end_hour=11, max_capacity=40, reservation=4),   # 10 % Calme

    # ── Entre Ciel et Terre (E09) — aérienne / animalière / mode — prix: 8 € ─
    # Faible (20%) → m=+5 | Cible : Adélie (P02, pb, m, 11h–13h + 18h–20h)
    Creneau(creneau_id="CH24", exposition_id="E09", start_hour=11, end_hour=12, max_capacity=40, reservation=8),   # 20 % Faible
    Creneau(creneau_id="CH25", exposition_id="E09", start_hour=12, end_hour=13, max_capacity=40, reservation=8),   # 20 % Faible
    Creneau(creneau_id="CH26", exposition_id="E09", start_hour=18, end_hour=19, max_capacity=40, reservation=8),   # 20 % Faible
    Creneau(creneau_id="CH27", exposition_id="E09", start_hour=19, end_hour=20, max_capacity=40, reservation=8),   # 20 % Faible

    # ── Architectures Nocturnes (E10) — architecture / conceptuelle / urbain — prix: 15 € ─
    # Surchargé (97%) → fo=+40 | Cible : Côme (P03, mb, fo, 19h–20h + 21h–23h)
    Creneau(creneau_id="CH28", exposition_id="E10", start_hour=19, end_hour=20, max_capacity=100, reservation=97), # 97 % Surchargé
    Creneau(creneau_id="CH29", exposition_id="E10", start_hour=21, end_hour=22, max_capacity=100, reservation=97), # 97 % Surchargé

    # ── Paysages au Crépuscule (E11) — paysage / n&b / portrait — prix: 20 € ─
    # Calme (12%) → fa=+20 | Cible : Annette (P04, gb, fa, 13h–14h + 18h–20h)
    Creneau(creneau_id="CH30", exposition_id="E11", start_hour=13, end_hour=14, max_capacity=50, reservation=6),   # 12 % Calme
    Creneau(creneau_id="CH31", exposition_id="E11", start_hour=18, end_hour=19, max_capacity=50, reservation=6),   # 12 % Calme
    Creneau(creneau_id="CH32", exposition_id="E11", start_hour=19, end_hour=20, max_capacity=50, reservation=6),   # 12 % Calme

    # ── Néons de la Ville (E12) — nuit / urbain / couleur — prix: 10 € ───────
    # Surchargé (96%) → tf=+60 | Cible : mark (P05, pb, tf, 17h–22h)
    Creneau(creneau_id="CH33", exposition_id="E12", start_hour=17, end_hour=18, max_capacity=80, reservation=77),  # 96 % Surchargé
    Creneau(creneau_id="CH34", exposition_id="E12", start_hour=18, end_hour=19, max_capacity=80, reservation=77),  # 96 % Surchargé
    Creneau(creneau_id="CH35", exposition_id="E12", start_hour=19, end_hour=20, max_capacity=80, reservation=77),  # 96 % Surchargé
    Creneau(creneau_id="CH36", exposition_id="E12", start_hour=20, end_hour=21, max_capacity=80, reservation=77),  # 96 % Surchargé
    Creneau(creneau_id="CH37", exposition_id="E12", start_hour=21, end_hour=22, max_capacity=80, reservation=77),  # 96 % Surchargé

    # ── Visions Conceptuelles (E13) — conceptuelle / urbain — prix: 12 € ─────
    # Surchargé (97%) → fo=+40 | Cible : Côme (P03, 2ème expo, fenêtre 21h–23h)
    Creneau(creneau_id="CH38", exposition_id="E13", start_hour=21, end_hour=22, max_capacity=70, reservation=68),  # 97 % Surchargé
    Creneau(creneau_id="CH39", exposition_id="E13", start_hour=22, end_hour=23, max_capacity=70, reservation=68),  # 97 % Surchargé

    # ── Plumes & Parures (E14) — mode / animalière / aérienne — prix: 9 € ────
    # Faible (20%) → m=+5 | Cible : Adélie (P02, 2ème expo fenêtre 18h–20h)
    Creneau(creneau_id="CH40", exposition_id="E14", start_hour=18, end_hour=19, max_capacity=40, reservation=8),   # 20 % Faible
    Creneau(creneau_id="CH41", exposition_id="E14", start_hour=19, end_hour=20, max_capacity=40, reservation=8),   # 20 % Faible

    # ── Nuit Argentique (E15) — paysage / n&b / portrait — prix: 20 € ────────
    # Calme (12%) → fa=+20 | Cible : Annette (P04, fenêtre 18h–20h)
    Creneau(creneau_id="CH42", exposition_id="E15", start_hour=18, end_hour=19, max_capacity=50, reservation=6),   # 12 % Calme
    Creneau(creneau_id="CH43", exposition_id="E15", start_hour=19, end_hour=20, max_capacity=50, reservation=6),   # 12 % Calme
]

# ─── Profils visiteurs ────────────────────────────────────────────────────────

VISITEURS: List[Visiteur] = [
    # Scénario 1 : gros budget, horreur de la foule, fenêtre matinale étroite
    Visiteur(
        visiteur_id="P01",
        name="Amaury",
        interet=["nuit", "culinaire", "rue"],
        disponibilites =[(9,11)],
        budget="gb",         
        tolerance_foule="ff", 
    ),

    # Scénario 2 : petit budget, tolérance neutre, deux fenêtres disponibles
    Visiteur(
        visiteur_id="P02",
        name="Adélie",
        interet=["mode", "aérienne", "animalière"],
        disponibilites =[(11,13),(18,20)],
        budget="pb",         
        tolerance_foule="m", 
    ),

    # Scénario 3 : adore la foule, disponible en soirée uniquement
    Visiteur(
        visiteur_id="P03",
        name="Côme",
        interet=["architecture", "conceptuelle", "urbain"],
        disponibilites =[(21,23),(19,20)],
        budget="mb",         
        tolerance_foule="fo", 
    ),

    # Scénario 4 : faible tolérance à la foule, trois fenêtres disponibles
    Visiteur(
        visiteur_id="P04",
        name="Annette",
        interet=["paysage", "n&b", "portrait"],
        disponibilites =[(8,12),(13,14),(18,20)],
        budget="gb",         
        tolerance_foule="fa", 
    ),

    # Scénario 5 : cherche la foule, petit budget, longue soirée
    Visiteur(
        visiteur_id="P05",
        name="mark",
        interet=["urbain", "couleur", "nuit"],
        disponibilites =[(9,11),(14,16),(17,22)],
        budget="pb",         
        tolerance_foule="tf", 
    ),
    
]
