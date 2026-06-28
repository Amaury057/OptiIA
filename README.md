# Festival Optimizer

Module d'aide à la décision pour le **Festival International de Photographie de Paris**.  
Recommande un parcours de visite personnalisé selon les intérêts du visiteur, sa tolérance à la foule, son budget et ses créneaux disponibles.

---

## Lancer le projet

**Prérequis** : Python 3.8+ — aucune dépendance externe.

```bash
cd festival_optimizer

# Tous les scénarios
python main.py

# Un visiteur précis
python main.py --visiteur P01

# Catalogue des expositions
python main.py --list-exposition

# Créneaux et taux d'occupation
python main.py --list-creneaux
```

---

## Structure

```
festival_optimizer/
├── data.py          # Modèles + jeu de données fictif (lieux, expos, créneaux, visiteurs)
├── scorer.py        # Algorithme de scoring multi-critères
├── recommender.py   # Sélection gloutonne de l'itinéraire
└── main.py          # CLI + affichage des scénarios
```

---

## Modèles de données

Les objets sont instanciés avec des **arguments nommés** pour la lisibilité :

```python
Creneau(
    creneau_id="CH01",
    exposition_id="E01",
    start_hour=9,
    end_hour=10,
    max_capacity=70,   # 50–95 % de Exposition.max_capacity
    reservation=14,    # 0–100 % de max_capacity → 20 % d'occupation
)
```

**Exposition** : `exposition_id`, `name`, `lieu_id`, `style`, `themes`, `duration_minutes`, `max_capacity`, `price`, `description`

**Créneau** : `creneau_id`, `exposition_id`, `start_hour`, `end_hour`, `max_capacity`, `reservation` → calcule `.remaining` et `.occupancy_pct`

**Visiteur** : `visiteur_id`, `name`, `interet` (3–4 thèmes), `disponibilites` (1–2 fenêtres horaires), `budget` (`pb`/`mb`/`gb`), `tolerance_foule` (`ff`/`fa`/`m`/`fo`/`tf`)

---

## Algorithme de scoring

Le score total peut être **négatif** (mauvaise adéquation tolérance/foule). Un créneau est exclu s'il passe sous **20 pts**.

### Intérêts (0 → 65 pts)

| Thèmes communs | Score |
|:--------------:|------:|
| 0 | 0 pts |
| 1 | 20 pts |
| 2 | 35 pts |
| 3 | 50 pts |
| 4 | 65 pts |

### Affluence × Tolérance (–60 → +60 pts)

| Niveau d'affluence | ff | fa | m | fo | tf |
|---|---:|---:|---:|---:|---:|
| Surchargé 96–100 % | –60 | –40 | –20 | +40 | +60 |
| Saturé 90–95 % | –30 | –20 | –10 | +10 | +30 |
| Élevé 70–89 % | –20 | –10 | –5 | +5 | +15 |
| Moyen 40–69 % | –5 | 0 | 0 | 0 | +5 |
| Faible 15–39 % | +15 | +10 | +5 | –5 | –15 |
| Calme 5–14 % | +30 | +20 | +10 | –10 | –30 |
| Paisible 0–4 % | +60 | +40 | +20 | –40 | –60 |

`ff` = très faible · `fa` = faible · `m` = moyenne · `fo` = forte · `tf` = très forte

### Budget (contrainte dure + score)

| Situation | Résultat |
|---|---:|
| Tarif > budget max | **Exposition exclue** |
| Tarif dans la fourchette | +30 pts |
| Tarif en dessous de la fourchette | +10 pts |

Fourchettes : `pb` = 7–10 €  ·  `mb` = 12–15 €  ·  `gb` = 18–20 €

### Contraintes dures (filtrées avant le scoring)

1. Le créneau doit s'inscrire dans l'une des fenêtres horaires du visiteur.
2. Le tarif de l'exposition ne doit pas dépasser le budget maximum du visiteur.
3. Des places restantes doivent être disponibles.

### Sélection de l'itinéraire

La sélection est **gloutonne** : les créneaux sont triés par score décroissant, puis ajoutés un à un en évitant les chevauchements et les doublons d'exposition.

---

## Scénarios de test

| ID | Visiteur | Fenêtre(s) | Intérêts | Budget | Tolérance | Cas illustré |
|----|----------|------------|----------|--------|-----------|--------------|
| P01 | Amaury | 09h–11h | nuit, culinaire, rue | gb (18–20 €) | ff | Gros budget, horreur de la foule, fenêtre matinale étroite |
| P02 | Adélie | 11h–13h / 18h–20h | mode, aérienne, animalière | pb (7–10 €) | m | Petit budget, deux fenêtres, tolérance neutre |
| P03 | Côme | 19h–20h / 21h–23h | architecture, conceptuelle, urbain | mb (12–15 €) | fo | Adore la foule, disponible en soirée uniquement |
| P04 | Annette | 08h–12h / 13h–14h / 18h–20h | paysage, n&b, portrait | gb (18–20 €) | fa | Faible tolérance, trois fenêtres disponibles |
| P05 | Mark | 09h–11h / 14h–16h / 17h–22h | urbain, couleur, nuit | pb (7–10 €) | tf | Cherche la foule, longue soirée, petit budget |

---

## Données fictives

- **15 expositions** dans **10 lieux parisiens réels** (Musée d'Art Moderne, Jeu de Paume, Fondation Henri Cartier-Bresson, Petit Palais, Musée du Louvre…)
- **43 créneaux** dont plusieurs saturés (≥ 90 %) pour tester les cas limites
- Tarifs : 7 €, 8 €, 9 €, 10 €, 12 €, 15 €, 18 €, 20 €
- **5 profils visiteurs** couvrant des cas limites variés

---

## Documentation technique des hypothèses

### 1. Construction des données fictives

- **Remplissage des salles** : Les taux d'occupation des créneaux ont été générés entre 0 % et 100 % pour couvrir tous les cas limites (salle vide, modérément fréquentée, saturée) et vérifier que le code réagit correctement à chaque palier.
- **Jauge par créneau** : La capacité max d'un créneau est volontairement inférieure à celle du lieu (entre 50 % et 95 %), pour simuler les contraintes de sécurité et de fluidité lors des rotations.
- **Tarif uniforme par exposition** : Le prix est identique pour tous les créneaux d'une même exposition ; il n'existe pas de tarif variable selon l'heure ou la saison.

### 2. Logique de scoring

- **Thèmes en commun** : La progression est non-linéaire (0 → 20 → 35 → 50 → 65 pts) pour valoriser les correspondances multiples sans rendre les matchs partiels insignifiants.
- **Budget** : Un tarif exactement dans la fourchette du visiteur vaut +30 pts ; un tarif en dessous vaut +10 pts (l'expo est accessible mais pas idéale). Le tarif supérieur au budget max est une contrainte dure : l'exposition est écartée avant même le calcul.
- **Affluence** : La matrice crowd est symétrique — un visiteur fuyant la foule perd autant de points qu'un visiteur cherchant l'ambiance en gagne, et vice-versa.
- **Seuil minimum à 20 pts** : Un créneau dont le score total est inférieur à 20 pts est écarté, car il ne correspond pas suffisamment au profil du visiteur pour être recommandé.

### 3. Critères d'élimination (contraintes dures)

Avant tout calcul de score, un créneau est éliminé si :

1. Il ne s'inscrit pas dans les fenêtres horaires du visiteur.
2. Le tarif de l'exposition dépasse le budget maximum du visiteur.
3. Il ne reste plus aucune place disponible.

### 4. Limites connues

- **Pondérations arbitraires** : les bonus/malus ont été choisis au jugé, sans validation terrain ni étude utilisateur.
- **Données statiques** : l'affluence est figée dans le code, sans mise à jour en temps réel.
- **Sélection gloutonne** : l'itinéraire résultant n'est pas globalement optimal (un créneau très bien noté peut bloquer une meilleure combinaison).
- **Distance non calculée** : seul l'arrondissement est affiché ; le temps de trajet entre deux expositions n'est pas estimé.
- **Granularité 1h** : impossible de gérer des expositions de 30 min ou 1h30.
- **Pas de préférences négatives** : un visiteur ne peut pas exclure un thème qu'il n'aime pas.



