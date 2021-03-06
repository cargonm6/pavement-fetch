import sys
import time
from copy import deepcopy
from datetime import datetime

from src.modules.module_common import load_csv, save_csv, to_hhmmss, etr


def int_month(date):
    """
    Extract month from date
    :param date: input month
    :return: output month
    """
    if str(date)[2:3] == "/":
        # Format: mm/dd/aaaa
        return int(str(date)[:2])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[5:7])


def int_year(date):
    """
    Extract year from date
    :param date: input date
    :return: output year
    """
    if str(date)[2:3] == "/":
        # Format: mm/dd/aaaa
        return int(str(date)[6:10])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[:4])


def date_diff(d1, d2):
    """
    Measure time difference between two dates
    :param d1: date of reference
    :param d2: second date
    :return: time difference (in days)
    """
    if str(d1)[2:3] == "/":
        # Format: mm/dd/aaaa - > YYYY, MM, DD
        d1 = datetime(int(str(d1)[6:10]), int(str(d1)[:2]), int(str(d1)[3:5]))
    else:
        # Format: yyyy-mm-dd - > YYYY, MM, DD
        d1 = datetime(int(str(d1)[:4]), int(str(d1)[5:7]), int(str(d1)[8:10]))

    if str(d2)[2:3] == "/":
        # Format: mm/dd/aaaa - > YYYY, MM, DD
        d2 = datetime(int(str(d2)[6:10]), int(str(d2)[:2]), int(str(d2)[3:5]))
    else:
        # Format: yyyy-mm-dd - > YYYY, MM, DD
        d2 = datetime(int(str(d2)[:4]), int(str(d2)[5:7]), int(str(d2)[8:10]))

    return (d1 - d2).days


def fix_pci_date(p_table):
    """
    Transform PCI format from "mm/dd/yyyy" (LTPP ft) to "yyyy-mm-dd 00:00:00" (LTPP SI)
    :param p_table:
    :return:
    """

    for i in range(1, len(p_table)):
        p_table[i][p_table[0].index("SURVEY_DATE")] = \
            p_table[i][p_table[0].index("SURVEY_DATE")][6:] + "-" + \
            p_table[i][p_table[0].index("SURVEY_DATE")][:2] + "-" + \
            p_table[i][p_table[0].index("SURVEY_DATE")][3:5] + " 00:00:00"
    return p_table


def master_table(p_pci, p_iri, p_def, p_skn, p_cnd, p_trf, p_snu, p_vws, p_table, p_path):
    """
    Master table generator function
    :param p_pci: PCI table
    :param p_iri: IRI table
    :param p_def: DEF table
    :param p_skn: SKN table
    :param p_cnd: CND table
    :param p_trf: TRF table
    :param p_snu: SNU table
    :param p_vws: VWS table
    :param p_table: table of interest
    :param p_path: destination path
    :return:
    """
    # Only for testing purposes
    table_number = None
    # table_number = 100

    if p_table == "pci":
        table_number = len(p_pci) if table_number is None else table_number
        table_master = deepcopy(p_pci[:table_number])
        table_dating = "SURVEY_DATE"
    elif p_table == "iri":
        table_number = len(p_iri) if table_number is None else table_number
        table_master = deepcopy(p_iri[:table_number])
        table_dating = "VISIT_DATE"
    elif p_table == "def":
        table_number = len(p_def) if table_number is None else table_number
        table_master = deepcopy(p_def[:table_number])
        table_dating = "TEST_DATE"
    else:
        table_number = len(p_skn) if table_number is None else table_number
        table_master = deepcopy(p_skn[:table_number])
        table_dating = "FRICTION_DATE"

    print("(i) Generating %s master table..." % p_table.upper())

    # == PCI ==

    if p_table != "pci":
        table_master[0].extend(p_pci[0][5:])
        table_master[0].append("PCI_YEAR_DIF")
        count = 0

        time_for = 0
        for i in range(1, table_number):
            time_iter = time.time()

            # Ordered list by date difference
            nearest = sorted(lc_pci(p_pci,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_pci[0].index("SURVEY_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Add index and date difference from head od list
            if len(nearest) > 0:
                table_master[i].extend(nearest[0][5:])
                table_master[i].append(date_diff(nearest[0][p_pci[0].index("SURVEY_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 55)

            time_est, time_for = etr(table_number, i, time_for, time_iter)
            if i < table_number - 1:
                sys.stdout.write(
                    "\r- PCI %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
            else:
                sys.stdout.write(
                    "\r- PCI %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
        print("")
    else:
        table_master[0].append("PCI_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

            # SHRP_ID length problem
            table_master[i][table_master[0].index("SHRP_ID")] = table_master[i][table_master[0].index("SHRP_ID")].zfill(
                4)

    # == IRI ==

    if p_table != "iri":
        table_master[0].extend(["IRI", "SLV", "IRI_YEAR_DIF"])
        count = 0

        time_for = 0
        for i in range(1, table_number):
            time_iter = time.time()

            # Ordered list by date difference
            nearest = sorted(lc_iri(p_iri,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_iri[0].index("VISIT_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Add index and date difference from head od list
            if len(nearest) > 0:
                table_master[i].append(nearest[0][p_iri[0].index("IRI")])
                table_master[i].append(nearest[0][p_iri[0].index("SLV")])
                table_master[i].append(date_diff(nearest[0][p_iri[0].index("VISIT_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 3)

            time_est, time_for = etr(table_number, i, time_for, time_iter)
            if i < table_number - 1:
                sys.stdout.write(
                    "\r- IRI %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
            else:
                sys.stdout.write(
                    "\r- IRI %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
        print("")
    else:
        table_master[0].append("IRI_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == DEF ==

    if p_table != "def":
        table_master[0].extend(p_def[0][4:])
        table_master[0].append("DEF_YEAR_DIF")
        count = 0

        time_for = 0
        for i in range(1, table_number):
            time_iter = time.time()

            # Ordered list by date difference
            nearest = sorted(lc_def(p_def,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_def[0].index("TEST_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Add index and date difference from head od list
            if len(nearest) > 0:
                table_master[i].extend(nearest[0][4:])
                table_master[i].append(date_diff(nearest[0][p_def[0].index("TEST_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 7)

            time_est, time_for = etr(table_number, i, time_for, time_iter)
            if i < table_number - 1:
                sys.stdout.write(
                    "\r- DEF %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
            else:
                sys.stdout.write(
                    "\r- DEF %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
        print("")
    else:
        table_master[0].append("DEF_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == SKN ==

    if p_table != "skn":
        table_master[0].extend(["FRICTION_NO_END", "SKN_YEAR_DIF"])
        count = 0

        time_for = 0
        for i in range(1, table_number):
            time_iter = time.time()

            # Ordered list by date difference
            nearest = sorted(lc_skn(p_skn,
                                    table_master[i][table_master[0].index("STATE_CODE")],
                                    table_master[i][table_master[0].index("SHRP_ID")],
                                    table_master[i][table_master[0].index("CONSTRUCTION_NO")]),
                             key=lambda x: abs(date_diff(x[p_skn[0].index("FRICTION_DATE")],
                                                         table_master[i][table_master[0].index(table_dating)])))

            # Add index and date difference from head od list
            if len(nearest) > 0:
                table_master[i].append(nearest[0][p_skn[0].index("FRICTION_NO_END")])
                table_master[i].append(date_diff(nearest[0][p_skn[0].index("FRICTION_DATE")],
                                                 table_master[i][table_master[0].index(table_dating)]) / 365)
                count += 1
            else:
                table_master[i].extend([""] * 2)

            time_est, time_for = etr(table_number, i, time_for, time_iter)
            if i < table_number - 1:
                sys.stdout.write(
                    "\r- SKN %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
            else:
                sys.stdout.write(
                    "\r- SKN %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
        print("")
    else:
        table_master[0].append("SKN_YEAR_DIF")
        for i in range(1, table_number):
            table_master[i].append("")

    # == CND ==

    table_master[0].append("Pa")
    count = 0

    time_for = 0
    for i in range(1, table_number):
        time_iter = time.time()

        # Value list
        nearest = lc_cnd(p_cnd,
                         table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         table_master[i][table_master[0].index("CONSTRUCTION_NO")])

        # Add date difference from head od list
        if len(nearest) > 0:
            table_master[i].append(date_diff(table_master[i][table_master[0].index(table_dating)],
                                             nearest[0][p_cnd[0].index("CN_ASSIGN_DATE")]) / 365)
            count += 1
        else:
            table_master[i].append("")

        time_est, time_for = etr(table_number, i, time_for, time_iter)
        if i < table_number - 1:
            sys.stdout.write(
                "\r- CND %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
        else:
            sys.stdout.write(
                "\r- CND %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
    print("")

    # == TRF ==

    table_master[0].extend(["AADT_AVG", "AADT_CUM", "AADTT_AVG", "AADTT_CUM", "KESAL_AVG", "KESAL_CUM"])
    count = 0

    time_for = 0
    for i in range(1, table_number):
        time_iter = time.time()

        # Value list
        nearest = lc_trf(p_trf, table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         int_year(table_master[i][table_master[0].index(table_dating)]))

        # Add index from head od list
        if len(nearest) > 0:
            table_master[i].extend([
                nearest[0][p_trf[0].index("AADT_AVG")], nearest[0][p_trf[0].index("AADT_CUM")],
                nearest[0][p_trf[0].index("AADTT_AVG")], nearest[0][p_trf[0].index("AADTT_CUM")],
                nearest[0][p_trf[0].index("KESAL_AVG")], nearest[0][p_trf[0].index("KESAL_CUM")]
            ])
            count += 1
        else:
            table_master[i].extend([""] * 6)

        time_est, time_for = etr(table_number, i, time_for, time_iter)
        if i < table_number - 1:
            sys.stdout.write(
                "\r- TRF %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
        else:
            sys.stdout.write(
                "\r- TRF %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
    print("")

    # == SNU ==

    table_master[0].append("SN")
    count = 0

    time_for = 0
    for i in range(1, table_number):
        time_iter = time.time()

        # Value list
        nearest = lc_snu(p_snu,
                         table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         table_master[i][table_master[0].index("CONSTRUCTION_NO")])

        # Add index from head od list
        if len(nearest) > 0:
            table_master[i].append(nearest[0][p_snu[0].index("SN_VALUE")])
            count += 1
        else:
            table_master[i].append("")

        time_est, time_for = etr(table_number, i, time_for, time_iter)
        if i < table_number - 1:
            sys.stdout.write(
                "\r- SNU %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
        else:
            sys.stdout.write(
                "\r- SNU %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
    print("")

    # == VWS ==

    table_master[0].extend(p_vws[0][4:-3] + p_vws[0][-2:])
    count = 0

    time_for = 0
    for i in range(1, table_number):
        time_iter = time.time()

        # Value list
        nearest = lc_vws(p_vws, table_master[i][table_master[0].index("STATE_CODE")],
                         table_master[i][table_master[0].index("SHRP_ID")],
                         int_year(table_master[i][table_master[0].index(table_dating)]),
                         int_month(table_master[i][table_master[0].index(table_dating)]))

        # Add index from head od list
        if len(nearest) > 0:
            table_master[i].extend(nearest[0][4:-3] + nearest[0][-2:])
            count += 1
        else:
            table_master[i].extend([""] * 19)

        time_est, time_for = etr(table_number, i, time_for, time_iter)
        if i < table_number - 1:
            sys.stdout.write(
                "\r- VWS %d/%d: added %s rows (ETR: %s)" % (i, table_number - 1, count, time_est))
        else:
            sys.stdout.write(
                "\r- VWS %d/%d: added %s rows (time: %s)" % (i, table_number - 1, count, to_hhmmss(time_for)))
    print("")

    table_master = form_table(table_master, table_dating)

    save_csv(p_path + datetime.now().strftime("(%Y-%m-%d_%H-%M-%S) ") + "master_" + p_table + ".csv", table_master)


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
                     (x[matrix[0].index("SLV")] != "") and
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
                     (int(str(x[matrix[0].index("YEAR_MON_EST")])[:4]) == p_y) and
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
    """

    :param table: input master table
    :param table_dating: name of table date column
    :return: formatted master table
    """
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
            table[i][table[0].index("IRI")], table[i][table[0].index("SLV")], table[i][table[0].index("IRI_YEAR_DIF")],

            # DEFLECTIONS
            table[i][table[0].index("F1_DEF_AVG")], table[i][table[0].index("F1_DEF_MAX")],
            table[i][table[0].index("F1_DEF_CHR")], table[i][table[0].index("F3_DEF_AVG")],
            table[i][table[0].index("F3_DEF_MAX")], table[i][table[0].index("F3_DEF_CHR")],
            table[i][table[0].index("DEF_YEAR_DIF")],

            # SKID NUMBER
            table[i][table[0].index("FRICTION_NO_END")], table[i][table[0].index("SKN_YEAR_DIF")],

            # Pavement age
            table[i][table[0].index("Pa")],

            # Traffic
            table[i][table[0].index("AADT_AVG")], table[i][table[0].index("AADT_CUM")],
            table[i][table[0].index("AADTT_AVG")], table[i][table[0].index("AADTT_CUM")],
            table[i][table[0].index("KESAL_AVG")], table[i][table[0].index("KESAL_CUM")],

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

        sys.stdout.write("\r- Shaping the table (%d/%d)" % (i + 1, len(table)))
    print("")

    table[0] = [
        # General columns
        "STATE_CODE", "SHRP_ID", "DATE", "CONSTRUCTION_NO",

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
        "IRI", "SLV", "IRI_YEAR_DIF",

        # DEFLECTIONS
        "F1_DEF_AVG", "F1_DEF_MAX", "F1_DEF_CHR", "F3_DEF_AVG", "F3_DEF_MAX", "F3_DEF_CHR", "DEF_YEAR_DIF",

        # SKID NUMBER
        "SKID_NUMBER", "SKN_YEAR_DIF",

        # Pavement age
        "Pa",

        # Traffic
        "AADT_AVG", "AADT_CUM", "AADTT_AVG", "AADTT_CUM", "KESAL_AVG", "KESAL_CUM",

        # Structural Number
        "SN",

        # VWS
        "TOTAL_ANN_PRECIP", "TOTAL_MON_PRECIP", "TOTAL_SNOWFALL_YR",
        "TOTAL_SNOWFALL_MONTH", "MEAN_ANN_TEMP_AVG", "MEAN_MON_TEMP_AVG", "FREEZE_INDEX_YR",
        "FREEZE_INDEX_MONTH", "FREEZE_THAW_YR", "FREEZE_THAW_MONTH", "MEAN_ANN_WIND_AVG",
        "MEAN_MON_WIND_AVG", "MAX_ANN_HUM_AVG", "MAX_MON_HUM_AVG", "MIN_ANN_HUM_AVG", "MIN_MON_HUM_AVG",
        "CLIMATIC ZONE", "MON_PREC_CUM", "MON_SNOW_CUM"]

    return table


def main(project_root):
    """
    Main function
    :param project_root: project root path
    :return:
    """
    start_time = time.time()

    print(" (i) Loading CSV files...")

    csv_path_in = project_root + "/res/csv/ready/"
    csv_path_out = project_root + "/res/csv/done/"

    csv_pci = load_csv(csv_path_in + "pci_fixed.csv")  # (PCI) Pavement Condition Index
    csv_iri = load_csv(csv_path_in + "iri.csv")  # (IRI) International Roughness Index
    csv_def = load_csv(csv_path_in + "def.csv")  # (DEF) Deflections
    csv_skn = load_csv(csv_path_in + "skn.csv")  # (SKN) Skid Number

    csv_cnd = load_csv(csv_path_in + "cnd.csv")  # (CND) Construction Number Date
    csv_trf = load_csv(csv_path_in + "trf.csv")  # (TRF) Traffic
    csv_snu = load_csv(csv_path_in + "snu.csv")  # (SNU) Structural Number
    csv_vws = load_csv(csv_path_in + "vws.csv")  # (VWS) Virtual Weather Station

    print(" ???  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")

    # =====================================================================

    master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "pci", csv_path_out)
    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "iri", csv_path_out)
    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "def", csv_path_out)
    # master_table(csv_pci, csv_iri, csv_def, csv_skn, csv_cnd, csv_trf, csv_snu, csv_vws, "skn", csv_path_out)

    print(" ???  Program finished in", '%.3f' % (time.time() - start_time), "seconds")
