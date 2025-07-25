
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import tempfile
import os
from fpdf import FPDF
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="ScanSanté", page_icon="💊", layout="centered")

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("ScanSante_dataset.csv")

data = load_data()

# En-tête
st.markdown("<h1 style='color:#2E8BC0;'>💊 ScanSanté</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#145DA0;'>Analyse intelligente d'ordonnances médicales à partir d'une image</p>", unsafe_allow_html=True)
st.divider()

# Téléversement d'image
uploaded_file = st.file_uploader("📸 Importer une image de l'ordonnance", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='🖼️ Ordonnance Importée', use_column_width=True)

    with st.spinner("🔍 Analyse du texte..."):
        text = pytesseract.image_to_string(image, lang="fra")
        st.success("✅ Texte extrait avec succès")
        st.text_area("📝 Texte détecté :", text, height=200)

        # Recherche de maladies et suggestions
        results = []
        for index, row in data.iterrows():
            if row["Maladie ou symptôme"].lower() in text.lower():
                results.append((row["Maladie ou symptôme"], row["Médicaments recommandés"]))

        if results:
            st.markdown("### 💡 Médicaments suggérés :")
            for maladie, meds in results:
                st.markdown(f"<div style='background-color:#DFF6FF;padding:10px;border-radius:10px;margin-bottom:5px;'>"
                            f"<strong>{maladie.capitalize()}</strong> ➜ <span style='color:#2C7865;'>{meds}</span>"
                            f"</div>", unsafe_allow_html=True)

            # Génération du rapport PDF
            if st.button("📄 Générer un rapport PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Rapport ScanSanté", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                pdf.ln(10)
                pdf.multi_cell(0, 10, f"Texte extrait de l'ordonnance :\n{text}")
                pdf.ln(5)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Médicaments suggérés :", ln=True)
                pdf.set_font("Arial", "", 12)
                for maladie, meds in results:
                    pdf.multi_cell(0, 10, f"{maladie.capitalize()} ➜ {meds}")
                    pdf.ln(1)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                    pdf.output(tmpfile.name)
                    st.success("📄 Rapport généré avec succès !")
                    st.download_button(label="📥 Télécharger le PDF",
                                       data=open(tmpfile.name, "rb").read(),
                                       file_name="rapport_scan_sante.pdf",
                                       mime="application/pdf")
        else:
            st.warning("Aucune maladie connue n'a été détectée.")
else:
    st.info("Veuillez importer une image pour commencer l'analyse.")
