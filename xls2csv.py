import os
import statistics
import sys

import pandas

import csv


def extract_pci(save_path, pci_filename, pci_sheet="MON_HSS_PROFILE_SECTION"):
    return save_path, pci_filename, pci_sheet


def extract_def(save_path, def_filename, def_sheet="MON_HSS_PROFILE_SECTION"):
    return save_path, def_filename, def_sheet


def extract_iri(save_path, iri_filename, iri_sheet="MON_HSS_PROFILE_SECTION"):
    # For each STATE_CODE + SHRP_ID + CONSTRUCTION_NO + VISIT_DATE:
    # - Obtain total number of runs
    # - Calculate the average MRI
    # - Compute the standard deviation

    # Dictionary
    iri_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "VISIT_DATE": None,
        "RUN_NUMBER": None, "MRI": None, "RUNS": None, "SD": None,
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
    iri_cols["SD"] = len(df.columns) + 1
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
                iri_results[j][iri_cols["SD"]].append(iri_list[i][iri_cols["MRI"]])
                status = True

        # Add a new register
        if not status:
            iri_results.append(iri_list[i])
            iri_results[-1].append(1)
            iri_results[-1].append([iri_list[i][iri_cols["MRI"]]])

        sys.stdout.write("\r- [IRI]: %d/%d" % (i, len(iri_list) - 1))

    for i in range(1, len(iri_results)):
        iri_results[i][iri_cols["MRI"]] = iri_results[i][iri_cols["MRI"]] / iri_results[i][iri_cols["RUNS"]]
        if len(iri_results[i][iri_cols["SD"]]) > 1:
            iri_results[i][iri_cols["SD"]] = (statistics.stdev(iri_results[i][iri_cols["SD"]]))
        else:
            iri_results[i][iri_cols["SD"]] = 0

        # Convert data to string
        for j in range(0, len(iri_results[i])):
            iri_results[i][j] = str(iri_results[i][j]).replace(".", ",")

    # Select only desired columns
    for i in range(len(iri_results)):
        iri_results[i] = [iri_results[i][iri_cols["STATE_CODE"]],
                          iri_results[i][iri_cols["SHRP_ID"]],
                          iri_results[i][iri_cols["CONSTRUCTION_NO"]],
                          iri_results[i][iri_cols["VISIT_DATE"]],
                          iri_results[i][iri_cols["MRI"]],
                          iri_results[i][iri_cols["RUNS"]],
                          iri_results[i][iri_cols["SD"]]]

    # Save to CSV
    save_csv(save_path, iri_results)


def extract_skn(save_path, skn_filename, skn_sheet="MON_FRICTION"):
    # For each STATE_CODE + SHRP_ID + CONSTRUCTION_NO + FRICTION_DATE:
    # - Obtain total number of runs
    # - Calculate the average FRICTION NUMBER
    # - Compute the standard deviation

    # Dictionary
    skn_cols = {
        "STATE_CODE": None, "SHRP_ID": None, "CONSTRUCTION_NO": None, "FRICTION_DATE": None,
        "FRICTION_TIME": None, "FRICTION_NO_BEGIN": None, "FRICTION_NO_END": None, "RUNS": None, "SD": None,
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
    skn_cols["SD"] = len(df.columns) + 1
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
                skn_results[j][skn_cols["SD"]].extend(
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
        skn_results[i][skn_cols["FRICTION_NO_END"]] = sum(skn_results[i][skn_cols["SD"]]) / skn_results[i][
            skn_cols["RUNS"]]

        if len(skn_results[i][skn_cols["SD"]]) > 1:
            skn_results[i][skn_cols["SD"]] = (statistics.stdev(skn_results[i][skn_cols["SD"]]))
        else:
            skn_results[i][skn_cols["SD"]] = 0

        # Convert data to string
        for j in range(0, len(skn_results[i])):
            skn_results[i][j] = str(skn_results[i][j]).replace(".", ",")

    # Select only desired columns
    for i in range(len(skn_results)):
        skn_results[i] = [skn_results[i][skn_cols["STATE_CODE"]],
                          skn_results[i][skn_cols["SHRP_ID"]],
                          skn_results[i][skn_cols["CONSTRUCTION_NO"]],
                          skn_results[i][skn_cols["FRICTION_DATE"]],
                          skn_results[i][skn_cols["FRICTION_NO_END"]],
                          skn_results[i][skn_cols["RUNS"]],
                          skn_results[i][skn_cols["SD"]]]

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
    vws_results = vws_add_values(vws_pr_m_list, vws_results, True, ["TOTAL_MON_PRECIP",
                                                                    "TOTAL_SNOWFALL_MONTH"])

    vws_results = vws_add_values(vws_te_m_list, vws_results, True, ["MEAN_MON_TEMP_AVG",
                                                                    "FREEZE_INDEX_MONTH",
                                                                    "FREEZE_THAW_MONTH"])

    vws_results = vws_add_values(vws_wi_m_list, vws_results, True, ["MEAN_MON_WIND_AVG"])

    vws_results = vws_add_values(vws_hu_m_list, vws_results, True, ["MAX_MON_HUM_AVG",
                                                                    "MIN_MON_HUM_AVG"])

    # ANNUAL measures
    vws_results = vws_add_values(vws_pr_a_list, vws_results, False, ["TOTAL_ANN_PRECIP",
                                                                     "TOTAL_SNOWFALL_YR"])

    vws_results = vws_add_values(vws_te_a_list, vws_results, False, ["MEAN_ANN_TEMP_AVG",
                                                                     "FREEZE_INDEX_YR",
                                                                     "FREEZE_THAW_YR"])

    vws_results = vws_add_values(vws_wi_a_list, vws_results, False, ["MEAN_ANN_WIND_AVG"])

    vws_results = vws_add_values(vws_hu_a_list, vws_results, False, ["MAX_ANN_HUM_AVG",
                                                                     "MIN_ANN_HUM_AVG"])

    # Convert data to string
    for i in range(1, len(vws_results)):
        for j in range(0, len(vws_results[i])):
            vws_results[i][j] = str(vws_results[i][j]).replace(".", ",")

    # Save to CSV
    save_csv(save_path, vws_results)


def vws_add_values(vws_in, vws_out, by_month, vws_columns):
    limit = len(vws_in)

    for i in range(1, limit):
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
    with open(p_path, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(p_data)

    print("\nData saved\n")


def question_yn(p_question):
    while True:
        value = input(p_question + " [S/n] > ")
        if value in ["s", "S"]:
            return True
        if value in ["n", "N", ""]:
            return False
        else:
            print("Command not recognized.")


if __name__ == '__main__':
    # Root directories
    csv_path, xls_path = "./csv", "./xls"

    if not os.path.isdir(xls_path):
        print("The input directory \"%s\" does not exist. " % xls_path)
        exit(1)

    if not os.path.isdir(csv_path):
        try:
            print("The output directory \"%s\" does not exist and will be created. " % csv_path)
            os.mkdir(csv_path)
        except OSError:
            print("The output directory \"%s\" does not exist and could not be created. " % csv_path)
            exit(1)

    # Excel input file addresses
    xls_pci = xls_iri = xls_def = xls_skn = xls_vws = xls_path + "/Bucket_98025.xlsx"

    # CSV output file addresses
    [csv_pci, csv_iri, csv_def, csv_skn, csv_vws] = [csv_path + s for s in
                                                     ["/pci.csv", "/iri.csv", "/def.csv", "/skn.csv", "/vws.csv"]]

    question = question_yn("Do you want to start a clean process?")

    if os.path.isfile(csv_pci) and (question or question_yn("\"%s\" already exists Regenerate?" % csv_pci)):
        extract_pci(csv_pci, xls_pci)
    if os.path.isfile(csv_iri) and (question or question_yn("\"%s\" already exists Regenerate?" % csv_iri)):
        extract_iri(csv_iri, xls_iri)
    if os.path.isfile(csv_def) and (question or question_yn("\"%s\" already exists Regenerate?" % csv_def)):
        extract_def(csv_def, xls_def)
    if os.path.isfile(csv_skn) and (question or question_yn("\"%s\" already exists Regenerate?" % csv_skn)):
        extract_skn(csv_skn, xls_skn)
    if os.path.isfile(csv_vws) and (question or question_yn("\"%s\" already exists Regenerate?" % csv_vws)):
        extract_vws(csv_vws, xls_vws)
