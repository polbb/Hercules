import time

def wait_on_run(client, run, thread):
    while run.status=='queued' or run.status=='in_progress':
        run = client.beta.threads.runs.retrieve(
            run_id= run.id,
            thread_id= thread.id
        )
        time.sleep(2)
        print(run.status)
    return run

def display_thread_messages(messages):
    for thread_message in messages.data:
        print(thread_message.content[0].text.value)
        print('-'*120)

def create_thread_message_lists(messages):
    messages_list = []
    for thread_message in messages.data:
        messages_list.append(thread_message.content[0].text.value)
    return messages_list

def create_a_thread(client):
    thread = client.beta.threads.create()
    return thread

def create_a_message(client, thread, message_content, file_id=None):
    message = client.beta.threads.messages.create(
        thread_id= thread.id,
        role= 'user',
        content= message_content,
        file_ids=file_id, 
        )
    return message

def create_a_run(client, assistant, thread):
    run = client.beta.threads.runs.create(
        assistant_id= assistant.id,
        thread_id= thread.id,
        )
    return run