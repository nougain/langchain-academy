from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage


# Messages
messages = [AIMessage(f"So you said you were researching ocean mammals?", name="Bot")]
messages.append(HumanMessage(f"Yes, I know about whales. But what others should I learn about?", name="Ramesh"))
for m in messages:
    m.pretty_print()

print("...........................LLM call w/o Graph...................................")
# Pass Messages as state to a Chat Model
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=20)
result = llm.invoke(messages)
print(result)
print(result.response_metadata)

print("...........................LLM call w/ Graph...................................")
from IPython.display import Image, display
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

# Node
def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"])}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

output = graph.invoke({'messages': messages})
for m in output['messages']:
    m.pretty_print()


# View
#display(Image(graph.get_graph().draw_mermaid_png()))

##
## A practical challenge when working with messages is managing long-running conversations. Long-running conversations
## result in high token usage and latency if we are not careful, because we pass a growing list of messages to the model.
## We have a few ways to address this. First, recall the trick we saw using RemoveMessage and the add_messages reducer.
##
## ***SEE THE NEXT FILE USING REDUCER TO SAVE ON TOKENS (TRIMMING)***
##