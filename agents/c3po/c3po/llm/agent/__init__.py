"""
1) Ask LLM to generate command list with verification command.

2) The commands will be run in order. For each command, the output
of the verification is fed to an LLM which will determine if the command
was successful. If successful, the next command is run an verified.
Otherwise the command execution is stopped and the error is fed to an LLM
to fix the command.

"""