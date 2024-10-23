
import time
import requests
import logging as log
import json
import pprint
from .metrics import extract_metrics, benchmark_statistics, format_results, write_results_to_file_csv


def format_response_dict(response):
    """
    Format the __dict__ of a response, including decoding and formatting the '_content' field if it's JSON.
    """
    response_dict = response.__dict__.copy()

    # Try to decode and pretty-print the '_content' field if it contains JSON data
    if isinstance(response_dict.get('_content'), bytes):
        try:
            decoded_content = response_dict['_content'].decode('utf-8')  # Decode bytes to string
            json_content = json.loads(decoded_content)  # Parse string as JSON
            response_dict['_content'] = json_content  # Store as a dict instead of a string
        except (UnicodeDecodeError, json.JSONDecodeError):
            # If _content is not valid JSON, leave it as-is
            pass

    return pprint.pformat(response_dict)


def sync_call(config):
    """
    Executes a synchronous call to the specified function.
    """
    url = config.apihost+'/namespaces/_/actions/'+config.function+'?blocking=true&result=true&workers='+str(config.workers)
    response = requests.post(url, json=config.payload, headers={'Authorization': config.authorization})
    response.client_elapsed_time = response.elapsed.total_seconds() * 1000
    return response


def async_call(config):
    """
    Executes an asynchronous call to the specified function.
    It first posts the request to the function endpoint and then polls the activation to get the result.
    """
    url = config.apihost+'/namespaces/_/actions/'+config.function+'?blocking=false&result=true&workers='+str(config.workers)

    start_time = time.time()
    post_response = requests.post(url, json=config.payload, headers={'Authorization': config.authorization})
    activation_id = post_response.json()["activationId"]
    url = config.apihost+'/namespaces/_/activations/'+activation_id

    # Wait until the worker completes the job
    while True:
        get_response = requests.get(url, headers={'Authorization': config.authorization})
        if get_response.status_code == 200: # Activation completed
            break
        time.sleep(config.time_precision/1000)
        
    get_response.client_elapsed_time = (time.time() - start_time) * 1000

    return post_response, get_response


def bench_single_invocations(config):
    """
    Executes a single invocation run based on the configuration.
    It handles both blocking and non-blocking calls.
    """
    if config.blocking:
        response = sync_call(config)
        #log.info(f"\n\nResponse: {response.__dict__}")
        log.info(f"\n\nResponse:\n{format_response_dict(response)}\n")
        return extract_metrics(response, config)
    else:
        post_response, get_response = async_call(config)
        log.info(f"\n\nPost response:\n{format_response_dict(post_response)}\n")
        log.info(f"\nGet response:\n{format_response_dict(get_response)}\n")
        return extract_metrics(get_response, config)


def bench_multiple_invocations(config, warmup=False):
    """
    Executes the specified number of invocations for a single invocation run.
    Collects the metrics for each invocation.
    """
    if warmup:
        for _ in range(config.warmup_invocations):
            bench_single_invocations(config)
    else:
        metrics_list = []
        for _ in range(config.num_invocations):
            metrics = bench_single_invocations(config)
            metrics_list.append(metrics)
        return metrics_list


def run_benchmark(config):
    """
    Executes the benchmark process based on the configuration.
    Handles multiple runs and gathers statistics for each run.
    """
    all_metrics = []

    # Warm-up runs (ignored in results)
    log.info(f"\nStarting Warm-up")
    bench_multiple_invocations(config, warmup=True)

    # Main benchmark runs
    for run in range(config.num_runs):
        log.info(f"\nStarting run {run + 1}/{config.num_runs}")
        metrics_list = bench_multiple_invocations(config)
        all_metrics.extend(metrics_list)

    # Calculate statistics
    stats = benchmark_statistics(all_metrics)

    # Format and display results
    results = format_results(stats, config)
    print(results)

    # Write to file if output file is specified
    if config.output_file:
        write_results_to_file_csv(stats, config)
        