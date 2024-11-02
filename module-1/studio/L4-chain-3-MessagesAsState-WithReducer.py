###Using messages as state###
# To retain previous messages, we want to append and not override the State
# For this we can use Reducers (Annotate State with add_messages)
# LangGraph has in-built reducer, MessagesState. MessagesState is defined with a pre-built single messages key. And it is a list of AnyMessage objects and uses the add_message reducer.
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage

# Problem with below declaration is that the messages key's value will be overridden
class MessagesState(TypedDict):
    messages: list[AnyMessage]

# Initial state
from langgraph.graph.message import add_messages
messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
            HumanMessage(content="I'm looking for information on marine biology.", name="Ramesh")
            ]
# New message to add
messages = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")
# Test
print("------------Normal-------------------------")
print(messages)


#
# Reducers
#
#To append, we will use reducers
#Reducers allow us to specify how state updates are performed.
#pre-built "add_messages" reducer
from typing import Annotated

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
# Initial state
messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
            HumanMessage(content="I'm looking for information on marine biology.", name="Ramesh")
            ]
# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")
# Test
messages = add_messages(messages, new_message)
print("------------Annotated/add_messages Reducer-------------------------")
print(messages)


#
# Since having a list of messages in graph state is so common, LangGraph has a pre-built MessagesState!
# MessagesState is defined with a pre-built single "messages" key. It is a list of "AnyMessage" objects. Uses the "add_message" reducer.
#
from langgraph.graph import MessagesState

class MessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built
    pass
# Initial state
messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
            HumanMessage(content="I'm looking for information on marine biology.", name="Ramesh")
            ]
# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")
# Test
messages = add_messages(messages, new_message)
print("------------In-built MessagesState-------------------------")
print(messages)
