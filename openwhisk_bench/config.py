import argparse
import logging as log
import json
import os
import yaml
class Config:
    def __init__(self):

        default_config_path = os.path.join('openwhisk_bench/configs', 'defaults.yaml')
        self.load_defaults(default_config_path)


    def load_defaults(self, config_path):
        """
        Load default configurations from a yaml file
        """
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        self.num_runs = config['num_runs']
        self.num_invocations = config['num_invocations']
        self.warmup_invocations = config['warmup_invocations']
        self.workers = config['workers']
        self.verbose = config['verbose']
        self.print_csv = config['print_csv']
        self.function = config['function']
        self.blocking = config['blocking']
        self.input_file = config['input_file']
        self.input_string = config['input_string']
        self.output_file = config['output_file']
        self.time_limit = config['time_limit']
        self.time_precision = config['time_precision']
        self.apihost = config['apihost']
        self.authorization = config['authorization']
        self.payload = config['payload']


    def print_config(self):
        """
        Print the configuration parameters in a formatted way
        """

        # Organizing configurations in a dictionary
        config = {
            "Number of runs": self.num_runs,
            "Number of invocations": self.num_invocations,
            "Warmup runs": self.warmup_invocations,
            "Workers": self.workers,
            "Verbose": self.verbose,
            "print_csv": self.print_csv,
            "Function": self.function,
            "Blocking": self.blocking,
            "Input file": self.input_file,
            "Input string": self.input_string,
            "Output file": self.output_file,
            "Time limit (s)": self.time_limit,
            "Time precision (ms)": self.time_precision,
            "APIHOST": self.apihost,
            "Authorization": self.authorization
        }

        if self.payload is not None:
            try:
                config["Payload"] = json.dumps(self.payload, indent=4)
            except json.JSONDecodeError:
                config["Payload"] = str(self.payload)
        else:
            config["Payload"] = "None"

        # Printing configurations in a formatted way
        log.info("Configuration Parameters:")
        for key, value in config.items():
            log.info(f"{key}: {value}")
        log.info("\n\n")

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Arguments for benchmarking')

        # Basic parameters
        parser.add_argument('-n', '--num-runs', type=int, default=self.num_runs, metavar='',
                            help=f'Number of runs for each benchmark (default: {self.num_runs})')
        
        parser.add_argument('-i', '--num-invocations', type=int, default=self.num_invocations, metavar='',
                            help=f'Number of invocations for each benchmark (default: {self.num_invocations})')
        
        parser.add_argument('-w', '--warmup_invocations', type=int, default=self.warmup_invocations, metavar='',
                            help=f'Number of warmup invocations (default: {self.warmup_invocations})')

        parser.add_argument('-W', '--workers', type=int, default=self.workers, metavar='',
                            help=f'Number of workers invoked por activation (for burst OpenWhisk) (default: {self.workers})')
        
        parser.add_argument('-f', '--function', type=str, default=self.function, metavar='',
                            help=f'Name of the function to benchmark (default: {self.function})')
        
        parser.add_argument('-b', '--blocking', action='store_true', default=self.blocking,
                    help='Enable blocking call (default: {})'.format(self.blocking))
        
        parser.add_argument('-t', '--time-limit', type=int, default=self.time_limit, metavar='',
                            help=f'Time limit for each benchmark (default: {self.time_limit} seconds)')

        parser.add_argument('-T', '--time-precision', type=int, default=self.time_precision, metavar='',
                            help=f'Time precision for measuring elapsed time (default: {self.time_precision} ms)')
        
        parser.add_argument('-v', '--verbose', action='store_true', default=self.verbose,
                            help='Enable verbose output (default: {})'.format(self.verbose))
        
        parser.add_argument('-c', '--print-csv', action='store_true', default=self.print_csv,
                            help='Print results in CSV format (default: {})'.format(self.print_csv))

        # Input-related parameters (mutually exclusive group)
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('-I', '--input_file', type=str, default=self.input_file, metavar='',
                                 help='Input file for the function (default: {})'.format(self.input_file))

        input_group.add_argument('-s', '--input_string', type=str, default=self.input_string, metavar='',
                                 help='Input string for the function (default: {})'.format(self.input_string))
                                
        parser.add_argument('-o', '--output_file', type=str, default=self.output_file, metavar='',
                            help='Output file for the function (default: {})'.format(self.output_file))

        # API-related parameters
        parser.add_argument('-A', '--apihost', type=str, default=self.apihost, metavar='',
                            help='APIHOST (default: {})'.format(self.apihost))

        parser.add_argument('-a', '--authorization', type=str, default=self.authorization, metavar='',
                            help='Authorization (default: {})'.format(self.authorization))

        parser.add_argument('-y', '--yaml', type=str,
                            help='Load configurations from a YAML file (other parameters will be ignored)')

        args = parser.parse_args()

        if args.yaml:
            print(f"Loading configurations from {args.yaml}")
            self.load_defaults(args.yaml)
        else:
            print("Loading configurations from command line arguments")
            # Updating configuration with parsed arguments
            self.num_runs = args.num_runs
            self.num_invocations = args.num_invocations
            self.warmup_invocations = args.warmup_invocations
            self.workers = args.workers
            self.function = args.function
            self.blocking = args.blocking
            self.input_file = args.input_file
            self.input_string = args.input_string
            self.output_file = args.output_file
            self.time_limit = args.time_limit
            self.time_precision = args.time_precision
            self.apihost = args.apihost
            self.authorization = args.authorization
            self.print_csv = args.print_csv
            self.verbose = args.verbose

            if self.input_file:
                self.payload = json.loads(open(self.input_file).read())
            elif self.input_string:
                self.payload = json.loads(self.input_string)
        
        if self.verbose: log.basicConfig(format='%(message)s', level=log.INFO)