from typing import List
import os
import shutil
import logging
import time
from openai import OpenAI, APIStatusError
from yaspin import yaspin
from yaspin.spinners import Spinners
from colorama import Fore
from c3po.melange import get_build_step_prompts
from c3po.repo import GitRepo


ASSISTANT_ID = os.environ["OPENAI_API_ASSISTANT_ID"]
PROMPT_TEXT = """
Generate minimalist and straightforward instructions for compiling and
installing the source code of the software project %s,
version %s. The GitHub repository is %s. Checkout %s for the correct version.
The instructions should be concise and solely focused on the build and installation process,
excluding any steps related to testing, linting, or other unrelated tasks.
If multiple build methods are available, choose the most direct and
uncomplicated method and provide a consistent set of steps without
mixing different approaches. You will respond in JSON form only.

The response should contain the following fields:

summary: A description of the components the project uses and how they are built. If able, provide
         step-by-step build instructions.

description: A single sentence description of the project. It should not start with the project's name.

license: The license under which the project is released. Include the license name only.

steps: An ordered list of build commands.
       Each build step is an object with specific fields depending on its type.
       There are different step types, each requiring unique fields. If using
       a place holder value or reporting any value that is not meant to be
       interpreted literally, surround the value with  "<< >>" e.g <<place holder>>.
       Assume you have root privileges on the system (no need to use sudo).

%s

Here is a list of the first 100 files in the projects GitHub repository:

%s
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


def _make_prompt(package: str, version: str, repo: GitRepo, file_list: List[str]) -> str:
    steps = "\n\n".join(get_build_step_prompts())
    file_list_str = "\n".join(file_list)
    return PROMPT_TEXT % (package, version, repo.url,
                          repo.curr_branch_or_tag, steps,
                          file_list_str)


def _rename_file(path: str, new_path: str) -> str:
    shutil.move(path, new_path)
    return new_path


def _create_files(client, doc_file_paths: List[str]) -> List[str]:
    file_ids = []
    for path in doc_file_paths:
        if "." not in path:
            path = _rename_file(path, path + ".txt") # For some reason this still does not ensure every file gets uploaded without error
        logging.info("Creating file %s", path)
        with open(path, "rb") as f:
            try:
                with yaspin(Spinners.line, text=Fore.BLUE + f"Uploading {path}", color="blue"):
                        file = client.files.create(
                            file=f,
                            purpose="assistants")
                print(Fore.GREEN + f"Uploaded {path}")
                logging.info("Created file %s", path)
                file_ids.append(file.id)
            except APIStatusError as e:
                print(Fore.RED + " Error uploading %s", path)
                logging.error(str(e.response))
    return file_ids


def _delete_files(client, file_ids: List[str]):
    for id in file_ids:
        client.files.delete(id)
        logging.info("Deleted %s", id)


def _get_top_message_text(client, run) -> str:
    msg_list = list(client.beta.threads.messages.list(thread_id=run.thread_id))
    return msg_list[0].content[0].text.value


def _first_n_repo_files(repo: GitRepo, n: int=100) -> List[str]:
    return [os.path.join(d, f) for d, f in repo.get_files()[:n]]


def run_assistant(package: str, version: str, repo: GitRepo, doc_file_paths: List[str]) -> str:
    """
    Runs an OpenAI assistant configured to provide build instructions from uploaded
    documentation.

    @param package: The package
    @param version: The package version
    @param doc_file_paths: A `List` of local paths to documentation
    @returns Build instructions
    """
    client = OpenAI()
    file_list = _first_n_repo_files(repo, n=100)
    prompt = _make_prompt(package, version, repo, file_list)
    logging.info("Using assistant prompt:\n%s", prompt)

    print(Fore.BLUE + "Initializing OpenAI assistant")
    file_ids = _create_files(client, doc_file_paths)

    logging.info("Creating run")
    with yaspin(Spinners.line, text=Fore.BLUE + "Generating YAML with OpenAI assistant", color="blue"):
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
    with yaspin(Spinners.line, text=Fore.BLUE + "Cleaning up OpenAI assistant env"):
        _delete_files(client, file_ids)
    # TODO: If the assistant fails, this method will sometimes fetch the prompt as there
    # is no response on top.
    return _get_top_message_text(client, run)
