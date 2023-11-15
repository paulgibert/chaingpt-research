"""
Classes representing different aspects of a melange YAML
"""

from typing import Dict
from abc import abstractmethod
import yaml


class MelangePipeline:
    """
    Base class for pipeline stage classes
    """
    @abstractmethod
    def as_dict(self) -> Dict:
        """
        Returns the Dict representation of the
        pipeline stage. Override this method in children.
        """
        raise NotImplementedError


class RunsPipeline(MelangePipeline):
    """
    Represents a runs pipeline stage
    """
    def __init__(self, command: str):
        self.command = command
    
    def as_dict(self) -> Dict:
        data = {
            "runs": self.command
        }

        return data
    

class GitCheckoutPipeline(MelangePipeline):
    """
    Represents a git-checkout pipeline stage
    """
    def __init__(self, repository: str, branch: str=None,
                 tag: str=None):
        self.repository = repository
        self.branch = branch
        self.tag = tag

    def as_dict(self) -> Dict:
        data = {
            "uses": "git-checkout",
            "with": {
                "repository": self.repository,
            }
        }
        # Prioritizes branch over tag
        if self.branch is not None:
            data["with"]["branch"] = self.branch

        elif self.tag is not None:
            data["with"]["tag"] = self.tag
        return data


class GoBuildPipeline(MelangePipeline):
    """
    Represents a go/build pipeline stage
    """
    def __init__(self, packages: str, output: str,
                 modroot: str=None, prefix: str=None,
                 ldflags: str=None, install_dir: str=None):
        self.packages = packages
        self.output = output
        self.modroot = modroot
        self.prefix = prefix
        self.ldflags = ldflags
        self.install_dir = install_dir
    
    def as_dict(self) -> Dict:
        data = {
            "uses": "go/build",
            "with": {
                "packages": self.packages,
                "output": self.output
            }
        }

        if self.modroot is not None:
            data["with"]["modroot"] = self.modroot
        if self.prefix is not None:
            data["with"]["prefix"] = self.prefix
        if self.ldflags is not None:
            data["with"]["ldflags"] = self.ldflags
        if self.install_dir is not None:
            data["with"]["install_dir"] = self.install_dir
    
        return data


class MelangeYaml:
    """
    Represents a melange YAML file
    """
    def __init__(self, package: str, version: str,
                 description: str, license: str):
        self.package = package
        self.version = version
        self.description = description
        self.license = license
        self.build_deps = []
        self.pipelines = []

    def add_build_dependency(self, dep: str):
        """
        Adds a build dependency
        """
        self.build_deps.append(dep)

    def add_pipeline(self, pipeline: MelangePipeline):
        """
        Adds a pipeline stage
        """
        self.pipelines.append(pipeline)

    def dump_yaml(self, f: any):
        """
        Compiles the object to a melange YAML file and
        dumps the result.
        @param f: The file object to dump to
        """
        # header
        data = {
            "package": {
                "name": self.package,
                "version": self.version,
                "description": self.description,
                "copyright": [{"license": self.license}]
            }
        }

        # environment
        if len(self.build_deps) > 0:
            data["environment"] = {}
            data["environment"]["contents"] = {}
            data["environment"]["contents"]["packages"] = self.build_deps

        # pipeline
        if len(self.pipelines) > 0:
            data["pipeline"] = [p.as_dict() for p in self.pipelines]

        # dump
        yaml.dump(data, f, sort_keys=False)
