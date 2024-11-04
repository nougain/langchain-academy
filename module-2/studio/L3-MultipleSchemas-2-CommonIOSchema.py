from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

##############################################################
class OverallState(TypedDict):
    question: str
    answer: str
    notes: str
##############################################################

def thinking_node(state: OverallState):
    return {"answer": "bye", "notes": "... his name is Ramesh"}

def answer_node(state: OverallState):
    return {"answer": "bye Ramesh"}

graph = StateGraph(OverallState)
graph.add_node("answer_node", answer_node)
graph.add_node("thinking_node", thinking_node)

graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)

graph = graph.compile()
result = graph.invoke({"question":"hi"})
print(result)

# View
#display(Image(graph.get_graph().draw_mermaid_png()))