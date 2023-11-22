from typing import List
import logging
import time
from openai import OpenAI


ASSISTANT_ID = "asst_6f9uzyHimrjjggaKfSw5DGeG"
PROMPT_TEXT = """
Provide instructions for building %s version %s from source.
"""
STATUS_DONE = ["cancelled", "failed", "completed", "expired"]
POLL_INTERVAL = 3
# STATUS_AWAITING_ACTION = ["requires_action"]


def _create_run(client, prompt: str, file_ids: List[str]):
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
    # Create an empty thread
    thread = client.beta.threads.create()
    # Create a message and attach files
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
        file_ids=file_ids
    )
    # Create and return a new run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    return run


# def _yield_on_required_action(client, run):
#     while run.status not in STATUS_DONE:
#         while run.status not in STATUS_AWAITING_ACTION:
#             time.sleep(3)
#             run = client.beta.threads.runs.retrieve(
#                 run.id, thread_id=run.thread_id)
#             print(run.status)
#         if run.status in STATUS_AWAITING_ACTION:
#             yield run
#     return run


# def _call(tool_call, thread_id:str):
#     tool = getattr(tools, tool_call.function.name)
#     kwargs = json.loads(tool_call.function.arguments)
#     return tool(**kwargs, thread_id=thread_id)


# def _call_tools(run):
#     tool_calls = run.required_action.submit_tool_outputs.tool_calls
#     tool_outputs = [{
#         "tool_call_id": tc.id,
#         "output": _call(tc, run.thread_id)
#         } for tc in tool_calls]
#     return tool_outputs


# def _send_tool_outputs(client, run, tool_outputs):
#     client.beta.threads.runs.submit_tool_outputs(
#         thread_id=run.thread_id,
#         run_id=run.id,
#         tool_outputs=tool_outputs)


def _create_files(client, doc_file_paths: List[str]) -> List[str]:
    file_ids = []
    for path in doc_file_paths:
        with open(path, "rb") as f:
            file = client.files.create(
                file=f,
                purpose="assistants")
            logging.info("Created file %s", path)
            file_ids.append(file.id)
    return file_ids


def _delete_files(client, file_ids: List[str]):
    for id in file_ids:
        client.files.delete(id)
        logging.info("Deleted %s", id)


def _get_top_message_text(client, run) -> str:
    msg_list = list(client.beta.threads.messages.list(thread_id=run.thread_id))
    return msg_list[0].content[0].text.value


def run_assistant(package: str, version: str, doc_file_paths: List[str]) -> str:
    """
    Runs an OpenAI assistant configured to provide build instructions from uploaded
    documentation.

    @param package: The package
    @param version: The package version
    @param doc_file_paths: A `List` of local paths to documentation
    @returns Build instructions
    """
    client = OpenAI()
    prompt = PROMPT_TEXT % (package, version)
    file_ids = _create_files(client, doc_file_paths)
    logging.info("Creating run")
    run = _create_run(client, prompt, file_ids)
    while run.status not in STATUS_DONE:
        time.sleep(POLL_INTERVAL)
        logging.info("Polling %s. Status: %s", run.id, run.status)
        if run.status == "requires_action":
            logging.info("Run requires action. Breaking run loop")
            break
        run = client.beta.threads.runs.retrieve(
            run.id, thread_id=run.thread_id)
    logging.info("Run complete")
    _delete_files(client, file_ids)
    return _get_top_message_text(client, run)
