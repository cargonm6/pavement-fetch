import math
import os
import statistics
import sys
import time
from operator import itemgetter

import pandas

import csv


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

    cnd_result = cnd_list
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


def extract_trf(save_path, trf_filename):
    trf_cols = {
        "SHRP_ID": None, "STATE_CODE": None, "YEAR_MON_EST": None,
        "AADT_ALL_VEHIC": None, "AADT_TRUCK_COMBO": None, "ANL_KESAL_LTPP_LN_YR": None
    }

    trf_sheet = ["TRF_HIST_EST_ESAL", "TRF_MON_EST_ESAL"]

    # Read Excel file and save as DataFrame
    trf_his = pandas.read_excel(io=trf_filename, sheet_name=trf_sheet[0])
    trf_mon = pandas.read_excel(io=trf_filename, sheet_name=trf_sheet[1])

    trf_his_list = [[column for column in trf_his.columns]]
    trf_mon_list = [[column for column in trf_mon.columns]]

    for values in trf_his.values:
        trf_his_list.append([value for value in values])
    for values in trf_mon.values:
        trf_mon_list.append([value for value in values])

    trf_results = [list(trf_cols.keys())]

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (trf_sheet[0], trf_filename))
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

    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (trf_sheet[1], trf_filename))
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

    extract_trf_cn(save_path, trf_results)


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
    cnd_list = load_csv("./csv/cnd.csv")

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

    trf_list[1:len(trf_list)] = list(
        sorted(trf_list[1:len(trf_list)], key=itemgetter(trf_list[0].index("YEAR_MON_EST"))))

    trf_result = trf_list

    for i in range(1, len(trf_result)):

        if len(list(filter(lambda x:
                           [x[trf_list[0].index("SHRP_ID")],
                            x[trf_list[0].index("STATE_CODE")],
                            x[trf_list[0].index("CONSTRUCTION_NO")]] == [
                               trf_result[i][trf_result[0].index("SHRP_ID")],
                               trf_result[i][trf_result[0].index("STATE_CODE")],
                               trf_result[i][trf_result[0].index("CONSTRUCTION_NO")]] and

                           x[trf_list[0].index("YEAR_MON_EST")] < trf_result[i][
                               trf_result[0].index("YEAR_MON_EST")], trf_list))) > 0:

            last_value = max(filter(lambda x:
                                    [x[trf_list[0].index("SHRP_ID")],
                                     x[trf_list[0].index("STATE_CODE")],
                                     x[trf_list[0].index("CONSTRUCTION_NO")]] == [
                                        trf_result[i][trf_result[0].index("SHRP_ID")],
                                        trf_result[i][trf_result[0].index("STATE_CODE")],
                                        trf_result[i][trf_result[0].index("CONSTRUCTION_NO")]] and

                                    x[trf_list[0].index("YEAR_MON_EST")] < trf_result[i][
                                        trf_result[0].index("YEAR_MON_EST")], trf_list),
                             key=itemgetter(trf_list[0].index("YEAR_MON_EST")))

            last_at = last_value[trf_list[0].index("AADT")]
            last_tt = last_value[trf_list[0].index("AADTT")]
            last_ke = last_value[trf_list[0].index("KESAL")]

            if trf_result[i][trf_result[0].index("AADT")] != "" and last_at != "":
                trf_result[i][trf_result[0].index("AADT")] = int_float(
                    trf_result[i][trf_result[0].index("AADT")]) + int_float(last_at)
            if trf_result[i][trf_result[0].index("AADTT")] != "" and last_tt != "":
                trf_result[i][trf_result[0].index("AADTT")] = int_float(
                    trf_result[i][trf_result[0].index("AADTT")]) + int_float(last_tt)
            if trf_result[i][trf_result[0].index("KESAL")] != "" and last_ke != "":
                trf_result[i][trf_result[0].index("KESAL")] = int_float(
                    trf_result[i][trf_result[0].index("KESAL")]) + int_float(last_ke)

        sys.stdout.write("\r- [TRF SUM]: %d/%d" % (i, len(trf_result) - 1))
    print("")
    save_csv(save_path, trf_result)


def extract_def(save_path, def_filename, def_sheet="MON_DEFL_DROP_DATA"):
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (def_sheet, def_filename))

    # Dictionary
    def_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "TEST_DATE": None,
        "POINT_LOC": None, "LANE_NO": None, "DROP_HEIGHT": None, "PEAK_DEFL_1": None, "PEAK_DEFL_2": None,
        "PEAK_DEFL_3": None, "PEAK_DEFL_4": None, "PEAK_DEFL_5": None, "PEAK_DEFL_6": None,
    }

    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=def_filename, sheet_name=def_sheet)

    # Append header
    def_list = [[column for column in df.columns]]
    def_sub1 = [[column for column in df.columns]]
    def_sub2 = [[column for column in df.columns]]
    def_sub3 = [[column for column in df.columns]]

    # Append values
    for values in df.values:
        def_list.append([value for value in values])

    for def_col in def_cols:
        if def_cols[def_col] is None:
            def_cols[def_col] = def_list[0].index(def_col)

    # Filter: only DROP_HEIGHT = 2 and LANE_NO = F1 | F3
    def_list = [[column for column in df.columns]] + list(
        filter(lambda x: x[def_cols["DROP_HEIGHT"]] == 2 and (x[def_cols["LANE_NO"]] in ["F1", "F3"]), def_list))

    # For loop in def_list
    for i in range(1, len(def_list)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub1)):
            if [def_list[i][def_cols["STATE_CODE"]],
                def_list[i][def_cols["SHRP_ID"]],
                def_list[i][def_cols["CONSTRUCTION_NO"]],
                def_list[i][def_cols["TEST_DATE"]],
                def_list[i][def_cols["LANE_NO"]],
                def_list[i][def_cols["POINT_LOC"]]] == [def_sub1[j][def_cols["STATE_CODE"]],
                                                        def_sub1[j][def_cols["SHRP_ID"]],
                                                        def_sub1[j][def_cols["CONSTRUCTION_NO"]],
                                                        def_sub1[j][def_cols["TEST_DATE"]],
                                                        def_sub1[j][def_cols["LANE_NO"]],
                                                        def_sub1[j][def_cols["POINT_LOC"]]]:

                # Si existía esa entrada, comprueba si PEAK_DEFL_1 es el máximo, y si no, lo copia
                if def_sub1[j][def_cols["PEAK_DEFL_1"]] < def_list[i][def_cols["PEAK_DEFL_1"]]:
                    def_sub1[j][def_cols["PEAK_DEFL_1"]] = def_list[i][def_cols["PEAK_DEFL_1"]]

                status = True

        # Si no existía esa entrada, la copia
        if not status:
            def_sub1.append(def_list[i])

        sys.stdout.write("\r- [DEF etapa 1]: %d/%d" % (i, len(def_list) - 1))

    print("")

    # For loop in def_list
    for i in range(1, len(def_sub1)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub2)):
            if [def_sub1[i][def_cols["STATE_CODE"]],
                def_sub1[i][def_cols["SHRP_ID"]],
                def_sub1[i][def_cols["CONSTRUCTION_NO"]],
                def_sub1[i][def_cols["TEST_DATE"]],
                def_sub1[i][def_cols["LANE_NO"]]] == [def_sub2[j][def_cols["STATE_CODE"]],
                                                      def_sub2[j][def_cols["SHRP_ID"]],
                                                      def_sub2[j][def_cols["CONSTRUCTION_NO"]],
                                                      def_sub2[j][def_cols["TEST_DATE"]],
                                                      def_sub2[j][def_cols["LANE_NO"]]]:
                # Añade la deflexión
                def_sub2[j].append(def_sub1[i][def_cols["PEAK_DEFL_1"]])
                status = True

        # Si no existía esa entrada, la copia y añade la deflexión al final
        if not status:
            def_sub2.append(def_sub1[i])
            def_sub2[-1].append(def_sub1[i][def_cols["PEAK_DEFL_1"]])

        sys.stdout.write("\r- [DEF etapa 2]: %d/%d" % (i, len(def_sub1) - 1))

    print("")

    for i in range(1, len(def_sub2)):
        deflections = def_sub2[i][len(def_sub2[0]):len(def_sub2[i])]
        def_sub2[i].append(statistics.mean(deflections))
        def_sub2[i].append(max(deflections))
        def_sub2[i].append(statistics.mean(deflections) + 2 * statistics.stdev(deflections))

    # For loop in def_list
    for i in range(1, len(def_sub2)):
        status = False

        # If there is a previous register
        for j in range(1, len(def_sub3)):
            if [def_sub2[i][def_cols["STATE_CODE"]],
                def_sub2[i][def_cols["SHRP_ID"]],
                def_sub2[i][def_cols["CONSTRUCTION_NO"]],
                def_sub2[i][def_cols["TEST_DATE"]]] == [def_sub3[j][def_cols["STATE_CODE"]],
                                                        def_sub3[j][def_cols["SHRP_ID"]],
                                                        def_sub3[j][def_cols["CONSTRUCTION_NO"]],
                                                        def_sub3[j][def_cols["TEST_DATE"]]]:
                if def_sub2[i][def_cols["LANE_NO"]] == "F1":
                    def_sub3[j][def_cols["PEAK_DEFL_1"]] = def_sub2[i][-3]
                    def_sub3[j][def_cols["PEAK_DEFL_2"]] = def_sub2[i][-2]
                    def_sub3[j][def_cols["PEAK_DEFL_3"]] = def_sub2[i][-1]
                else:
                    def_sub3[j][def_cols["PEAK_DEFL_4"]] = def_sub2[i][-3]
                    def_sub3[j][def_cols["PEAK_DEFL_5"]] = def_sub2[i][-2]
                    def_sub3[j][def_cols["PEAK_DEFL_6"]] = def_sub2[i][-1]

                status = True

        # Si no existía esa entrada, la copia y añade la deflexión al final
        if not status:
            def_sub3.append(def_sub2[i][0:len(def_sub2[0])])
            if def_sub2[i][def_cols["LANE_NO"]] == "F1":
                def_sub3[-1][def_cols["PEAK_DEFL_1"]] = def_sub2[i][-3]
                def_sub3[-1][def_cols["PEAK_DEFL_2"]] = def_sub2[i][-2]
                def_sub3[-1][def_cols["PEAK_DEFL_3"]] = def_sub2[i][-1]
            else:
                def_sub3[-1][def_cols["PEAK_DEFL_4"]] = def_sub2[i][-3]
                def_sub3[-1][def_cols["PEAK_DEFL_5"]] = def_sub2[i][-2]
                def_sub3[-1][def_cols["PEAK_DEFL_6"]] = def_sub2[i][-1]

        sys.stdout.write("\r- [DEF etapa 3]: %d/%d" % (i, len(def_sub2) - 1))

    [def_sub3[0][def_cols["PEAK_DEFL_1"]], def_sub3[0][def_cols["PEAK_DEFL_2"]],
     def_sub3[0][def_cols["PEAK_DEFL_3"]], def_sub3[0][def_cols["PEAK_DEFL_4"]],
     def_sub3[0][def_cols["PEAK_DEFL_5"]], def_sub3[0][def_cols["PEAK_DEFL_6"]]] = ["F1_DEF_AVG", "F1_DEF_MAX",
                                                                                    "F1_DEF_CHR", "F3_DEF_AVG",
                                                                                    "F3_DEF_MAX", "F3_DEF_CHR"]

    for i in range(0, len(def_sub3)):
        def_sub3[i] = [def_sub3[i][def_cols["STATE_CODE"]], def_sub3[i][def_cols["SHRP_ID"]],
                       def_sub3[i][def_cols["CONSTRUCTION_NO"]], def_sub3[i][def_cols["TEST_DATE"]],
                       def_sub3[i][def_cols["PEAK_DEFL_1"]], def_sub3[i][def_cols["PEAK_DEFL_2"]],
                       def_sub3[i][def_cols["PEAK_DEFL_3"]], def_sub3[i][def_cols["PEAK_DEFL_4"]],
                       def_sub3[i][def_cols["PEAK_DEFL_5"]], def_sub3[i][def_cols["PEAK_DEFL_6"]]]

    print("")

    save_csv(save_path, def_sub3)


def extract_iri(save_path, iri_filename, iri_sheet="MON_HSS_PROFILE_SECTION"):
    print("\U0001F6C8 Extracting \"%s\" from \"%s\"" % (iri_sheet, iri_filename))

    # For each STATE_CODE + SHRP_ID + CONSTRUCTION_NO + VISIT_DATE:
    # - Obtain total number of runs
    # - Calculate the average MRI
    # - Compute the standard deviation

    # Dictionary
    iri_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "VISIT_DATE": None,
        "RUN_NUMBER": None, "MRI": None, "RUNS": None, "CV": None,
    }

    # Read Excel file and save as DataFrame
    df = pandas.read_excel(io=iri_filename, sheet_name=iri_sheet)

    # Append header
    iri_list = [[column for column in df.columns]]
    iri_results = [[column for column in df.columns]]
    iri_results[0].append('RUNS')
    iri_results[0].append('SD')

    # Append values
    for values in df.values:
        iri_list.append([value for value in values])

    # Assign indexes to dictionary
    iri_cols["RUNS"] = len(df.columns)
    iri_cols["CV"] = len(df.columns) + 1
    for iri_col in iri_cols:
        if iri_cols[iri_col] is None:
            iri_cols[iri_col] = iri_list[0].index(iri_col)

    # For loop in iri_list
    for i in range(1, len(iri_list)):
        status = False

        # For loop in iri_results
        for j in range(1, len(iri_results)):
            # If there is a previous register
            if [iri_list[i][iri_cols["STATE_CODE"]],
                iri_list[i][iri_cols["SHRP_ID"]],
                iri_list[i][iri_cols["CONSTRUCTION_NO"]],
                iri_list[i][iri_cols["VISIT_DATE"]]] == [iri_results[j][iri_cols["STATE_CODE"]],
                                                         iri_results[j][iri_cols["SHRP_ID"]],
                                                         iri_results[j][iri_cols["CONSTRUCTION_NO"]],
                                                         iri_results[j][iri_cols["VISIT_DATE"]]]:
                # Sum MRI and increase run counter
                iri_results[j][iri_cols["MRI"]] += iri_list[i][iri_cols["MRI"]]
                iri_results[j][iri_cols["RUNS"]] += 1
                iri_results[j][iri_cols["CV"]].append(iri_list[i][iri_cols["MRI"]])
                status = True

        # Add a new register
        if not status:
            iri_results.append(iri_list[i])
            iri_results[-1].append(1)
            iri_results[-1].append([iri_list[i][iri_cols["MRI"]]])

        sys.stdout.write("\r- [IRI]: %d/%d" % (i, len(iri_list) - 1))

    for i in range(1, len(iri_results)):
        iri_results[i][iri_cols["MRI"]] = iri_results[i][iri_cols["MRI"]] / iri_results[i][iri_cols["RUNS"]]
        if len(iri_results[i][iri_cols["CV"]]) > 1:
            iri_results[i][iri_cols["CV"]] = \
                (statistics.stdev(iri_results[i][iri_cols["CV"]]) / statistics.mean(iri_results[i][iri_cols["CV"]]))
        else:
            iri_results[i][iri_cols["CV"]] = 0

    # Select only desired columns
    for i in range(len(iri_results)):
        iri_results[i] = [iri_results[i][iri_cols["STATE_CODE"]],
                          iri_results[i][iri_cols["SHRP_ID"]],
                          iri_results[i][iri_cols["CONSTRUCTION_NO"]],
                          iri_results[i][iri_cols["VISIT_DATE"]],
                          iri_results[i][iri_cols["MRI"]],
                          iri_results[i][iri_cols["RUNS"]],
                          iri_results[i][iri_cols["CV"]]]

    # Save to CSV
    save_csv(save_path, iri_results)


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

    # Save to CSV
    save_csv(save_path, vws_results)


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


def load_csv(file):
    with open(file, 'r', newline='') as f:
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


if __name__ == '__main__':
    # Root directories
    csv_path, xls_path = "./csv", "./xls"

    if not os.path.isdir(xls_path):
        print("\U000026D4 The input directory \"%s\" does not exist. " % xls_path)
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

    # Excel input file addresses
    xls_iri = xls_def = xls_skn = xls_vws = xls_path + "/Bucket_98025.xlsx"
    xls_trf = xls_snu = xls_cnd = xls_path + "/Bucket_98500.xlsx"

    # CSV output file addresses
    [csv_iri, csv_def, csv_skn,
     csv_vws, csv_trf, csv_snu, csv_cnd] = [csv_path + s for s in ["/iri.csv", "/def.csv", "/skn.csv",
                                                                   "/vws.csv", "/trf.csv", "/snu.csv", "/cnd.csv"]]

    question = question_yn("\U0001F4BB\U0001F4AC Do you want to start a clean process?")

    csv_tables = [csv_iri, csv_def, csv_skn, csv_vws, csv_snu, csv_cnd, csv_trf]
    xls_tables = [xls_iri, xls_def, xls_skn, xls_vws, xls_snu, xls_cnd, xls_trf]

    total_time = 0

    for k in range(0, len(csv_tables)):
        if not os.path.isfile(csv_tables[k]) or (os.path.isfile(csv_tables[k]) and (question or question_yn(
                "\U0001F4BB\U0001F4AC File \"%s\" already exists. Regenerate?" % csv_tables[k]))):
            start_time = time.time()

            extract_iri(csv_tables[k], xls_tables[k]) if k == 0 else 0
            extract_def(csv_tables[k], xls_tables[k]) if k == 1 else 0
            extract_skn(csv_tables[k], xls_tables[k]) if k == 2 else 0
            extract_vws(csv_tables[k], xls_tables[k]) if k == 3 else 0
            extract_snu(csv_tables[k], xls_tables[k]) if k == 4 else 0
            extract_cnd(csv_tables[k], xls_tables[k]) if k == 5 else 0
            extract_trf(csv_tables[k], xls_tables[k]) if k == 6 else 0

            partial_time = time.time() - start_time
            total_time += partial_time
            print("\U00002BA1 File \"%s\" converted in \"%s\" (%s)\n" % (
                csv_tables[k], xls_tables[k], str_time(partial_time)))

    print("\U0001F6C8 Program finished in %s" % str_time(total_time))
