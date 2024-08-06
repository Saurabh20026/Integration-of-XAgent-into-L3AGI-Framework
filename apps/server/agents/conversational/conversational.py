import asyncio

# REMOVED: Unused Langchain imports
# from langchain import hub
# from langchain.agents import (AgentExecutor, AgentType, create_react_agent,
#                               initialize_agent)

# ADDED: Import XAgent and XAgentConfig
from xagent import XAgent
from xagent.config import XAgentConfig
from xagent.tools import BaseTool

from agents.base_agent import BaseAgent
# REMOVED: Unused import
# from agents.conversational.output_parser import ConvoOutputParser
from agents.conversational.streaming_aiter import AsyncCallbackHandler
from agents.handle_agent_errors import handle_agent_error
from config import Config
from memory.zep.zep_memory import ZepMemory
from postgres import PostgresChatMessageHistory
from services.pubsub import ChatPubSubService
from services.run_log import RunLogsManager
from services.voice import speech_to_text, text_to_speech
from typings.agent import AgentWithConfigsOutput
from typings.config import AccountSettings, AccountVoiceSettings
from utils.model import get_llm
from utils.system_message import SystemMessageBuilder


class ConversationalAgent(BaseAgent):
    async def run(
        self,
        settings: AccountSettings,
        voice_settings: AccountVoiceSettings,
        chat_pubsub_service: ChatPubSubService,
        agent_with_configs: AgentWithConfigsOutput,
        tools,
        prompt: str,
        voice_url: str,
        history: PostgresChatMessageHistory,
        human_message_id: str,
        run_logs_manager: RunLogsManager,
        pre_retrieved_context: str,
    ):
        memory = ZepMemory(
            session_id=str(self.session_id),
            url=Config.ZEP_API_URL,
            api_key=Config.ZEP_API_KEY,
            memory_key="chat_history",
            return_messages=True,
        )

        memory.human_name = self.sender_name
        memory.ai_name = agent_with_configs.agent.name

        system_message = SystemMessageBuilder(
            agent_with_configs, pre_retrieved_context
        ).build()

        res: str

        try:
            if voice_url:
                configs = agent_with_configs.configs
                prompt = speech_to_text(voice_url, configs, voice_settings)

            llm = get_llm(
                settings,
                agent_with_configs,
            )

            # REMOVED: Unused streaming handler
            # streaming_handler = AsyncCallbackHandler()

            # REMOVED: Langchain agent initialization
            # agent = initialize_agent(
            #     tools,
            #     llm,
            #     agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            #     verbose=True,
            #     memory=memory,
            #     handle_parsing_errors="Check your output and make sure it conforms!",
            #     agent_kwargs={
            #         "system_message": system_message,
            #         "output_parser": ConvoOutputParser(),
            #     },
            #     callbacks=[run_logs_manager.get_agent_callback_handler()],
            # )

            # ADDED: XAgent initialization
            config = XAgentConfig(
                llm=llm,
                system_message=system_message,
            )
            agent = XAgent(config)

            # ADDED: Convert tools to XAgent format
            xagent_tools = [self.convert_to_xagent_tool(tool) for tool in tools]
            for tool in xagent_tools:
                agent.add_tool(tool)

            # CHANGED: Use XAgent's astream method
            chunks = []
            async for chunk in agent.astream(prompt):
                chunks.append(chunk)
                yield chunk

            res = "".join(chunks)

        except Exception as err:
            res = handle_agent_error(err)

            memory.save_context(
                {
                    "input": prompt,
                    "chat_history": memory.load_memory_variables({})["chat_history"],
                },
                {
                    "output": res,
                },
            )

            yield res

        try:
            configs = agent_with_configs.configs
            voice_url = None
            if "Voice" in configs.response_mode:
                voice_url = text_to_speech(res, configs, voice_settings)
        except Exception as err:
            res = f"{res}\n\n{handle_agent_error(err)}"

            yield res

        ai_message = history.create_ai_message(
            res,
            human_message_id,
            agent_with_configs.agent.id,
            voice_url,
        )

        chat_pubsub_service.send_chat_message(chat_message=ai_message)

    # ADDED: Method to convert tools to XAgent format
    def convert_to_xagent_tool(self, tool):
        class XAgentTool(BaseTool):
            name = tool.name
            description = tool.description

            def _run(self, query: str) -> str:
                return tool.run(query)

        return XAgentTool()