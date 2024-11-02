import os
import getpass


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI
gpt4o_chat = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=20)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=20)

from langchain_core.messages import HumanMessage

# Create a message
msg = HumanMessage(content="Hello. Please give me a motivational quote with it's author and source.", name="Ramesh")

# Message list
messages = [msg]

# Invoke the model with a list of messages
aimsg = gpt4o_chat.invoke(messages)
print("-------------gpt4o_chat.invoke(messages)--------------")
print(aimsg)
print(aimsg.response_metadata)

#
# Search Tools (Tavily)
#
_set_env("TAVILY_API_KEY")
from langchain_community.tools.tavily_search import TavilySearchResults
tavily_search = TavilySearchResults(max_results=2)
search_docs = tavily_search.invoke("Is it mandatory to use LangGraph with LangChain?")
print("------------tavily_search.invoke(....)---------------")
print(search_docs)