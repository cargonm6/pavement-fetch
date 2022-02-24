import calendar
import math
import os
import statistics
import sys
import time
from operator import itemgetter
from copy import deepcopy
from typing import List, Any

import pandas
import pandas as pd

import csv

global_csv_path = "./csv/"

# TODO
"""
extract_iri OK
extract_def OK
extract_skn
extract_vws
extract_snu
extract_cnd
extract_trf OK
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

    # Create original matrix from data header
    m_original = [[column for column in df.columns]]

    # Append data values to original matrix
    for values in df.values:
        m_original.append([value for value in values])

    # Append data values to original matrix
    for i in range(1, len(m_original)):
        m_original[i] = [m_original[i][m_original[0].index("STATE_CODE")],
                         m_original[i][m_original[0].index("SHRP_ID")],
                         m_original[i][m_original[0].index("CONSTRUCTION_NO")],
                         m_original[i][m_original[0].index("VISIT_DATE")],
                         m_original[i][m_original[0].index("MRI")]]

    m_original[0] = ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "VISIT_DATE", "MRI"]
    m_results: List[Any] = [["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "VISIT_DATE", "IRI", 'ARRAY', "RUNS", "SD"]]

    # For loop in iri_list
    for i in range(1, len(m_original)):
        status = False

        # For loop in iri_results
        for j in range(1, len(m_results)):
            # If there is a previous register
            if [m_original[i][m_original[0].index("STATE_CODE")],
                m_original[i][m_original[0].index("SHRP_ID")],
                m_original[i][m_original[0].index("CONSTRUCTION_NO")],
                m_original[i][m_original[0].index("VISIT_DATE")]] == \
                    [m_results[j][m_results[0].index("STATE_CODE")],
                     m_results[j][m_results[0].index("SHRP_ID")],
                     m_results[j][m_results[0].index("CONSTRUCTION_NO")],
                     m_results[j][m_results[0].index("VISIT_DATE")]]:
                # Append IRI to ARRAY
                m_results[j][m_results[0].index("ARRAY")].append(m_original[i][m_original[0].index("MRI")])
                status = True

        # Add a new register and append IRI to ARRAY
        if not status:
            m_results.append(m_original[i] + [[m_original[i][m_original[0].index("MRI")]], "", ""])

        sys.stdout.write("\r- [IRI]: %d/%d" % (i, len(m_original) - 1))

    for m_result in m_results[1:]:
        # RUNS is equal to ARRAY length
        m_result[m_results[0].index("RUNS")] = len(m_result[m_results[0].index("ARRAY")])

        # MRI is equal to the sum of MRI values divided by RUNS
        m_result[m_results[0].index("IRI")] = \
            sum(m_result[m_results[0].index("ARRAY")]) / m_result[m_results[0].index("RUNS")]

        # If RUNS > 1, Standard Deviation SD will be obtained
        if m_result[m_results[0].index("RUNS")] > 1:
            m_result[m_results[0].index("SD")] = statistics.stdev(m_result[m_results[0].index("ARRAY")]) / \
                                                 statistics.mean(m_result[m_results[0].index("ARRAY")])

    # Select only desired columns
    for i in range(1, len(m_results)):
        m_results[i] = [m_results[i][m_results[0].index("STATE_CODE")], m_results[i][m_results[0].index("SHRP_ID")],
                        m_results[i][m_results[0].index("CONSTRUCTION_NO")],
                        m_results[i][m_results[0].index("VISIT_DATE")],
                        m_results[i][m_results[0].index("IRI")], m_results[i][m_results[0].index("RUNS")],
                        m_results[i][m_results[0].index("SD")]]

    # sys.stdout.write("\r- (%d%%) Reducing results matrix..." % (i / len(m_results) * 100))
    m_results[0] = ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "VISIT_DATE", "IRI", "RUNS", "SD"]

    # Save to CSV
    save_csv(p_path, m_results)


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

    # Append header
    def_list = [[column for column in df.columns]]
    def_sub1 = deepcopy(def_list)
    def_sub2 = deepcopy(def_list)
    def_sub3 = deepcopy(def_list)

    # Append values
    for values in df.values:
        def_list.append([value for value in values])

    # Filter: only DROP_HEIGHT = 2 and LANE_NO = F1 | F3
    def_list[1:] = list(
        filter(lambda x: x[def_list[0].index("DROP_HEIGHT")] == 2 and (x[def_list[0].index("LANE_NO")] in ["F1", "F3"]),
               def_list[1:]))

    # (1) Obtain max values from PEAK_DEFL_1 and place them into PEAK_DEFL_1_MAX
    def_sub1[0].append("MAX_DEF")

    # For loop in def_list
    for i in range(1, len(def_list)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub1)):
            if [def_list[i][def_list[0].index("STATE_CODE")],
                def_list[i][def_list[0].index("SHRP_ID")],
                def_list[i][def_list[0].index("CONSTRUCTION_NO")],
                def_list[i][def_list[0].index("TEST_DATE")],
                def_list[i][def_list[0].index("LANE_NO")],
                def_list[i][def_list[0].index("POINT_LOC")]] == [def_sub1[j][def_sub1[0].index("STATE_CODE")],
                                                                 def_sub1[j][def_sub1[0].index("SHRP_ID")],
                                                                 def_sub1[j][def_sub1[0].index("CONSTRUCTION_NO")],
                                                                 def_sub1[j][def_sub1[0].index("TEST_DATE")],
                                                                 def_sub1[j][def_sub1[0].index("LANE_NO")],
                                                                 def_sub1[j][def_sub1[0].index("POINT_LOC")]]:

                # Copy PEAK_DEFL_1 if it was not the maximum
                if def_sub1[j][def_sub1[0].index("MAX_DEF")] < def_list[i][def_list[0].index("PEAK_DEFL_1")]:
                    def_sub1[j][def_sub1[0].index("MAX_DEF")] = def_list[i][def_list[0].index("PEAK_DEFL_1")]

                status = True

        # Copy new entry
        if not status:
            def_sub1.append(def_list[i])
            def_sub1[-1].append(def_list[i][def_list[0].index("PEAK_DEFL_1")])

        sys.stdout.write("\r- [DEF 1]: %d/%d" % (i, len(def_list) - 1))

    print("")

    # (2) Create PEAK_DEFL_1_MAX lists for all POINT_LOC
    def_sub2[0].append("MAX_DEFS")

    # For loop in def_list
    for i in range(1, len(def_sub1)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub2)):
            if [def_sub1[i][def_sub1[0].index("STATE_CODE")],
                def_sub1[i][def_sub1[0].index("SHRP_ID")],
                def_sub1[i][def_sub1[0].index("CONSTRUCTION_NO")],
                def_sub1[i][def_sub1[0].index("TEST_DATE")],
                def_sub1[i][def_sub1[0].index("LANE_NO")]] == [def_sub2[j][def_sub2[0].index("STATE_CODE")],
                                                               def_sub2[j][def_sub2[0].index("SHRP_ID")],
                                                               def_sub2[j][def_sub2[0].index("CONSTRUCTION_NO")],
                                                               def_sub2[j][def_sub2[0].index("TEST_DATE")],
                                                               def_sub2[j][def_sub2[0].index("LANE_NO")]]:
                # Add deflection
                def_sub2[j][def_sub2[0].index("MAX_DEFS")].append(def_sub1[i][def_sub1[0].index("MAX_DEF")])
                status = True

        if not status:
            def_sub2.append(def_sub1[i][:-1])
            def_sub2[-1].append([def_sub1[i][def_sub1[0].index("MAX_DEF")]])

        sys.stdout.write("\r- [DEF 2]: %d/%d" % (i, len(def_sub1) - 1))

    print("")

    # (3) Calc mean, max and characteristic deflections
    def_sub3[0].extend(["F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR"])

    for i in range(1, len(def_sub2)):

        status = False
        max_defs = def_sub2[i][def_sub2[0].index("MAX_DEFS")]
        deflections = ["", "", ""]
        if len(deflections) > 1:
            deflections[0] = statistics.mean(max_defs)  # Average DEF
            deflections[1] = max(max_defs)  # Maximum DEF
            deflections[2] = statistics.mean(max_defs) + statistics.stdev(max_defs) * 2  # Characteristic DEF

        # If there is a previous register
        for j in range(1, len(def_sub3)):
            if [def_sub2[i][def_sub2[0].index("STATE_CODE")],
                def_sub2[i][def_sub2[0].index("SHRP_ID")],
                def_sub2[i][def_sub2[0].index("CONSTRUCTION_NO")],
                def_sub2[i][def_sub2[0].index("TEST_DATE")]] == [def_sub3[j][def_sub3[0].index("STATE_CODE")],
                                                                 def_sub3[j][def_sub3[0].index("SHRP_ID")],
                                                                 def_sub3[j][def_sub3[0].index("CONSTRUCTION_NO")],
                                                                 def_sub3[j][def_sub3[0].index("TEST_DATE")]]:

                if def_sub2[i][def_sub2[0].index("LANE_NO")] == "F1":
                    def_sub3[j][def_sub3[0].index("F1_DEF_AVG")] = deflections[0]
                    def_sub3[j][def_sub3[0].index("F1_DEF_MAX")] = deflections[1]
                    def_sub3[j][def_sub3[0].index("F1_DEF_CHR")] = deflections[2]
                else:
                    def_sub3[j][def_sub3[0].index("F3_DEF_AVG")] = deflections[0]
                    def_sub3[j][def_sub3[0].index("F3_DEF_MAX")] = deflections[1]
                    def_sub3[j][def_sub3[0].index("F3_DEF_CHR")] = deflections[2]

                status = True

        if not status:
            def_sub3.append(def_sub2[i][:-1])
            def_sub3[-1].extend([""] * 6)
            if def_sub2[i][def_sub2[0].index("LANE_NO")] == "F1":
                def_sub3[-1][-6] = deflections[0]
                def_sub3[-1][-5] = deflections[1]
                def_sub3[-1][-4] = deflections[2]
            else:
                def_sub3[-1][-3] = deflections[0]
                def_sub3[-1][-2] = deflections[1]
                def_sub3[-1][-1] = deflections[2]

        sys.stdout.write("\r- [DEF 3]: %d/%d" % (i, len(def_sub2) - 1))

    print("")

    for i in range(1, len(def_sub3)):
        def_sub3[i] = [def_sub3[i][def_sub3[0].index("STATE_CODE")], def_sub3[i][def_sub3[0].index("SHRP_ID")],
                       def_sub3[i][def_sub3[0].index("CONSTRUCTION_NO")], def_sub3[i][def_sub3[0].index("TEST_DATE")],
                       def_sub3[i][def_sub3[0].index("F1_DEF_AVG")], def_sub3[i][def_sub3[0].index("F1_DEF_MAX")],
                       def_sub3[i][def_sub3[0].index("F1_DEF_CHR")], def_sub3[i][def_sub3[0].index("F3_DEF_AVG")],
                       def_sub3[i][def_sub3[0].index("F3_DEF_MAX")], def_sub3[i][def_sub3[0].index("F3_DEF_CHR")]]

    def_sub3[0] = ["STATE_CODE", "SHRP_ID", "CONSTRUCTION_NO", "TEST_DATE",
                   "F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR"]

    save_csv(p_path, def_sub3)


def extract_cnd(save_path, cnd_filename, cnd_sheet="EXPERIMENT_SECTION"):
    cnd_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "CN_ASSIGN_DATE": None,
    }
    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=cnd_filename, sheet_name=cnd_sheet)

    # Append header
    cnd_list = [[column for column in df.columns]]

    for cnd_col in cnd_cols:
        if cnd_cols[cnd_col] is None:
            cnd_cols[cnd_col] = cnd_list[0].index(cnd_col)

    # Append values
    for values in df.values:
        cnd_list.append([value for value in values])

    for i in range(0, len(cnd_list)):
        row = []
        for cnd_col in cnd_cols:
            row.append(cnd_list[i][cnd_cols[cnd_col]])
        cnd_list[i] = row

    cnd_result = deepcopy(cnd_list)
    cnd_result[0].append("MAX_CN")
    #
    for i in range(1, len(cnd_result)):
        result = max(filter(lambda x:
                            x[cnd_list[0].index("STATE_CODE")] == cnd_result[i][cnd_result[0].index("STATE_CODE")] and
                            x[cnd_list[0].index("SHRP_ID")] == cnd_result[i][cnd_result[0].index("SHRP_ID")], cnd_list),
                     key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[cnd_list[0].index("CONSTRUCTION_NO")]

        cnd_result[i].append(result)

    save_csv(save_path, cnd_result)


def extract_snu(save_path, snu_filename, snu_sheet="TRF_ESAL_INPUTS_SUMMARY"):
    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=snu_filename, sheet_name=snu_sheet)

    # Append header
    snu_list = [[column for column in df.columns]]

    # Append values
    for values in df.values:
        snu_list.append([value for value in values])

    save_csv(save_path, snu_list)


def extract_trf(p_path, p_file, p_sheet=("TRF_HIST_EST_ESAL", "TRF_MON_EST_ESAL")):
    """
    Extract, prepare and unify data from historic and LTPP traffic estimation tables

    :param p_path: path of output file
    :param p_file: path of input file
    :param p_sheet: Excel worksheet tabs
    :return:
    """

    # Read Excel file and save as DataFrame
    trf_his = pandas.read_excel(io=p_file, sheet_name=p_sheet[0])
    trf_mon = pandas.read_excel(io=p_file, sheet_name=p_sheet[1])

    trf_his_list = [[column for column in trf_his.columns]]
    trf_mon_list = [[column for column in trf_mon.columns]]

    for values in trf_his.values:
        trf_his_list.append([value for value in values])
    for values in trf_mon.values:
        trf_mon_list.append([value for value in values])

    trf_results = [["SHRP_ID", "STATE_CODE", "YEAR_MON_EST",
                    "AADT_ALL_VEHIC", "AADT_TRUCK_COMBO", "ANL_KESAL_LTPP_LN_YR"]]

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (p_sheet[0], p_file))
    for i in range(1, len(trf_his_list)):
        trf_results.append([
            trf_his_list[i][trf_his_list[0].index("SHRP_ID")],
            trf_his_list[i][trf_his_list[0].index("STATE_CODE")],
            trf_his_list[i][trf_his_list[0].index("YEAR_HIST_EST")],
            trf_his_list[i][trf_his_list[0].index("AADT_ALL_VEHIC")],
            trf_his_list[i][trf_his_list[0].index("AADT_TRUCK_COMBO")],
            trf_his_list[i][trf_his_list[0].index("ANL_KESAL_LTPP_LN_YR")],
        ])
        sys.stdout.write("\r- [TRF HIS]: %d/%d" % (i, len(trf_his_list) - 1))
    print("")

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (p_sheet[1], p_file))
    for i in range(1, len(trf_mon_list)):
        status = False

        for j in range(1, len(trf_results)):
            if [trf_mon_list[i][trf_mon_list[0].index("SHRP_ID")],
                trf_mon_list[i][trf_mon_list[0].index("STATE_CODE")],
                trf_mon_list[i][trf_mon_list[0].index("YEAR_MON_EST")]] == \
                    [trf_results[j][trf_results[0].index("SHRP_ID")],
                     trf_results[j][trf_results[0].index("STATE_CODE")],
                     trf_results[j][trf_results[0].index("YEAR_MON_EST")]]:
                #
                [trf_results[j][trf_results[0].index("AADT_ALL_VEHIC")],
                 trf_results[j][trf_results[0].index("AADT_TRUCK_COMBO")],
                 trf_results[j][trf_results[0].index("ANL_KESAL_LTPP_LN_YR")]] = \
                    [trf_mon_list[i][trf_mon_list[0].index("AADT_ALL_VEHIC")],
                     trf_mon_list[i][trf_mon_list[0].index("AADT_TRUCK_COMBO")],
                     trf_mon_list[i][trf_mon_list[0].index("ANL_KESAL_LTPP_LN_YR")]]

                status = True
                break

        if not status:
            trf_results.append([
                trf_mon_list[i][trf_mon_list[0].index("SHRP_ID")],
                trf_mon_list[i][trf_mon_list[0].index("STATE_CODE")],
                trf_mon_list[i][trf_mon_list[0].index("YEAR_MON_EST")],
                trf_mon_list[i][trf_mon_list[0].index("AADT_ALL_VEHIC")],
                trf_mon_list[i][trf_mon_list[0].index("AADT_TRUCK_COMBO")],
                trf_mon_list[i][trf_mon_list[0].index("ANL_KESAL_LTPP_LN_YR")],
            ])

        sys.stdout.write("\r- [TRF MON]: %d/%d" % (i, len(trf_mon_list) - 1))
    print("")

    [trf_results[0][trf_results[0].index("AADT_ALL_VEHIC")],
     trf_results[0][trf_results[0].index("AADT_TRUCK_COMBO")],
     trf_results[0][trf_results[0].index("ANL_KESAL_LTPP_LN_YR")]] = ["AADT", "AADTT", "KESAL"]

    extract_trf_cn(p_path, trf_results)


def row_to_str(p_row):
    for j in range(0, len(p_row)):
        p_row[j] = str(p_row[j])  # Convert data to string
        p_row[j] = p_row[j].replace(".", ",")  # Replace dots with commas
        p_row[j] = p_row[j].replace("nan", "")  # Replace "nan" with void
    return p_row


def int_float(p_value):
    p_value = (str(p_value)).replace(",", ".")
    return int(float(p_value))


def extract_trf_cn(save_path, trf_list):
    """
    Take traffic unified data and accumulate values depending on Construction Number assign date

    :param save_path: path of output file
    :param trf_list: traffic unified data
    :return:
    """
    cnd_list = load_csv(global_csv_path + "cnd.csv")

    for i in range(1, len(trf_list)):
        trf_list[i] = row_to_str(trf_list[i])

        if len(trf_list[i][trf_list[0].index("SHRP_ID")]) < 4:
            trf_list[i][trf_list[0].index("SHRP_ID")] = "0" + trf_list[i][trf_list[0].index("SHRP_ID")]

        # Si existe, obtiene el Número de Construcción de fecha IGUAL o MENOR MÁXIMA que la de Tráfico
        if len(list(filter(lambda x:
                           x[cnd_list[0].index("STATE_CODE")] == trf_list[i][trf_list[0].index("STATE_CODE")] and
                           x[cnd_list[0].index("SHRP_ID")] == trf_list[i][trf_list[0].index("SHRP_ID")] and
                           x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] <= trf_list[i][
                               trf_list[0].index("YEAR_MON_EST")],
                           cnd_list))) > 0:
            trf_list[i].append(max(filter(lambda x:
                                          x[cnd_list[0].index("STATE_CODE")] == trf_list[i][
                                              trf_list[0].index("STATE_CODE")] and
                                          x[cnd_list[0].index("SHRP_ID")] == trf_list[i][
                                              trf_list[0].index("SHRP_ID")] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] <= trf_list[i][
                                              trf_list[0].index("YEAR_MON_EST")],
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])

        # Si existe, obtiene el Número de Construcción de fecha MAYOR MÍNIMA que la de Tráfico
        elif len(list(filter(lambda x:
                             x[cnd_list[0].index("STATE_CODE")] == trf_list[i][trf_list[0].index("STATE_CODE")] and
                             x[cnd_list[0].index("SHRP_ID")] == trf_list[i][trf_list[0].index("SHRP_ID")] and
                             x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] > trf_list[i][
                                 trf_list[0].index("YEAR_MON_EST")],
                             cnd_list))) > 0:
            trf_list[i].append(min(filter(lambda x:
                                          x[cnd_list[0].index("STATE_CODE")] == trf_list[i][
                                              trf_list[0].index("STATE_CODE")] and
                                          x[cnd_list[0].index("SHRP_ID")] == trf_list[i][
                                              trf_list[0].index("SHRP_ID")] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] > trf_list[i][
                                              trf_list[0].index("YEAR_MON_EST")],
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
                                      trf_result[i][trf_result[0].index("STATE_CODE")],
                                      trf_result[i][trf_result[0].index("CONSTRUCTION_NO")]] and

                                  x[trf_list[0].index("YEAR_MON_EST")] <= trf_result[i][
                                      trf_result[0].index("YEAR_MON_EST")], trf_list))

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

    save_csv(save_path, trf_result)


def get_last_day(year, month):
    day = calendar.monthrange(int(year), int(month))[1]
    date = str(year).zfill(4) + str(month).zfill(2) + str(day).zfill(2)
    date = str(pd.to_datetime(date, format="%Y%m%d"))
    return date


def extract_vws_cn(save_path, vws_list):
    """
    Take VWS unified data and accumulate values depending on Construction Number assign date

    :param save_path: path of output file
    :param vws_list: VWS unified data
    :return:
    """
    cnd_list = load_csv(global_csv_path + "cnd.csv")

    for i in range(1, len(vws_list)):
        vws_list[i] = row_to_str(vws_list[i])

        # Completa con ceros si el ID no tiene 4 cifras
        vws_list[i][vws_list[0].index("SHRP_ID")] = vws_list[i][vws_list[0].index("SHRP_ID")].zfill(4)

        # Si existe, obtiene el Número de Construcción de fecha IGUAL o MENOR MÁXIMA que la de Tráfico
        if len(list(filter(lambda x:
                           [x[cnd_list[0].index("STATE_CODE")],
                            x[cnd_list[0].index("SHRP_ID")]] ==
                           [vws_list[i][vws_list[0].index("STATE_CODE")],
                            vws_list[i][vws_list[0].index("SHRP_ID")]] and
                           x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] <= get_last_day(
                               vws_list[i][vws_list[0].index("YEAR")],
                               vws_list[i][vws_list[0].index("MONTH")]),
                           cnd_list))) > 0:
            vws_list[i].append(max(filter(lambda x:
                                          [x[cnd_list[0].index("STATE_CODE")],
                                           x[cnd_list[0].index("SHRP_ID")]] ==
                                          [vws_list[i][vws_list[0].index("STATE_CODE")],
                                           vws_list[i][vws_list[0].index("SHRP_ID")]] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] <= get_last_day(
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
                             x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] > get_last_day(
                                 vws_list[i][vws_list[0].index("YEAR")],
                                 vws_list[i][vws_list[0].index("MONTH")]),
                             cnd_list))) > 0:
            vws_list[i].append(min(filter(lambda x:
                                          [x[cnd_list[0].index("STATE_CODE")],
                                           x[cnd_list[0].index("SHRP_ID")]] ==
                                          [vws_list[i][vws_list[0].index("STATE_CODE")],
                                           vws_list[i][vws_list[0].index("SHRP_ID")]] and
                                          x[cnd_list[0].index("CN_ASSIGN_DATE")][0:4] > get_last_day(
                                              vws_list[i][vws_list[0].index("YEAR")],
                                              vws_list[i][vws_list[0].index("MONTH")]),
                                          cnd_list), key=itemgetter(cnd_list[0].index("CONSTRUCTION_NO")))[
                                   cnd_list[0].index("CONSTRUCTION_NO")])
        else:
            vws_list[i].append("")
        sys.stdout.write("\r- [VWS CN]: %d/%d" % (i, len(vws_list) - 1))
    print("")
    vws_list[0].extend(["CONSTRUCTION_NO", "MON_PREC_CUM", "MON_SNOW_CUM"])

    # FIXME
    # vws_list[0].extend(["ANN_PREC_CUM", "ANN_SNOW_CUM"])

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
            # FIXME
            # Cumulate annual values
            # year = ann_prec = ann_snow = []
            # for j in range(0, len(last_values)):
            #     if last_values[j][vws_list[0].index("YEAR")] not in year:
            #         year.append(last_values[j][vws_list[0].index("YEAR")])
            #         ann_prec.append(last_values[j][vws_result[0].index("TOTAL_ANN_PRECIP")])
            #         ann_snow.append(last_values[j][vws_result[0].index("TOTAL_SNOWFALL_YR")])

            # Cumulate monthly values
            mon_prec = [x[vws_list[0].index("TOTAL_MON_PRECIP")] for x in last_values]
            mon_snow = [x[vws_list[0].index("TOTAL_SNOWFALL_MONTH")] for x in last_values]

            vws_result[i].append(addition(mon_prec)) if addition(mon_prec) is not None else vws_result[i].append("")
            vws_result[i].append(addition(mon_snow)) if addition(mon_snow) is not None else vws_result[i].append("")

            # FIXME
            # vws_result[i].append(addition(ann_prec)) if addition(ann_prec) is not None else vws_result[i].append("")
            # vws_result[i].append(addition(ann_snow)) if addition(ann_snow) is not None else vws_result[i].append("")

        sys.stdout.write("\r- [VWS SUM]: %d/%d" % (i, len(vws_result) - 1))
    print("")
    save_csv(save_path, vws_result)


def average(p_list):
    result = count = 0
    for value in p_list:
        if value != "":
            result += int_float(value)
            count += 1
    if count > 0:
        return result / count
    else:
        return None


def addition(p_list):
    result = count = 0
    for value in p_list:
        if value != "":
            result += int_float(value)
            count += 1
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

    vws_cols = {
        "SHRP_ID": None, "STATE_CODE": None, "YEAR": None, "MONTH": None,
        "TOTAL_ANN_PRECIP": None, "TOTAL_MON_PRECIP": None,
        "TOTAL_SNOWFALL_YR": None, "TOTAL_SNOWFALL_MONTH": None,
        "MEAN_ANN_TEMP_AVG": None, "MEAN_MON_TEMP_AVG": None,
        "FREEZE_INDEX_YR": None, "FREEZE_INDEX_MONTH": None,
        "FREEZE_THAW_YR": None, "FREEZE_THAW_MONTH": None,
        "MEAN_ANN_WIND_AVG": None, "MEAN_MON_WIND_AVG": None,
        "MAX_ANN_HUM_AVG": None, "MAX_MON_HUM_AVG": None,
        "MIN_ANN_HUM_AVG": None, "MIN_MON_HUM_AVG": None
    }

    vws_sheet = ["CLM_VWS_PRECIP_ANNUAL", "CLM_VWS_PRECIP_MONTH",
                 "CLM_VWS_TEMP_ANNUAL", "CLM_VWS_TEMP_MONTH",
                 "CLM_VWS_WIND_ANNUAL", "CLM_VWS_WIND_MONTH",
                 "CLM_VWS_HUMIDITY_ANNUAL", "CLM_VWS_HUMIDITY_MONTH"]

    # Read Excel file and save as DataFrame
    vws_pr_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[0])
    vws_pr_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[1])
    vws_te_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[2])
    vws_te_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[3])
    vws_wi_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[4])
    vws_wi_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[5])
    vws_hu_a = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[6])
    vws_hu_m = pandas.read_excel(io=vws_filename, sheet_name=vws_sheet[7])

    vws_pr_a_list = [[column for column in vws_pr_a.columns]]
    vws_pr_m_list = [[column for column in vws_pr_m.columns]]
    vws_te_a_list = [[column for column in vws_te_a.columns]]
    vws_te_m_list = [[column for column in vws_te_m.columns]]
    vws_wi_a_list = [[column for column in vws_wi_a.columns]]
    vws_wi_m_list = [[column for column in vws_wi_m.columns]]
    vws_hu_a_list = [[column for column in vws_hu_a.columns]]
    vws_hu_m_list = [[column for column in vws_hu_m.columns]]

    for values in vws_pr_a.values:
        vws_pr_a_list.append([value for value in values])
    for values in vws_pr_m.values:
        vws_pr_m_list.append([value for value in values])
    for values in vws_te_a.values:
        vws_te_a_list.append([value for value in values])
    for values in vws_te_m.values:
        vws_te_m_list.append([value for value in values])
    for values in vws_wi_a.values:
        vws_wi_a_list.append([value for value in values])
    for values in vws_wi_m.values:
        vws_wi_m_list.append([value for value in values])
    for values in vws_hu_a.values:
        vws_hu_a_list.append([value for value in values])
    for values in vws_hu_m.values:
        vws_hu_m_list.append([value for value in values])

    vws_results = [list(vws_cols.keys())]

    # MONTH measures
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[1], vws_filename))
    vws_results = vws_add_values(vws_pr_m_list, vws_results, True, ["TOTAL_MON_PRECIP",
                                                                    "TOTAL_SNOWFALL_MONTH"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[3], vws_filename))
    vws_results = vws_add_values(vws_te_m_list, vws_results, True, ["MEAN_MON_TEMP_AVG",
                                                                    "FREEZE_INDEX_MONTH",
                                                                    "FREEZE_THAW_MONTH"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[5], vws_filename))
    vws_results = vws_add_values(vws_wi_m_list, vws_results, True, ["MEAN_MON_WIND_AVG"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[7], vws_filename))
    vws_results = vws_add_values(vws_hu_m_list, vws_results, True, ["MAX_MON_HUM_AVG",
                                                                    "MIN_MON_HUM_AVG"])

    # ANNUAL measures
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[0], vws_filename))
    vws_results = vws_add_values(vws_pr_a_list, vws_results, False, ["TOTAL_ANN_PRECIP",
                                                                     "TOTAL_SNOWFALL_YR"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[2], vws_filename))
    vws_results = vws_add_values(vws_te_a_list, vws_results, False, ["MEAN_ANN_TEMP_AVG",
                                                                     "FREEZE_INDEX_YR",
                                                                     "FREEZE_THAW_YR"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[4], vws_filename))
    vws_results = vws_add_values(vws_wi_a_list, vws_results, False, ["MEAN_ANN_WIND_AVG"])

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (vws_sheet[6], vws_filename))
    vws_results = vws_add_values(vws_hu_a_list, vws_results, False, ["MAX_ANN_HUM_AVG",
                                                                     "MIN_ANN_HUM_AVG"])

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

    extract_vws_cn(save_path, vws_results)


def vws_add_values(vws_in, vws_out, by_month, vws_columns):
    for i in range(1, len(vws_in)):
        status = False
        for j in range(1, len(vws_out)):
            if by_month:
                if [vws_out[j][vws_out[0].index("SHRP_ID")],
                    vws_out[j][vws_out[0].index("STATE_CODE")],
                    vws_out[j][vws_out[0].index("YEAR")],
                    vws_out[j][vws_out[0].index("MONTH")]] == [vws_in[i][vws_in[0].index("SHRP_ID")],
                                                               vws_in[i][vws_in[0].index("STATE_CODE")],
                                                               vws_in[i][vws_in[0].index("YEAR")],
                                                               vws_in[i][vws_in[0].index("MONTH")]]:
                    for vws_column in vws_columns:
                        vws_out[j][vws_out[0].index(vws_column)] = vws_in[i][
                            vws_in[0].index(vws_column)]
                    status = True
                    break
            else:
                if [vws_out[j][vws_out[0].index("SHRP_ID")],
                    vws_out[j][vws_out[0].index("STATE_CODE")],
                    vws_out[j][vws_out[0].index("YEAR")]] == [vws_in[i][vws_in[0].index("SHRP_ID")],
                                                              vws_in[i][vws_in[0].index("STATE_CODE")],
                                                              vws_in[i][vws_in[0].index("YEAR")]]:
                    for vws_column in vws_columns:
                        vws_out[j][vws_out[0].index(vws_column)] = vws_in[i][
                            vws_in[0].index(vws_column)]
                    status = True

        if not status:
            vws_out.append([""] * len(vws_out[0]))
            vws_out[-1][vws_out[0].index("SHRP_ID")] = vws_in[i][vws_in[0].index("SHRP_ID")]
            vws_out[-1][vws_out[0].index("STATE_CODE")] = vws_in[i][vws_in[0].index("STATE_CODE")]
            vws_out[-1][vws_out[0].index("YEAR")] = vws_in[i][vws_in[0].index("YEAR")]
            if by_month:
                vws_out[-1][vws_out[0].index("MONTH")] = vws_in[i][vws_in[0].index("MONTH")]
            for vws_column in vws_columns:
                vws_out[-1][vws_out[0].index(vws_column)] = vws_in[i][vws_in[0].index(vws_column)]

        sys.stdout.write("\r- [VWS] %s: %d/%d" % (vws_columns[0], i, len(vws_in) - 1))
    print("")
    return vws_out


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


def main(xls_file, csv_path, question=False):
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
    csv_tables = [csv_path + s for s in ["iri.csv", "def.csv", "skn.csv", "cnd.csv", "snu.csv", "vws.csv", "trf.csv"]]

    if not question:
        question = question_yn("\U0001F4BB\U0001F4AC Do you want to start a clean process?")

    total_time = 0

    for k in range(0, len(csv_tables)):
        if not os.path.isfile(csv_tables[k]) or (os.path.isfile(csv_tables[k]) and (question or question_yn(
                "\U0001F4BB\U0001F4AC File \"%s\" already exists. Regenerate?" % csv_tables[k]))):
            start_time = time.time()

            extract_iri(csv_tables[k], xls_file) if k == 0 else 0
            extract_def(csv_tables[k], xls_file) if k == 1 else 0
            extract_skn(csv_tables[k], xls_file) if k == 2 else 0
            extract_cnd(csv_tables[k], xls_file) if k == 3 else 0
            extract_snu(csv_tables[k], xls_file) if k == 4 else 0
            extract_vws(csv_tables[k], xls_file) if k == 5 else 0
            extract_trf(csv_tables[k], xls_file) if k == 6 else 0

            partial_time = time.time() - start_time
            total_time += partial_time
            print("\U00002BA1 File \"%s\" generated from \"%s\" (%s)\n" % (
                csv_tables[k], xls_file, str_time(partial_time)))

    print("\U0001F6C8 Program finished in %s" % str_time(total_time))


if __name__ == '__main__':
    xls_list = []

    for file in os.listdir("./xls"):
        if file.endswith(".xlsx"):
            xls_list.append(os.path.join("./xls", file).replace("\\", "/"))

    # xls_list = ["./xls/08_Colorado.xlsx"]

    for k in range(0, len(xls_list)):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("(%s/%s) Current file: \"%s\"" % (k + 1, len(xls_list), xls_list[k]))

        csv_path = "./csv/" + os.path.basename(xls_list[k])[0:-5] + "/"
        main(xls_list[k], csv_path, True)
