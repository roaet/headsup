#Headsup

Headsup is a git tool for the Networks Control Plane team. It can be used for
other projects and teams with proper configuration.

##Usage

```
Usage: headsup [OPTIONS] REPO

Options:
--config FILENAME    Configuration file for runtime
--start-branch TEXT  Start branch for comparison
--end-branch TEXT    End branch for comparison
--columns TEXT       Comma-separated list of columns to show during output
--help               Show this message and exit.
```

##Limitations

Currently if your running user doesn't have access to the partiuclar
repositories configured it will fail to fetch.
