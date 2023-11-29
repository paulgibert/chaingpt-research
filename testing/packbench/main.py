from melange import melange_build_wolfi
from apko import apko_build_wolfi_test_image, apko_run_command
from log_parser import LogLevel, LogParser


err = melange_build_wolfi("grype.yaml",
                    arch="x86_64")

if err is not None:
    print("Build ERROR: " + err)
    exit()

image, tag = apko_build_wolfi_test_image("grype", "test", "x86_64")

if image is not None:
    r = apko_run_command(image, tag + "-amd64", "ls /usr/bin")
    import pdb
    pdb.set_trace()
    print("done")