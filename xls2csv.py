import calendar
import math
import os
import shutil
import statistics
import sys
import time
from copy import deepcopy
from operator import itemgetter

import pandas
import pandas as pd

import csv

global_csv_path = "./csv/"

# TODO
"""
extract_iri OK
extract_def IN PROCESS (MIXED)
extract_skn
extract_vws
extract_snu
extract_cnd DELETED (SEE TRF)
extract_trf  IN PROCESS (MIXED)
"""


def extract_iri(p_path, p_file, p_sheet="MON_HSS_PROFILE_SECTION"):
    """
    Extract, prepare and unify data from LTPP IRI table

    For each STATE_CODE + SHRP_ID + CONSTRUCTION_NO + VISIT_DATE:
    - Obtain total number of runs (RUNS)
    - Calculate the average MRI (IRI)
    - Compute the standard deviation (SD)

    :param p_path: path of output file
    :param p_file: path of input file
    :param p_sheet: Excel worksheet tab
    :return:
    """
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (p_sheet, p_file))

    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=p_file, sheet_name=p_sheet)

    df = df[["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "VISIT_DATE", "MRI"]]

    df = df.groupby(["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "VISIT_DATE"])["MRI"].agg(
        [("IRI", lambda x: x.unique().mean()),
         ("RUNS", lambda x: x.nunique()),
         ("SD", lambda x: x.unique().std())]).reset_index()

    iri_list = [[column for column in df.columns]]

    # Append values
    for values in df.values:
        iri_list.append([value for value in values])

    save_csv(p_path, iri_list)


def extract_def(p_path, p_file, p_sheet="MON_DEFL_DROP_DATA"):
    """
    Extract, prepare and unify data from LTPP deflections table

    :param p_path: path of output file
    :param p_file: path of input file
    :param p_sheet: Excel worksheet tab
    :return:
    """
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (p_sheet, p_file))

    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=p_file, sheet_name=p_sheet)

    # ---------------------------------

    df = df[
        ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "TEST_DATE", "DROP_HEIGHT", "LANE_NO", "POINT_LOC", "PEAK_DEFL_1"]]

    df = df[(df["DROP_HEIGHT"] == 2) & ((df["LANE_NO"] == "F1") | (df["LANE_NO"] == "F3"))]

    df = df.groupby(["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "TEST_DATE", "LANE_NO", "POINT_LOC"], as_index=False)[
        "PEAK_DEFL_1"].max()

    # Append header
    def_list = [[column for column in df.columns]]
    def_sub1 = deepcopy(def_list)
    def_sub2 = deepcopy(def_list)

    # Append values
    for values in df.values:
        def_list.append([value for value in values])

    # (2) Create PEAK_DEFL_1_MAX lists for all POINT_LOC
    def_sub1[0].append("MAX_DEFS")

    # For loop in def_list
    for i in range(1, len(def_list)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub1)):
            if [def_list[i][def_list[0].index("STATE_CODE")],
                def_list[i][def_list[0].index("SHRP_ID")],
                def_list[i][def_list[0].index("CONSTRUCTION_NO")],
                def_list[i][def_list[0].index("TEST_DATE")],
                def_list[i][def_list[0].index("LANE_NO")]] == [def_sub1[j][def_sub1[0].index("STATE_CODE")],
                                                               def_sub1[j][def_sub1[0].index("SHRP_ID")],
                                                               def_sub1[j][def_sub1[0].index("CONSTRUCTION_NO")],
                                                               def_sub1[j][def_sub1[0].index("TEST_DATE")],
                                                               def_sub1[j][def_sub1[0].index("LANE_NO")]]:
                # Add deflection
                def_sub1[j][def_sub1[0].index("MAX_DEFS")].append(def_list[i][def_list[0].index("PEAK_DEFL_1")])
                status = True

        if not status:
            def_sub1.append(def_list[i])
            def_sub1[-1].append([def_list[i][def_list[0].index("PEAK_DEFL_1")]])

        sys.stdout.write("\r- [DEF 2]: %d/%d" % (i, len(def_list) - 1))

    print("")

    # (3) Calc mean, max and characteristic deflections
    def_sub2[0].extend(["F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR"])

    for i in range(1, len(def_sub1)):

        status = False
        max_defs = def_sub1[i][def_sub1[0].index("MAX_DEFS")]
        deflections = ["", "", ""]
        if len(max_defs) > 1:
            deflections[0] = statistics.mean(max_defs)  # Average DEF
            deflections[1] = max(max_defs)  # Maximum DEF
            deflections[2] = statistics.mean(max_defs) + statistics.stdev(max_defs) * 2  # Characteristic DEF

        # If there is a previous register
        for j in range(1, len(def_sub2)):
            if [def_sub1[i][def_sub1[0].index("STATE_CODE")],
                def_sub1[i][def_sub1[0].index("SHRP_ID")],
                def_sub1[i][def_sub1[0].index("CONSTRUCTION_NO")],
                def_sub1[i][def_sub1[0].index("TEST_DATE")]] == [def_sub2[j][def_sub2[0].index("STATE_CODE")],
                                                                 def_sub2[j][def_sub2[0].index("SHRP_ID")],
                                                                 def_sub2[j][def_sub2[0].index("CONSTRUCTION_NO")],
                                                                 def_sub2[j][def_sub2[0].index("TEST_DATE")]]:

                if def_sub1[i][def_sub1[0].index("LANE_NO")] == "F1":
                    def_sub2[j][def_sub2[0].index("F1_DEF_AVG")] = deflections[0]
                    def_sub2[j][def_sub2[0].index("F1_DEF_MAX")] = deflections[1]
                    def_sub2[j][def_sub2[0].index("F1_DEF_CHR")] = deflections[2]
                else:
                    def_sub2[j][def_sub2[0].index("F3_DEF_AVG")] = deflections[0]
                    def_sub2[j][def_sub2[0].index("F3_DEF_MAX")] = deflections[1]
                    def_sub2[j][def_sub2[0].index("F3_DEF_CHR")] = deflections[2]

                status = True

        if not status:
            def_sub2.append(def_sub1[i][:-1])
            def_sub2[-1].extend([""] * 6)
            if def_sub1[i][def_sub1[0].index("LANE_NO")] == "F1":
                def_sub2[-1][-6] = deflections[0]
                def_sub2[-1][-5] = deflections[1]
                def_sub2[-1][-4] = deflections[2]
            else:
                def_sub2[-1][-3] = deflections[0]
                def_sub2[-1][-2] = deflections[1]
                def_sub2[-1][-1] = deflections[2]

        sys.stdout.write("\r- [DEF 3]: %d/%d" % (i, len(def_sub1) - 1))

    print("")

    for i in range(1, len(def_sub2)):
        def_sub2[i] = [def_sub2[i][def_sub2[0].index("STATE_CODE")], def_sub2[i][def_sub2[0].index("SHRP_ID")],
                       def_sub2[i][def_sub2[0].index("CONSTRUCTION_NO")], def_sub2[i][def_sub2[0].index("TEST_DATE")],
                       def_sub2[i][def_sub2[0].index("F1_DEF_AVG")], def_sub2[i][def_sub2[0].index("F1_DEF_MAX")],
                       def_sub2[i][def_sub2[0].index("F1_DEF_CHR")], def_sub2[i][def_sub2[0].index("F3_DEF_AVG")],
                       def_sub2[i][def_sub2[0].index("F3_DEF_MAX")], def_sub2[i][def_sub2[0].index("F3_DEF_CHR")]]

    def_sub2[0] = ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "TEST_DATE",
                   "F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR"]

    save_csv(p_path, def_sub2)


def extract_snu(save_path, snu_filename, snu_sheet="TRF_ESAL_INPUTS_SUMMARY"):
    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=snu_filename, sheet_name=snu_sheet)

    # Append header
    snu_list = [[column for column in df.columns]]

    # Append values
    for values in df.values:
        snu_list.append([value for value in values])

    save_csv(save_path, snu_list)


def extract_trf(p_path, p_file, p_sheet=("TRF_HIST_EST_ESAL", "TRF_MON_EST_ESAL", "EXPERIMENT_SECTION")):
    """
    Extract, prepare and unify data from historic and LTPP traffic estimation tables

    :param p_path: path of output file
    :param p_file: path of input file
    :param p_sheet: Excel worksheet tabs
    :return:
    """

    # Read Excel file and save as DataFrame
    df_trf_hist = pandas.read_excel(io=p_file, sheet_name=p_sheet[0])
    df_trf_ltpp = pandas.read_excel(io=p_file, sheet_name=p_sheet[1])

    df_trf_hist = df_trf_hist.rename(columns={"YEAR_HIST_EST": "YEAR"})
    df_trf_ltpp = df_trf_ltpp.rename(columns={"YEAR_MON_EST": "YEAR"})

    df_trf = df_trf_hist.merge(df_trf_ltpp, how="outer",
                               on=["SHRP_ID", "STATE_CODE", "YEAR", "AADT_ALL_VEHIC", "AADT_TRUCK_COMBO",
                                   "ANL_KESAL_LTPP_LN_YR"])

    # Convert YEAR column to timestamp (YEAR/12/31)
    df_trf["YEAR"] = pandas.to_datetime(df_trf["YEAR"], format="%Y").apply(lambda dt: dt.replace(month=12, day=31))

    df_trf = df_trf.rename(
        columns={"AADT_ALL_VEHIC": "AADT", "AADT_TRUCK_COMBO": "AADTT", "ANL_KESAL_LTPP_LN_YR": "KESAL"})
    df_trf = df_trf[["STATE_CODE", "SHRP_ID", "YEAR", "AADT", "AADTT", "KESAL"]]

    df_cnd = pandas.read_excel(io=p_file, sheet_name=p_sheet[2])
    df_cnd = df_cnd[["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "CN_ASSIGN_DATE"]]

    # -------------------------------------------------------------------------------

    trf_list = [[column for column in df_trf.columns]]
    for values in df_trf.values:
        trf_list.append([value for value in values])

    cnd_list = [[column for column in df_cnd.columns]]
    for values in df_cnd.values:
        cnd_list.append([value for value in values])

    print(type(cnd_list[1][cnd_list[0].index("STATE_CODE")]),
          type(cnd_list[1][cnd_list[0].index("SHRP_ID")]),
          type(cnd_list[1][cnd_list[0].index("CN_ASSIGN_DATE")]))

    print(type(trf_list[1][trf_list[0].index("STATE_CODE")]),
          type(trf_list[1][trf_list[0].index("SHRP_ID")]),
          type(trf_list[1][trf_list[0].index("YEAR")]))

    for i in range(1, len(trf_list)):

        # Si existe, obtiene el Número de Construcción de fecha IGUAL o MENOR MÁXIMA que la de Tráfico
        if len(list(filter(lambda x:
                           x[cnd_list[0].index("STATE_CODE")] ==
                           trf_list[i][trf_list[0].index("STATE_CODE")] and
                           x[cnd_list[0].index("SHRP_ID")] == trf_list[i][trf_list[0].index("SHRP_ID")] and
                           x[cnd_list[0].index("CN_ASSIGN_DATE")] <=
                           trf_list[i][trf_list[0].index("YEAR")],
                           cnd_list))) > 0:
            trf_list[i].append(max(filter(lambda x:
                                          x[cnd_list[0].index("STATE_CODE")] ==
                                          trf_list[i][trf_list[0].index("STATE_CODE")] and
                                          x[cnd_list[0].index("SHRP_ID")] == trf_list[i][
                                              trf_list[0].index("SHRP_ID")] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")] <=
                                          trf_list[i][trf_list[0].index("YEAR")],
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])

        # Si existe, obtiene el Número de Construcción de fecha MAYOR MÍNIMA que la de Tráfico
        elif len(list(filter(lambda x:
                             x[cnd_list[0].index("STATE_CODE")] ==
                             trf_list[i][trf_list[0].index("STATE_CODE")] and
                             x[cnd_list[0].index("SHRP_ID")] == trf_list[i][trf_list[0].index("SHRP_ID")] and
                             x[cnd_list[0].index("CN_ASSIGN_DATE")] >
                             trf_list[i][trf_list[0].index("YEAR")],
                             cnd_list))) > 0:
            trf_list[i].append(min(filter(lambda x:
                                          x[cnd_list[0].index("STATE_CODE")] ==
                                          trf_list[i][trf_list[0].index("STATE_CODE")] and
                                          x[cnd_list[0].index("SHRP_ID")] == trf_list[i][
                                              trf_list[0].index("SHRP_ID")] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")] >
                                          trf_list[i][trf_list[0].index("YEAR")],
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])
        else:
            trf_list[i].append("")
        sys.stdout.write("\r- [TRF CN]: %d/%d" % (i, len(trf_list) - 1))
    print("")
    trf_list[0].append("CONSTRUCTION_NO")

    trf_result = deepcopy(trf_list)

    trf_result[0].extend(["AADT_AVG", "AADT_CUM", "AADTT_AVG", "AADTT_CUM", "KESAL_AVG", "KESAL_CUM"])

    for i in range(1, len(trf_result)):

        last_values = list(filter(lambda x:
                                  [x[trf_list[0].index("SHRP_ID")],
                                   x[trf_list[0].index("STATE_CODE")],
                                   x[trf_list[0].index("CONSTRUCTION_NO")]] == [
                                      trf_result[i][trf_result[0].index("SHRP_ID")],
                                      trf_list[i][trf_list[0].index("STATE_CODE")],
                                      trf_result[i][trf_result[0].index("CONSTRUCTION_NO")]] and

                                  x[trf_list[0].index("YEAR")] <= trf_result[i][
                                      trf_result[0].index("YEAR")], trf_list))

        if len(last_values) > 0:
            aadt = [x[trf_result[0].index("AADT")] for x in last_values]
            aadtt = [x[trf_result[0].index("AADTT")] for x in last_values]
            kesal = [x[trf_result[0].index("KESAL")] for x in last_values]

            trf_result[i].extend([0] * 6)

            trf_result[i][trf_result[0].index("AADT_AVG")] = average(aadt) if average(aadt) is not None else 0
            trf_result[i][trf_result[0].index("AADT_CUM")] = addition(aadt) if addition(aadt) is not None else 0
            trf_result[i][trf_result[0].index("AADTT_AVG")] = average(aadtt) if average(aadtt) is not None else 0
            trf_result[i][trf_result[0].index("AADTT_CUM")] = addition(aadtt) if addition(aadtt) is not None else 0
            trf_result[i][trf_result[0].index("KESAL_AVG")] = average(kesal) if average(kesal) is not None else 0
            trf_result[i][trf_result[0].index("KESAL_CUM")] = addition(kesal) if addition(kesal) is not None else 0

        sys.stdout.write("\r- [TRF SUM]: %d/%d" % (i, len(trf_result) - 1))
    print("")

    save_csv(p_path, trf_result)


def row_to_str(p_row):
    for j in range(0, len(p_row)):
        p_row[j] = str(p_row[j])  # Convert data to string
        p_row[j] = p_row[j].replace(".", ",")  # Replace dots with commas
        p_row[j] = p_row[j].replace("nan", "")  # Replace "nan" with void
    return p_row


def str_to_int(p_value):
    try:
        p_value = (str(p_value)).replace(",", ".")
        return int(float(p_value)), 1
    except Exception:
        return 0, 0


def int_to_str(p_value):
    return str(int(float(p_value.replace(",", "."))))


def get_last_day(year, month):
    day = calendar.monthrange(int(year), int(month))[1]
    date = str(int(year)).zfill(4) + str(int(month)).zfill(2) + str(day).zfill(2)
    date = pd.to_datetime(date, format="%Y%m%d")
    return date


def extract_vws_cn(save_path, vws_list, vws_filename):
    """
    Take VWS unified data and accumulate values depending on Construction Number assign date

    :param save_path: path of output file
    :param vws_list: VWS unified data
    :return:
    """

    df_cnd = pandas.read_excel(io=vws_filename, sheet_name="EXPERIMENT_SECTION")[
        ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "CN_ASSIGN_DATE"]]
    df_cnd["SHRP_ID"] = df_cnd["SHRP_ID"].astype(str)

    cnd_list = [[column for column in df_cnd.columns]]
    for values in df_cnd.values:
        cnd_list.append([value for value in values])

    for i in range(1, len(vws_list)):

        # Si existe, obtiene el Número de Construcción de fecha IGUAL o MENOR MÁXIMA que la de Tráfico
        if len(list(filter(lambda x:
                           [x[cnd_list[0].index("STATE_CODE")],
                            x[cnd_list[0].index("SHRP_ID")]] ==
                           [vws_list[i][vws_list[0].index("STATE_CODE")],
                            vws_list[i][vws_list[0].index("SHRP_ID")]] and
                           x[cnd_list[0].index("CN_ASSIGN_DATE")] <= get_last_day(
                               vws_list[i][vws_list[0].index("YEAR")],
                               vws_list[i][vws_list[0].index("MONTH")]),
                           cnd_list))) > 0:
            vws_list[i].append(max(filter(lambda x:
                                          [x[cnd_list[0].index("STATE_CODE")],
                                           x[cnd_list[0].index("SHRP_ID")]] ==
                                          [vws_list[i][vws_list[0].index("STATE_CODE")],
                                           vws_list[i][vws_list[0].index("SHRP_ID")]] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")] <= get_last_day(
                                              vws_list[i][vws_list[0].index("YEAR")],
                                              vws_list[i][vws_list[0].index("MONTH")]),
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])

        # Si existe, obtiene el Número de Construcción de fecha MAYOR MÍNIMA que la de Tráfico
        elif len(list(filter(lambda x:
                             [x[cnd_list[0].index("STATE_CODE")],
                              x[cnd_list[0].index("SHRP_ID")]] ==
                             [vws_list[i][vws_list[0].index("STATE_CODE")],
                              vws_list[i][vws_list[0].index("SHRP_ID")]] and
                             x[cnd_list[0].index("CN_ASSIGN_DATE")] > get_last_day(
                                 vws_list[i][vws_list[0].index("YEAR")],
                                 vws_list[i][vws_list[0].index("MONTH")]),
                             cnd_list))) > 0:
            vws_list[i].append(min(filter(lambda x:
                                          [x[cnd_list[0].index("STATE_CODE")],
                                           x[cnd_list[0].index("SHRP_ID")]] ==
                                          [vws_list[i][vws_list[0].index("STATE_CODE")],
                                           vws_list[i][vws_list[0].index("SHRP_ID")]] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")] > get_last_day(
                                              vws_list[i][vws_list[0].index("YEAR")],
                                              vws_list[i][vws_list[0].index("MONTH")]),
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])
        else:
            vws_list[i].append("")
        sys.stdout.write("\r- [VWS CN]: %d/%d" % (i, len(vws_list) - 1))
    print("")
    vws_list[0].extend(["CONSTRUCTION_NO", "MON_PREC_CUM", "MON_SNOW_CUM"])

    vws_result = deepcopy(vws_list)

    for i in range(1, len(vws_result)):

        last_values = list(filter(lambda x:
                                  [x[vws_list[0].index("SHRP_ID")],
                                   x[vws_list[0].index("STATE_CODE")],
                                   x[vws_list[0].index("CONSTRUCTION_NO")]] == [
                                      vws_result[i][vws_result[0].index("SHRP_ID")],
                                      vws_result[i][vws_result[0].index("STATE_CODE")],
                                      vws_result[i][vws_result[0].index("CONSTRUCTION_NO")]] and
                                  get_last_day(x[vws_list[0].index("YEAR")],
                                               x[vws_list[0].index("MONTH")]) <=
                                  get_last_day(vws_result[i][vws_list[0].index("YEAR")],
                                               vws_result[i][vws_list[0].index("MONTH")]), vws_list[1:]))

        if len(last_values) > 0:
            # Cumulate monthly values
            try:
                mon_prec = sum([x[vws_list[0].index("TOTAL_MON_PRECIP")] for x in last_values])
                mon_snow = sum([x[vws_list[0].index("TOTAL_SNOWFALL_MONTH")] for x in last_values])
            except Exception:
                mon_prec = mon_snow = None

            vws_result[i].append(mon_prec) if mon_prec is not None else vws_result[i].append("")
            vws_result[i].append(mon_snow) if mon_snow is not None else vws_result[i].append("")

        sys.stdout.write("\r- [VWS SUM]: %d/%d" % (i, len(vws_result) - 1))
    print("")
    save_csv(save_path, vws_result)


def average(p_list):
    result = count = 0
    for value in p_list:
        if value not in ("", "nan"):
            value = str_to_int(value)
            result += value[0]
            count += value[1]
    if count > 0:
        return result / count
    else:
        return None


def addition(p_list):
    result = count = 0
    for value in p_list:
        if value not in ("", "nan"):
            value = str_to_int(value)
            result += value[0]
            count += value[1]
    if count > 0:
        return result
    else:
        return None


def extract_skn(save_path, skn_filename, skn_sheet="MON_FRICTION"):
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (skn_sheet, skn_filename))

    # For each STATE_CODE + SHRP_ID + CONSTRUCTION_NO + FRICTION_DATE:
    # - Obtain total number of runs
    # - Calculate the average FRICTION NUMBER
    # - Compute the standard deviation

    # Dictionary
    skn_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "FRICTION_DATE": None,
        "FRICTION_TIME": None, "FRICTION_NO_BEGIN": None, "FRICTION_NO_END": None, "RUNS": None, "CV": None,
    }

    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=skn_filename, sheet_name=skn_sheet)

    # Append header
    skn_list = [[column for column in df.columns]]
    skn_results = [[column for column in df.columns]]
    skn_results[0].append('RUNS')
    skn_results[0].append('SD')

    # Append values
    for values in df.values:
        skn_list.append([value for value in values])

    # Assign indexes to dictionary
    skn_cols["RUNS"] = len(df.columns)
    skn_cols["CV"] = len(df.columns) + 1
    for skn_col in skn_cols:
        if skn_cols[skn_col] is None:
            skn_cols[skn_col] = skn_list[0].index(skn_col)

    # For loop in skn_list
    for i in range(1, len(skn_list)):
        status = False

        # For loop in skn_results
        for j in range(1, len(skn_results)):
            # If there is a previous register
            if [skn_list[i][skn_cols["STATE_CODE"]],
                skn_list[i][skn_cols["SHRP_ID"]],
                skn_list[i][skn_cols["CONSTRUCTION_NO"]],
                skn_list[i][skn_cols["FRICTION_DATE"]]] == [skn_results[j][skn_cols["STATE_CODE"]],
                                                            skn_results[j][skn_cols["SHRP_ID"]],
                                                            skn_results[j][skn_cols["CONSTRUCTION_NO"]],
                                                            skn_results[j][skn_cols["FRICTION_DATE"]]]:
                # Sum MRI and increase run counter
                skn_results[j][skn_cols["RUNS"]] += 2
                skn_results[j][skn_cols["CV"]].extend(
                    [skn_list[i][skn_cols["FRICTION_NO_BEGIN"]] + skn_list[i][skn_cols["FRICTION_NO_END"]]])
                status = True

        # Add a new register
        if not status:
            skn_results.append(skn_list[i])
            skn_results[-1].append(2)
            skn_results[-1].append(
                [skn_list[i][skn_cols["FRICTION_NO_BEGIN"]], skn_list[i][skn_cols["FRICTION_NO_END"]]])

        sys.stdout.write("\r- [FRICTION]: %d/%d" % (i, len(skn_list) - 1))

    for i in range(1, len(skn_results)):
        skn_results[i][skn_cols["FRICTION_NO_END"]] = sum(skn_results[i][skn_cols["CV"]]) / skn_results[i][
            skn_cols["RUNS"]]

        if len(skn_results[i][skn_cols["CV"]]) > 1:
            skn_results[i][skn_cols["CV"]] = \
                (statistics.stdev(skn_results[i][skn_cols["CV"]]) / statistics.mean(skn_results[i][skn_cols["CV"]]))
        else:
            skn_results[i][skn_cols["CV"]] = 0

    # Select only desired columns
    for i in range(len(skn_results)):
        skn_results[i] = [skn_results[i][skn_cols["STATE_CODE"]],
                          skn_results[i][skn_cols["SHRP_ID"]],
                          skn_results[i][skn_cols["CONSTRUCTION_NO"]],
                          skn_results[i][skn_cols["FRICTION_DATE"]],
                          skn_results[i][skn_cols["FRICTION_NO_END"]],
                          skn_results[i][skn_cols["RUNS"]],
                          skn_results[i][skn_cols["CV"]]]

    # Save to CSV
    save_csv(save_path, skn_results)


def extract_vws(save_path, vws_filename):
    # For each STATE_CODE + SHRP_ID + YEAR + MONTH:
    # - Obtain the MONTH averages of: precipitation, snowfall, temperature, freeze, wind and humidity
    # For each STATE_CODE + SHRP_ID + YEAR:
    # - Obtain the ANNUAL averages of: precipitation, snowfall, temperature, freeze, wind and humidity

    vws_sheet = ["CLM_VWS_PRECIP_ANNUAL", "CLM_VWS_PRECIP_MONTH",
                 "CLM_VWS_TEMP_ANNUAL", "CLM_VWS_TEMP_MONTH",
                 "CLM_VWS_WIND_ANNUAL", "CLM_VWS_WIND_MONTH",
                 "CLM_VWS_HUMIDITY_ANNUAL", "CLM_VWS_HUMIDITY_MONTH"]

    # Read Excel file and save as DataFrame
    vws_pr_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[0])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "TOTAL_ANN_PRECIP", "TOTAL_SNOWFALL_YR"]]
    vws_pr_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[1])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MONTH", "TOTAL_MON_PRECIP", "TOTAL_SNOWFALL_MONTH"]]
    vws_te_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[2])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MEAN_ANN_TEMP_AVG", "FREEZE_INDEX_YR", "FREEZE_THAW_YR"]]
    vws_te_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[3])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MONTH", "MEAN_MON_TEMP_AVG", "FREEZE_INDEX_MONTH", "FREEZE_THAW_MONTH"]]
    vws_wi_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[4])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MEAN_ANN_WIND_AVG"]]
    vws_wi_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[5])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MONTH", "MEAN_MON_WIND_AVG"]]
    vws_hu_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[6])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MAX_ANN_HUM_AVG", "MIN_ANN_HUM_AVG"]]
    vws_hu_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[7])[
        ["SHRP_ID", "STATE_CODE", "YEAR", "MONTH", "MAX_MON_HUM_AVG", "MIN_MON_HUM_AVG"]]

    vws_pr_m["SHRP_ID"] = vws_pr_m["SHRP_ID"].astype(str)
    vws_te_m["SHRP_ID"] = vws_te_m["SHRP_ID"].astype(str)
    vws_wi_m["SHRP_ID"] = vws_wi_m["SHRP_ID"].astype(str)
    vws_hu_m["SHRP_ID"] = vws_hu_m["SHRP_ID"].astype(str)

    vws_pr_a["SHRP_ID"] = vws_pr_a["SHRP_ID"].astype(str)
    vws_te_a["SHRP_ID"] = vws_te_a["SHRP_ID"].astype(str)
    vws_wi_a["SHRP_ID"] = vws_wi_a["SHRP_ID"].astype(str)
    vws_hu_a["SHRP_ID"] = vws_hu_a["SHRP_ID"].astype(str)

    df_month_vws = vws_pr_m.merge(vws_te_m, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR", "MONTH"])
    df_month_vws = df_month_vws.merge(vws_wi_m, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR", "MONTH"])
    df_month_vws = df_month_vws.merge(vws_hu_m, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR", "MONTH"])

    df_year_vws = vws_pr_a.merge(vws_te_a, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR"])
    df_year_vws = df_year_vws.merge(vws_wi_a, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR"])
    df_year_vws = df_year_vws.merge(vws_hu_a, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR"])

    df_vws = df_month_vws.merge(df_year_vws, how="outer", on=["SHRP_ID", "STATE_CODE", "YEAR"]).fillna(method="ffill")

    # df_vws.to_csv(path_or_buf="./csv/test_vws.csv", index=False)

    vws_results = [[column for column in df_vws.columns]]
    for values in df_vws.values:
        vws_results.append([value for value in values])

    # CLIMATIC ZONES
    vws_results[0].append("CLIMATIC ZONE")

    for i in range(1, len(vws_results)):
        # Lista de valores con igual ID
        nearest = list(filter(lambda x:
                              [x[vws_results[0].index("SHRP_ID")],
                               x[vws_results[0].index("STATE_CODE")]] == [
                                  vws_results[i][vws_results[0].index("SHRP_ID")],
                                  vws_results[i][vws_results[0].index("STATE_CODE")]] and
                              x[vws_results[0].index("MONTH")] in [6, 7, 8], vws_results))

        if len(nearest) > 0:
            vws_temp = count_temp = 0
            vws_prec = count_prec = 0

            for j in range(0, len(nearest)):
                # Sumamos todas las precipitaciones anuales no nulas
                if nearest[j][vws_results[0].index("TOTAL_ANN_PRECIP")] != "":
                    vws_prec += nearest[j][vws_results[0].index("TOTAL_ANN_PRECIP")]
                    count_prec += 1
                # Sumamos todas las temperaturas mensuales no nulas
                if nearest[j][vws_results[0].index("MEAN_MON_TEMP_AVG")] != "":
                    vws_temp += nearest[j][vws_results[0].index("MEAN_MON_TEMP_AVG")]
                    count_temp += 1

            if count_temp != 0:
                vws_temp = vws_temp / count_temp
                vws_prec = vws_prec / count_prec

                if 11 <= vws_temp <= 16:
                    vws_temp = "TEMPLADA"
                elif 16 < vws_temp < 23:
                    vws_temp = "MEDIA"
                elif 23 <= vws_temp <= 29:
                    vws_temp = "CÁLIDA"
                else:
                    vws_temp = "FUERA DE RANGO"
            else:
                vws_temp = "DESCONOCIDA"

            if vws_prec < 600:
                vws_prec = "POCO LLUVIOSA"
            else:
                vws_prec = "LLUVIOSA"

            vws_results[i].append(vws_prec + " - " + vws_temp)

        sys.stdout.write("\r- [VWS] ZONE: %d/%d" % (i, len(vws_results) - 1))
    print("")

    extract_vws_cn(save_path, vws_results, vws_filename)

    return


def save_csv(p_path, p_data):
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
    with open(p_file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data


def question_yn(p_question):
    while True:
        value = input(p_question + " [S/n] > ")
        if value in ["s", "S"]:
            return True
        if value in ["n", "N", ""]:
            return False
        else:
            print("Command not recognized.")


def str_time(p_time):
    return time.strftime('%Hh %Mm %Ss ', time.gmtime(p_time)) + str(
        round(p_time * 1000) - 1000 * math.floor(p_time)) + "ms"


def main(xls_file, csv_path, xls_path):
    """
    Main function

    :param xls_file: input list with Excel files
    :param csv_path: CSV destination path
    :param xls_path: XLS destination path
    :return:
    """
    global global_csv_path
    global_csv_path = csv_path

    if not os.path.isfile(xls_file):
        print("\U000026D4 The input file \"%s\" does not exist. " % xls_file)
        exit(1)

    if not os.path.isdir(csv_path):
        try:
            print("\U000026A0 The output directory \"%s\" does not exist and will be created. " % csv_path)
            os.mkdir(csv_path)
        except OSError:
            print("\U000026D4 The output directory \"%s\" does not exist and could not be created. " % csv_path)
            exit(1)
    else:
        print("\U0001F6C8 Output directory: \"%s\"" % csv_path)

    # CSV output file addresses
    csv_tables = [csv_path + s for s in ["iri.csv", "def.csv", "skn.csv", "snu.csv", "vws.csv", "trf.csv"]]

    # if question:
    #     question = question_yn("\U0001F4BB\U0001F4AC Do you want to start a clean process?")

    total_time = 0

    for n in range(0, len(csv_tables)):
        # if not os.path.isfile(csv_tables[k]) or (os.path.isfile(csv_tables[k]) and (question or question_yn(
        #         "\U0001F4BB\U0001F4AC File \"%s\" already exists. Regenerate?" % csv_tables[k]))):
        start_time = time.time()

        # extract_iri(csv_tables[n], xls_file) if n == 0 else 0
        # extract_def(csv_tables[n], xls_file) if n == 1 else 0
        # extract_skn(csv_tables[n], xls_file) if n == 2 else 0
        extract_snu(csv_tables[n], xls_file) if n == 3 else 0
        extract_vws(csv_tables[n], xls_file) if n == 4 else 0
        extract_trf(csv_tables[n], xls_file) if n == 5 else 0

        partial_time = time.time() - start_time
        total_time += partial_time
        print("\U00002BA1 File \"%s\" generated from \"%s\" (%s)\n" % (
            csv_tables[n], xls_file, str_time(partial_time)))

    # Move processed Excel to another folder
    shutil.move(xls_file, xls_path + os.path.basename(xls_file))

    print("\U0001F6C8 Process finished in %s" % str_time(total_time))


if __name__ == '__main__':
    p_xls_ready = "./xls/ready/"
    p_xls_done = "./xls/done/"
    p_xls_list = []

    for file in os.listdir(p_xls_ready):
        if file.endswith(".xlsx"):
            p_xls_list.append(os.path.join(p_xls_ready, file).replace("\\", "/"))

    for k in range(0, len(p_xls_list)):
        string = "(" + str(k + 1) + "/" + str(len(p_xls_list)) + ") Current file: \"" + p_xls_list[k] + "\""

        print("·" * len(string))
        print(string)
        print("·" * len(string))

        p_csv_path = "./csv/" + os.path.basename(p_xls_list[k])[0:-5] + "/"
        main(p_xls_list[k], p_csv_path, p_xls_done)
