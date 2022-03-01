import math
import os
# import shutil
import sys
import time
from copy import deepcopy
from datetime import datetime

import csv


# import xls2csv


def load_csv(p_path):
    with open(p_path, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data


def save_csv(p_path, p_data):
    for n in range(1, len(p_data)):
        p_data[n] = row_to_str(p_data[n])

        # Fix zero prefix in SHRP_ID
        if "SHRP_ID" in p_data[0] and len(p_data[n][p_data[0].index("SHRP_ID")]) < 4:
            p_data[n][p_data[0].index("SHRP_ID")] = "0" + p_data[n][p_data[0].index("SHRP_ID")]

    with open(p_path, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(p_data)

    print("\n\U0001F5AB Data saved")


def row_to_str(p_row):
    for n in range(0, len(p_row)):
        p_row[n] = str(p_row[n])  # Convert data to string
        p_row[n] = p_row[n].replace(".", ",")  # Replace dots with commas
        p_row[n] = p_row[n].replace("nan", "")  # Replace "nan" with void
    return p_row


def int_month(date):
    if str(date)[2:3] == "/":
        # Format: mm/dd/aaaa
        return int(str(date)[0:2])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[5:7])


def int_year(date):
    if str(date)[2:3] == "/":
        # Format: mm/dd/aaaa
        return int(str(date)[6:10])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[0:4])


def date_diff(d1, d2):
    if str(d1)[2:3] == "/":
        # Format: mm/dd/aaaa - > YYYY, MM, DD
        d1 = datetime(int(str(d1)[6:10]), int(str(d1)[0:2]), int(str(d1)[3:5]))
    else:
        # Format: yyyy-mm-dd - > YYYY, MM, DD
        d1 = datetime(int(str(d1)[0:4]), int(str(d1)[5:7]), int(str(d1)[8:10]))

    if str(d2)[2:3] == "/":
        # Format: mm/dd/aaaa - > YYYY, MM, DD
        d2 = datetime(int(str(d2)[6:10]), int(str(d2)[0:2]), int(str(d2)[3:5]))
    else:
        # Format: yyyy-mm-dd - > YYYY, MM, DD
        d2 = datetime(int(str(d2)[0:4]), int(str(d2)[5:7]), int(str(d2)[8:10]))

    return (d1 - d2).days


def csv_group(p_code, p_path="./csv/", p_path_res="./csv/00_All_States/"):
    if not os.path.isdir(p_path_res):
        try:
            print("\U000026A0 The output directory \"%s\" does not exist and will be created. " % p_path_res)
            os.mkdir(p_path_res)
        except OSError:
            print("\U000026D4 The output directory \"%s\" does not exist and could not be created. " % p_path_res)
            exit(1)
    else:
        print("\U0001F6C8 Output directory: \"%s\"" % p_path_res)

    print("\n\U0001F6C8 Finding \"" + p_code + "\" files under path \"" + p_path + "\"")
    p_list = []
    for root, dirs, files in os.walk(p_path):
        for f in files:
            p_list.append((os.path.join(root, f)).replace("\\", "/")) if f.startswith(p_code) else 0

    if len(p_list) == 0:
        print("(!) Code \"%s\" was not found under path \"%s\"" % (p_code, p_path))
        return

    p_result = None

    for n in range(0, len(p_list)):
        if p_result is None:
            p_result = load_csv(p_list[n])
        else:
            [p_result.append(p_row) for p_row in load_csv(p_list[n])[1:]]
        sys.stdout.write("\r- %d/%d files joined" % (n + 1, len(p_list)))

    save_csv(p_path_res + p_code + "_join.csv", p_result)


def fix_pci_date(p_table):
    for i in range(1, len(p_table)):
        p_table[i][p_table[0].index("SURVEY_DATE")] = \
            p_table[i][p_table[0].index("SURVEY_DATE")][6:] + "-" + \
            p_table[i][p_table[0].index("SURVEY_DATE")][0:2] + "-" + \
            p_table[i][p_table[0].index("SURVEY_DATE")][3:5] + " 00:00:00"
    return p_table


def etr(p_total, p_index, p_time):
    seconds = (-1 + p_total - p_index) * (time.time() - p_time)
    hh = math.floor(seconds / 3600)
    mm = math.floor(seconds / 60) - (hh * 60)
    ss = math.floor(seconds) - (hh * 3600) - (mm * 60)
    return str(int(hh)).zfill(2) + ":" + str(int(mm)).zfill(2) + ":" + str(int(ss)).zfill(2)


def master_table(p_pci, p_iri, p_def, p_skn, p_cnd, p_trf, p_snu, p_vws, p_table):
    # Only for testing purposes
    # table_number = 20

    if p_table == "pci":
        table_number = len(p_pci)
        table_master = deepcopy(p_pci[0:table_number])
        table_dating = "SURVEY_DATE"
    elif p_table == "iri":
        table_number = len(p_iri)
        table_master = deepcopy(p_iri[0:table_number])
        table_dating = "VISIT_DATE"
    elif p_table == "def":
        table_number = len(p_def)
        table_master = deepcopy(p_def[0:table_number])
        table_dating = "TEST_DATE"
    else:
        table_number = len(p_skn)
        table_master = deepcopy(p_skn[0:table_number])
        table_dating = "FRICTION_DATE"

    # == PCI ==

    if p_table != "pci":
        table_master[0].extend(p_pci[0][5:len(p_pci[0])])
        table_master[0].append("PCI_YEAR_DIF")
        count = 0

        for i in range(1, table_number):
            ini_time = time.time()

            # Ordered list by date difference
            nearest = sorted(lc_pci(p_pci,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_pci[0].index("SURVEY_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Add index and date difference from head od list
            if len(nearest) > 0:
                table_master[i].extend(nearest[0][5:len(nearest[0])])
                table_master[i].append(date_diff(nearest[0][p_pci[0].index("SURVEY_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 55)

            sys.stdout.write(
                "\r- PCI %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
        print("")
    else:
        table_master[0].append("PCI_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == IRI ==

    if p_table != "iri":
        table_master[0].extend(["IRI", "IRI_YEAR_DIF"])
        count = 0

        for i in range(1, table_number):
            ini_time = time.time()

            # Lista ordenada de valores por diferencia de fechas
            nearest = sorted(lc_iri(p_iri,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_iri[0].index("VISIT_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Añade el índice y diferencia de fechas del primer valor de la lista
            if len(nearest) > 0:
                table_master[i].append(nearest[0][p_iri[0].index("IRI")])
                table_master[i].append(date_diff(nearest[0][p_iri[0].index("VISIT_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 2)
            sys.stdout.write(
                "\r- IRI %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
        print("")
    else:
        table_master[0].append("IRI_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == DEF ==

    if p_table != "def":
        table_master[0].extend(p_def[0][4:len(p_def[0])])
        table_master[0].append("DEF_YEAR_DIF")
        count = 0

        for i in range(1, table_number):
            ini_time = time.time()

            # Lista ordenada de valores por diferencia de fechas
            nearest = sorted(lc_def(p_def,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_def[0].index("TEST_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Añade el índice y diferencia de fechas del primer valor de la lista
            if len(nearest) > 0:
                table_master[i].extend(nearest[0][4:len(nearest[0])])
                table_master[i].append(date_diff(nearest[0][p_def[0].index("TEST_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 7)
            sys.stdout.write(
                "\r- DEF %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
        print("")
    else:
        table_master[0].append("DEF_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == SKN ==

    if p_table != "skn":
        table_master[0].extend(["SKID_NUMBER", "SKN_YEAR_DIF"])
        count = 0

        for i in range(1, table_number):
            ini_time = time.time()

            # Lista ordenada de valores por diferencia de fechas
            nearest = sorted(lc_skn(p_skn,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_skn[0].index("FRICTION_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Añade el índice y diferencia de fechas del primer valor de la lista
            if len(nearest) > 0:
                table_master[i].append(nearest[0][p_skn[0].index("FRICTION_NO_END")])
                table_master[i].append(date_diff(nearest[0][p_skn[0].index("FRICTION_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 2)
            sys.stdout.write(
                "\r- SKN %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
        print("")
    else:
        table_master[0][table_master[0].index("FRICTION_NO_END")] = "SKID_NUMBER"
        table_master[0].append("SKN_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == CND ==

    table_master[0].append("Pa")
    count = 0

    for i in range(1, table_number):
        ini_time = time.time()

        # Lista de valores
        nearest = lc_cnd(p_cnd,
                         table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         table_master[i][table_master[0].index("CONSTRUCTION_NO")])

        # Añade la diferencia de fechas del primer valor de la lista
        if len(nearest) > 0:
            table_master[i].append(date_diff(table_master[i][table_master[0].index(table_dating)],
                                             nearest[0][p_cnd[0].index("CN_ASSIGN_DATE")]) / 365)
            count += 1
        else:
            table_master[i].append("")

        sys.stdout.write(
            "\r- CND %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
    print("")

    # == TRF ==

    table_master[0].extend(p_trf[0][3:6])
    count = 0

    for i in range(1, table_number):
        ini_time = time.time()

        # Lista de valores
        nearest = lc_trf(p_trf, table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         int_year(table_master[i][table_master[0].index(table_dating)]))

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            table_master[i].extend(nearest[0][3:6])
            count += 1
        else:
            table_master[i].extend([""] * 3)

        sys.stdout.write(
            "\r- TRF %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
    print("")

    # == SNU ==

    table_master[0].append("SN")
    count = 0

    for i in range(1, table_number):
        ini_time = time.time()

        # Lista de valores
        nearest = lc_snu(p_snu,
                         table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         table_master[i][table_master[0].index("CONSTRUCTION_NO")])

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            table_master[i].append(nearest[0][p_snu[0].index("SN_VALUE")])
            count += 1
        else:
            table_master[i].append("")

        sys.stdout.write(
            "\r- SNU %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
    print("")

    # == VWS ==

    table_master[0].extend(p_vws[0][4:-3] + p_vws[0][-2:])
    count = 0

    for i in range(1, table_number):
        ini_time = time.time()

        # Lista de valores
        nearest = lc_vws(p_vws, table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         int_year(table_master[i][table_master[0].index(table_dating)]),
                         int_month(table_master[i][table_master[0].index(table_dating)]))

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            table_master[i].extend(nearest[0][4:-3] + nearest[0][-2:])
            count += 1
        else:
            table_master[i].extend([""] * 19)

        sys.stdout.write(
            "\r- VWS %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, etr(table_number, i, ini_time)))
    print("")

    table_master = form_table(table_master, table_dating)

    save_csv("./res/master_" + p_table + ".csv", table_master)


def lc_pci(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("PCI")] != "") and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_iri(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("IRI")] != "") and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_def(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("F1_DEF_AVG")] != "") and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_skn(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("FRICTION_NO_END")] != "") and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_cnd(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_trf(matrix, p_sc, p_id, p_y):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_y: YEAR external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (int(str(x[matrix[0].index("YEAR_MON_EST")])[0:4]) == p_y) and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc)]

    return filtered_list


def lc_snu(matrix, p_sc, p_id, p_cn):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_cn: CONSTRUCTION_NO external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc) and
                     (x[matrix[0].index("CONSTRUCTION_NO")] == p_cn)]

    return filtered_list


def lc_vws(matrix, p_sc, p_id, p_y, p_m):
    """
    PCI list comprehension
    :param matrix: input matrix
    :param p_sc: STATE_CODE external comparator
    :param p_id: SHRP_ID external comparator
    :param p_m: YEAR external comparator
    :param p_y: MONTH external comparator
    :return: filtered_list (without headers)
    """
    filtered_list = [x for x in matrix[1:] if
                     (int(x[matrix[0].index("YEAR")]) == p_y) and
                     (int(x[matrix[0].index("MONTH")]) == p_m) and
                     (x[matrix[0].index("SHRP_ID")] == p_id) and
                     (x[matrix[0].index("STATE_CODE")] == p_sc)]

    return filtered_list


def form_table(table, table_dating):
    for i in range(1, len(table)):
        table[i] = [
            # General columns
            table[i][table[0].index("STATE_CODE")], table[i][table[0].index("SHRP_ID")],
            table[i][table[0].index(table_dating)], table[i][table[0].index("CONSTRUCTION_NO")],

            # Pavement distress + PCI
            table[i][table[0].index("GATOR_CRACK_A_L")], table[i][table[0].index("GATOR_CRACK_A_M")],
            table[i][table[0].index("GATOR_CRACK_A_H")], table[i][table[0].index("BLK_CRACK_A_L")],
            table[i][table[0].index("BLK_CRACK_A_M")], table[i][table[0].index("BLK_CRACK_A_H")],
            table[i][table[0].index("EDGE_CRACK_L_L")], table[i][table[0].index("EDGE_CRACK_L_M")],
            table[i][table[0].index("EDGE_CRACK_L_H")], table[i][table[0].index("LONG_CRACK_WP_L_L")],
            table[i][table[0].index("LONG_CRACK_WP_L_M")], table[i][table[0].index("LONG_CRACK_WP_L_H")],
            table[i][table[0].index("LONG_CRACK_WP_SEAL_L_L")], table[i][table[0].index("LONG_CRACK_WP_SEAL_L_M")],
            table[i][table[0].index("LONG_CRACK_WP_SEAL_L_H")], table[i][table[0].index("LONG_CRACK_NWP_L_L")],
            table[i][table[0].index("LONG_CRACK_NWP_L_M")], table[i][table[0].index("LONG_CRACK_NWP_L_H")],
            table[i][table[0].index("LONG_CRACK_NWP_SEAL_L_L")],
            table[i][table[0].index("LONG_CRACK_NWP_SEAL_L_M")],
            table[i][table[0].index("LONG_CRACK_NWP_SEAL_L_H")], table[i][table[0].index("TRANS_CRACK_NO_L")],
            table[i][table[0].index("TRANS_CRACK_NO_M")], table[i][table[0].index("TRANS_CRACK_NO_H")],
            table[i][table[0].index("TRANS_CRACK_L_L")], table[i][table[0].index("TRANS_CRACK_L_M")],
            table[i][table[0].index("TRANS_CRACK_L_H")], table[i][table[0].index("TRANS_CRACK_SEAL_L_L")],
            table[i][table[0].index("TRANS_CRACK_SEAL_L_M")], table[i][table[0].index("TRANS_CRACK_SEAL_L_H")],
            table[i][table[0].index("PATCH_NO_L")], table[i][table[0].index("PATCH_NO_M")],
            table[i][table[0].index("PATCH_NO_H")], table[i][table[0].index("PATCH_A_L")],
            table[i][table[0].index("PATCH_A_M")], table[i][table[0].index("PATCH_A_H")],
            table[i][table[0].index("POTHOLES_NO_L")], table[i][table[0].index("POTHOLES_NO_M")],
            table[i][table[0].index("POTHOLES_NO_H")], table[i][table[0].index("POTHOLES_A_L")],
            table[i][table[0].index("POTHOLES_A_M")], table[i][table[0].index("POTHOLES_A_H")],
            table[i][table[0].index("SHOVING_NO")], table[i][table[0].index("SHOVING_A")],
            table[i][table[0].index("BLEEDING")], table[i][table[0].index("POLISH_AGG_A")],
            table[i][table[0].index("RAVELING")], table[i][table[0].index("PUMPING_NO")],
            table[i][table[0].index("PUMPING_L")], table[i][table[0].index("OTHER")],
            table[i][table[0].index("SURVEY_WIDTH")], table[i][table[0].index("WP_LENGTH_CRACKED")],
            table[i][table[0].index("TRANS_CRACK_L_GT183")], table[i][table[0].index("PCI")],
            table[i][table[0].index("PCI_YEAR_DIF")],

            # IRI
            table[i][table[0].index("IRI")], table[i][table[0].index("IRI_YEAR_DIF")],

            # DEFLECTIONS
            table[i][table[0].index("F1_DEF_AVG")], table[i][table[0].index("F1_DEF_MAX")],
            table[i][table[0].index("F1_DEF_CHR")], table[i][table[0].index("F3_DEF_AVG")],
            table[i][table[0].index("F3_DEF_MAX")], table[i][table[0].index("F3_DEF_CHR")],
            table[i][table[0].index("DEF_YEAR_DIF")],

            # SKID NUMBER
            table[i][table[0].index("SKID_NUMBER")], table[i][table[0].index("DEF_YEAR_DIF")],

            # Pavement age
            table[i][table[0].index("Pa")],

            # Traffic
            table[i][table[0].index("AADT")], table[i][table[0].index("AADTT")], table[i][table[0].index("KESAL")],

            # Structural Number
            table[i][table[0].index("SN")],

            # VWS
            table[i][table[0].index("TOTAL_ANN_PRECIP")], table[i][table[0].index("TOTAL_MON_PRECIP")],
            table[i][table[0].index("TOTAL_SNOWFALL_YR")], table[i][table[0].index("TOTAL_SNOWFALL_MONTH")],
            table[i][table[0].index("MEAN_ANN_TEMP_AVG")], table[i][table[0].index("MEAN_MON_TEMP_AVG")],
            table[i][table[0].index("FREEZE_INDEX_YR")], table[i][table[0].index("FREEZE_INDEX_MONTH")],
            table[i][table[0].index("FREEZE_THAW_YR")], table[i][table[0].index("FREEZE_THAW_MONTH")],
            table[i][table[0].index("MEAN_ANN_WIND_AVG")], table[i][table[0].index("MEAN_MON_WIND_AVG")],
            table[i][table[0].index("MAX_ANN_HUM_AVG")], table[i][table[0].index("MAX_MON_HUM_AVG")],
            table[i][table[0].index("MIN_ANN_HUM_AVG")], table[i][table[0].index("MIN_MON_HUM_AVG")],
            table[i][table[0].index("CLIMATIC ZONE")], table[i][table[0].index("MON_PREC_CUM")],
            table[i][table[0].index("MON_SNOW_CUM")]
        ]

        sys.stdout.write("\r- VWS %d/%d: formando tabla" % (i + 1, len(table)))
        print("")

    table[0] = [
        # General columns
        "STATE_CODE", "SHRP_ID", table_dating, "CONSTRUCTION_NO",

        # Pavement distress + PCI
        "GATOR_CRACK_A_L", "GATOR_CRACK_A_M", "GATOR_CRACK_A_H", "BLK_CRACK_A_L", "BLK_CRACK_A_M",
        "BLK_CRACK_A_H", "EDGE_CRACK_L_L", "EDGE_CRACK_L_M", "EDGE_CRACK_L_H", "LONG_CRACK_WP_L_L",
        "LONG_CRACK_WP_L_M", "LONG_CRACK_WP_L_H", "LONG_CRACK_WP_SEAL_L_L", "LONG_CRACK_WP_SEAL_L_M",
        "LONG_CRACK_WP_SEAL_L_H", "LONG_CRACK_NWP_L_L", "LONG_CRACK_NWP_L_M", "LONG_CRACK_NWP_L_H",
        "LONG_CRACK_NWP_SEAL_L_L", "LONG_CRACK_NWP_SEAL_L_M", "LONG_CRACK_NWP_SEAL_L_H", "TRANS_CRACK_NO_L",
        "TRANS_CRACK_NO_M", "TRANS_CRACK_NO_H", "TRANS_CRACK_L_L", "TRANS_CRACK_L_M", "TRANS_CRACK_L_H",
        "TRANS_CRACK_SEAL_L_L", "TRANS_CRACK_SEAL_L_M", "TRANS_CRACK_SEAL_L_H", "PATCH_NO_L", "PATCH_NO_M",
        "PATCH_NO_H", "PATCH_A_L", "PATCH_A_M", "PATCH_A_H", "POTHOLES_NO_L", "POTHOLES_NO_M",
        "POTHOLES_NO_H", "POTHOLES_A_L", "POTHOLES_A_M", "POTHOLES_A_H", "SHOVING_NO", "SHOVING_A",
        "BLEEDING", "POLISH_AGG_A", "RAVELING", "PUMPING_NO", "PUMPING_L", "OTHER", "SURVEY_WIDTH",
        "WP_LENGTH_CRACKED", "TRANS_CRACK_L_GT183", "PCI", "PCI_YEAR_DIF",

        # IRI
        "IRI", "IRI_YEAR_DIF",

        # DEFLECTIONS
        "F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR", "DEF_YEAR_DIF",

        # SKID NUMBER
        "SKID_NUMBER", "SKN_YEAR_DIF",

        # Pavement age
        "Pa",

        # Traffic
        "AADT", "AADTT", "KESAL",

        # Structural Number
        "SN",

        # VWS
        "TOTAL_ANN_PRECIP", "TOTAL_MON_PRECIP", "TOTAL_SNOWFALL_YR",
        "TOTAL_SNOWFALL_MONTH", "MEAN_ANN_TEMP_AVG", "MEAN_MON_TEMP_AVG", "FREEZE_INDEX_YR",
        "FREEZE_INDEX_MONTH", "FREEZE_THAW_YR", "FREEZE_THAW_MONTH", "MEAN_ANN_WIND_AVG",
        "MEAN_MON_WIND_AVG", "MAX_ANN_HUM_AVG", "MAX_MON_HUM_AVG", "MIN_ANN_HUM_AVG", "MIN_MON_HUM_AVG",
        "CLIMATIC ZONE", "MON_PREC_CUM", "MON_SNOW_CUM"]

    return table


if __name__ == '__main__':
    start_time = time.time()
    #
    # xls_list = []
    #
    # for file in os.listdir("./xls"):
    #     if file.endswith(".xlsx"):
    #         xls_list.append(os.path.join("./xls", file).replace("\\", "/"))
    #
    # for k in range(0, len(xls_list)):
    #     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #     print("(%s/%s) Current file: \"%s\"" % (k + 1, len(xls_list), xls_list[k]))
    #
    #     csv_path = "./csv/" + os.path.basename(xls_list[k])[0:-5] + "/"
    #
    #     try:
    #         xls2csv.main(xls_list[k], csv_path, True)
    #     except BaseException as e:
    #         print("(!) Error with file: ", e)
    #         continue

    # Join CSV files
    # for code in ["cnd", "def", "iri", "skn", "snu", "trf", "vws"]:
    #     csv_group(code)

    #     save_path = "./res/" + os.path.basename(xls_list[k])[0:-5] + ".csv"
    #     shutil.copyfile("./csv/pci.csv", save_path)
    #
    # for
    #
    print("(i) Loading CSV files...")

    csv_path = "./csv/00_All_States/"

    csv_pci = fix_pci_date(load_csv(csv_path + "pci.csv"))  # (PCI) Pavement Condition Index
    csv_iri = load_csv(csv_path + "iri.csv")  # (IRI) International Roughness Index
    csv_def = load_csv(csv_path + "def.csv")  # (DEF) Deflections
    csv_skn = load_csv(csv_path + "skn.csv")  # (SKN) Skid Number

    csv_cnd = load_csv(csv_path + "cnd.csv")  # (CND) Construction Number Date
    csv_trf = load_csv(csv_path + "trf.csv")  # (TRF) Traffic
    csv_snu = load_csv(csv_path + "snu.csv")  # (SNU) Structural Number
    csv_vws = load_csv(csv_path + "vws.csv")  # (VWS) Virtual Weather Station

    print(" ✓  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")

    # =====================================================================

    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "pci")
    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "iri")
    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "def")
    master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "skn")

    print(" ✓  Program finished in", '%.3f' % (time.time() - start_time), "seconds")

    exit(0)
