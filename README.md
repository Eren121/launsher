# Launsher

This project aims to more easely **compile** and **test** applications based on **CMake** and **git** running on remote servers using ssh.
A project configuration is contained into a JSON file.

## Example

`example.json`:
```json
{
  "project": "my-client-server-application",
  
  "applications": {
    "test1": {
      "host": "192.168.0.1",
      "path": "/home/me/path-to-the-git-project",
      "cmake-config": "release",
      "repository": "https://github.com/me/my-app"
    }
  },
  
  "scenarios": {
    "client-server-test": [
      {
        "name": "client",
        "app": "test1",
        "cmake-target": "my-client",
        "cmd": "./my-client --arg1 --arg2"
      },
      {
        "name": "server",
        "app": "test1",
        "cmake-target": "my-server",
        "cmd": "./my-server --arg1 --arg2"
      }
    ]
  }
}
```

Running `launsher.py example.json client-server-test` will run both the client and the server into a **tmux** session over **ssh**.

## Configuration file

- **project** (string): The name of your project.
- **applications** (object): Each key is the name of one code project.
  - **host** (string): The IP address where to compile and run the application.
  - **path** (string): The path to the application on the host.
  - **cmake-config** (string): One of `debug`, `release`, `relwithdebinfo`. It will compile into the subdirectory `cmake-build-<config>`.
  - **repository** (string): The path to the git repository of your project.
- **scenarios** (object): Each key is the name of one scenario, containing an array of applications to launch.
  - **name** (string): The descriptive name of the application to run. 
  - **app** (string): The name (JSON key) of the application to run.
  - **cmake-target** (string): The name of the CMake target to compile
  - **cmd** (string): The name of the binary (with arguments), relative to the CMake's build directory.

## Actions

For one scenarios, the applications are run in order, doing theses actions for each application:
1. Connect via SSH to the host
2. Pull the git repository to detect any change
3. Try to compile the project
4. Run the application

At the end, a tmux session is launch, with a window for each application.