import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Préquestionnaire Neurodiversité", layout="wide")

st.title("Préquestionnaire de Neurodiversité – Prototype (Streamlit)")
st.caption("Dr Béatrice Millettre – Questionnaire en ligne, radar et interprétation automatique")

st.sidebar.header("Barème")
st.sidebar.write("0 = Jamais | 1 = Rarement | 2 = Parfois | 3 = Souvent | 4 = Toujours")
patient_name = st.sidebar.text_input("Nom / identifiant du patient", value="Patient A")

mode = st.sidebar.radio("Mode d'utilisation", ["Questionnaire", "Importer un CSV de scores"])

# ----------------------------- Items (D1..D8) -----------------------------
dimensions = {
"D1 - Traitement de l'information":[
"Quand on me donne une regle ou une consigne, je cherche d'abord a comprendre sa logique globale avant de l'appliquer.",
"Quand quelqu'un me raconte un evenement, plusieurs images et idees apparaissent en meme temps dans ma tete.",
"Face a un probleme, plusieurs solutions possibles surgissent spontaneement, sans effort conscient.",
"Pendant une reunion, j'ai souvent l'impression de voir rapidement la conclusion, avant que les autres n'y arrivent.",
"Quand on me donne une liste de taches, je prefere les faire dans l'ordre exact ou elles ont ete donnees.",
"Je progresse etape par etape, en terminant une partie avant de passer a la suivante.",
"Pour resoudre un probleme, j'applique d'abord les methodes apprises et connues.",
"Quand une explication est longue et detaillee, je perds le fil et je ne sais plus quel etait le point principal.",
"Quand on me donne une consigne complexe, j'oublie parfois une partie ou je melange les etapes.",
"Quand on me demande quelque chose de precis, je l'execute exactement comme cela a ete dit, meme si cela parait inhabituel."
],
"D2 - Sensorialite":[
"Dans une cantine bruyante, les conversations et les bruits se melangent et je n'arrive plus a suivre mon interlocuteur.",
"Une couture ou une etiquette de vetement peut m'empecher de le porter.",
"Apres un moment dans une piece eclairee au neon, je me sens fatigue(e) ou irrite(e).",
"Je remarque immediatement un changement minime de gout ou d'odeur dans un aliment.",
"Apres une journee en ville, j'ai besoin de silence pour retrouver mon equilibre.",
"Quand plusieurs personnes parlent en meme temps, je perds le fil de la discussion.",
"Pour me sentir bien, j'ai parfois besoin de musique forte, de bouger ou de rechercher des sensations intenses.",
"Quand une porte claque, je sursaute fortement, parfois avec une reaction physique marquee.",
"Une odeur persistante peut me rester longtemps en tete.",
"Dans un repas ou une soiree animee, je remarque le bruit et la lumiere, mais je m'y adapte sans gene particuliere."
],
"D3 - Attention et concentration":[
"Quand je travaille, un bruit soudain me detourne et je perds le fil de ce que je faisais.",
"Quand je parle avec quelqu'un, un detail declenche des associations d'idees tout en continuant la conversation.",
"Quand je lis, je peux interrompre et reprendre plus tard sans difficulte.",
"Enfant, j'oubliais mes devoirs ou je les laissais inacheves malgre mes efforts.",
"Quand une activite me passionne, je peux oublier de manger ou de dormir.",
"Pendant une reunion, j'ecoute tout en preparant une idee parallele a presenter.",
"Quand je cuisine, je reste attentif(ve) et je reprends sans effort apres une interruption.",
"En conversation, je decroche parfois en plein milieu d'une phrase.",
"En cours, je comprends vite puis je decroche par ennui.",
"Quand on me donne une consigne claire, je la suis jusqu'au bout et je reprends facilement apres une interruption."
],
"D4 - Cognition sociale et communication":[
"Quand on me dit 'reviens dans 5 minutes', je prends cela au mot pres et je suis contrarie(e) si ce n'est pas respecte.",
"Quand quelqu'un ne tient pas sa parole, je le vis comme un manquement a une valeur.",
"Quand on me dit 'reviens dans 5 minutes', je comprends que cela signifie 'un peu plus tard'.",
"Je prends souvent les phrases au pied de la lettre et l'ironie m'echappe.",
"Apres une soiree, je repense longtemps aux conversations.",
"Dans un diner, je comprends les sous-entendus et je passe a autre chose.",
"Si une regle sociale n'est pas respectee (prevenir d'un retard), je ressens une gene importante.",
"Une blague a double sens peut me destabiliser.",
"Je prefere discuter en petit comite qu'en grand groupe.",
"Je participe avec aise a des conversations legeres."
],
"D5 - Emotions et regulation":[
"Une remarque peut rester longtemps dans mon esprit.",
"Face a une injustice, ma reaction est immediate et intense.",
"Une emotion forte m'empeche parfois d'agir ou de reflechir clairement.",
"Mon stress s'exprime physiquement (maux de ventre, tensions, migraines).",
"Quand un ami est triste, je ressens son emotion dans mon corps.",
"Mon humeur peut changer brutalement dans la journee.",
"Apres une dispute, je revis la scene longtemps dans ma tete.",
"Apres une rencontre sociale, j'ai besoin de temps seul(e) pour recuperer.",
"Dans certaines situations, j'ai du mal a identifier clairement mon emotion.",
"Apres une contrariete, j'arrive a passer vite a autre chose."
],
"D6 - Creativite et intuition":[
"En marchant ou en conduisant, une solution complete peut surgir sans effort.",
"En rencontrant quelqu'un, j'ai une impression immediate de sa personnalite.",
"Quand je cherche une idee, je relie spontaneament des domaines tres differents.",
"Mon imagination produit facilement des images ou des histoires detaillees.",
"Mes reves sont longs et tres clairs, comme un film.",
"En entrant dans un lieu, je ressens parfois une ambiance particuliere.",
"J'invente facilement une nouvelle maniere d'accomplir une tache.",
"Pour decider, je sens parfois un 'oui' ou un 'non' interieur evident.",
"Je commence souvent par appliquer une methode connue et eprouvee.",
"Quand on me demande une solution, je propose d'abord ce qui me parait logique et deja teste."
],
"D7 - Double exceptionnelite":[
"Je reussis un exercice complexe mais j'echoue parfois sur une tache simple.",
"Mes notes ou resultats varient beaucoup selon les domaines.",
"On m'a decrit comme 'brillant(e) mais inconstant(e)'.",
"Meme apres une reussite, je doute d'etre vraiment competent(e).",
"Je depense beaucoup d'energie pour compenser certaines difficultes.",
"Mes forces cachent mes fragilites, ou l'inverse.",
"Apres une journee d'efforts, je me sens epuise(e) mentalement.",
"Mon parcours alterne periodes de grande reussite et d'echec marque.",
"J'ai parfois ete mal oriente(e) car on a juge une partie de mon profil seulement.",
"On me percoit parfois comme exceptionnel(le), parfois comme en difficulte, selon le contexte."
],
"D8 - Temporalite et rythmes":[
"Je fais souvent mes taches a la derniere minute et je reussis dans l'urgence.",
"Absorbe(e) par une activite, je perds completement la notion du temps.",
"Je prefere avancer sur plusieurs projets en parallele plutot que d'en finir un seul.",
"Un changement de programme de derniere minute me perturbe longtemps.",
"J'alterne entre periodes de grande activite et moments ou je n'arrive plus a avancer.",
"J'ai du mal a estimer le temps que prendra une tache et je suis souvent en retard.",
"Quand j'ai de l'avance, je perds la motivation et j'attends le moment de l'urgence.",
"Dans une reunion, je comprends la conclusion avant la fin et je m'impatiente.",
"Quand on me donne une consigne simple avec un debut et une fin clairs, je l'execute sans me disperser.",
"Je m'adapte sans difficulte a une routine stable avec des horaires fixes."
]
}

# ----------------------------- Utils -----------------------------
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
    title = f"Profil en etoile – {patient_name}\n" + " | ".join(title_lines)
    plt.title(title, fontsize=10, pad=20)
    fig.tight_layout()
    return fig

def interpret_profile(df):
    scores = dict(zip(df["Dimension"], df["Score"]))
    out = []

    d1 = scores.get("D1 - Traitement de l'information", scores.get("D1 - Traitement de l’information", 0))
    d2 = scores.get("D2 - Sensorialite", scores.get("D2 - Sensorialité", 0))
    d3 = scores.get("D3 - Attention et concentration", 0)
    d4 = scores.get("D4 - Cognition sociale et communication", 0)
    d5 = scores.get("D5 - Emotions et regulation", scores.get("D5 - Émotions et régulation", 0))
    d6 = scores.get("D6 - Creativite et intuition", scores.get("D6 - Créativité et intuition", 0))
    d7 = scores.get("D7 - Double exceptionnelite", scores.get("D7 - Double exceptionnalité", 0))
    d8 = scores.get("D8 - Temporalite et rythmes", scores.get("D8 - Temporalité et rythmes", 0))

    # HPI
    if (d1 >= 20) and (d6 >= 28) and (d5 >= 24) and (d4 >= 20):
        out.append("🟣 Profil compatible HPI : pensee associative, creativite intuitive, intensite emotionnelle et exigence de valeurs.")

    # TDAH
    if d3 >= 24:
        out.append("🟠 Profil compatible TDAH : difficultes attentionnelles persistantes avec impact fonctionnel (oublis, taches inachevees).")

    # TSA
    if (d4 >= 24) and (d2 >= 24):
        out.append("🔵 Profil compatible TSA : literalite sociale et/ou sensibilite sensorielle elevee.")

    # 2E
    if (d7 >= 24) and ((d1 >= 28) or (d6 >= 28) or (d5 >= 28)):
        out.append("🟢 Profil compatible 2E (double exceptionnalite) : coexistence de forces marquees et de difficultes importantes.")

    # NT
    if all(v <= 15 for v in [d1, d2, d3, d4, d5, d6, d7, d8]):
        out.append("⚪ Profil compatible Neurotypique (NT) : equilibre attentionnel, emotionnel et sensoriel sans particularite marquee.")

    if not out:
        out.append("Profil nuance : aucune orientation claire unique. Interpretez cliniquement et croisez avec l'anamnese / l'historique.")
    return out

def show_results(df_scores):
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
        st.subheader("Vision en etoile (Radar)")
        fig = plot_radar(df_scores)
        st.pyplot(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        st.download_button("⬇️ Télécharger le radar (PNG)",
                           data=buf.getvalue(),
                           file_name=f"radar_{patient_name.replace(' ','_')}.png",
                           mime="image/png")
    st.subheader("🧾 Interpretation automatique")
    for t in interpret_profile(df_scores):
        st.markdown(t)

# ----------------------------- Mode: Import CSV -----------------------------
if mode == "Importer un CSV de scores":
    st.info("Importez un fichier CSV avec les colonnes: Dimension, Score, Max.")
    uploaded = st.file_uploader("Importer un fichier de scores (CSV)", type="csv")
    if uploaded is not None:
        try:
            df_scores = pd.read_csv(uploaded)
            need_cols = {"Dimension","Score","Max"}
            if not need_cols.issubset(df_scores.columns):
                st.error("Le CSV doit contenir les colonnes: Dimension, Score, Max.")
            else:
                show_results(df_scores)
        except Exception as e:
            st.error(f"Erreur de lecture du CSV: {e}")

# ----------------------------- Mode: Questionnaire -----------------------------
if mode == "Questionnaire":
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

    if submitted:
        df_scores = compute_dimension_scores(all_scores)
        show_results(df_scores)

st.markdown("---")
st.caption("⚠️ Outil d'orientation clinique. Ce questionnaire n'est pas un diagnostic.")
