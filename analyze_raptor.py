import csv
import json
import os
import sys

from argparse import ArgumentParser, Namespace

args = None


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

def calculate(pageload_times, path_to_logs, args):
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

    if args.csv:
        csv_file_name = os.path.join(path_to_logs, 'results.csv')
        with open(csv_file_name, 'wb') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([
                '',
                'Average',
                'Maximum Difference',
                'Maximum',
                'Minimum',
                'Maximum Deviation from Average'
            ])
            for suite in pageload_times.keys():
                with open(csv_file_name, 'wb') as csvfile:
                    csv_writer.writerow([
                        suite,
                        average(),
                        maximum_difference(),
                        max(pageload_times[suite]),
                        min(pageload_times[suite]),
                        maximum_deviation(average())
                    ])
        print('File successfully written to {}'.format(csv_file_name))
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
        list_of_dirs = os.listdir(path_to_logs)

    if not list_of_dirs:
        print('No runs were detected.')
        return

    json_logs = [os.path.join(path_to_logs, item) for index, item in enumerate(list_of_dirs) if item.endswith('json')]
    directories = [os.path.join(path_to_logs, item) for index, item in enumerate(list_of_dirs) if os.path.isdir(os.path.join(path_to_logs, item))]

    for directory in directories:
        args.directory = directory
        analyze_logs(args)

    if json_logs and all(map(lambda x: os.path.isfile(x), json_logs)):
        pageload_times = analyze_raptor_run(json_logs)
        calculate(pageload_times, path_to_logs, args)

def cli():
    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', action='store', default=None, help='Directory containing raptor logs to analyze.')
    parser.add_argument('-c', '--csv', action='store_true', default=False, help='Enable output in CSV file format.')

    args, _ = parser.parse_known_args(sys.argv)
    return args


if __name__ == "__main__":
    args = cli()
    analyze_logs(args)