from IPython.utils.coloransi import value
from langgraph.errors import InvalidUpdateError
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

from operator import add
from typing import Annotated

##################################################
def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
               If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

class DefaultState(TypedDict):
    foo: Annotated[list[int], add]                          ### NORMAL REDUCER

class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]                  ### CUSTOM REDUCER
##################################################

def node_1(state):
    print("---Node 1---")
    return {"foo": [99]}


# Build graph
builder = StateGraph(DefaultState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

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
#display(Image(graph.get_graph().draw_mermaid_png()))

print("...............................................................")

# Build graph
builder = StateGraph(CustomReducerState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()
try:
    result = graph.invoke({"foo" : [3]})        # It will retain the previous states
    print(result)
    result = graph.invoke({"foo" : [6,8]})      # It will retain the previous states
    print(result)
    result = graph.invoke({"foo" : None})       # NOW it will NOT throw exception (see the previous .py file for context)
    print(result)
except InvalidUpdateError as iue:
    print(f"RCN_ERROR: InvalidUpdateError occurred: {iue}")
except Exception as e: # Any other except:
    print(f"RCN_ERROR: Exception occurred: {e}")

# View
#display(Image(graph.get_graph().draw_mermaid_png()))