import time
from xagent import XAgent
from xagent.config import XAgentConfig
from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatOpenAI

def test_performance():
    queries = [
        "What's the capital of France?",
        "Who wrote Romeo and Juliet?",
        "What's the square root of 144?",
    ]

    # XAgent performance
    xagent_config = XAgentConfig()
    xagent = XAgent(xagent_config)
    
    xagent_start = time.time()
    for query in queries:
        xagent.run(query)
    xagent_end = time.time()
    
    print(f"XAgent took {xagent_end - xagent_start} seconds")

    # Langchain performance (for comparison)
    llm = ChatOpenAI(temperature=0)
    tools = []  # Add your tools here
    langchain_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    langchain_start = time.time()
    for query in queries:
        langchain_agent.run(query)
    langchain_end = time.time()
    
    print(f"Langchain took {langchain_end - langchain_start} seconds")

if __name__ == '__main__':
    test_performance()