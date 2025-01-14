import streamlit as st
import pandas as pd
import time
from io import BytesIO
import sqlite3

st.set_page_config(
    page_title="Application M2E",
    layout="centered",  # ou "wide" selon vos préférences
    initial_sidebar_state="collapsed"
)


# Initialisation des données dans st.session_state
if "posts" not in st.session_state:
    st.session_state["posts"] = {}  # Dictionnaire pour stocker les données par poste
if "selected_post" not in st.session_state:
    st.session_state["selected_post"] = None  # Poste actuellement sélectionné
if "timing" not in st.session_state:
    st.session_state["timing"] = {}  # Chronométrage actif des sous-opérations

# Titre de l'application
st.title("Cotation M2E")

# Étape 1 : Gestion des postes
st.header("1. Gestion des Postes")

# Ajouter un poste
with st.form("add_post"):
    departement = st.text_input("Département :")
    atelier = st.text_input("Atelier :")
    uet = st.text_input("UET :")
    poste = st.text_input("Poste :")
    ergonome = st.text_input("Ergonome :")
    date = st.date_input("Date :")
    temps_cycle = st.number_input("Temps de cycle (cmin) :", min_value=1, step=1)
    frequence_horaire = st.number_input("Fréquence horaire globale :", min_value=1, step=1)

    submitted = st.form_submit_button("Ajouter le poste")
    if submitted:
        if all([departement, atelier, uet, poste, ergonome, date, temps_cycle, frequence_horaire]):
            post_data = {
                "Département": departement,
                "Atelier": atelier,
                "UET": uet,
                "Poste": poste,
                "Ergonome": ergonome,
                "Date": str(date),
                "Temps de cycle (cmin)": temps_cycle,
                "Fréquence horaire globale": frequence_horaire,
                "Sous-opérations": [],  # Liste des sous-opérations pour ce poste
            }
            st.session_state["posts"][poste] = post_data
            st.success(f"Le poste '{poste}' a été ajouté.")
        else:
            st.error("Veuillez remplir tous les champs.")

# Sélection d'un poste
if st.session_state["posts"]:
    st.header("2. Sélection du Poste")
    selected_post_name = st.selectbox("Choisissez un poste à coter :", list(st.session_state["posts"].keys()))

    if st.button("Sélectionner le poste"):
        st.session_state["selected_post"] = st.session_state["posts"][selected_post_name]
        st.success(f"Le poste '{selected_post_name}' a été sélectionné pour la cotation.")

# Étape 3 : Gestion des sous-opérations
if st.session_state["selected_post"]:
    selected_post = st.session_state["selected_post"]
    st.header(f"3. Cotation du Poste : {selected_post['Poste']}")

    operations = {
        "Assembler à la main": ["Prévisser", "Emmancher/clipser", "Indexer"],
        "Assembler avec l'aide d'un outil": ["Visser", "Prévisser et visser", "Riveter", "Goujonner", "Coller et/ou mastiquer"],
        "Manutentionner BR / Chariot / Bac": ["Manutentionner BR", "Pousser Chariot Kit", "Déposer bac", "Plier bac odette", "Déposer intercalaire"],
        "Manutentionner Pièce / Gabarit": ["Déposer pièce", "Déposer pièce assemblée", "Déposer pièce avec assistance", "Déposer pièce à 2 opérateurs",
                                           "Retourner pièce", "Basculer pièce", "Déposer un gabarit", "Déposer une coiffe"],
        "Souder Pince manuel SR": ["Appui boutons", "Pince TI en X", "Pince TI en J", "Prendre pince et souder x pts", 
                                    "Dégager / Engager et souder x pts", "Dégager avec rotation et souder x pts", 
                                    "Dégager avec basculement et souder x pts", "Déplacer pince et souder x pts", "Accrocher pince"],
        "Autre": []
    }

    operation = st.selectbox("Choisissez une opération principale :", [""] + list(operations.keys()))
    sous_operation = None

    if operation:
        if operation == "Autre":
            sous_operation = st.text_input("Entrez une sous-opération personnalisée :")
        else:
            sous_operation = st.selectbox("Choisissez une sous-opération :", [""] + operations[operation])


    if sous_operation and st.button("Ajouter la sous-opération"):
        sous_op_data = {
            "Sous-opération": sous_operation,
            "Durée": 0,  # Initialiser la durée pour cette sous-opération
            "Postures": [],  # Initialiser les postures pour cette sous-opération
            "Effort (kg)": 0,  # Initialiser l'effort
            "Pondération": "",  # Pondération vide par défaut
            "Fréquence posture (/h)": 0,  # Fréquence réelle pour les postures
            "Fréquence effort (/h)": 0,  # Fréquence réelle pour les efforts
        }
        if sous_op_data not in selected_post["Sous-opérations"]:
            selected_post["Sous-opérations"].append(sous_op_data)
            st.success(f"La sous-opération '{sous_operation}' a été ajoutée au poste '{selected_post['Poste']}'.")
        else:
            st.warning(f"La sous-opération '{sous_operation}' existe déjà pour ce poste.")

    # Gérer les sous-opérations existantes
    st.write("### Sous-opérations enregistrées")
    for i, sous_op_data in enumerate(selected_post["Sous-opérations"]):
        sous_op = sous_op_data["Sous-opération"]
        st.write(f"#### {sous_op}")

        # Gestion des postures
        postures = st.multiselect(
            f"Postures pour '{sous_op}' :",
            options=["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5",
                     "C1", "C2", "C3", "C4", "C5", "D1", "D2", "D3", "D4", "D5",
                     "E1", "E4", "E5", "F1", "F2", "F3", "F4", "F5", "G1", "G2", "G3", "G4",
                     "H1", "H3", "H4", "H5", "K3", "K4", "K5"],
            #default=sous_op_data.get("Postures", []),
            key=f"postures_{selected_post['Poste']}_{i}"
        )
        # Mise à jour immédiate de sous_op_data avec les nouvelles postures
        sous_op_data["Postures"] = postures
        
        repetitions_postures = st.number_input(
            f"Répétitions pour les postures '{sous_op}' :",
            min_value=1,
            value=1,
            step=1,
            key=f"repetitions_posture_{selected_post['Poste']}_{i}"
        )
        sous_op_data["Fréquence posture (/h)"] = repetitions_postures * selected_post["Fréquence horaire globale"]
        sous_op_data["Postures"] = postures

        # Gestion de l'effort
        effort = st.number_input(
            f"Effort (kg) pour '{sous_op}' :",
            min_value=0.0,
            value=float(sous_op_data.get("Effort (kg)", 0.0)),
            step=0.1,
            key=f"effort_{selected_post['Poste']}_{i}"
        )
        repetitions_effort = st.number_input(
            f"Répétitions pour les efforts '{sous_op}' :",
            min_value=1,
            value=1,
            step=1,
            key=f"repetitions_effort_{selected_post['Poste']}_{i}"
        )
        sous_op_data["Effort (kg)"] = effort * repetitions_effort
        sous_op_data["Fréquence effort (/h)"] = repetitions_effort * selected_post["Fréquence horaire globale"]

        # Gestion de la pondération
        pondérations = {"M1": 0.5, "M2": 0.7, "M3": 1.5, "M4": 1.5, "M5": 1.5, "M6": 1.5,
                        "M7": 1.5, "M8": 1.5, "M9": 1.5, "M10": 1.5, "M11": 2, "M12": 2}
        pondération = st.selectbox(
            f"Pondération pour '{sous_op}' :",
            options=[""] + list(pondérations.keys()),  # L'option vide est ajoutée au début
            index=0,  # Par défaut, aucune pondération sélectionnée
            key=f"pondération_{selected_post['Poste']}_{i}"
        )
        sous_op_data["Pondération"] = pondération

        # Chronométrage
        if st.button(f"Démarrer/Arrêter : {sous_op}", key=f"toggle_{selected_post['Poste']}_{i}"):
            if sous_op not in st.session_state["timing"]:
                st.session_state["timing"][sous_op] = time.time()
                st.success(f"Le chronomètre pour '{sous_op}' a commencé.")
            else:
                duration = time.time() - st.session_state["timing"][sous_op]
                del st.session_state["timing"][sous_op]
                sous_op_data["Durée"] += duration
                st.success(f"Le chronomètre pour '{sous_op}' a été arrêté. Temps : {round(duration, 2)} cmin.")

    # Résultats pour le poste sélectionné
    st.write("### Résultats pour le poste sélectionné")
    temps_total = sum(op["Durée"] for op in selected_post["Sous-opérations"])
    st.write(f"Temps total des sous-opérations : {round(temps_total, 2)} cmin")

    if temps_total > 0:
        st.write("Temps et pourcentage par sous-opération :")
        for sous_op_data in selected_post["Sous-opérations"]:
            percentage = (sous_op_data["Durée"] / temps_total) * 100 if temps_total > 0 else 0
            st.write(f"- {sous_op_data['Sous-opération']} : {round(sous_op_data['Durée'], 2)} cmin ({round(percentage, 2)} %)")

        engagement = (temps_total / selected_post["Temps de cycle (cmin)"]) * 100
        st.write(f"Engagement de l'opérateur : {round(engagement, 2)} %")

# Exportation des données
st.header("4. Exportation des données")
if st.button("Télécharger toutes les données en Excel"):
    all_data = []
    for post_name, post_data in st.session_state["posts"].items():
        for sous_op_data in post_data["Sous-opérations"]:
            all_data.append({
                "Poste": post_name,
                "Sous-opération": sous_op_data["Sous-opération"],
                "Postures": ", ".join(sous_op_data["Postures"]),
                "Effort total (kg)": sous_op_data["Effort (kg)"],
                "Fréquence posture (/h)": sous_op_data["Fréquence posture (/h)"],
                "Fréquence effort (/h)": sous_op_data["Fréquence effort (/h)"],
                "Pondération": sous_op_data["Pondération"] if sous_op_data["Pondération"] else "Non défini",
                "Temps (cmin)": round(sous_op_data["Durée"], 2)
            })

    df = pd.DataFrame(all_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Cotation")
    st.download_button(
        label="Télécharger le fichier Excel",
        data=output.getvalue(),
        file_name="cotation_postes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )