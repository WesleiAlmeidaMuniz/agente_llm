from dotenv import load_dotenv
from langchain import hub
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent, Tool
from banco_de_dados_tool import busca_todas_as_coletas_data
from input.input import DadosColetas
from langchain.prompts import PromptTemplate


load_dotenv()

# tools = [busca_todas_as_coletas_data]

# #Prompt

# #LLM
# llm = ChatOllama(model='gemma2', temperature=0)

# #Juntar Tools Prompt LLM, Agent
# agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# # Executor
# agente_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


# response = agente_executor.invoke({'input': """
#                                    Você é um assistente de coletas e não possui interação humana.
#                                     Execute a tarefa nos passos a seguir:
#                                     1 - Extraia os dados de coleta da data 2025-01-01.
#                                     2 - Responda apenas com os dados retornados da função.
#                                    """})
# print(response['output'])

pergunta = 'Busque os dados de coleta da data 2025-01-01 e me retorne se conseguiu ou não.'


dados_de_coleta = DadosColetas()

llm = ChatOllama(model='gemma2', temperature=0)

tools = [
    Tool(name = dados_de_coleta.name,
         func = dados_de_coleta.run,
         description = dados_de_coleta.description)
]

prompt = hub.pull("hwchase17/react")

# prompt = PromptTemplate(
#     input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
#     template="""
#     Você é um assistente inteligente e tem acesso às seguintes ferramentas:
#     {tools}

#     As ferramentas disponíveis são: {tool_names}

#     Quando precisar chamar uma ferramenta, siga rigorosamente este formato:

#     ```
#     Thought: [Explique seu raciocínio]
#     Action: [Nome da ferramenta]
#     Action Input: [JSON com os parâmetros necessários]
#     ```

#     Nunca use formatação incorreta.

#     Pergunta: {input}
#     {agent_scratchpad}
#     """
# )


agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools= tools, verbose=True)

resposta = executor.invoke({"input": pergunta})

print(resposta)