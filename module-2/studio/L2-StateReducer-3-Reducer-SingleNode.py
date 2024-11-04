from langgraph.errors import InvalidUpdateError
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

from operator import add
from typing import Annotated

##################################################
class State(TypedDict):
    # foo: int
    foo: Annotated[list[int], add]          # <--- Reducer specified by Annotated type, using list with operator.add
##################################################

def node_1(state):
    print("---Node 1---")
    lastIndex = len(state['foo'])-1
    return {"foo": [state['foo'][lastIndex] + 1]}

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()
try:
    result = graph.invoke({"foo" : [3]})    # It will retain the previous states
    print(result)
    result = graph.invoke({"foo" : [6,8]})    # It will retain the previous states
    print(result)
except  InvalidUpdateError  as e:
    print(f"RCN_ERROR: InvalidUpdateError occurred: {e}")

# View
display(Image(graph.get_graph().draw_mermaid_png()))