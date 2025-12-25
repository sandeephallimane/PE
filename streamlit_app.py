import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(page_title="PDF Table Extractor", layout="wide")

st.title("📊 PDF Table Extractor & Previewer")
st.write("Upload your PDF to view and extract tables into Excel.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF..."):
        all_tables = []
        
        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                
                for j, table in enumerate(tables):
                    # Process the table into a clean DataFrame
                    df = pd.DataFrame(table)
                    # Use first row as header and remove it from data
                    df.columns = df.iloc[0]
                    df = df[1:].reset_index(drop=True)
                    
                    all_tables.append(df)
                    
                    # --- DATA PREVIEW SECTION ---
                    st.subheader(f"Table {len(all_tables)} (Page {i+1})")
                    st.dataframe(df, use_container_width=True) 
                    # ----------------------------

        if all_tables:
            # Create the Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for idx, table_df in enumerate(all_tables):
                    table_df.to_excel(writer, sheet_name=f'Table_{idx+1}', index=False)
            
            st.divider()
            st.success(f"Successfully found {len(all_tables)} tables!")
            
            # Centered Download Button
            st.download_button(
                label="📥 Download All Tables as Excel",
                data=output.getvalue(),
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Click here to download the tables shown above."
            )
        else:
            st.warning("No tables were detected. Ensure the PDF contains structured grid data.")
