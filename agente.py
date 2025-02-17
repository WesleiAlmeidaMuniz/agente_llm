from dotenv import load_dotenv
from langchain import hub
from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, Tool
from banco_de_dados.search import DadosColetas

load_dotenv()

class Agente:
    def __init__(self):
        llm = ChatOllama(model='gemma2', temperature=0)
        dados_de_coleta = DadosColetas()
        self.tools = [
            Tool(name = dados_de_coleta.name,
                func = dados_de_coleta.run,
                description = dados_de_coleta.description)
        ]

        prompt = hub.pull("hwchase17/react")
        self.agent = create_react_agent(llm=llm, tools=self.tools, prompt=prompt)
