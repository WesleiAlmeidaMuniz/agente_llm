from dotenv import load_dotenv
from langchain import hub
from langchain_ollama import ChatOllama
from langchain_community.tools import YouTubeSearchTool
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper
from langchain.agents import AgentExecutor, create_react_agent
from banco_de_dados_tool import busca_todos_os_pedidos_com_data, busca_todos_os_pedidos_banco

load_dotenv()

#Tools
youtube_tool = YouTubeSearchTool()
google_trends = GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper())


tools = [youtube_tool, google_trends, busca_todos_os_pedidos_com_data, busca_todos_os_pedidos_banco]

#Prompt
prompt = hub.pull("hwchase17/react")
#LLM
llm = ChatOllama(model='gemma2', temperature=0)

#Juntar Tools Prompt LLM, Agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Executor
agente_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


response =agente_executor.invoke({'input': """
                                  Eu quero processar um fluxo de dados sobre pedidos. Cada pedido tem um id, valor_total, status, criado_em e atualizado_em. 
                                    O fluxo deve passar por esses estágios:
                                    1. Buscar no banco de dados todos os pedidos com status "em_processamento".
                                    2. Fazer a soma de todos os pedidos com a variavel valor_total.
                                    3. Caso contrário, deve ser ignorado.
                                  """})

print(response['output'])