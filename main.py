from dotenv import load_dotenv
from langchain import hub
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from banco_de_dados_tool import busca_todas_as_coletas_data

load_dotenv()

tools = [busca_todas_as_coletas_data]

#Prompt
prompt = hub.pull("hwchase17/react")
#LLM
llm = ChatOllama(model='gemma2', temperature=0)

#Juntar Tools Prompt LLM, Agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Executor
agente_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


response =agente_executor.invoke({'input': """
                                  Busque para mim dados de coleta na data = 2025-01-16
                                  """})

print(response['output'])