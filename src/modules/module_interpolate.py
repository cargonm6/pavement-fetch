import datetime
import os.path
import sys
import time
from copy import deepcopy

import numpy
import pandas as pd

from src.modules.module_common import row_to_str, save_csv, etr, to_hhmmss

project_root = ""


def transform_date(p_date, in_format="yyyy-mm-dd", out_format="mm/dd/yyyy"):
    p_day, p_mon, p_yea = ["", "", ""]
    if in_format == "yyyy-mm-dd":
        p_day = str(p_date)[8:10]
        p_mon = str(p_date)[5:7]
        p_yea = str(p_date)[0:4]

    if out_format == "mm/dd/yyyy":
        p_date = p_mon + "/" + p_day + "/" + p_yea

    return p_date


def to_float(p_str):
    p_str = float(str(p_str).replace(",", "."))  # Replace dots with commas
    return p_str


def main(p_root, time_factor=30):
    """

    :param p_root: project root path
    :param time_factor: time period (by default, 30 days)
    :return:
    """
    global project_root
    project_root = p_root

    p_sheet = "MON_DIS_AC_REV"
    path_input = "/res/LTPP.xlsx"
    path_output = "/res/csv/ready/pci.csv"

    if not os.path.exists(project_root + path_input):
        print("File does not exist")
        return

    df = pd.read_excel(io=project_root + path_input, sheet_name=p_sheet)

    # df = pd.read_csv(project_root + path_input, sep=";", encoding="unicode_escape")
    df["SURVEY_DATE"] = pd.to_datetime(df["SURVEY_DATE"])
    df.sort_values(by=["STATE_CODE", "SHRP_ID", "SURVEY_DATE"], inplace=True)

    df_list = [[column for column in df.columns]]
    for values in df.values:
        df_list.append([value for value in values])

    # Without interpolation
    if time_factor == 0:
        save_csv(p_path=project_root + path_output, p_data=df_list)
        return

    # With interpolation
    new_list = [[column for column in df.columns]]

    time_for = 0

    limit = len(df_list)  # 2

    for i in range(1, limit):
        time_iter = time.time()

        # Add current row
        new_list.append(df_list[i])

        if i < (len(df_list) - 1) and [df_list[i][df_list[0].index("STATE_CODE")],
                                       df_list[i][df_list[0].index("SHRP_ID")],
                                       df_list[i][df_list[0].index("CONSTRUCTION_NO")]] == \
                [df_list[i + 1][df_list[0].index("STATE_CODE")],
                 df_list[i + 1][df_list[0].index("SHRP_ID")],
                 df_list[i + 1][df_list[0].index("CONSTRUCTION_NO")]]:
            duration = (df_list[i + 1][df_list[0].index("SURVEY_DATE")] - df_list[i][
                df_list[0].index("SURVEY_DATE")]).days

            for step in range(1, int(numpy.floor(duration / time_factor))):
                new_row = deepcopy(df_list[i])

                # Time increment
                old_date = new_row[df_list[0].index("SURVEY_DATE")]
                new_date = old_date + datetime.timedelta(days=step * time_factor)

                new_row[df_list[0].index("SURVEY_DATE")] = new_date

                # Linear interpolation
                for n in range(5, len(new_list[-1]) - 4):
                    # Add to origin the step distance multiplied by step number
                    new_row[n] = to_float(df_list[i][n]) + (
                            to_float(df_list[i + 1][n]) - to_float(df_list[i][n])) * step / numpy.floor(duration)

                    if new_row[n] < 0:
                        new_row[n] = 0.0

                    # Get ceil integer if it is a number column
                    if new_list[0][n] in ["TRANS_CRACK_NO_L", "TRANS_CRACK_NO_M", "TRANS_CRACK_NO_H",
                                          "PATCH_NO_L", "PATCH_NO_M", "PATCH_NO_H",
                                          "POTHOLES_NO_L", "POTHOLES_NO_M", "POTHOLES_NO_H",
                                          "SHOVING_NO", "PUMPING_NO"]:
                        new_row[n] = numpy.ceil(new_row[n])

                new_list.append(new_row)

        # ETR

        time_est, time_for = etr(len(df_list), i, time_for, time_iter)
        if i < len(df_list) - 1:
            sys.stdout.write("\r (%d/%d) ETR: %s" % (i, len(df_list) - 1, time_est))
        else:
            sys.stdout.write(
                "\r (%d/%d) Total time: %s" % (i, len(df_list) - 1, to_hhmmss(time_for)))

    for i in range(1, len(new_list)):
        new_list[i][df_list[0].index("SURVEY_DATE")] = transform_date(new_list[i][df_list[0].index("SURVEY_DATE")],
                                                                      "yyyy-mm-dd", "mm/dd/yyyy")
        new_list[i] = row_to_str(new_list[i])

    save_csv(p_path=project_root + path_output, p_data=new_list)
