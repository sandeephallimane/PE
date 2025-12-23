import streamlit as st
import pandas as pd
import pdfplumber
import tempfile
import os

st.set_page_config(page_title="PDF Table to Excel", layout="centered")

st.title("📊 PDF Table → Excel")
st.caption("Extracts ONLY tables (Streamlit Cloud compatible)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                if not df.empty:
                    tables.append(df)

    if not tables:
        st.warning("No tables found.")
    else:
        st.success(f"✅ {len(tables)} tables extracted")

        for i, df in enumerate(tables, start=1):
            st.subheader(f"Table {i}")
            st.dataframe(df)

        excel_path = pdf_path.replace(".pdf", ".xlsx")
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for i, df in enumerate(tables, start=1):
                df.to_excel(writer, sheet_name=f"Table_{i}", index=False)

        with open(excel_path, "rb") as f:
            st.download_button(
                "⬇️ Download Excel",
                data=f,
                file_name="tables_only.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    os.remove(pdf_path)
