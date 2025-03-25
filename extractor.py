import json
import re
import os
from schema import InvoiceData
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

def load_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        return json.load(f)

def extract_data_regex(text, config):
    extracted = {}
    for field in config.get('fields', []):
        name = field['name']
        pattern = field['match']
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            if field['type'] == 'float':
                value = float(value)
            extracted[name] = value
    return extracted

def extract_data_with_langchain(text, config):
    parser = PydanticOutputParser(pydantic_object=InvoiceData)
    system_template = """
Você é um assistente que extrai dados de faturas.
Retorne SOMENTE um JSON **válido** com as chaves:
- invoice_number (string)
- date (YYYY-MM-DD)
- total_amount (float)

Use o texto fornecido para encontrar esses valores.
Se não encontrar, retorne "N/A" ou "0.0" nesses campos.

Exemplo de resposta (use chaves duplas para exibir JSON literal):
{{
  "invoice_number": "123456",
  "date": "2023-03-15",
  "total_amount": 1234.56
}}

{format_instructions}
    """
    system_message = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "Texto da fatura:\n{text}"
    human_message = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    llm = ChatOpenAI(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    chain = chat_prompt | llm
    result = chain.invoke({
        "text": text,
        "format_instructions": parser.get_format_instructions()
    })
    if hasattr(result, "content"):
        raw_text = result.content
    else:
        raw_text = str(result)
    try:
        data = parser.parse(raw_text)
        return data.dict()
    except Exception as e:
        return {"error": f"Falha ao converter resposta em JSON: {str(e)}", "raw_output": raw_text}

def validate_data(data):
    try:
        invoice = InvoiceData(**data)
        return invoice.dict()
    except Exception as e:
        return {"error": str(e)}
