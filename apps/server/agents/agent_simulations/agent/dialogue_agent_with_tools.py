from typing import List, Optional

# REMOVED: Unused Langchain imports
# from langchain.agents import AgentType, initialize_agent

# ADDED: Import XAgent and XAgentConfig
from xagent import XAgent
from xagent.config import XAgentConfig

from langchain.schema import AIMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI

from agents.agent_simulations.agent.dialogue_agent import DialogueAgent
# REMOVED: Unused import
# from agents.conversational.output_parser import ConvoOutputParser
from config import Config
from memory.zep.zep_memory import ZepMemory
from services.run_log import RunLogsManager
from typings.agent import AgentWithConfigsOutput


class DialogueAgentWithTools(DialogueAgent):
    def __init__(
        self,
        name: str,
        agent_with_configs: AgentWithConfigsOutput,
        system_message: SystemMessage,
        model: ChatOpenAI,
        tools: List[any],
        session_id: str,
        sender_name: str,
        is_memory: bool = False,
        run_logs_manager: Optional[RunLogsManager] = None,
        **tool_kwargs,
    ) -> None:
        super().__init__(name, agent_with_configs, system_message, model)
        self.tools = tools
        self.session_id = session_id
        self.sender_name = sender_name
        self.is_memory = is_memory
        self.run_logs_manager = run_logs_manager

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """

        memory = ZepMemory(
            session_id=self.session_id,
            url=Config.ZEP_API_URL,
            api_key=Config.ZEP_API_KEY,
            memory_key="chat_history",
            return_messages=True,
        )

        memory.human_name = self.sender_name
        memory.ai_name = self.agent_with_configs.agent.name
        memory.auto_save = False

        # REMOVED: Langchain agent initialization
        # agent = initialize_agent(
        #     self.tools,
        #     self.model,
        #     agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        #     verbose=True,
        #     handle_parsing_errors=True,
        #     memory=memory,
        #     callbacks=callbacks,
        #     agent_kwargs={
        #         "system_message": self.system_message.content,
        #         "output_parser": ConvoOutputParser(),
        #     },
        # )

        # ADDED: XAgent initialization
        config = XAgentConfig(
            llm=self.model,
            system_message=self.system_message.content,
        )
        agent = XAgent(config)

        # ADDED: Convert tools to XAgent format
        for tool in self.tools:
            agent.add_tool(self.convert_to_xagent_tool(tool))

        prompt = "\n".join(self.message_history + [self.prefix])

        # CHANGED: Use XAgent's run method
        res = agent.run(prompt)

        message = AIMessage(content=res)

        return message.content

    # ADDED: Method to convert tools to XAgent format
    def convert_to_xagent_tool(self, tool):
        from xagent.tools import BaseTool

        class XAgentTool(BaseTool):
            name = tool.name
            description = tool.description

            def _run(self, query: str) -> str:
                return tool.run(query)

        return XAgentTool()