from typing import List
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool, StructuredTool


from .file import (file_read_from_path,
                   file_write_to_path,
                   file_refine_and_read)

class FileToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in (
                file_read_from_path,
                file_write_to_path,
                file_refine_and_read)]


from .system import system_run_sh, system_list_dir

class SystemToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in (
                system_run_sh,
                system_list_dir)]
    

from .git import git_list_branches_and_tags, git_clone

class GitToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in (
                git_list_branches_and_tags,
                git_clone)]


from .web import web_websearch

class WebToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in (
                web_websearch,)]


from .melange import (melange_add_header,
                      melange_add_build_dependency,
                      melange_add_pipeline_runs,
                      melange_add_pipeline_git_checkout,
                      melange_add_pipeline_go_build,
                      melange_write_model)

class MelangeToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(f) for f in (
                melange_add_header,
                melange_add_build_dependency,
                melange_add_pipeline_runs,
                melange_add_pipeline_git_checkout,
                melange_add_pipeline_go_build,
                melange_write_model)]
