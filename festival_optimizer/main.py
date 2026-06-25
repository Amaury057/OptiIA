"""
Festival Optimizer — Point d'entrée CLI.

Usage :
    py main.py
    py main.py --visiteur P01
    py main.py --list-exposition
    py main.py --list-creneaux
"""

import argparse
import sys
from typing import List, Dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from data import (
    VISITEURS, EXPOSITIONS, CRENEAUX, Visiteur,
    BUDGET_LABELS, TOLERANCE_FOULE_LABELS,
)
from recommender import build_itinerary, MIN_SCORE


# ─── Formatage ────────────────────────────────────────────────────────────────

SEP  = "═" * 64
SEP2 = "─" * 64


def fmt_hour(h: int) -> str:
    return f"{int(h):02d}:00"


def crowd_label(occupancy_pct: int) -> str:
    if occupancy_pct > 95: return "⚠ Surchargé"
    if occupancy_pct > 89: return "⚠ Saturé"
    if occupancy_pct > 69: return "! Élevé"
    if occupancy_pct > 39: return "  Moyen"
    if occupancy_pct > 14: return "  Faible"
    if occupancy_pct > 4:  return "  Calme"
    return "  Paisible"


def score_bar(score: float, max_val: float = 115, width: int = 20) -> str:
    """Barre proportionnelle — max_val ≈ score parfait théorique (65+30+20)."""
    filled = max(0, min(width, round((score / max_val) * width)))
    return "[" + "█" * filled + "░" * (width - filled) + f"] {score:+.0f} pts"


# ─── Affichage de l'itinéraire ────────────────────────────────────────────────

def print_header():
    print()
    print(SEP)
    print("   FESTIVAL OPTIMIZER — Recommandations de parcours de visite")
    print("   Festival International de Photographie · Paris")
    print(SEP)


def print_legend():
    print()
    print("  CRITÈRES DE SCORING")
    print("  " + SEP2)
    print("  Intérêts   (0 → 65 pts)  : thèmes communs expo ↔ visiteur")
    print("    0 commun = 0 pts  |  1 = 20  |  2 = 35  |  3 = 50  |  4 = 65")
    print()
    print("  Affluence  (–60 → +60 pts): matrice occupation × tolérance du visiteur")
    print("    Valeur positive si l'ambiance correspond, négative sinon")
    print()
    print("  Budget     (10 ou 30 pts) : correspondance tarif ↔ fourchette budget")
    print("    Tarif dans fourchette = +30  |  Tarif en dessous = +10")
    print("    Tarif supérieur au budget max → exposition exclue (contrainte dure)")
    print()
    print(f"  Score minimum pour être retenu : {MIN_SCORE} pts")
    print()


def print_itinerary(visiteur: Visiteur, itinerary: List[Dict]):
    print()
    print(SEP)
    print(f"  VISITEUR : {visiteur.name}")

    windows = "  /  ".join(
        f"{fmt_hour(s)} → {fmt_hour(e)}" for s, e in visiteur.disponibilites
    )
    print(f"  Fenêtres : {windows}")
    print(f"  Intérêts : {', '.join(visiteur.interet)}")
    print(f"  Budget   : {BUDGET_LABELS[visiteur.budget]}")
    print(f"  Foule    : {TOLERANCE_FOULE_LABELS[visiteur.tolerance_foule]}")
    print("  " + SEP2)

    if not itinerary:
        print("  Aucune recommandation disponible pour ce profil.")
        print("  Causes possibles : toutes les expos sont saturées pour ce profil de")
        print("  tolérance, hors budget, ou aucun créneau dans la fenêtre horaire.")
        return

    total_pts = sum(i["total"] for i in itinerary)
    print(f"  {len(itinerary)} exposition(s) recommandée(s)  ·  Score cumulé : {total_pts:+.0f} pts")
    print()

    for rank, item in enumerate(itinerary, 1):
        expo   = item["exposition"]
        lieu   = item["lieu"]
        scores = item["scores"]

        print(f"  [{rank}] {expo.name}  —  {expo.style}")
        print(f"      {expo.description}")
        print(f"      Thèmes   : {', '.join(expo.themes)}")
        print(f"      Lieu     : {lieu.name}")
        print(f"               : {lieu.address}  ({lieu.district})")
        print(f"      Créneau  : {fmt_hour(item['start_hour'])} → {fmt_hour(item['end_hour'])}")
        print(f"      Tarif    : {expo.price} €")
        print(f"      Affluence: {item['occupancy_pct']:>3} %  {crowd_label(item['occupancy_pct'])}"
              f"  ·  {item['remaining_spots']} place(s) restante(s)")
        print()
        print(f"      Score    : {score_bar(item['total'])}")
        print(f"               ├─ intérêts : {scores['interests']:>+4} pts")
        print(f"               ├─ affluence: {scores['crowd']:>+4} pts")
        print(f"               └─ budget   : {scores['budget']:>+4} pts")
        print()

    _print_gaps(visiteur, itinerary)


def _print_gaps(visiteur: Visiteur, itinerary: List[Dict]):
    """Signale les plages libres dans chaque fenêtre du visiteur."""
    for w_start, w_end in visiteur.disponibilites:
        expos_in_window = [
            i for i in itinerary
            if i["start_hour"] >= w_start and i["end_hour"] <= w_end
        ]
        if not expos_in_window:
            print(f"  Fenêtre {fmt_hour(w_start)}–{fmt_hour(w_end)} : aucune expo recommandée dans cette plage.")
            continue

        gaps = []
        current = w_start
        for item in sorted(expos_in_window, key=lambda x: x["start_hour"]):
            if item["start_hour"] > current:
                gaps.append((current, item["start_hour"]))
            current = item["end_hour"]
        if current < w_end:
            gaps.append((current, w_end))

        for g_start, g_end in gaps:
            print(f"  Créneau libre {fmt_hour(g_start)}–{fmt_hour(g_end)} : "
                  f"aucune expo ne dépasse le seuil de {MIN_SCORE} pts dans cette plage.")


# ─── Commandes utilitaires ────────────────────────────────────────────────────

def print_exposition():
    print()
    print(SEP)
    print("  CATALOGUE DES EXPOSITIONS")
    print("  " + SEP2)
    for expo in EXPOSITIONS:
        print(f"  [{expo.exposition_id}] {expo.name}  ({expo.price} €  ·  {expo.duration_minutes} min)")
        print(f"        Style  : {expo.style}")
        print(f"        Thèmes : {', '.join(expo.themes)}")
        print(f"        {expo.description}")
        print()


def print_creneaux():
    print()
    print(SEP)
    print("  CRÉNEAUX ET TAUX D'OCCUPATION")
    print(f"  {'ID':<6} {'Expo':<5} {'Horaire':<14} {'Réservé':>8} {'Restant':>8}  Statut")
    print("  " + SEP2)
    for s in CRENEAUX:
        horaire = f"{fmt_hour(s.start_hour)} → {fmt_hour(s.end_hour)}"
        pct = round(s.occupancy_pct * 100)
        print(f"  {s.creneau_id:<6} {s.exposition_id:<5} {horaire:<14} {pct:>6} %  {s.remaining:>7}   {crowd_label(pct)}")
    print()


# ─── Limites du modèle ────────────────────────────────────────────────────────

def print_limitations():
    print()
    print(SEP)
    print("  LIMITES DU MODÈLE")
    print("  " + SEP2)
    limits = [
        "Pondérations arbitraires (0/20/35/50/65 intérêts, matrice foule) — non validées terrain.",
        "Affluence figée dans les données : aucune mise à jour temps réel.",
        "Sélection gloutonne : l'itinéraire obtenu n'est pas globalement optimal.",
        "Distance entre lieux non calculée : l'arrondissement seul est affiché.",
        "Créneaux du visiteur en heures entières : granularité de 1h uniquement.",
        "Pas de prise en compte des préférences négatives (expos à éviter).",
    ]
    for limit in limits:
        print(f"  · {limit}")
    print(SEP)
    print()


# ─── Point d'entrée ───────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Festival Optimizer — recommandations de parcours de visite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--visiteur", "-v",
        metavar="ID",
        help="ID du visiteur (P01–P05). Défaut : tous.",
        default=None,
    )
    parser.add_argument(
        "--list-exposition",
        action="store_true",
        help="Affiche le catalogue des expositions.",
    )
    parser.add_argument(
        "--list-creneaux",
        action="store_true",
        help="Affiche tous les créneaux avec leur taux d'occupation.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print_header()

    if args.list_exposition:
        print_exposition()
        return

    if args.list_creneaux:
        print_creneaux()
        return

    print_legend()

    if args.visiteur:
        visiteur = next((v for v in VISITEURS if v.visiteur_id == args.visiteur), None)
        if visiteur is None:
            print(f"  Visiteur '{args.visiteur}' introuvable. IDs valides : P01, P02, P03, P04, P05")
            sys.exit(1)
        visiteurs_to_run = [visiteur]
    else:
        visiteurs_to_run = VISITEURS

    for visiteur in visiteurs_to_run:
        itinerary = build_itinerary(visiteur)
        print_itinerary(visiteur, itinerary)

    print_limitations()


if __name__ == "__main__":
    main()
