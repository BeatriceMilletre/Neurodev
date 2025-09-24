import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Préquestionnaire Neurodiversité", layout="wide")

st.title("Préquestionnaire de Neurodiversité – Prototype (Streamlit)")
st.caption("Dr Béatrice Millêtre – Prototype de passation en ligne avec profil en étoile")

st.markdown('''
Ce prototype permet :
1) de **passer le questionnaire** (80 items, échelle 0–4) ;
2) de **générer automatiquement** les scores par dimension ;
3) d’**afficher un profil en étoile (radar)** ;
4) d’**exporter** les résultats (CSV et image) ;
5) de **proposer une interprétation automatique**.
''')

# --- Dimensions and items (simplifié ici pour la lisibilité, gardez vos 80 items) ---
dimensions = {
"D1 - Traitement de l’information":[
"Quand on me donne une règle ou une consigne, je cherche d’abord à comprendre sa logique globale avant de l’appliquer.",
"Quand quelqu’un me raconte un événement, plusieurs images et idées apparaissent en même temps dans ma tête.",
"Face à un problème, plusieurs solutions possibles surgissent spontanément, sans effort conscient.",
"Pendant une réunion, j’ai souvent l’impression de voir rapidement la conclusion, avant que les autres n’y arrivent.",
"Quand on me donne une liste de tâches, je préfère les faire dans l’ordre exact où elles ont été données.",
"Je progresse étape par étape, en terminant une partie avant de passer à la suivante.",
"Pour résoudre un problème, j’applique d’abord les méthodes apprises et connues.",
"Quand une explication est longue et détaillée, je perds le fil et je ne sais plus quel était le point principal.",
"Quand on me donne une consigne complexe, j’oublie parfois une partie ou je mélange les étapes.",
"Quand on me demande quelque chose de précis, je l’exécute exactement comme cela a été dit, même si cela paraît inhabituel."
],
"D2 - Sensorialité":[
"Dans une cantine bruyante, les conversations et les bruits se mélangent et je n’arrive plus à suivre mon interlocuteur.",
"Une couture ou une étiquette de vêtement peut m’empêcher de le porter.",
"Après un moment dans une pièce éclairée au néon, je me sens fatigué(e) ou irrité(e).",
"Je remarque immédiatement un changement minime de goût ou d’odeur dans un aliment.",
"Après une journée en ville, j’ai besoin de silence pour retrouver mon équilibre.",
"Quand plusieurs personnes parlent en même temps, je perds le fil de la discussion.",
"Pour me sentir bien, j’ai parfois besoin de musique forte, de bouger ou de rechercher des sensations intenses.",
"Quand une porte claque, je sursaute fortement, parfois avec une réaction physique marquée.",
"Une odeur persistante peut me rester longtemps en tête.",
"Dans un repas ou une soirée animée, je remarque le bruit et la lumière, mais je m’y adapte sans gêne particulière."
],
# ... Ajoutez ici vos autres dimensions D3 à D8 comme dans la version précédente ...
}

st.sidebar.header("Barème")
st.sidebar.write("**0 = Jamais | 1 = Rarement | 2 = Parfois | 3 = Souvent | 4 = Toujours**")
patient_name = st.sidebar.text_input("Nom / identifiant du patient", value="Patient A")
st.sidebar.info("Renseignez un identifiant (initiales ou code) si vous souhaitez anonymiser.")

# --- Questionnaire UI ---
all_scores = {}
with st.form("questionnaire"):
    for dim, items in dimensions.items():
        with st.expander(dim, expanded=False):
            dim_scores = []
            for i, item in enumerate(items, start=1):
                s = st.slider(f"{i}. {item}", min_value=0, max_value=4, value=0, step=1, key=f"{dim}_{i}")
                dim_scores.append(s)
            all_scores[dim] = dim_scores
    submitted = st.form_submit_button("Calculer le profil")

def compute_dimension_scores(all_scores):
    rows = []
    for dim, scores in all_scores.items():
        total = int(np.sum(scores))
        rows.append({"Dimension": dim, "Score": total, "Max": 40})
    return pd.DataFrame(rows)

def plot_radar(df):
    dims = df["Dimension"].tolist()
    scores = df["Score"].astype(float).to_numpy()
    maxs = df["Max"].astype(float).to_numpy()
    vals = scores / maxs

    N = len(dims)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    vals = np.concatenate((vals, [vals[0]]))
    angles += angles[:1]

    fig = plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=9)

    ax.set_rlabel_position(0)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["10/40", "20/40", "30/40", "40/40"], fontsize=8)
    ax.set_ylim(0, 1)

    ax.plot(angles, vals, linewidth=2)
    ax.fill(angles, vals, alpha=0.25)

    title_lines = [f"{d}: {int(s)}/40" for d, s in zip(dims, scores)]
    title = f"Profil en étoile – {st.session_state.get('patient_name', 'Patient')}\n" + " | ".join(title_lines)
    plt.title(title, fontsize=10, pad=20)
    fig.tight_layout()
    return fig

# --- Interprétation automatique ---
def interpret_profile(df):
    scores = dict(zip(df["Dimension"], df["Score"]))
    txts = []

    # HPI
    if scores.get("D1 - Traitement de l’information", 0) >= 20 \
       and scores.get("D6 - Créativité et intuition", 0) >= 28 \
       and scores.get("D5 - Émotions et régulation", 0) >= 24 \
       and scores.get("D4 - Cognition sociale et communication", 0) >= 20:
        txts.append("🟣 Profil compatible **HPI** : pensée associative, créativité intuitive, intensité émotionnelle et exigence de valeurs.")

    # TDAH
    if scores.get("D3 - Attention et concentration", 0) >= 24:
        txts.append("🟠 Profil compatible **TDAH** : difficultés attentionnelles persistantes avec impact fonctionnel (oubli, inachèvement).")

    # TSA
    if scores.get("D4 - Cognition sociale et communication", 0) >= 24 \
       and scores.get("D2 - Sensorialité", 0) >= 24:
        txts.append("🔵 Profil compatible **TSA** : littéralité sociale, rigidité ou sensibilité sensorielle élevée.")

    # 2E
    if scores.get("D7 - Double exceptionnalité", 0) >= 24 \
       and (scores.get("D1 - Traitement de l’information", 0) >= 28 \
            or scores.get("D6 - Créativité et intuition", 0) >= 28 \
            or scores.get("D5 - Émotions et régulation", 0) >= 28):
        txts.append("🟢 Profil compatible **2E (double exceptionnalité)** : coexistence de forces remarquables et de difficultés importantes.")

    # NT
    if all(v <= 15 for v in scores.values()):
        txts.append("⚪ Profil compatible **Neurotypique (NT)** : équilibre attentionnel, émotionnel et sensoriel sans particularité marquée.")

    if not txts:
        txts.append("Profil nuancé : aucune orientation claire unique. L’interprétat
