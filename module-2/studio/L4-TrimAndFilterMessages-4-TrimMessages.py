from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage


##
## If you don't need or want to modify the graph state, you can just filter the messages you pass to the chat model.
## For example, just pass in a filtered list: llm.invoke(messages[-1:]) to the model.
##


# Message list with a preamble
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Ramesh", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Ramesh", id="4"))


print("...........................LLM call through Node...................................")
# Pass Messages as state to a Chat Model
from IPython.display import Image, display
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import RemoveMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=30)

#
# TRIM BASED ON THE NUMBER OF TOKENS
#
# Another approach is to trim messages, based upon a set number of tokens.
# This restricts the message history to a specified number of tokens.
# While filtering only returns a post-hoc subset of the messages between agents, trimming restricts
# the number of tokens that a chat model can use to respond.
#############################################################################
from langchain_core.messages import trim_messages
def chat_model_node(state: MessagesState):
    messages = trim_messages(
            state["messages"],
            max_tokens=50,
            strategy="last",                            # Start with the most recent messages in the list
            token_counter=ChatOpenAI(model="gpt-4o"),
            allow_partial=False,                        # If true, it will truncate messages
        )
    return {"messages": [llm.invoke(messages, {"tags": ["RCNTag-trim."], "metadata": {"RCNKey1":len(messages)}})]}
#############################################################################


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

print("...........................Invoke, using trimming messages...................................")
output = graph.invoke({'messages': messages}, {"tags": ["RCNTag-Trim.."], "metadata": {"RCNKey1":len(messages)}})
for m in output['messages']:
    m.pretty_print()

print("...........................List of messages post adding a new HumanMessage...................................")
messages.append(output['messages'][-1])     #Appending the AiMessage response to the very last message
messages.append(HumanMessage(f"Tell me more about Orcas live!", name="Ramesh"))
for m in messages:
    m.pretty_print()

print("...........................Invoke, using trimming messages (after adding a new HumanMessage)............")
messages=trim_messages(
    messages,
    max_tokens=50,
    strategy="last",
    token_counter=ChatOpenAI(model="gpt-4o"),
    allow_partial=False
)
# Invoke, using message trimming
output = graph.invoke({'messages': messages}, {"tags": ["RCNTag-Trim..."], "metadata": {"RCNKey1":len(messages)}})
for m in output['messages']:
    m.pretty_print()

##
## The state has all of the messages. But, let's look at the LangSmith trace to see that the model invocation
## only uses tokens upto the max_tokens specified.
##