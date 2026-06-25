"""
Moteur de scoring multi-critères (idée 4 du CONTEXTE.md).

Score total = intérêts + affluence + budget
Le score peut être négatif (mauvaise tolérance à la foule) → créneau exclu.

Contraintes dures (filtrées AVANT le calcul du score) :
    - Créneau hors fenêtre horaire du visiteur → rejeté
    - Tarif expo > budget max du visiteur → rejeté
"""

from typing import Dict, Optional
from data import Exposition, Creneau, Visiteur, BUDGET_RANGES


# ─── Score centres d'intérêt ──────────────────────────────────────────────────
# Nombre de thèmes en commun entre l'expo et les intérêts du visiteur

INTEREST_SCORE: Dict[int, int] = {
    0: 0,
    1: 20,
    2: 35,
    3: 50,
    4: 65,
}

# ─── Matrice affluence × tolérance à la foule ────────────────────────────────
# Chaque entrée : (limite_haute_pct, {tolérance: score})

CROWD_MATRIX = [
    (4,   {"ff": 60, "fa": 40, "m": 20,  "fo": -40, "tf": -60}),  # Paisible  0–4 %
    (14,  {"ff": 30, "fa": 20, "m": 10,  "fo": -10, "tf": -30}),  # Calme     5–14 %
    (39,  {"ff": 15, "fa": 10, "m": 5,   "fo": -5,  "tf": -15}),  # Faible   15–39 %
    (69,  {"ff": -5, "fa": 0,  "m": 0,   "fo": 0,   "tf": 5}),    # Moyen    40–69 %
    (89,  {"ff": -20,"fa": -10,"m": -5,  "fo": 5,   "tf": 15}),   # Élevé    70–89 %
    (95,  {"ff": -30,"fa": -20,"m": -10, "fo": 10,  "tf": 30}),   # Saturé   90–95 %
    (100, {"ff": -60,"fa": -40,"m": -20, "fo": 40,  "tf": 60}),   # Surchargé 96–100 %
]


def interest_score(exhibition: Exposition, visitor: Visiteur) -> int:
    """Score basé sur le nombre de thèmes communs (plafonné à 4)."""
    matches = len(set(exhibition.themes) & set(visitor.interet))
    matches = min(matches, 4)
    return INTEREST_SCORE.get(matches, 0)


def crowd_score(slot: Creneau, visitor: Visiteur) -> int:
    """Score positif ou négatif selon la matrice affluence × tolérance."""
    pct = slot.occupancy_pct * 100
    for limit, scores in CROWD_MATRIX:
        if pct <= limit:
            return scores.get(visitor.tolerance_foule, 0)
    return 0  # sécurité si pct > 100 %


def budget_score(exhibition: Exposition, visitor: Visiteur) -> Optional[int]:
    """
    Retourne :
        None  → tarif supérieur au budget max (contrainte dure : exposition exclue)
        30    → tarif dans la fourchette budget du visiteur (correspondance parfaite)
        10    → tarif inférieur à la fourchette (visiteur peut se le permettre)
    """
    budget_min, budget_max = BUDGET_RANGES[visitor.budget]

    if exhibition.price > budget_max:
        return None  # exclu

    if exhibition.price >= budget_min:
        return 30    # correspondance parfaite

    return 10        # tarif en dessous de sa fourchette


def score_slot(exhibition: Exposition, slot: Creneau, visitor: Visiteur) -> Optional[Dict]:
    """
    Calcule le score complet d'un créneau pour un visiteur.
    Retourne None si une contrainte dure est violée (budget).
    """
    b = budget_score(exhibition, visitor)
    if b is None:
        return None  # contrainte budget violée

    i  = interest_score(exhibition, visitor)
    cr = crowd_score(slot, visitor)
    total = i + cr + b

    return {
        "exposition_id": exhibition.exposition_id,
        "creneau_id":        slot.creneau_id,
        "start_hour":     slot.start_hour,
        "end_hour":       slot.end_hour,
        "scores": {
            "interests": i,
            "crowd":     cr,
            "budget":    b,
        },
        "total":           total,
        "occupancy_pct":   round(slot.occupancy_pct * 100),
        "remaining_spots": slot.remaining,
    }
