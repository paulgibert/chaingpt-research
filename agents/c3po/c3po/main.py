import argparse
from c3po.agent import run_agent


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("package",
                        help="The name of the package")
    parser.add_argument("version",
                        help="The version of the package")
    parser.add_argument("--workspace",
                        default=".agent-workspace",
                        help="The name of the tmp directory used as a workspace")
    parser.add_argument("--output-yaml",
                        default="out.yaml",
                        help="The location to save the generated YAML")
    parser.add_argument("--output-log",
                        default="agent.log",
                        help="The location to save the log file")
    parser.add_argument("--output-summary",
                        required=False,
                        help="The location to save the build summary")
    parser.add_argument("--repository",
                        required=False,
                        help="Force the agent to use a GitHub repository")
    return parser.parse_args()


def run_agent_cmd():
    args = parse_args()
    run_agent(args.package, args.version,
              output_yaml=args.output_yaml,
              repository=args.repository,
              workspace=args.workspace,
              output_log=args.output_log,
              output_summary=args.output_summary)


if __name__ == "__main__":
    run_agent_cmd()