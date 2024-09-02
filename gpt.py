from time import sleep


def calculate_cost(total_tokens, price_per_million_tokens=5.00):
    """
    Calculate the cost of an API call based on the number of tokens used.

    Args:
        total_tokens (int): The total number of tokens used in the call.
        price_per_million_tokens (float): The price per 1 million tokens (default is $5.00 for GPT-4 mini).

    Returns:
        float: The cost of the API call in dollars.
    """
    # Calculate the cost by scaling the total tokens to a million
    cost = (total_tokens / 1000000) * price_per_million_tokens
    return round(cost, 4)


def get_diagnosis(client, input, assistant_id):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": input,
            },
        ],
    )

    ## Submit the thread to the assistant (as a new run)
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )
    # print(f"👉 Run Created: {run.id}")

    ## Wait for run to complete.
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        # print(f"🏃 Run Status: {run.status}")
        sleep(0.5)
    else:
        # print(f"🏁 Run Completed!")
        pass

    ## Get the latest message from the thread.
    message_response = client.beta.threads.messages.list(thread_id=thread.id)
    messages = message_response.data

    ## Summarize everything in a dictionary
    gpt_dict = {
        "id": run.id,
        "assistant_id": run.assistant_id,
        "instructions": run.instructions,
        "input_message": input,
        "gpt_message": messages[0].content[0].text.value,
        "completion_tokens": run.usage.completion_tokens,
        "prompt_tokens": run.usage.prompt_tokens,
        "total_tokens": run.usage.total_tokens,
        "total_cost": calculate_cost(run.usage.total_tokens),
        "temperature": run.temperature,
        "top_p": run.top_p,
        "model": run.model,
    }

    return gpt_dict
