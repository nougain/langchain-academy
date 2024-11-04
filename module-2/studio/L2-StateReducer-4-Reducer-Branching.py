from IPython.utils.coloransi import value
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
    value = state['foo'][-1]
    print(f"---Node 1---(value: " + str(value) +")")
    return {"foo":  [value + 1]}


def node_2(state):
    value = state['foo'][-1]
    print(f"---Node 2---(value: " + str(value) +")")
    return {"foo":  [value + 1]}


def node_3(state):
    value = state['foo'][-1]
    print(f"---Node 3---(value: " + str(value) +")")
    return {"foo":  [value + 1]}


# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()
try:
    result = graph.invoke({"foo" : [3]})        # It will retain the previous states
    print(result)
    result = graph.invoke({"foo" : [6,8]})      # It will retain the previous states
    print(result)
    result = graph.invoke({"foo" : None})       # THROWS EXCEPTION: can only concatenate list (not "NoneType") to list
    print(result)
except InvalidUpdateError as iue:
    print(f"RCN_ERROR: InvalidUpdateError occurred: {iue}")
except Exception as e: # Any other except:
    print(f"RCN_ERROR: Exception occurred: {e}")

# View
display(Image(graph.get_graph().draw_mermaid_png()))