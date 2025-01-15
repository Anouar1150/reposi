import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Application de Cotation", layout="centered")

# Initialisation de la session
if "posts" not in st.session_state:
    st.session_state["posts"] = {}  # Dictionnaire des postes
if "selected_post" not in st.session_state:
    st.session_state["selected_post"] = None  # Poste sélectionné
if "selected_operation" not in st.session_state:
    st.session_state["selected_operation"] = None  # Opération sélectionnée
if "timing" not in st.session_state:
    st.session_state["timing"] = {}  # Chronométrage des opérations

# Titre de l'application
st.title("Application de Cotation - Gestion des Opérations et Postures")

# Section 1 : Ajouter un poste
st.header("Ajouter un nouveau poste")
col1, col2 = st.columns(2)

with col1:
    department = st.text_input("Département")
    workshop = st.text_input("Atelier")
    uet = st.text_input("UET")
    position_name = st.text_input("Nom du poste")

with col2:
    ergonome = st.text_input("Ergonome")
    date = st.date_input("Date")
    cycle_time = st.number_input("Temps de cycle (cmin)", min_value=1, step=1)
    frequency = st.number_input("Fréquence horaire globale", min_value=1, step=1)

if st.button("Ajouter le poste"):
    if all([department, workshop, uet, position_name, ergonome, date, cycle_time, frequency]):
        st.session_state["posts"][position_name] = {
            "Département": department,
            "Atelier": workshop,
            "UET": uet,
            "Nom du poste": position_name,
            "Ergonome": ergonome,
            "Date": str(date),
            "Temps de cycle (cmin)": cycle_time,
            "Fréquence horaire globale": frequency,
            "Opérations": {},  # Dictionnaire pour les opérations
        }
        st.success(f"Le poste '{position_name}' a été ajouté avec succès.")
    else:
        st.error("Veuillez remplir tous les champs.")

# Section 2 : Sélectionner un poste
st.header("Sélectionner un poste")
if st.session_state["posts"]:
    selected_post_key = st.selectbox("Choisissez un poste :", list(st.session_state["posts"].keys()))

    if st.button("Sélectionner ce poste"):
        st.session_state["selected_post"] = st.session_state["posts"][selected_post_key]
        st.success(f"Le poste '{selected_post_key}' a été sélectionné.")
else:
    st.write("Aucun poste disponible. Veuillez en ajouter un.")

# Section 3 : Gestion des opérations et des postures
if st.session_state["selected_post"]:
    selected_post = st.session_state["selected_post"]
    st.header(f"Gestion des Opérations pour le Poste : {selected_post['Nom du poste']}")

    # Ajout d'une opération
    operation = st.text_input("Saisissez une opération :", key="operation_input")
    if st.button("Ajouter l'opération"):
        if operation:
            if operation not in selected_post["Opérations"]:
                selected_post["Opérations"][operation] = {"Postures": [], "Durées": [], "Effort": {}}
                st.success(f"L'opération '{operation}' a été ajoutée.")
            else:
                st.warning(f"L'opération '{operation}' existe déjà.")
        else:
            st.error("Veuillez entrer une opération avant de valider.")

    # Affichage des opérations disponibles
    st.subheader("Opérations disponibles")
    for operation_name in selected_post["Opérations"].keys():
        if st.button(f"Opération : {operation_name}"):
            st.session_state["selected_operation"] = operation_name
            st.success(f"Vous avez sélectionné l'opération '{operation_name}'.")

    # Gestion des postures et ajout de l'effort
    if st.session_state["selected_operation"]:
        selected_operation = st.session_state["selected_operation"]
        st.header(f"Gestion des Postures et de l'Effort pour l'Opération : {selected_operation}")

        # Affichage des postures sous forme de colonnes
        st.subheader("Sélectionnez une posture")

        # Groupes de postures
        postures = {
            "A": ["A1", "A2", "A3", "A4", "A5"],
            "B": ["B1", "B2", "B3", "B4", "B5"],
            "C": ["C1", "C2", "C3", "C4", "C5"],
            "D": ["D1", "D2", "D3", "D4", "D5"],
            "E": ["E1", "E4", "E5"],
            "F": ["F1", "F2", "F3", "F4", "F5"],
            "G": ["G1", "G2", "G3", "G4", "G5"],
            "H": ["H1", "H3", "H4", "H5"],
            "K": ["K3", "K4", "K5"],
        }

        # Création d'une colonne par groupe
        cols = st.columns(len(postures))  # Une colonne par clé du dictionnaire

        for col, (group_name, posture_list) in zip(cols, postures.items()):
            with col:
                st.write(f"**{group_name}**")  # Nom du groupe (A, B, C...)
                for posture in posture_list:
                    if st.button(posture, key=f"posture_{posture}"):
                        if posture not in selected_post["Opérations"][selected_operation]["Postures"]:
                            selected_post["Opérations"][selected_operation]["Postures"].append(posture)
                            st.success(f"Posture '{posture}' ajoutée à l'opération '{selected_operation}'.")
                        else:
                            st.warning(f"Posture '{posture}' existe déjà pour cette opération.")


        # Ajout de l'effort
        st.subheader("Documenter l'Effort")
        effort_description = st.text_input("Description de l'effort :", key="effort_description")
        effort_weight = st.number_input("Poids de la pièce (kg) :", min_value=0.0, step=0.1, key="effort_weight")
        if st.button("Ajouter l'effort"):
            if effort_description or effort_weight > 0:
                selected_post["Opérations"][selected_operation]["Effort"] = {
                    "Description": effort_description,
                    "Poids (kg)": effort_weight,
                }
                st.success(f"Effort documenté : {effort_description} - Poids : {effort_weight} kg.")
            else:
                st.error("Veuillez renseigner une description ou un poids valide.")

    # Chronométrage des opérations
    st.header("Chronométrage des opérations")
    st.subheader("Démarrer/Arrêter le chronométrage")
    for operation_name, operation_data in selected_post["Opérations"].items():
        is_running = operation_name in st.session_state["timing"]
        if st.button(f"Démarrer/Arrêter : {operation_name}", key=f"toggle_{operation_name}"):
            if is_running:
                # Arrêter le chronométrage
                start_time = st.session_state["timing"].pop(operation_name)
                duration = (datetime.now() - start_time).total_seconds()
                operation_data["Durées"].append({
                    "Début": start_time,
                    "Fin": datetime.now(),
                    "Durée (s)": duration,
                })
                st.success(f"Chronométrage arrêté pour '{operation_name}'. Durée : {round(duration, 2)} secondes.")
            else:
                # Démarrer le chronométrage
                st.session_state["timing"][operation_name] = datetime.now()
                st.success(f"Chronométrage démarré pour '{operation_name}'.")

# Section 4 : Visualisation chronologique
st.header("Visualisation Chronologique")
if st.session_state["selected_post"] and any("Durées" in op for op in st.session_state["selected_post"]["Opérations"].values()):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Préparer les données pour le graphique
    start_times = []
    end_times = []
    operations = []
    postures = []
    efforts = []
    durations = []
    for operation_name, operation_data in st.session_state["selected_post"]["Opérations"].items():
        if "Durées" in operation_data:
            for timing in operation_data["Durées"]:
                start_times.append(timing["Début"])
                end_times.append(timing["Fin"])
                operations.append(operation_name)
                postures.append(", ".join(operation_data.get("Postures", [])))
                effort = operation_data.get("Effort", {})
                efforts.append(f"{effort.get('Description', '')} ({effort.get('Poids (kg)', 0)} kg)")
                durations.append(round(timing["Durée (s)"], 2))

    # Ajouter les traits au graphique
    for i, (start, end) in enumerate(zip(start_times, end_times)):
        ax.hlines(y=operations[i], xmin=start, xmax=end, color="blue", linewidth=2)
        # Texte avec posture, effort et durée
        ax.text(
            start + (end - start) / 2, operations[i],
            f"{postures[i]}\n{efforts[i]}\nDurée : {durations[i]} s",
            ha="center", va="bottom", fontsize=9, color="black"
        )

    # Configuration du graphique
    ax.set_xlabel("Temps")
    ax.set_ylabel("Opérations")
    ax.set_title("Chronologie des Opérations")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("Aucune durée enregistrée pour générer le graphique.")
