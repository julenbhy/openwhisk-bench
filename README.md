# openwhisk-bench

This project provides a benchmarking tool for measuring the performance of OpenWhisk functions, particularly in a cloud computing environment using WebAssembly. It allows users to execute synchronous or asynchronous function invocations, collect various metrics, and analyze the results.


## Features

- **Configurable Runs and Invocations**: Set the number of runs and invocations for each benchmark.
- **Synchronous and Asynchronous Calls**: Supports both blocking and non-blocking function executions.
- **Customizable Payloads**: Send payloads from a file or as a string input.
- **Metrics Collection**: Collects key performance metrics such as:
  - `initTime:` Time it took to initialize an action, such as Docker initialization or setting up the execution environment.
  - `waitTime:` Internal system hold time before the action starts executing, which may include queuing or scheduling delays.
  - `duration:` Actual time the action code was running, measured from the start to the end of the execution.
  - `client elapsed time:` Time measured by the client from when the request was sent until the response was received, including network latency and server processing.
  - `elapsed:` Time measured by the system for processing the request, provided directly by the server in microseconds.
  - `success:` Invocation success rate, indicating whether the function execution completed without errors.
- **Verbose Logging**: Option to enable detailed logging of the benchmarking process.
- **Result Storage**: Outputs metrics to the console and optionally saves them to a file.

# Usage:

The tool can be executed from the command line with various arguments to customize the benchmarking process.

## Basic Example
```bash
python run_benchmark.py -f add -s '{"param1": 3, "param2": 1}'
```

# TODO:
- breaks when running multiple worker invocations
