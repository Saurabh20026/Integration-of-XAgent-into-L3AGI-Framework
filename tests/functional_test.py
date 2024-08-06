from xagent import XAgent
from xagent.config import XAgentConfig

def test_xagent_functionality():
    config = XAgentConfig()
    agent = XAgent(config)
    
    # Test basic query
    result = agent.run("What's the weather like today?")
    print(f"Weather query result: {result}")

    # Test using a tool
    result = agent.run("Calculate 15% of 85")
    print(f"Calculation result: {result}")

    # Test a more complex query
    result = agent.run("Summarize the plot of the movie Inception")
    print(f"Movie summary result: {result}")

if __name__ == '__main__':
    test_xagent_functionality()