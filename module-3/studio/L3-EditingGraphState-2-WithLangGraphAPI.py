from langgraph_sdk import get_client
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_core.messages import convert_to_messages

#
# A helper function for better formatting of the tool calls in messages.
#
def format_tool_calls(tool_calls):
    """
    Format a list of tool calls into a readable string.

    Args:
        tool_calls (list): A list of dictionaries, each representing a tool call.
            Each dictionary should have 'id', 'name', and 'args' keys.

    Returns:
        str: A formatted string of tool calls, or "No tool calls" if the list is empty.

    """
    if tool_calls:
        formatted_calls = []
        for call in tool_calls:
            formatted_calls.append(
                f"Tool Call ID: {call['id']}, Function: {call['name']}, Arguments: {call['args']}"
            )
        return "\n".join(formatted_calls)
    return "No tool calls"

#
# Streaming using LangGraph API
#
async def UsingAPI():
    # Replace this with the URL of your own deployed graph
    URL = "http://localhost:8123"
    client = get_client(url=URL)

    # Search all hosted graphs
    assistants = await client.assistants.search()
    assistantid = "3-agent"
    question = "Multiply 2 and 3"

    # Create a new thread
    thread = await client.threads.create()

    # Input message
    input_message = HumanMessage(content=question)

    msgs = ""
    count = 0

    # Our agent is defined in assistant/agent.py (RCN: 3-agent.py).
    #
    # If you look at the code, you'll see that it does not have a breakpoint! Of course, we can add it to agent.py,
    # but one very nice feature of the API is that we can pass in a breakpoint!
    #
    # Here, we pass a interrupt_before=["assistant"].
    async for event in client.runs.stream(thread["thread_id"],
                                          assistant_id=assistantid,
                                          input={"messages": [input_message]},
                                          stream_mode="values",
                                          interrupt_before=["assistant"],):         ##<--- interrupt_before=["assistant"],
        count = count + 1

        # Just dump the event
        print("---event:" +str(count) +"-------------")
        print(f"Receiving new event of type: {event.event}...")

        # Getting messages state from the event. Using the last message only.
        messages = event.data.get('messages', [])
        if messages:
            msgs = msgs +"\n..........................\n" + str(convert_to_messages(messages)[-1])

    print(msgs)
    print("========================================================")


    # Get the current state
    current_state = await client.threads.get_state(thread['thread_id'])
    print("current_state:: " +str(current_state))

    # Get the last message in the state AND edit it............. Hahooo!!!
    last_message = current_state['values']['messages'][-1]
    print("last_message:: " +str(last_message))
    print("")
    last_message['content'] = "No, actually add 1 and -8!"  # Modifying content of the same message id
    print("last_message (edited):: " +str(last_message))
    print("")
    # Remember, as we said before, updates to the messages key will use the same add_messages reducer.
    # If we want to over-write the existing message, then we can supply the message id. Here, we did that.
    # We only modified the message content, as shown above.

    print("========================================================")

    input("PRESS ENTER TO RESUME")

    # Update State
    await client.threads.update_state(thread['thread_id'], {"messages": last_message})

    # Now, we resume by passing None
    count = 0
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=assistantid,
        input=None,
        stream_mode="values",
        interrupt_before=["assistant"],
    ):
        count = count + 1

        # Just dump the event
        print("---event:" + str(count) + "-------------")
        print(f"Receiving new event of type: {chunk.event}...")

        # Getting messages state from the event. Using the last message only.
        messages = chunk.data.get('messages', [])
        if messages:
            print(convert_to_messages(messages)[-1])

    print("========================================================")

    # Now, we're back at the assistant, which has our breakpoint.
    # We can again pass None to proceed.
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=assistantid,
        input=None,
        stream_mode="values",
        interrupt_before=["assistant"],
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        messages = chunk.data.get('messages', [])
        if messages:
            print(messages[-1])
        print("-" * 50)

import asyncio
asyncio.run(UsingAPI())