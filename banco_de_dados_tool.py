# banco_de_dados_tool.py
from langchain.agents import tool
import os
import json
from datetime import datetime
import mysql.connector


# Função para buscar pedidos no banco de dados
@tool
def busca_todas_as_coletas_data(query: str) -> str:
    """
    Busca todas as coletas no banco de dados com base na data fornecida e salva no banco de dados.
    
    Args:
        date (datetime): Data para filtrar os pedidos.
        
    Returns:
        str: String de resultados com as coletas que correspondem a data informada.
    """ 

    #date_str = query.split("=")[1].strip().replace('"', '').replace("'", '')

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
                        where DATE(mt.created_at) = %s;""", (query,))
        resultados = cursor.fetchall()

        sucesso = salvar_no_banco(resultados)

        cursor.close()
        conn.close()

        if sucesso:
            return resultados
        else:
            return 'Não foi possivel salvar os dados'

    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        return [] 
    

def salvar_no_banco(resultados: list):

    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        for coleta in resultados:

                # Inserir dados em ufs
            cursor.execute("""
                INSERT IGNORE INTO ufs (id, nome) 
                VALUES (%(id_ufs)s, %(estado)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO cidades (id, nome, uf_id) 
                VALUES (%(id_cidade)s, %(cidade)s, %(id_ufs)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO bairros (id, nome, cidade_id) 
                VALUES (%(id_bairro)s, %(bairro)s, %(id_cidade)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO enderecos (id, entidade_id, logradouro, numero, complemento, bairro_id) 
                VALUES (%(id_enderecos)s, %(id_cliente)s, %(rua)s, %(numero_rua)s, %(complemento)s, %(id_bairro)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO entidades (id, nome) 
                VALUES (%(id_cliente)s, %(nome_cliente)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO coletas (id, minuta_id, chave_nf, remetente_id) 
                VALUES (%(id_coleta)s, %(minuta)s, %(chave_nf)s, %(id_cliente)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO minutas (id, codigo_rastreio, criado_em) 
                VALUES (%(minuta)s, %(codigo_rastreio)s, %(criado_em)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO eventos (id, minuta_id, criado_em) 
                VALUES (%(evento_id)s, %(minuta)s, %(criado_em)s);
            """, coleta)
            conn.commit()

            cursor.execute("""
                INSERT IGNORE INTO verificar (minuta_id, eventos_id) 
                VALUES (%(minuta)s, %(evento_id)s);
            """, coleta)
            conn.commit()


        conn.close()

        return True

    except Exception as e:
        print(f"Erro ao salvar pedidos: {e}")
        return False