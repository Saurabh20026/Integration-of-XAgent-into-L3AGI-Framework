# ADDED: Import XAgent and XAgentConfig
from xagent import XAgent
from xagent.config import XAgentConfig

from langchain.smith import RunEvalConfig, run_on_dataset
from langchain_community.chat_models import ChatOpenAI
from langsmith import Client

# REMOVED: Commented out unused imports and code
# from langchain.agents import AgentType, initialize_agent
# from langchain.agents.react.base import ReActDocstoreAgent

def agent_factory():
    # CHANGED: Replaced Langchain agent initialization with XAgent
    config = XAgentConfig()
    return XAgent(config)

    # REMOVED: Old Langchain agent code
    # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    # tools = get_tools(["SerpGoogleSearch"])
    # return initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    #     verbose=True,
    #     handle_parsing_errors="Check your output and make sure it conforms!",
    #     agent_kwargs={
    #         "system_message": system_message,
    #         "output_parser": ConvoOutputParser(),
    #     },
    #     max_iterations=5,
    # )

agent = agent_factory()

client = Client()

eval_config = RunEvalConfig(
    evaluators=[
        "qa",
        RunEvalConfig.Criteria("helpfulness"),
        RunEvalConfig.Criteria("conciseness"),
    ],
    input_key="input",
    eval_llm=ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo"),
)

chain_results = run_on_dataset(
    client,
    dataset_name="test-dataset",
    llm_or_chain_factory=agent_factory,
    evaluation=eval_config,
    concurrency_level=1,
    verbose=True,
)