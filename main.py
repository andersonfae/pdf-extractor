import streamlit as st
import json
import tempfile
from langchain_community.document_loaders.pdf import PyPDFLoader
from extractor import load_config, extract_data_regex, extract_data_with_langchain, validate_data

st.title("PDF-to-Structured-JSON Extractor")
method = st.radio("Selecione o método de extração:", ("Regex", "LangChain"))
uploaded_files = st.file_uploader("Escolha um ou mais arquivos PDF", type="pdf", accept_multiple_files=True)

if st.button("Extrair Dados"):
    if uploaded_files:
        config = load_config()
        all_data = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name
            loader = PyPDFLoader(temp_path)
            pages = loader.load()
            text = "\n".join([page.page_content for page in pages])
            if method == "Regex":
                extracted = extract_data_regex(text, config)
            else:
                extracted = extract_data_with_langchain(text, config)
            validated = validate_data(extracted)
            all_data.append(validated)
        st.json(all_data)
        json_data = json.dumps(all_data, ensure_ascii=False, indent=4)
        st.download_button("Baixar JSON", data=json_data, file_name="extracted_data.json")
    else:
        st.error("Por favor, faça upload de pelo menos um arquivo PDF.")
