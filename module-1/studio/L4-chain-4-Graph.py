from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage


# Tools
def rcn_add(a: int, b: int) -> int:
    print("tool_called...rcn_add...")
    """Add a and b.
    Args:
        a: first int
        b: second int
    """
    return (2*a) + (2*b)

def rcn_multiply(a: int, b: int) -> int:
    print("tool_called...rcn_multiply...")
    """Multiply a and b.
    Args:
        a: first int
        b: second int
    """
    return (2*a) * (2*b)


# ChatModel
llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=20)
llm_with_tools = llm.bind_tools([rcn_add, rcn_multiply])


# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# View
#jupyter# display(Image(graph.get_graph().draw_mermaid_png()))


# Invoke
messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
for m in messages['messages']:
    m.pretty_print()

# Invoke, picking a tool
messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
for m in messages['messages']:
    m.pretty_print()