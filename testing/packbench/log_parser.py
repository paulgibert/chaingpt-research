from typing import List, Tuple, Iterator
import os
from enum import Enum
import re


class LogLevel(Enum):
    """
    The various log levels used by the apko logger
    """
    PANIC = 0
    FATAL = 0 # PANIC and FATAL are treated equivalently in the apko logger
    ERROR = 1
    WARN = 2
    INFO = 3
    DEFAULT = 4


class LogSymbol(Enum):
    """
    The symbols for each log level used in the apko logger
    """
    # The padded space is included in the apko logger
    PANIC = "🛑 " 
    FATAL = "🛑 "
    ERROR = "❌ "
    WARN = "⚠️ "
    INFO = "ℹ️ "
    DEFAULT =  "❕"


def _get_symbols_pattern(level: LogLevel) -> List[str]:
    """
    Builds and returns a regular expression matching the symbols of every
    log level at or below the provided log level
    """
    symbols = []
    for e in LogLevel:
        if e.value <= level.value:
            symbols.append(getattr(LogSymbol, e.name).value)
    return f"({'|'.join(symbols)})"


def _get_level(line: str) -> LogLevel:
    """
    Gets the level of a log msg
    """
    for symbol in LogSymbol:
        if symbol.value in line:
            return getattr(LogLevel, symbol.name)


class LogParser:
    """
    A parser object for apko log files
    """
    def __init__(self, log_file: str):
        """
        @param log_file: The log file
        @raises `FileNotFoundError` if the log file does not exist 
        """
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"{log_file} not found")
        self.log_file = log_file

    def iter_logs(self, level: LogLevel=LogLevel.DEFAULT) -> Iterator[Tuple[LogLevel, str]]:
        """
        Returns an `Iterator` over the logs.

        @param level: The maximum log level
        @returns: An `Iterator` over the logs. Each element is a `Tuple` of
                  the form (log level, log message).
        """
        symbols_pattern = _get_symbols_pattern(level)

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                m = re.match(f"{symbols_pattern}.+\|", line)
                if m is None:
                    continue
                else:
                    level = _get_level(line)
                    msg = line[m.end(0):-1].strip(" ")
                    yield (level, msg)
        
    
    def iter_melange_build_errors(self, history_len=1) -> Iterator[Tuple[str, List[Tuple[LogLevel, str]]]]:
        """
        Returns an `Iterator` over melange build errors found in the logs.
        Melange build reports build errors at the warning level followed by a
        string containing ERROR. Every instance of these ERROR strings are
        iterated over and returned with a history of the last warning log messages.

        @param history_len: The max number of recent log messages to report
                            for each error found.
        @returns: An `Iterator` over the errors. Each element is a `Tuple` of
                  the form (error message, [(log level, log message), (log level, log message), ...).
        """
        history = []
        for level, msg in self.iter_logs(LogLevel.WARN):
            

            symbols_pattern = _get_symbols_pattern(level)

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if "ERROR" in line:
                    yield (line.strip("\n"), history)
                else:
                    m = re.match(f"{symbols_pattern}.+\|", line)
                    if m is None:
                        continue
                    else:
                        level = _get_level(line)
                        msg = line[m.end(0):-1].strip(" ")
                        while len(history) >= history_len:
                            history.pop(0)
                        history.append((level, msg))
