import geopandas as gpd
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (
    GeoJSONDataSource, HoverTool, LinearColorMapper,
    ColorBar, Select, CustomJS, Div
)
from bokeh.layouts import column, row


def styled_election_map(shapefile_path, csv_url):
    """
    Carte interactive Bokeh des élections présidentielles 2024 en Mauritanie.

    Parameters
    ----------
    shapefile_path : str
        Chemin vers le fichier .shp
    csv_url : str
        URL du fichier CSV des résultats
    """

    # -------------------------------
    # Chargement des données
    # -------------------------------
    gdf_moughataas = gpd.read_file(shapefile_path)
    gdf_moughataas = gdf_moughataas.rename(columns={"ADM2_EN": "moughataa"})

    df_elections = pd.read_csv(csv_url)
    df_elections_2024 = df_elections[df_elections['year'] == 2024]

    # Agrégation des voix par Moughataa et par candidat
    df_agg_2024 = df_elections_2024.groupby(["moughataa", "candidate"], as_index=False)["nb_votes"].sum()

    # Pivoter les données pour avoir tous les candidats en colonnes
    df_pivot = df_agg_2024.pivot(index="moughataa", columns="candidate", values="nb_votes").fillna(0)
    df_pivot = df_pivot.reset_index()

    # Liste des candidats
    candidats = [col for col in df_pivot.columns if col != "moughataa"]

    # Calculer le total des votes
    df_pivot['total_votes'] = df_pivot[candidats].sum(axis=1)

    # Calculer les totaux nationaux par candidat
    totaux_nationaux = {candidat: df_pivot[candidat].sum() for candidat in candidats}

    # Identifier le gagnant national
    gagnant_national = max(totaux_nationaux, key=totaux_nationaux.get)

    # Fusion avec le GeoDataFrame
    gdf_merged = gdf_moughataas.merge(df_pivot, on="moughataa", how="left")

    # Convertir en Web Mercator pour Bokeh
    gdf_merged = gdf_merged.to_crs(epsg=3857)

    # Nettoyage pour éviter l'erreur JSON
    colonnes_necessaires = ['geometry', 'moughataa'] + candidats + ['total_votes']
    gdf_clean = gdf_merged[colonnes_necessaires].copy()

    # Calculer le pourcentage pour chaque candidat
    for candidat in candidats:
        gdf_clean[f'{candidat}_pct'] = (gdf_clean[candidat] / gdf_clean['total_votes'] * 100).round(2)

    # Remplacer NaN et inf
    gdf_clean = gdf_clean.replace([np.inf, -np.inf], 0)
    gdf_clean = gdf_clean.fillna(0)

    # Convertir tous les nombres en float
    for col in gdf_clean.columns:
        if col not in ['geometry', 'moughataa']:
            gdf_clean[col] = gdf_clean[col].astype(float)

    # Préparer les données pour Bokeh
    geojson_str = gdf_clean.to_json()
    geosource = GeoJSONDataSource(geojson=geojson_str)

    # -------------------------------
    # Style
    # -------------------------------
    palette_simple = [
        '#1e3a8a', '#1e40af', '#1d4ed8',
        '#2563eb', '#3b82f6', '#60a5fa',
        '#93c5fd', '#bfdbfe', '#dbeafe'
    ]

    # Créer le color mapper initial
    candidat_initial = candidats[0]
    max_votes_initial = gdf_clean[candidat_initial].max()

    color_mapper = LinearColorMapper(
        palette=palette_simple,
        low=0,
        high=max_votes_initial,
        nan_color='#e5e7eb'
    )

    # Figure avec design épuré
    p = figure(
        title=f"Résultats de {candidat_initial} - Élections 2024",
        width=1200,
        height=850,
        toolbar_location="below",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        background_fill_color="#ffffff"
    )

    # Dessiner les polygones
    patches = p.patches(
        'xs', 'ys',
        source=geosource,
        fill_color={'field': candidat_initial, 'transform': color_mapper},
        fill_alpha=0.8,
        line_color="#6b7280",
        line_width=1,
        hover_fill_alpha=1.0,
        hover_line_color="#111827",
        hover_line_width=2
    )

    # Barre de couleur simple
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=10,
        width=15,
        height=250,
        location=(0, 0),
        title="Voix",
        title_text_font_size="11pt",
        major_label_text_font_size="10pt"
    )
    p.add_layout(color_bar, 'right')

    # HoverTool simple
    hover = HoverTool(
        tooltips=[
            ("Moughataa", "@moughataa"),
            ("Voix", f"@{{{candidat_initial}}}{{0,0}}"),
            ("Part", f"@{{{candidat_initial}_pct}}{{0.0}}%")
        ]
    )
    p.add_tools(hover)

    # Style minimaliste

    p.xaxis.visible = False
    p.yaxis.visible = False
    p.outline_line_color = "#d1d5db"
    p.outline_line_width = 1
    p.title.text_font_size = "16pt"
    p.title.align = "center"
    p.title.text_color = "#111827"

    # -------------------------------
    # Widgets
    # -------------------------------
    # Panneau d'information simple
    stats_candidat = totaux_nationaux[candidat_initial]
    stats_pct = (stats_candidat / sum(totaux_nationaux.values()) * 100)

    info_html = f"""
    <div style="padding: 15px;
                background: #f9fafb;
                border-radius: 8px;
                border: 1px solid #d1d5db;">
        <h3 style="margin: 0 0 12px 0;
                   font-size: 16px;
                   color: #111827;
                   border-bottom: 2px solid #3b82f6;
                   padding-bottom: 8px;">
            Statistiques
        </h3>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Candidat:</strong> {candidat_initial}
        </p>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Total:</strong> {stats_candidat:,.0f} voix
        </p>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Part:</strong> {stats_pct:.1f}%
        </p>
        <p style="margin: 10px 0 0 0;
                  padding-top: 8px;
                  border-top: 1px solid #e5e7eb;
                  font-size: 14px;
                  color: #374151;">
            <strong>Leader:</strong> {gagnant_national}
        </p>
    </div>
    """

    info_div = Div(text=info_html, width=300, height=200)

    # Menu simple
    select = Select(
        title="Candidat:",
        value=candidat_initial,
        options=candidats,
        width=300,
        height=50
    )

    # Callback
    callback_code = """
    const candidate = cb_obj.value;
    const data = source.data;

    let max_val = 0;
    let total_votes = 0;
    for (let i = 0; i < data[candidate].length; i++) {
        if (data[candidate][i] > max_val) {
            max_val = data[candidate][i];
        }
        total_votes += data[candidate][i];
    }

    color_mapper.high = max_val;
    patches.glyph.fill_color.field = candidate;
    plot.title.text = "Résultats de " + candidate + " - Élections 2024";

    const pct_field = candidate + "_pct";
    hover.tooltips = [
        ["Moughataa", "@moughataa"],
        ["Voix", "@{" + candidate + "}{0,0}"],
        ["Part", "@{" + pct_field + "}{0.0}%"]
    ];

    const total_national = """ + str(sum(totaux_nationaux.values())) + """;
    const pct_national = (total_votes / total_national * 100).toFixed(1);

    info_div.text = `
    <div style="padding: 15px;
                background: #f9fafb;
                border-radius: 8px;
                border: 1px solid #d1d5db;">
        <h3 style="margin: 0 0 12px 0;
                   font-size: 16px;
                   color: #111827;
                   border-bottom: 2px solid #3b82f6;
                   padding-bottom: 8px;">
            Statistiques
        </h3>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Candidat:</strong> ${candidate}
        </p>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Total:</strong> ${total_votes.toLocaleString()} voix
        </p>
        <p style="margin: 6px 0; font-size: 14px; color: #374151;">
            <strong>Part:</strong> ${pct_national}%
        </p>
        <p style="margin: 10px 0 0 0;
                  padding-top: 8px;
                  border-top: 1px solid #e5e7eb;
                  font-size: 14px;
                  color: #374151;">
            <strong>Leader:</strong> """ + gagnant_national + """
        </p>
    </div>
    `;

    source.change.emit();
    """

    callback = CustomJS(
        args=dict(
            source=geosource,
            color_mapper=color_mapper,
            patches=patches,
            plot=p,
            hover=hover,
            info_div=info_div
        ),
        code=callback_code
    )

    select.js_on_change('value', callback)

    # Titre simple
    titre = Div(
        text="""
        <div style="text-align: center;
                    padding: 15px;
                    background: #f3f4f6;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border: 1px solid #d1d5db;">
            <h1 style="color: #111827;
                       margin: 0;
                       font-size: 22px;">
                Élections Présidentielles 2024 - Mauritanie
            </h1>
            <p style="color: #6b7280;
                      margin: 5px 0 0 0;
                      font-size: 14px;">
                Résultats par Moughataa
            </p>
        </div>
        """,
        width=1200
    )

    # Layout final
    layout = column(
        titre,
        row(column(select, info_div), p)
    )

    return layout