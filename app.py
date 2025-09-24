# --- Interpretation automatique (version robuste) ---
def interpret_profile(df):
    scores = dict(zip(df["Dimension"], df["Score"]))
    out = []

    d1 = scores.get("D1 - Traitement de l’information", 0)
    d2 = scores.get("D2 - Sensorialité", 0)
    d3 = scores.get("D3 - Attention et concentration", 0)
    d4 = scores.get("D4 - Cognition sociale et communication", 0)
    d5 = scores.get("D5 - Émotions et régulation", 0)
    d6 = scores.get("D6 - Créativité et intuition", 0)
    d7 = scores.get("D7 - Double exceptionnalité", 0)
    d8 = scores.get("D8 - Temporalité et rythmes", 0)

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
    if all(v <= 15 for v in [d1,d2,d3,d4,d5,d6,d7,d8]()
