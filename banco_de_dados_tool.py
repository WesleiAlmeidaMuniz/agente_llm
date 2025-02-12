# banco_de_dados_tool.py
from langchain.agents import tool
import os
import json
from datetime import datetime
import mysql.connector


# Função para buscar pedidos no banco de dados
@tool
def busca_todas_as_coletas_data(query: str) -> list:
    """
    Busca todas as coletas no banco de dados com base na data fornecida e salva no banco de dados.
    
    Args:
        date (datetime): Data para filtrar os pedidos.
        
    Returns:
        list: Lista de resultados com os pedidos que correspondem ao status.
    """ 

    # date_str = query.split("=")[1].strip().replace('"', '')

    # date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    try:
        # Estabelecendo a conexão com o banco
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST_TMS"),
            port=os.getenv("DB_PORT_TMS"),
            user=os.getenv("DB_USERNAME_TMS"),
            password=os.getenv("DB_PASSWORD_TMS"),
            database=os.getenv("DB_NAME_TMS")
        )
        cursor = conn.cursor(dictionary=True)

        # Executa a consulta SQL com comparação apenas de data
        cursor.execute("""
                       SELECT 
                            ef.id AS evento_id,
                            mt.id AS minuta, 
                            mt.codigo_rastreio AS codigo_rastreio,
                            mt.created_at AS criado_em,
                            ct.chave_nf as chave_nf,
                            et.nome as nome_cliente,
                            edr.logradouro as rua,
                            edr.numero as numero_rua,
                            bir.nome as bairro,
                            cdd.nome as cidade,
                            ufs.nome as estado,
                            edr.complemento as complemento
                        FROM ccdblog_eventos.frete_criado ef
                        INNER JOIN ccdblog_temis.minutas mt ON ef.minutas_id = mt.id
                        LEFT JOIN ccdblog_temis.coletas ct on mt.id = ct.minuta_id
                        LEFT JOIN ccdblog_temis.entidades et on et.id = ct.remetente
                        LEFT JOIN ccdblog_temis.enderecos edr on edr.entidade_id = et.id
                        LEFT JOIN ccdblog_temis.bairros bir on bir.id = edr.bairro_id
                        LEFT JOIN ccdblog_temis.cidades cdd on bir.cidade_id = cdd.id
                        LEFT JOIN ccdblog_temis.ufs ufs on cdd.uf_id = ufs.id
                        where DATE(mt.created_at) = %s;""", (query,))
        resultados = cursor.fetchall()

        salvar_no_banco(resultados)

        cursor.close()
        conn.close()

        return resultados  # Lista dos pedidos que estão no status 'em_processamento'

    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        return []  # Caso ocorra um erro, retorne uma lista vazia
    

def salvar_no_banco(resultados: list):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        for linha in resultados:
            # Verifica se a minuta já existe na tabela
            cursor.execute("SELECT 1 FROM verificados WHERE minuta = %s LIMIT 1", (linha["minuta"],))
            existe = cursor.fetchone()

            if not existe:  # Se não existir, insere no banco
                cursor.execute("""
                    INSERT INTO verificados (
                        minuta, chave_nf, dt_nf, valor_nf, peso_bruto, peso_liquido, 
                        peso_cubado, volumes, status_coleta, criado_em, atualizado_em, 
                        codigo_rastreio, status_minuta, tipo, nome_embarcador, 
                        documento_embarcador, status_entidade, tipo_entidade
                    ) 
                    VALUES (
                        %(minuta)s, %(chave_nf)s, %(dt_nf)s, %(valor_nf)s, %(peso_bruto)s, %(peso_liquido)s, 
                        %(peso_cubado)s, %(volumes)s, %(status_coleta)s, %(criado_em)s, %(atualizado_em)s, 
                        %(codigo_rastreio)s, %(status_minuta)s, %(tipo)s, %(nome_embarcador)s, 
                        %(documento_embarcador)s, %(status_entidade)s, %(tipo_entidade)s
                    );
                """, linha)

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar pedidos: {e}")