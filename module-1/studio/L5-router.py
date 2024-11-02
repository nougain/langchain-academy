from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


# Tools
def rcn_add(a: int, b: int) -> int:
    """Add a and b.
    
    Args:
        a: first int
        b: second int
    """
    print("tool_called (rcn_add)...")
    return a+b


def rcn_multiply(a: int, b: int) -> int:
    """Multiply a and b.
    
    Args:
        a: first int
        b: second int
    """
    print("tool_called (rcn_multiply)...")
    return a*b

tools = [rcn_add, rcn_multiply]
tool_node = ToolNode(tools)


# LLM with bound tool
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", tool_node)

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)

# Compile graph
graph = builder.compile()

# View
#Jupyter# display(Image(graph.get_graph().draw_mermaid_png()))

# Execute
from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="Multiply 4 by -3.")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()