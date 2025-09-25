import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io, os, re, random, string, smtplib, ssl
from email.message import EmailMessage
from datetime import datetime

# ----------------------------- Config -----------------------------
st.set_page_config(page_title="Préquestionnaire Neurodiversité", layout="wide")
DEFAULT_PRACTITIONER_EMAIL = "BeatriceMilletre@gmail.com"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.title("Préquestionnaire de Neurodiversité")
st.caption("Deux parcours : 📝 Passer le test | 🔑 Accès praticien")

# ----------------------------- Utils -----------------------------
def gen_code(n=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def sanitize_filename(name: str):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)

def save_artifacts(code: str, df_scores: pd.DataFrame, md_text: str):
    base = os.path.join(DATA_DIR, sanitize_filename(code))
    csv_path = base + ".csv"
    md_path  = base + ".md"
    df_scores.to_csv(csv_path, index=False)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    return csv_path, md_path

def try_send_email(to_email: str, subject: str, body: str):
    # Try SMTP via Streamlit secrets (recommended)
    # Expected st.secrets keys:
    # email.host, email.port, email.username, email.password, email.use_tls (true/false)
    try:
        email_conf = st.secrets.get("email", None)
    except Exception:
        email_conf = None

    if not email_conf:
        return False, "Configuration e-mail absente (st.secrets['email']). E-mail non envoyé."

    host = email_conf.get("host")
    port = int(email_conf.get("port", 587))
    username = email_conf.get("username")
    password = email_conf.get("password")
    use_tls = str(email_conf.get("use_tls", "true")).lower() in ["1","true","yes"]

    if not (host and port and username and password):
        return False, "Configuration e-mail incomplète. E-mail non envoyé."

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=context)
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(host, port) as server:
                server.login(username, password)
                server.send_message(msg)
        return True, "E-mail envoyé."
    except Exception as e:
        return False, f"E-mail non envoyé : {e}"

def compute_dimension_scores(all_scores):
    rows = []
    for dim, scores in all_scores.items():
        total = int(np.sum(scores))
        rows.append({"Dimension": dim, "Score": total, "Max": 40})
    return pd.DataFrame(rows)

def plot_radar(df, patient_name):
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
    title = f"Profil en étoile – {patient_name}\n" + " | ".join(title_lines)
    plt.title(title, fontsize=10, pad=20)
    fig.tight_layout()
    return fig

def interpret_profile(df):
    scores = dict(zip(df["Dimension"], df["Score"]))
    # Clés tolérantes aux accents
    d1 = scores.get("D1 - Traitement de l'information", scores.get("D1 - Traitement de l’information", 0))
    d2 = scores.get("D2 - Sensorialite", scores.get("D2 - Sensorialité", 0))
    d3 = scores.get("D3 - Attention et concentration", 0)
    d4 = scores.get("D4 - Cognition sociale et communication", 0)
    d5 = scores.get("D5 - Emotions et regulation", scores.get("D5 - Émotions et régulation", 0))
    d6 = scores.get("D6 - Creativite et intuition", scores.get("D6 - Créativité et intuition", 0))
    d7 = scores.get("D7 - Double exceptionnelite", scores.get("D7 - Double exceptionnalité", 0))
    d8 = scores.get("D8 - Temporalite et rythmes", scores.get("D8 - Temporalité et rythmes", 0))

    out = []
    if (d1 >= 20) and (d6 >= 28) and (d5 >= 24) and (d4 >= 20):
        out.append("🟣 Profil compatible HPI : pensée associative, créativité intuitive, intensité émotionnelle et exigence de valeurs.")
    if d3 >= 24:
        out.append("🟠 Profil compatible TDAH : difficultés attentionnelles persistantes avec impact fonctionnel (oublis, tâches inachevées).")
    if (d4 >= 24) and (d2 >= 24):
        out.append("🔵 Profil compatible TSA : littéralité sociale et/ou sensibilité sensorielle élevée.")
    if (d7 >= 24) and ((d1 >= 28) or (d6 >= 28) or (d5 >= 28)):
        out.append("🟢 Profil compatible 2E (double exceptionnalité) : coexistence de forces marquées et de difficultés importantes.")
    if all(v <= 15 for v in [d1, d2, d3, d4, d5, d6, d7, d8]):
        out.append("⚪ Profil compatible Neurotypique (NT) : équilibre attentionnel, émotionnel et sensoriel sans particularité marquée.")
    if not out:
        out.append("Profil nuancé : aucune orientation claire unique. Interprétation clinique nécessaire.")
    return out

def build_markdown_report(code, patient_name, df_scores):
    lines = []
    lines.append(f"# Préquestionnaire de Neurodiversité — Rapport")
    lines.append(f"- **Code** : `{code}`")
    lines.append(f"- **Patient** : {patient_name}")
    lines.append(f"- **Date** : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## Scores par dimension (/40)")
    for _, r in df_scores.iterrows():
        lines.append(f"- {r['Dimension']} : **{int(r['Score'])}/40**")
    lines.append("")
    lines.append("## Interprétation automatique")
    for t in interpret_profile(df_scores):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("_Outil d'orientation clinique : ce questionnaire n’est pas un diagnostic._")
    return "\n".join(lines)

# ----------------------------- Items (D1..D8) -----------------------------
st.sidebar.subheader("Barème réponses")
st.sidebar.write("0 = Jamais | 1 = Rarement | 2 = Parfois | 3 = Souvent | 4 = Toujours")

patient_name = st.sidebar.text_input("Nom / identifiant (peut être anonymisé)", value="Patient A")

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

# ----------------------------- UI: parcours -----------------------------
parcours = st.radio("Choisir un parcours :", ["📝 Passer le test", "🔑 Accès praticien"], horizontal=True)

# ============================= 📝 PASSER LE TEST =============================
if parcours == "📝 Passer le test":
    practitioner_email = st.text_input("E-mail du praticien", value=DEFAULT_PRACTITIONER_EMAIL)
    all_scores = {}

    with st.form("form_test"):
        for dim, items in dimensions.items():
            with st.expander(dim, expanded=False):
                dim_scores = []
                for i, item in enumerate(items, start=1):
                    s = st.slider(f"{i}. {item}", min_value=0, max_value=4, value=0, step=1, key=f"{dim}_{i}")
                    dim_scores.append(s)
                all_scores[dim] = dim_scores
        submitted = st.form_submit_button("Envoyer")

    if submitted:
        df_scores = compute_dimension_scores(all_scores)
        code = gen_code()
        md_text = build_markdown_report(code, patient_name, df_scores)
        csv_path, md_path = save_artifacts(code, df_scores, md_text)

        # envoyez e-mail (si config)
        subject = f"[Préquestionnaire] Nouveau résultat – Code {code}"
        body = (f"Bonjour,\n\nUn répondreur vient de terminer le préquestionnaire.\n\n"
                f"- Code : {code}\n- Patient : {patient_name}\n- Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Vous pouvez récupérer le rapport (.md) et le CSV dans l'onglet 'Accès praticien' en entrant le code.\n\n"
                f"(Sur ce déploiement de test, les fichiers ont été enregistrés côté serveur dans le dossier '{DATA_DIR}/')\n")
        ok, msg = try_send_email(practitioner_email, subject, body)

        # BANNERS
        if ok:
            st.success("📧 E-mail envoyé au praticien.")
        else:
            st.warning("E-mail non envoyé automatiquement.")
            with st.expander("Voir le message e-mail à copier-coller", expanded=False):
                st.code(f"À: {practitioner_email}\nObjet: {subject}\n\n{body}")

        st.info(f"💾 Résultats enregistrés avec le code **{code}**.")
        st.caption("Le praticien peut accéder au rapport et au CSV via l'onglet 'Accès praticien'.")

# ============================= 🔑 ACCÈS PRATICIEN =============================
if parcours == "🔑 Accès praticien":
    code_in = st.text_input("Entrer le code")
    if st.button("Récupérer"):
        base = os.path.join(DATA_DIR, sanitize_filename(code_in))
        csv_path = base + ".csv"
        md_path  = base + ".md"
        if os.path.exists(csv_path) and os.path.exists(md_path):
            df_scores = pd.read_csv(csv_path)
            st.subheader("Scores par dimension")
            st.dataframe(df_scores, use_container_width=True)

            st.subheader("Vision en étoile (Radar)")
            fig = plot_radar(df_scores, patient_name=f"Code {code_in}")
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
            st.download_button("⬇️ Télécharger le radar (PNG)", data=buf.getvalue(),
                               file_name=f"radar_{code_in}.png", mime="image/png")

            with open(csv_path, "rb") as f:
                st.download_button("⬇️ Télécharger le CSV", data=f, file_name=f"{os.path.basename(csv_path)}", mime="text/csv")
            with open(md_path, "rb") as f:
                st.download_button("⬇️ Télécharger le rapport (.md)", data=f, file_name=f"{os.path.basename(md_path)}", mime="text/markdown")

            st.subheader("🧾 Interprétation automatique")
            for t in interpret_profile(df_scores):
                st.markdown(f"- {t}")
        else:
            st.error("Code introuvable. Vérifiez le code ou attendez que l’enregistrement soit terminé.")
            
st.markdown("---")
st.caption("⚠️ Confidentialité : ce prototype enregistre les résultats sur le disque de l'application (dossier 'data/'). "
           "Sur Streamlit Cloud, ce stockage est temporaire. Pour un stockage pérenne, configurez une base (ex. Google Sheet, Supabase) et un e-mail via st.secrets.")
