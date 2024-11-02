from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage

### Messages ###
messages = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]
messages.append(HumanMessage(content=f"Yes, that's right.",name="Ramesh"))
messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Ramesh"))

for m in messages:
    m.pretty_print()

### Chat Model ###
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=20)
result = llm.invoke(messages)
print(result)
print(result.response_metadata)