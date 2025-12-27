# MyViz - 


—Visualisation des Élections en Mauritanie 🇲🇷

Package Python pour créer des cartes interactives des résultats des élections présidentielles en Mauritanie.

## Fonctionnalités

-  Carte interactive des résultats par Moughataa
-  Visualisations diverses (bar, hist, line, scatter, box)
-  Statistiques dynamiques
-  Design moderne avec Bokeh

##  Installation
```bash
# Cloner le repository
git clone https://github.com/VOTRE-USERNAME/myviz.git
cd myviz

# Installer les dépendances
pip install -r requirements.txt

# Installer le package en mode développement
pip install -e .
```

##  Utilisation
```python
from bokeh.io import output_notebook, show
from myviz import styled_election_map

output_notebook()

show(styled_election_map(
    shapefile_path="mrshape/mrt_admbnda_adm2_ansade_20240327.shp",
    csv_url="https://raw.githubusercontent.com/binorassocies/rimdata/refs/heads/main/data/results_elections_rim_2019-2024.csv"
))
```

##  Structure
```
myviz/
├── myviz/              # Package principal
│   ├── __init__.py
│   ├── bokeh_maps.py   # Cartes interactives
│   ├── bar.py
│   ├── hist.py
│   ├── line.py
│   ├── scatter.py
│   ├── box.py
│   └── style.py
├── mrshape/            # Données géographiques
├── setup.py
├── requirements.txt
└── README.md
```

## 🔧 Dépendances

- geopandas
- pandas
- numpy
- bokeh


