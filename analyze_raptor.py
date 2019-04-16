import csv
import json
import os
import sys

from argparse import ArgumentParser, Namespace


def analyze_raptor_run(raptor_log_files):
    pageload_times = {"amazon": [], 'facebook': [], 'google': [], 'youtube': []}

    for log_file in raptor_log_files:
        with open(log_file, 'r') as opened_file:
            suites = json.loads(opened_file.read())['suites']
        for suite in suites:
            for key in pageload_times.keys():
                if key in suite['name']:
                    pageload_times[key].append(suite['value'])

    return pageload_times

def calculate(pageload_times, path_to_logs):
    def maximum_deviation(average):
        return max(map(lambda x: abs(x - average), pageload_times[suite]))

    def average():
        return float(sum(pageload_times[suite]) / len(pageload_times[suite]))

    def maximum_difference():
        return float(max(pageload_times[suite]) - min(pageload_times[suite]))

    def print_results():
        print('-----------------------')
        print(' '.join([
            'Results for',
            os.path.basename(path_to_logs),
            ':',
            suite
        ]))
        print(
            '\n'.join([
                "Average",
                str(average()),
                "Maximum Difference (max - min)",
                str(maximum_difference()),
                "Maximum",
                str(max(pageload_times[suite])),
                "Minimum",
                str(min(pageload_times[suite])),
                "Maximum Deviation from Average",
                str(maximum_deviation(average()))
            ])
        )
        print('-----------------------')

    for suite in pageload_times.keys():
        print_results()


def analyze_logs(args):
    """
    """
    # build the path with assumption it lies below the script directory
    path_to_logs = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        args.directory
    )
    if not os.path.exists(path_to_logs):
        print('Invalid path to logs.')
        return
    else:
        logs = os.listdir(path_to_logs)

    if not logs:
        print('No runs were detected.')
        return

    for index, instance in enumerate(logs):
        instance = os.path.join(path_to_logs, instance)
        if os.path.isdir(instance):
            analyze_logs(Namespace(directory=instance))
        else:
            logs[index] = instance

    if all(map(lambda x: os.path.isfile(x), logs)):
        pageload_times = analyze_raptor_run(logs)
        calculate(pageload_times, path_to_logs)


def cli():
    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', action='store', default=None, help='Directory containing raptor logs to analyze.')
    parser.add_argument('-c', '--csv', action='store_true', default=False, help='Enable output in CSV file format.')

    args, _ = parser.parse_known_args(sys.argv)
    return args


if __name__ == "__main__":
    args = cli()
    analyze_logs(args)