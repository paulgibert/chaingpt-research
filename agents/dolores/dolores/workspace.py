# stdlib
from typing import List
import os
import shutil
import glob
import pathlib

# 3rd party
from sh import git


# TODO: Read file methods do not support files that cannot fit in memory


class Workspace:
    def __init__(self, url: str, branch_or_tag: str=None, parent_dir: str="/tmp"):
        self.url = url
        self.branch_or_tag = branch_or_tag

        self.path = os.path.join(parent_dir, "dolores")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.repo_path = os.path.join(self.path, "repo")
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

        if branch_or_tag is None:
            git.clone(url, self.repo_path)
        else:
            git.clone(url, "-b", branch_or_tag, self.repo_path)

    def _trim_parent_dir(self, path: str) -> str:
        parent_len = len(pathlib.Path(self.repo_path).parts)
        child_parts = pathlib.Path(path).parts[parent_len:]
        return os.path.join(*child_parts)

    def search_path(self, path: str) -> List[str]:
        results = glob.glob(os.path.join(self.repo_path, path))
        return [self._trim_parent_dir(r) for r in results]

    def read_file(self, path: str) -> str:
        local_path = os.path.join(self.repo_path, path)
        if not os.path.exists(local_path):
            print(local_path)
            raise ValueError(f"{path} is not a valid path")

        with open(local_path, "r", encoding="utf-8") as f:
            text = f.read()
            return text

