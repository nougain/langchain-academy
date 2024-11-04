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


#############################################################################
# We are maintaining the state uptodate with full list of messages, however
# the LLM receives only the last message to respond (see.... [-1:]
#
# https://docs.smith.langchain.com/observability/how_to_guides/tracing/add_metadata_tags
#############################################################################
# Nodes
import langsmith as ls
@ls.traceable(
  run_type="llm",
  name="RCN OpenAI Call Decorator",
  tags=["RCNTag-Filter"],
  metadata={"RCNKey-1": "RCNValue-1"}
)
def chat_model_node(state: MessagesState):
    tags = ["RCNTag-1", "RCNTag-2"]
    metadata = {"RCNKey-2": "RCNValue-2"}
    return {
        "messages": llm.invoke(
            state["messages"][-1:],                         ##****Invoke LLM with the LAST MESSAGE ONLY****
            {"tags": tags, "metadata": metadata}
        )
    }
#############################################################################


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

output = graph.invoke({'messages': messages}, {"tags": ["RCNTag-Filter."], "metadata": {"RCNKey1":len(messages)}})
for m in output['messages']:
    m.pretty_print()

print("...........................List of messages post adding a new HumanMessage...................................")
messages.append(output['messages'][-1])         #Appending the AiMessage response
messages.append(HumanMessage(f"Tell me more about Narwhals!", name="Ramesh"))
for m in messages:
    m.pretty_print()

print("...........................Invoke, using message filtering...................................")
# Invoke, using message filtering
output = graph.invoke({'messages': messages}, {"tags": ["RCNTag-Filter.."], "metadata": {"RCNKey1":len(messages)}})
for m in output['messages']:
    m.pretty_print()

##
## The state has all of the messages. But, let's look at the LangSmith trace to see that the model invocation
## only uses the last message.
##