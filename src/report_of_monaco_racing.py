from datetime import datetime
import argparse

def get_user_input_data_from_cli():
    """
    Parses command-line arguments.

    Returns:
    tuple: A tuple containing the following elements:
            - file (str): The input file path for reading.
            - order (str): The sort order ('--asc' or '--desc').
            - driver (str): The driver's name.
    """
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--file', type=str, help='Input file path for read')
    parser.add_argument('--desc', dest='accumulate', action='store_const', const='--desc', default='--asc')
    parser.add_argument('--driver', type=str)

    data = parser.parse_args()
    return data.file, data.accumulate, data.driver

def read_file(folder_path, file_name, chunk_size=1024):
    """
        Reads the contents of a file and returns it as a generator object.

        Parameters:
        folder_path (str): A string representing the path of the folder where the file is located.
        file_name (str): A string representing the name of the file.

        Returns:
        generator: A generator object that yields each line of the file.
    """

    file_path = folder_path + file_name
    try:
        for line in open(file_path, 'r', encoding='utf-8'):
            yield line

    except FileNotFoundError:
        print(f"{file_name} does not exist.")
        return {}
    except MemoryError:
        print("Out of memory error occurred while reading the file.")
        return {}
    except IOError:
        print(f"Cannot open {file_name}.")
        return {}

def process_file_data(drivers_report, file_data, file_type):
    """
        Update the driver's report based on the given file data.

        Parameters:
        drivers_report (dict): A dictionary representing the driver's report.
        file_data (str): A string representing the data to be processed.
        path (str): A string representing the path of the file.
    """
    if file_type == 'abbr':
        abbr, name, auto = file_data.split('_')
        drivers_report[abbr] = {'name': name, 'auto': auto.rstrip()}
    else:
        abbr, time_start = file_data[0:3], file_data[3:].rstrip()
        drivers_report[abbr][file_type] = time_start

def update_best_lap_time_in_drivers_report(drivers_report):
    """
        Update the driver's report with the best lap time for each driver.

        Parameters:
        drivers_report (dict): A dictionary representing the driver's report.

        Returns:
        dict: A dictionary representing the updated driver's report.
    """

    for abbr in drivers_report:
        start_time = drivers_report[abbr]['start']
        end_time = drivers_report[abbr]['end']

        best_lap_time = count_best_lap(start_time, end_time)
        drivers_report[abbr]['best_lap_time'] = best_lap_time

    return drivers_report


def count_best_lap(start_time, end_time) -> str:
    """
        Calculate the best lap time from the given start and end times.

        Parameters:
        start_time (str): A string representing the start time in the format '%Y-%m-%d_%H:%M:%S.%f'.
        end_time (str): A string representing the end time in the format '%Y-%m-%d_%H:%M:%S.%f'.

        Returns:
        str: A string representing the best lap time in the format 'HH:MM:SS.mmm'.

        Raises:
        None: The function does not raise any exceptions, but it handles negative lap times by returning the string 'X NEGATIVE TIME'.
    """
    start_time = datetime.strptime(start_time, '%Y-%m-%d_%H:%M:%S.%f')
    end_time = datetime.strptime(end_time, '%Y-%m-%d_%H:%M:%S.%f')
    best_lap_time = str(end_time - start_time)

    if "day" in best_lap_time:
        best_lap_time = "X NEGATIVE TIME"

    return best_lap_time

def sort_time_of_dict(drivers_report, sort_order):
    drivers_report = dict(sorted(drivers_report.items(), key=lambda x: x[1]['best_lap_time'], reverse=sort_order))
    return drivers_report

def save_abbr_cli_driver_name(log_files):
    return {'abbr': log_files.split('_')[0]}

def print_report(drivers_report):
    """
        Print the driver's report to the console.

        Parameters:
        drivers_report (dict): A dictionary representing the driver's report.
    """
    for number, driver_character in enumerate(drivers_report.values(), start=1):
        top_num = number
        name_dr = driver_character['name']
        auto_dr = driver_character['auto']
        best_lap = driver_character['best_lap_time']
        line = '-' * 70

        print(f"{top_num}. {name_dr} | {auto_dr} | {best_lap}")

        if number == 15:
            print(line)

def process_all_files(folder_path, file_names, driver_name=None):
    """
        Processes all the files, updates the driver's report, sorts it, and returns the resulting dictionary.

        Parameters:
        folder_path (str): The path to the folder containing the files to be processed.
        sort_order (str): The sort order ('--asc' or '--desc') for the drivers' best lap times.
        file_names (list): A list of tuples containing the file type and file name for each file to be processed.
        driver_name (str, optional): The name of a specific driver to be focused on. If not provided, all drivers will be processed.

        Returns:
        dict: A dictionary representing the processed and sorted driver's report.

    """
    drivers_report = {}
    one_driver_cli_input = {}

    for file_type, file_path_name in file_names:
        for log_files in read_file(folder_path, file_path_name):
            process_file_data(drivers_report, log_files, file_type)

            if driver_name and driver_name in log_files:
                one_driver_cli_input = save_abbr_cli_driver_name(log_files)

    return drivers_report, one_driver_cli_input

def main():
    """
        The main function that processes the driver's report.
    """
    file_names = [('abbr', '/abbreviations.txt'), ('start', '/start.log'), ('end', '/end.log')]
    folder_path, sort_order, driver_name = get_user_input_data_from_cli()
    sort_type = sort_order != '--asc'

    drivers_report, one_driver_cli_input = process_all_files(folder_path, file_names, driver_name)
    drivers_report = update_best_lap_time_in_drivers_report(drivers_report)
    drivers_report = sort_time_of_dict(drivers_report, sort_type)

    if driver_name:
        drivers_report = {one_driver_cli_input['abbr']: drivers_report[one_driver_cli_input['abbr']]}

    print_report(drivers_report)
    return drivers_report

if __name__ == '__main__':
    main()


