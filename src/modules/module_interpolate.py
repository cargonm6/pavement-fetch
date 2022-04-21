import datetime
import os.path
import sys
import time
from copy import deepcopy

import numpy
import pandas as pd

from src.modules.module_common import row_to_str, save_csv, etr, to_hhmmss

project_root = ""


def to_float(p_str):
    p_str = str(p_str)
    p_str = p_str.replace(",", ".")  # Replace dots with commas
    p_str = float(p_str)
    return p_str


def main(p_root):
    global project_root
    project_root = p_root

    if not os.path.exists(project_root + "/res/LTPP.csv"):
        print("File does not exist")
        return

    df = pd.read_csv(project_root + "/res/LTPP.csv", sep=";", encoding="unicode_escape")
    df["SURVEY_DATE"] = pd.to_datetime(df["SURVEY_DATE"])
    df.sort_values(by=["STATE_CODE", "SHRP_ID", "SURVEY_DATE"], inplace=True)

    df_list = [[column for column in df.columns]]
    for values in df.values:
        df_list.append([value for value in values])

    new_list = [[column for column in df.columns]]

    time_for = 0

    for i in range(1, len(df_list)):
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

            time_factor = 30  # month

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
        new_list[i] = row_to_str(new_list[i])

    save_csv(p_path=project_root + "/res/LTPP_interpolated.csv", p_data=new_list)

    exit(0)
