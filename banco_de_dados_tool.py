# banco_de_dados_tool.py
from langchain.agents import tool
import psycopg2
import os
import json
from datetime import datetime

#Busca todos os pedidos com query
@tool
def busca_todos_os_pedidos_banco(query: str) -> list:
    """
    Busca todos os pedidos no banco de dados com base no status fornecido.
    
    Args:
        status (str): O status dos pedidos a serem buscados no banco de dados.
        
    Returns:
        list: Lista de resultados com os pedidos que correspondem ao status.
    """ 
    if "em_processamento" in query.lower():
        status_pedido = "em_processamento"
    elif "concluido" in query.lower():
        status_pedido = "concluido"

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM public.pedido WHERE status = %s", (status_pedido,))
        resultados = cursor.fetchall()

        resultado_lista = []

        for linha in resultados:
            dicionario = {
                "id": linha[0],
                "valor_total": linha[1],
                "status": linha[2],
                 "criado_em": linha[3].strftime("%Y-%m-%d %H:%M:%S") if isinstance(linha[3], datetime) else linha[3],
                "atualizado_em": linha[4].strftime("%Y-%m-%d %H:%M:%S") if isinstance(linha[4], datetime) else linha[4],
                "usuarioid": linha[6]
            }

            resultado_lista.append(dicionario)

        caminho = os.path.join('dadosPedidos', 'resultado.json')
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(resultado_lista, f, ensure_ascii=False, indent=4)

        cursor.close()
        conn.close()

        return resultado_lista  # Lista dos pedidos que estão no status 'em_processamento'

    except Exception as e:
        return []  # Caso ocorra um erro, retorne uma lista vazia

# Função para buscar pedidos no banco de dados
@tool
def busca_todos_os_pedidos_com_data(query: str) -> list:
    """
    Busca todos os pedidos no banco de dados com base no status fornecido.
    
    Args:
        status (str): O status dos pedidos a serem buscados no banco de dados.
        date (datetime): Data para filtrar os pedidos.
        
    Returns:
        list: Lista de resultados com os pedidos que correspondem ao status.
    """ 

    input_parts = query.split(", ")
    status = input_parts[0].split("=")[1].replace('"', '')
    date_str = input_parts[1].split("=")[1]

    if "em_processamento" in status.lower():
        status_pedido = "em_processamento"
    elif "concluido" in status.lower():
        status_pedido = "concluido"

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    try:
        # Converte a data para o formato "date" sem considerar a hora
        date = date_obj.date()

        # Estabelecendo a conexão com o banco
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # Executa a consulta SQL com comparação apenas de data
        cursor.execute("SELECT * FROM public.pedido WHERE status = %s and DATE(created_at) = %s", (status_pedido, date))
        resultados = cursor.fetchall()

        resultado_lista = []

        for linha in resultados:
            # Cria um dicionário com os resultados formatados
            dicionario = {
                "id": linha[0],
                "valor_total": linha[1],
                "status": linha[2],
                "criado_em": linha[3].strftime("%Y-%m-%d %H:%M:%S") if isinstance(linha[3], datetime) else linha[3],
                "atualizado_em": linha[4].strftime("%Y-%m-%d %H:%M:%S") if isinstance(linha[4], datetime) else linha[4],
                "usuarioid": linha[6]
            }

            resultado_lista.append(dicionario)

        # Salva o resultado em um arquivo JSON
        data_agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = './dadosPedidos'
        file_name = f'resultado - {status_pedido} - {data_agora}.json'
        caminho = os.path.join(path, file_name)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(resultado_lista, f, ensure_ascii=False, indent=4)

        cursor.close()
        conn.close()

        return resultado_lista  # Lista dos pedidos que estão no status 'em_processamento'

    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        return []  # Caso ocorra um erro, retorne uma lista vazia