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
    async for event in client.runs.stream(thread["thread_id"],
                                          assistant_id=assistantid,
                                          input={"messages": [input_message]},
                                          stream_mode="values"):
        count = count + 1

        # Just dump the event
        print("---event:" +str(count) +"-------------")
        print(event)

        # Getting messages state from the event. Using the last message only.
        messages = event.data.get('messages', None)
        if messages:
            msgs = msgs +"\n..........................\n" + str(convert_to_messages(messages)[-1])

    print("========================================================")
    print(msgs)

    #
    # There are some new streaming mode that are only supported via the API.
    # For example, we can use ***messages mode*** to better handle the above case!
    #
    print("========================================================")
    '''
    Event types seen :
    ------------------
    metadata
    messages/metadata
    messages/partial
    messages/complete
    '''
    async for event in client.runs.stream(thread["thread_id"],
                                          assistant_id=assistantid,
                                          input={"messages": [input_message]},
                                          stream_mode="messages"):
        print(str(event.event))


    print("========================================================")
    '''
    Event types seen :
    ------------------
    metadata
    messages/metadata
    messages/partial
    messages/complete
    '''
    async for event in client.runs.stream(thread["thread_id"],
                                          assistant_id=assistantid,
                                          input={"messages": [input_message]},
                                          stream_mode="messages"):
        # Handle metadata events
        if event.event == "metadata":
            print(f"Metadata: Run ID - {event.data['run_id']}")
            print("-" * 50)
        # Handle messages/metadata events
        elif event.event == "messages/metadata":
            print(f"messages/Metadata: {event.data}")
            print("-" * 50)
        # Handle partial message events
        elif event.event == "messages/partial":
            for data_item in event.data:
                # Process user messages
                if "role" in data_item and data_item["role"] == "user":
                    print(f"Human: {data_item['content']}")
                else:
                    # Extract relevant data from the event
                    tool_calls = data_item.get("tool_calls", [])
                    invalid_tool_calls = data_item.get("invalid_tool_calls", [])
                    content = data_item.get("content", "")
                    response_metadata = data_item.get("response_metadata", {})

                    if content:
                        print(f"AI: {content}")

                    if tool_calls:
                        print("Tool Calls:")
                        print(format_tool_calls(tool_calls))

                    if invalid_tool_calls:
                        print("Invalid Tool Calls:")
                        print(format_tool_calls(invalid_tool_calls))

                    if response_metadata:
                        finish_reason = response_metadata.get("finish_reason", "N/A")
                        print(f"Response Metadata: Finish Reason - {finish_reason}")
            print("-" * 50)
        # Handle complete message events
        elif event.event == "messages/complete":
            print(f"messages/complete: content={event.data[0]['content']}")
            print("-" * 50)
        # Handle unknown message events
        else:
            print(f"ERROR:: Unknown Event Type: " +str(event.event))
            print("-" * 50)


import asyncio
asyncio.run(UsingAPI())