import csv
import math
import time


def row_to_str(p_row):
    """
    Parse all data from a row to string type
    :param p_row: input row
    :return: string row
    """
    for j in range(0, len(p_row)):
        p_row[j] = str(p_row[j])  # Convert data to string
        p_row[j] = p_row[j].replace(".", ",")  # Replace dots with commas
        p_row[j] = p_row[j].replace("nan", "")  # Replace "nan" with void
    return p_row


def save_csv(p_path, p_data):
    """
    Export matrix to CSV file
    :param p_path: destination path
    :param p_data: data matrix
    :return:
    """
    for i in range(1, len(p_data)):
        p_data[i] = row_to_str(p_data[i])

        # Fix zero prefix in SHRP_ID
        if "SHRP_ID" in p_data[0] and len(p_data[i][p_data[0].index("SHRP_ID")]) < 4:
            p_data[i][p_data[0].index("SHRP_ID")] = "0" + p_data[i][p_data[0].index("SHRP_ID")]

    with open(p_path, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(p_data)

    print("\n\U0001F5AB Data saved")


def load_csv(p_file):
    """
    Import matrix from CSV file
    :param p_file: origin path
    :return: data matrix
    """
    with open(p_file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data


def to_hhmmss(p_seconds):
    """
    Format seconds to hh:mm:ss
    :param p_seconds: input time
    :return: output string
    """
    hh = math.floor(p_seconds / 3600)
    mm = math.floor(p_seconds / 60) - (hh * 60)
    ss = math.floor(p_seconds) - (hh * 3600) - (mm * 60)
    return str(int(hh)).zfill(2) + ":" + str(int(mm)).zfill(2) + ":" + str(int(ss)).zfill(2)


def etr(p_count_total, p_count_current, p_time_total, p_time_current):
    """
    Estimated time remaining function
    :param p_count_total: total time counted
    :param p_count_current: current iteration time
    :param p_time_total: total time
    :param p_time_current: current time
    :return: formatted time count, total time
    """
    p_time_total += (time.time() - p_time_current)
    p_seconds = (-1 + p_count_total - p_count_current) * p_time_total / p_count_current
    return to_hhmmss(p_seconds), p_time_total
