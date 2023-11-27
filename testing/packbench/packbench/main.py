from melange import melange_build_wolfi
from log_parser import LogLevel, LogParser


melange_build_wolfi("grype.yaml",
                    arch="x86_64")

parser = LogParser("build.log")

for error_msg, history in parser.iter_melange_build_errors():
    print(error_msg)
    for level, msg in history:
        print(f"\t{level.name}: {msg}")
    print()
