# Schema
from IPython.lib.pretty import pretty
from typing_extensions import TypedDict
from typing import Literal
import random
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

####################################
# State Schema (TypedDict)
####################################
class TypedDictState(TypedDict):
    name: str
    mood: Literal["happy","sad"]

####################################
# State Schema (dataclass)
####################################
from dataclasses import dataclass
@dataclass
class DataclassState:
    name: str
    mood: Literal["happy","sad"]

####################################
# State Schema (Pydantic)
####################################
from pydantic import BaseModel, field_validator, ValidationError
class PydanticState(BaseModel):
    name: str
    mood: str # "happy" or "sad"

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, value):
        # Ensure the mood is either "happy" or "sad"
        if value not in ["happy", "sad"]:
            raise ValueError(f"Each mood must be either 'happy' or 'sad' (i.e. {value} is not a valid mood)")
        return value

################################
# 1: TypedDictState
# 2: DataclassState
# 3: PydanticState
#
# :::NOTE:::
# TypedDictState and DataclassState provide type hints but they don't enforce types at runtime.
# Pydantic is a data validation and settings management library using Python type annotations.
################################
CaseNum = 3
################################

# Nodes
def node_1(state):
    print(f"---Node 1---(CaseNum={CaseNum})---")
    if CaseNum == 1:
        return {"name": state['name'] + " is ... "}
    elif CaseNum == 2:
        return {"name": state.name + " is ... "}
    elif CaseNum == 3:
        return {"name": state.name + " is ... "}
    else:
        return {"name": "ERROR"}


def node_2(state):
    print("---Node 2---")
    return {"mood": "happy"}


def node_3(state):
    print("---Node 3---")
    return {"mood": "sad"}


def decide_mood(state) -> Literal["node_2", "node_3"]:
    # Here, let's just do a 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:
        # 50% of the time, we return Node 2
        return "node_2"

    # 50% of the time, we return Node 3
    return "node_3"


# Build graph
if CaseNum == 1:
    builder = StateGraph(TypedDictState)
elif CaseNum == 2:
    builder = StateGraph(DataclassState)
elif CaseNum == 3:
    builder = StateGraph(PydanticState)
else:
    builder = StateGraph(TypedDictState)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# View
display(Image(graph.get_graph().draw_mermaid_png()))

if CaseNum == 1:
    result = graph.invoke({"name":"Ramesh"})
elif CaseNum == 2:
    result = graph.invoke(DataclassState(name="Ramesh",mood="sad"))
elif CaseNum == 3:
    try:
        state = PydanticState(name="Ramesh", mood="sad")
        #state = PydanticState(name="Ramesh", mood="mad")
        result = graph.invoke(state)
    except ValidationError as e:
        print("hehe Validation Error:", e)
        result = "Error"
else:
    result = "Error"


print(result)