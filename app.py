
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
4) d’**exporter** les résultats (CSV et image).
''')

# --- Dimensions and items (exact phrasing, situation-based) ---
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
"D3 - Attention et concentration":[
"Quand je travaille, un bruit soudain me détourne et je perds le fil de ce que je faisais.",
"Quand je parle avec quelqu’un, un détail déclenche des associations d’idées tout en continuant la conversation.",
"Quand je lis, je peux interrompre et reprendre plus tard sans difficulté.",
"Enfant, j’oubliais mes devoirs ou je les laissais inachevés malgré mes efforts.",
"Quand une activité me passionne, je peux oublier de manger ou de dormir.",
"Pendant une réunion, j’écoute tout en préparant une idée parallèle à présenter.",
"Quand je cuisine, je reste attentif(ve) et je reprends sans effort après une interruption.",
"En conversation, je décroche parfois en plein milieu d’une phrase.",
"En cours, je comprends vite puis je décroche par ennui.",
"Quand on me donne une consigne claire, je la suis jusqu’au bout et je reprends facilement après une interruption."
],
"D4 - Cognition sociale et communication":[
"Quand on me dit « reviens dans 5 minutes », je prends cela au mot près et je suis contrarié(e) si ce n’est pas respecté.",
"Quand quelqu’un ne tient pas sa parole, je le vis comme un manquement à une valeur.",
"Quand on me dit « reviens dans 5 minutes », je comprends que cela signifie « un peu plus tard ».",
"Je prends souvent les phrases au pied de la lettre et l’ironie m’échappe.",
"Après une soirée, je repense longtemps aux conversations.",
"Dans un dîner, je comprends les sous-entendus et je passe à autre chose.",
"Si une règle sociale n’est pas respectée (prévenir d’un retard), je ressens une gêne importante.",
"Une blague à double sens peut me déstabiliser.",
"Je préfère discuter en petit comité qu’en grand groupe.",
"Je participe avec aisance à des conversations légères."
],
"D5 - Émotions et régulation":[
"Une remarque peut rester longtemps dans mon esprit.",
"Face à une injustice, ma réaction est immédiate et intense.",
"Une émotion forte m’empêche parfois d’agir ou de réfléchir clairement.",
"Mon stress s’exprime physiquement (maux de ventre, tensions, migraines).",
"Quand un ami est triste, je ressens son émotion dans mon corps.",
"Mon humeur peut changer brutalement dans la journée.",
"Après une dispute, je revis la scène longtemps dans ma tête.",
"Après une rencontre sociale, j’ai besoin de temps seul(e) pour récupérer.",
"Dans certaines situations, j’ai du mal à identifier clairement mon émotion.",
"Après une contrariété, j’arrive à passer vite à autre chose."
],
"D6 - Créativité et intuition":[
"En marchant ou en conduisant, une solution complète peut surgir sans effort.",
"En rencontrant quelqu’un, j’ai une impression immédiate de sa personnalité.",
"Quand je cherche une idée, je relie spontanément des domaines très différents.",
"Mon imagination produit facilement des images ou des histoires détaillées.",
"Mes rêves sont longs et très clairs, comme un film.",
"En entrant dans un lieu, je ressens parfois une ambiance particulière.",
"J’invente facilement une nouvelle manière d’accomplir une tâche.",
"Pour décider, je sens parfois un “oui” ou un “non” intérieur évident.",
"Je commence souvent par appliquer une méthode connue et éprouvée.",
"Quand on me demande une solution, je propose d’abord ce qui me paraît logique et déjà testé."
],
"D7 - Double exceptionnalité":[
"Je réussis un exercice complexe mais j’échoue parfois sur une tâche simple.",
"Mes notes ou résultats varient beaucoup selon les domaines.",
"On m’a décrit comme « brillant(e) mais inconstant(e) ».",
"Même après une réussite, je doute d’être vraiment compétent(e).",
"Je dépense beaucoup d’énergie pour compenser certaines difficultés.",
"Mes forces cachent mes fragilités, ou l’inverse.",
"Après une journée d’efforts, je me sens épuisé(e) mentalement.",
"Mon parcours alterne périodes de grande réussite et d’échec marqué.",
"J’ai parfois été mal orienté(e) car on a jugé une partie de mon profil seulement.",
"On me perçoit parfois comme exceptionnel(le), parfois comme en difficulté, selon le contexte."
],
"D8 - Temporalité et rythmes":[
"Je fais souvent mes tâches à la dernière minute et je réussis dans l’urgence.",
"Absorbé(e) par une activité, je perds complètement la notion du temps.",
"Je préfère avancer sur plusieurs projets en parallèle plutôt que d’en finir un seul.",
"Un changement de programme de dernière minute me perturbe longtemps.",
"J’alterne entre périodes de grande activité et moments où je n’arrive plus à avancer.",
"J’ai du mal à estimer le temps que prendra une tâche et je suis souvent en retard.",
"Quand j’ai de l’avance, je perds la motivation et j’attends le moment de l’urgence.",
"Dans une réunion, je comprends la conclusion avant la fin et je m’impatiente.",
"Quand on me donne une consigne simple avec un début et une fin clairs, je l’exécute sans me disperser.",
"Je m’adapte sans difficulté à une routine stable avec des horaires fixes."
]
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
    title = f"Profil en étoile – {st.session_state.get('patient_name', 'Patient')}\\n" + " | ".join(title_lines)
    plt.title(title, fontsize=10, pad=20)
    fig.tight_layout()
    return fig

# Save patient name for title
st.session_state["patient_name"] = patient_name

if submitted:
    df_scores = compute_dimension_scores(all_scores)

    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("Scores par dimension")
        st.dataframe(df_scores, use_container_width=True)
        csv = df_scores.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Télécharger les scores (CSV)",
                           data=csv,
                           file_name=f"scores_{patient_name.replace(' ','_')}.csv",
                           mime="text/csv")
    with col2:
        st.subheader("Vision en étoile (Radar)")
        fig = plot_radar(df_scores)
        st.pyplot(fig)
        # Save image to bytes
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        st.download_button("⬇️ Télécharger le radar (PNG)",
                           data=buf.getvalue(),
                           file_name=f"radar_{patient_name.replace(' ','_')}.png",
                           mime="image/png")

st.markdown("---")
st.caption("⚠️ Outil d'orientation clinique. Ce questionnaire n’est pas un diagnostic.")
