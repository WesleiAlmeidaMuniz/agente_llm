from langchain.tools import BaseTool
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from pydantic import Field, BaseModel
from langchain_core.output_parsers import JsonOutputParser
import mysql.connector
import os
import json
from datetime import datetime


def default_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Tipo não serializável")


def busca_dados_coleta_com_data(data):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST_TMS"),
            port=os.getenv("DB_PORT_TMS"),
            user=os.getenv("DB_USERNAME_TMS"),
            password=os.getenv("DB_PASSWORD_TMS"),
            database=os.getenv("DB_NAME_TMS")
        )
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
                        SELECT 
                                ef.id AS evento_id,
                                mt.id AS minuta, 
                                mt.codigo_rastreio AS codigo_rastreio,
                                mt.created_at AS criado_em,
                                ct.id as id_coleta,
                                ct.chave_nf as chave_nf,
                                et.id as id_cliente,
                                et.nome as nome_cliente,
                                edr.id as id_enderecos,
                                edr.logradouro as rua,
                                edr.numero as numero_rua,
                                edr.complemento as complemento,
                                bir.id as id_bairro,
                                bir.nome as bairro,
                                cdd.id as id_cidade,
                                cdd.nome as cidade,
                                ufs.id as id_ufs,
                                ufs.nome as estado
                            FROM ccdblog_eventos.frete_criado ef
                            INNER JOIN ccdblog_temis.minutas mt ON ef.minutas_id = mt.id
                            LEFT JOIN ccdblog_temis.coletas ct on mt.id = ct.minuta_id
                            LEFT JOIN ccdblog_temis.entidades et on et.id = ct.remetente
                            LEFT JOIN ccdblog_temis.enderecos edr on edr.entidade_id = et.id
                            LEFT JOIN ccdblog_temis.bairros bir on bir.id = edr.bairro_id
                            LEFT JOIN ccdblog_temis.cidades cdd on bir.cidade_id = cdd.id
                            LEFT JOIN ccdblog_temis.ufs ufs on cdd.uf_id = ufs.id
                            where DATE(mt.created_at) = %s;""", (data,))
        resultados = cursor.fetchall()


        return resultados
    except mysql.connector.Error as e:
        print(f"Erro de conexão com o banco de dados: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

class ExtratorDeData(BaseModel):
    data:str = Field("Data da coleta. Exemplo: 2025-01-01, 2024-09-10, 2025-02-13")

class DadosColetas(BaseTool):
    name:str = "DadosColetas"
    description:str = """
                    Esta ferramenta extrai dados de coletas do banco de dados dada uma data especifica. 
                """ 
    
    def _run(self, input:str) -> str:
        llm = ChatOllama(model='gemma2', temperature=0)

        parser = JsonOutputParser(pydantic_object=ExtratorDeData)
        template = PromptTemplate(template="""Você deve analisar a {input} e extrair a data informada
                       Formado de saída:
                       {formato_saida}""",
                       input_variables=["input"],
                       partial_variables={"formato_saida": parser.get_format_instructions()})
                
        cadeia = template | llm | parser

        try:
            response = cadeia.invoke({"input": input})

            data = response['data']

            dados = busca_dados_coleta_com_data(data)

            if dados:
                return "Dados Acessados com Sucesso!"
            else:
                return "Nenhum dado encontrado para a data fornecida."
        
        except Exception as e:
            print(f"Erro ao processar a solicitação: {e}")
            return json.dumps({"erro": "Houve um erro ao processar a solicitação."})


