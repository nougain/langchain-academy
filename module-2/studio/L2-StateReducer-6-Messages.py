from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Define a custom TypedDict that includes a list of messages with add_messages reducer
class CustomMessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    added_key_1: str
    added_key_2: str
    # etc

# Use MessagesState, which includes the messages key with add_messages reducer
# NOTE: CustomMessagesState(TypedDict) and ExtendedMessagesState(MessagesState) are equivalent of each other
class ExtendedMessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built
    added_key_1: str
    added_key_2: str
    # etc


from langchain_core.messages import AIMessage, HumanMessage
# Initial state
messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
            HumanMessage(content="I'm looking for information on marine biology.", name="Ramesh")
           ]
# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")
# Test
messages = add_messages(messages, new_message)
for m in messages:
    m.pretty_print()

print("........................Re-writing (Note 'id')...........................")
# Initial state
messages = [AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
            HumanMessage(content="I'm looking for information on marine biology.", name="Ramesh", id="2")
           ]
# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model", id="2")
# Test
messages = add_messages(messages, new_message)
for m in messages:
    m.pretty_print()

print("........................Removal...........................")
from langchain_core.messages import RemoveMessage
# Message list
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Ramesh", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Ramesh", id="4"))
# Isolate messages to delete
delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
print(delete_messages)
messages = add_messages(messages, delete_messages)
for m in messages:
    m.pretty_print()