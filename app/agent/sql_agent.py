from langchain.agents import create_agent
from app.llms.openai_chat_client import default_chat_client
from app.prompts.sql_agent_prompt import build_sql_agent_prompt
from app.db.database import sql_db
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import json

class SQLAgent:

    def __init__(self):
        self.model = default_chat_client

        self.toolkit = SQLDatabaseToolkit(
            db=sql_db,
            llm=self.model
        )

        self.agent = create_agent(
            model=self.model,
            system_prompt=build_sql_agent_prompt(sql_db),  
            tools=self.toolkit.get_tools()
        )

    def run(self, query: str):
        response = self.agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        try:
            data = json.loads(response["messages"][-1].content)
            return data
        except:
            return []