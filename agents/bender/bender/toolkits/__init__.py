from typing import List
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool, StructuredTool
from .file import (file_read, file_write, file_refine_text, file_refine_language,
                   file_store_lookup_text, file_store_lookup_language)
from .system import run_sh, list_dir
from .git import git_list_branches_and_tags, git_clone
from .melange import (melange_add_header,
                      melange_add_build_dependency,
                      melange_add_pipeline_runs,
                      melange_add_pipeline_git_checkout,
                      melange_add_pipeline_go_build,
                      melange_write_model)


class FileToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(file_read),
            StructuredTool.from_function(file_store_lookup_text),
            StructuredTool.from_function(file_store_lookup_language),
            StructuredTool.from_function(file_refine_text),
            StructuredTool.from_function(file_refine_language),
            StructuredTool.from_function(file_write)
        ]


class SystemToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in [
                run_sh, list_dir
            ]
        ]


class GitToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in [
                git_clone,
                git_list_branches_and_tags
            ]
        ]


class FileToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in [
                file_read, file_write, file_refine_text,
                file_refine_language, file_store_lookup_text,
                file_store_lookup_language
            ]
        ]


class MelangeToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in [
                melange_add_header,
                melange_add_build_dependency,
                melange_add_pipeline_runs,
                melange_add_pipeline_git_checkout,
                melange_add_pipeline_go_build,
                melange_write_model
            ]
        ]