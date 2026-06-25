"""
Moteur de recommandation : sélection gloutonne (greedy) de créneaux non
chevauchants, sans doublon d'exposition, triés par score décroissant.

Contraintes dures appliquées avant le scoring :
    1. Le créneau doit s'inscrire dans l'une des disponibilités du visiteur.
    2. Le tarif de l'exposition ne doit pas dépasser le budget max du visiteur.

Limites connues :
    - Sélection greedy : non globalement optimale.
    - Pondérations du scoring arbitraires (CONTEXTE.md §idée 4).
    - Affluence figée : aucune donnée temps réel.
    - Distance entre lieux non calculée (arrondissement uniquement).
"""

from typing import List, Dict, Optional, Tuple
from data import Exposition, Lieu, Visiteur, EXPOSITIONS, CRENEAUX, LIEUX
from scorer import score_slot

MIN_SCORE = 20


def _get_lieu(lieu_id: str) -> Lieu:
    return next(l for l in LIEUX if l.lieu_id == lieu_id)


def _get_exposition(exposition_id: str) -> Optional[Exposition]:
    return next((e for e in EXPOSITIONS if e.exposition_id == exposition_id), None)


def _fits_in_window(
    heure_debut: int,
    heure_fin: int,
    disponibilites: List[Tuple[int, int]],
) -> bool:
    return any(
        heure_debut >= w_debut and heure_fin <= w_fin
        for w_debut, w_fin in disponibilites
    )


def _overlaps(a_debut: int, a_fin: int, b_debut: int, b_fin: int) -> bool:
    return not (a_fin <= b_debut or a_debut >= b_fin)


def build_itinerary(visiteur: Visiteur) -> List[Dict]:
    """
    Construit l'itinéraire recommandé pour un visiteur.

    Étapes :
        1. Contraintes dures : fenêtre horaire + places disponibles.
        2. Scoring (peut exclure par budget → None, ou score < MIN_SCORE).
        3. Tri par score décroissant.
        4. Sélection gloutonne : pas de chevauchement, pas de doublon d'exposition.
        5. Retour trié par heure de début.
    """
    candidates = []

    for creneau in CRENEAUX:
        if creneau.remaining <= 0:
            continue

        if not _fits_in_window(creneau.start_hour, creneau.end_hour, visiteur.disponibilites):
            continue

        exposition = _get_exposition(creneau.exposition_id)
        if exposition is None:
            continue

        result = score_slot(exposition, creneau, visiteur)
        if result is None:
            continue

        if result["total"] < MIN_SCORE:
            continue

        candidates.append({
            **result,
            "exposition": exposition,
            "lieu":       _get_lieu(exposition.lieu_id),
        })

    candidates.sort(key=lambda x: x["total"], reverse=True)

    selected: List[Dict] = []
    booked_windows: List[Tuple[int, int]] = []
    visited_expositions: set = set()

    for c in candidates:
        start, end = c["start_hour"], c["end_hour"]
        exp_id = c["exposition_id"]

        if exp_id in visited_expositions:
            continue

        if any(_overlaps(start, end, s, e) for s, e in booked_windows):
            continue

        selected.append(c)
        booked_windows.append((start, end))
        visited_expositions.add(exp_id)

    selected.sort(key=lambda x: x["start_hour"])
    return selected
