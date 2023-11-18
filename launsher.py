# Press the green button in the gutter to run the script.
import libtmux as tmux
import argparse
import json
import subprocess as sp
from pathlib import Path

class Project:
    def __init__(self, json):
        self.name = json["project"]
        self.repository = json["project"]
        self.applications = json["applications"]
        self.scenarios = json["scenarios"]
        self.tmux_session_name = f"launsher-{self.name}"
        self.cmake_setup_args = json.get("cmake-setup-args", "")

        # Start tmux session in background
        sp.run(["tmux", "new-session", "-d", "-s", self.tmux_session_name])

        server = tmux.Server()
        self.tmux_session = server.sessions.filter(session_name=self.tmux_session_name)[0]

    def tmux_attach_session(self):
        sp.run(["tmux", "attach-session", "-t", self.tmux_session_name])

    def run_scenario(self, scenario_name):
        scenario = self.scenarios[scenario_name]
        for scenario_entry in scenario:
            self.run_scenario_entry(scenario_entry)

        self.tmux_session.kill_window(":0") # Delete first window created by default
        self.tmux_attach_session()

    def get_cmake_build_dir_name(cmake_config):
        match cmake_config:
            case "release":
                return "cmake-build-release"
            case "debug":
                return "cmake-build-debug"
            case "relwithdebinfo":
                return "cmake-build-relwithdebinfo"
            case _:
                raise Exception(f"Invalid cmake config: {cmake_config}.")

    def get_cmake_build_type(cmake_config):
        match cmake_config:
            case "release":
                return "Release"
            case "debug":
                return "Debug"
            case "relwithdebinfo":
                return "RelWithDebInfo"
            case _:
                raise Exception(f"Invalid cmake config: {cmake_config}.")

    def run_scenario_entry(self, scenario_entry):
        cmake_setup_args = self.cmake_setup_args
        app = self.applications[scenario_entry["app"]]
        delay = scenario_entry.get("delay", "0")
        git_repo = app["repository"]
        host = app.get("host", None)
        path = Path(app["path"]).absolute()
        path_parent = path.parent.absolute()
        cmake_config = app["cmake-config"]
        cmake_target = scenario_entry["cmake-target"]
        cmd = scenario_entry["cmd"]
        cmake_build_dir_name = Project.get_cmake_build_dir_name(cmake_config)
        cmake_build_type = Project.get_cmake_build_type(cmake_config)
        window = self.tmux_session.new_window(attach=False, window_name=scenario_entry["name"])
        pane = window.panes[0]

        if host is not None:
            pane.send_keys(f"ssh {host}")


        # Send all the commands
        # Chain all with `&&`, so of one fails, stop here
        all_cmds = ":"

        # Clone the repository if the directory does not exist
        all_cmds += f" && if [ ! -e '{path}' ]; then mkdir -p {path_parent} && git clone {git_repo} {path}; fi"

        all_cmds += f" && cd {path}"
        all_cmds += f" && git pull"
        all_cmds += f" && mkdir -p {cmake_build_dir_name}"
        all_cmds += f" && cd {cmake_build_dir_name}"
        all_cmds += f" && cmake .. {cmake_setup_args} && cmake --build . --target {cmake_target}"
        all_cmds += f" && {cmd}"

        pane.send_keys(all_cmds)


def run(json_path: str, scenario: str) -> None:
    with open(json_path) as json_file:
        project = Project(json.load(json_file))
    project.run_scenario(scenario)

def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    # 1st positional argument
    parser.add_argument("json_path", help="Path to the project's JSON file")
    parser.add_argument("scenario", help="Scenario to run")
    return parser

def main() -> None:
    args = get_arg_parser().parse_args()
    json_path = args.json_path
    run(json_path, args.scenario)

if __name__ == '__main__':
    main()