from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from agente import Agente

load_dotenv()

pergunta = 'Busque os dados de coleta das data 2025-01-01 e me retorne se conseguiu ou não.'

agente = Agente()
executor = AgentExecutor(agent=agente.agent, tools=agente.tools, verbose=True)

resposta = executor.invoke({"input": pergunta})

print(resposta)