from time import sleep


def get_diagnosis(client, input, assistant_id):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": input,
            },
        ],
    )

    # Submit the thread to the assistant (as a new run).
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id
    )
    print(f"👉 Run Created: {run.id}")

    # Wait for run to complete.
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"🏃 Run Status: {run.status}")
        sleep(0.5)
    else:
        print(f"🏁 Run Completed!")

    # Get the latest message from the thread.
    message_response = client.beta.threads.messages.list(thread_id=thread.id)
    messages = message_response.data

    # Print the latest message.
    latest_message = messages[0]
    print(f"💬 Response: {latest_message.content[0].text.value}")
    return latest_message.content[0].text.value
