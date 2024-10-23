import statistics
import json
from tabulate import tabulate


def extract_metrics(response, config):
    """
    Extracts relevant metrics from the get_response JSON content, including initTime, duration, client_elapsed_time, waitTime, and success.
    """
    try:
        json_response = response.json()
        annotations = {item['key']: item['value'] for item in json_response.get('annotations', [])}
        
        init_time = annotations.get('initTime', 0)
        wait_time = annotations.get('waitTime', 0)
        duration = json_response.get('duration', 0)
        client_elapsed_time = getattr(response, 'client_elapsed_time', 0)
        if config.blocking: success = json_response.get('success', False)
        else: success = json_response.get('response', {}).get('status', '').lower() == 'success'

        return {
            'initTime': init_time,
            'waitTime': wait_time,
            'duration': duration,
            'client_elapsed_time': client_elapsed_time,
            'success': success
        }
    except (ValueError, KeyError): return {'initTime': 0, 'waitTime': 0, 'duration': 0, 'client_elapsed_time': 0, 'success': False}


def benchmark_statistics(metrics_list):
    """
    Computes statistics for each metric.
    Returns average, minimum, and maximum for initTime, duration, and client_elapsed_time,
    and the overall success rate.
    """
    init_times = [m['initTime'] for m in metrics_list]
    wait_times = [m['waitTime'] for m in metrics_list]
    durations = [m['duration'] for m in metrics_list]
    client_elapsed_times = [m['client_elapsed_time'] for m in metrics_list]
    success_rate = sum(1 for m in metrics_list if m['success']) / len(metrics_list) * 100

    stats = {
        'initTime': {'avg': statistics.mean(init_times), 'min': min(init_times), 'max': max(init_times), 'std': statistics.stdev(init_times)},
        'waitTime': {'avg': statistics.mean(wait_times), 'min': min(wait_times), 'max': max(wait_times), 'std': statistics.stdev(wait_times)},
        'duration': {'avg': statistics.mean(durations), 'min': min(durations), 'max': max(durations), 'std': statistics.stdev(durations)},
        'client_elapsed_time': {'avg': statistics.mean(client_elapsed_times), 'min': min(client_elapsed_times), 'max': max(client_elapsed_times), 'std': statistics.stdev(client_elapsed_times)},
        'success_rate': success_rate
    }
    return stats


def format_results(stats, config):
    """
    Formats the benchmark results for display.
    """

    if config.print_csv:
        # Print the results as a CSV string
        result = (
            f"Metric,Average,Minimum,Maximum,Standard Deviation\n"
            f"InitTime,{stats['initTime']['avg']:.4f},{stats['initTime']['min']:.4f},{stats['initTime']['max']:.4f},{stats['initTime']['std']:.4f}\n"
            f"WaitTime,{stats['waitTime']['avg']:.4f},{stats['waitTime']['min']:.4f},{stats['waitTime']['max']:.4f},{stats['waitTime']['std']:.4f}\n"
            f"Duration,{stats['duration']['avg']:.4f},{stats['duration']['min']:.4f},{stats['duration']['max']:.4f},{stats['duration']['std']:.4f}\n"
            f"Client Elapsed Time,{stats['client_elapsed_time']['avg']:.4f},{stats['client_elapsed_time']['min']:.4f},{stats['client_elapsed_time']['max']:.4f},{stats['client_elapsed_time']['std']:.4f}\n"
            f"Success Rate,{stats['success_rate']:.2f}%,-,-,-\n"
        )


    else:
        headers = ["Metric", "Average", "Minimum", "Maximum", "Standard Deviation"]
        table_data = [
            ["InitTime", f"{stats['initTime']['avg']:.4f}", f"{stats['initTime']['min']:.4f}", f"{stats['initTime']['max']:.4f}", f"{stats['initTime']['std']:.4f}"],
            ["WaitTime", f"{stats['waitTime']['avg']:.4f}", f"{stats['waitTime']['min']:.4f}", f"{stats['waitTime']['max']:.4f}", f"{stats['waitTime']['std']:.4f}"],
            ["Duration", f"{stats['duration']['avg']:.4f}", f"{stats['duration']['min']:.4f}", f"{stats['duration']['max']:.4f}", f"{stats['duration']['std']:.4f}"],
            ["Client Elapsed Time", f"{stats['client_elapsed_time']['avg']:.4f}", f"{stats['client_elapsed_time']['min']:.4f}", f"{stats['client_elapsed_time']['max']:.4f}", f"{stats['client_elapsed_time']['std']:.4f}"],
            ["Success Rate", f"{stats['success_rate']:.2f}%", "-", "-", "-"]
        ]

        # Truncate the payload if it exceeds the maximum length
        payload_str = json.dumps(config.payload, indent=4)
        if len(payload_str) > 500:
            payload_str = payload_str[:500] + '... (truncated)'

        # Display the number of runs and invocations
        result = (
            f"\n\n-------------------------------------------------------------------"
            f"\nBenchmark Results:\n"
            f"Number of Warp-up invocations: {config.warmup_invocations}\n"
            f"Number of runs: {config.num_runs}\n"
            f"Number of invocations per run: {config.num_invocations}\n\n"
            f"Payload size: {len(json.dumps(config.payload))} bytes\n"
            f"Payload: {payload_str}\n\n"
            f"{tabulate(table_data, headers=headers, tablefmt='grid')}\n"
        )

    return result


def write_results_to_file_csv(stats, config):
    """
    Writes the benchmark results to a specified CSV file.
    """
    with open(config.output_file, 'w', newline='') as csvfile:
        fieldnames = ['Metric', 'Average', 'Min', 'Max', 'Std', 'Success Rate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write headers
        writer.writeheader()

        # Write rows for each metric
        writer.writerow({'Metric': 'InitTime', 'Average': f"{stats['initTime']['avg']:.4f}",
                         'Min': f"{stats['initTime']['min']:.4f}", 'Max': f"{stats['initTime']['max']:.4f}", 'Std': f"{stats['initTime']['std']:.4f}"})
        writer.writerow({'Metric': 'WaitTime', 'Average': f"{stats['waitTime']['avg']:.4f}",
                         'Min': f"{stats['waitTime']['min']:.4f}", 'Max': f"{stats['waitTime']['max']:.4f}", 'Std': f"{stats['waitTime']['std']:.4f}"})
        writer.writerow({'Metric': 'Duration', 'Average': f"{stats['duration']['avg']:.4f}",
                         'Min': f"{stats['duration']['min']:.4f}", 'Max': f"{stats['duration']['max']:.4f}", 'Std': f"{stats['duration']['std']:.4f}"})
        writer.writerow({'Metric': 'Client Elapsed Time', 'Average': f"{stats['client_elapsed_time']['avg']:.4f}",
                         'Min': f"{stats['client_elapsed_time']['min']:.4f}", 'Max': f"{stats['client_elapsed_time']['max']:.4f}", 'Std': f"{stats['client_elapsed_time']['std']:.4f}"})
        writer.writerow({'Metric': 'Success Rate', 'Average': f"{stats['success_rate']:.2f}%", 'Min': '', 'Max': ''})

    log.info(f"Results written to {config.output_file}")
