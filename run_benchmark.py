from openwhisk_bench import Config, run_benchmark

def main():
    config = Config()
    config.parse_arguments()
    config.print_config()
    run_benchmark(config)


if __name__ == '__main__':
    main()