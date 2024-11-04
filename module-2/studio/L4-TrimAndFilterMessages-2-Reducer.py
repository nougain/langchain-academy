from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage


##
## A practical challenge when working with messages is managing long-running conversations. Long-running conversations
## result in high token usage and latency if we are not careful, because we pass a growing list of messages to the model.
## We have a few ways to address this. First, recall the trick we saw using RemoveMessage and the add_messages reducer.
##
## ***SEE THIS FILE USING REDUCER TO SAVE ON TOKENS (TRIMMING)***
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


# Nodes
def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"], {"tags": ["RCNTag-Reducer"], "metadata": {"RCNKey1":len(messages)}})}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter")
builder.add_edge("filter", "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

output = graph.invoke({'messages': messages}, {"tags": ["RCNTag-Reducer"], "metadata": {"RCNKey1":len(messages)}})
for m in output['messages']:
    m.pretty_print()


# View
#display(Image(graph.get_graph().draw_mermaid_png()))


##
## NOTICE THAT ONLY THE LAST TWO MESSAGES ARE RETAINED, ALL OTHERS WERE REMOVED>
##