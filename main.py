import time

import csv
import math
from datetime import datetime

pci_columns = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "SURVEY_DATE": None,  # Own parameters
    "PCI": None
}

iri_columns = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "VISIT_DATE": None,  # Own parameters
    "RUN_NUMBER": None,
    "MRI": None
}

def_columns = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "TEST_DATE": None,  # Own parameters
    "PEAK_DEFL_1": None,
    "PEAK_DEFL_2": None,
    "PEAK_DEFL_3": None,
    "PEAK_DEFL_4": None,
    "PEAK_DEFL_5": None,
    "PEAK_DEFL_6": None,
    "PEAK_DEFL_7": None,
    "PEAK_DEFL_8": None,
    "PEAK_DEFL_9": None,
}

skn_columns = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "FRICTION_DATE": None,  # Own parameters
    "FRICTION_NO_BEGIN": None,
    "FRICTION_NO_END": None
}


def load_csv(file):
    with open(file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data


def save_csv(file, data):
    with open(file, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(data)
    print("Data saved")


def us_is(data, factor):
    return str(float(data) * factor)


def list_equals(items):
    if len(items) > 1:
        for i in range(1, len(items)):
            if float(items[0]) - float(items[i]) != 0:
                return False
    return True


def to_date(txt, date_f):
    return datetime.strptime(txt[0:10], date_f)


def near_date(items, pivot):
    flag = 0
    # Nearest date minor or equal than pivot, and difference
    try:
        nearest_under = min([i for i in items if i <= pivot], key=lambda x: abs(x - pivot))
        timedelta_under = nearest_under - pivot
    # If there are no minor or equal data
    except ValueError:
        nearest_under = min([i for i in items if i > pivot], key=lambda x: abs(x - pivot))
        timedelta_under = nearest_under - pivot
        flag = 1

    # Nearest date major than pivot, and difference
    try:
        nearest_over = min([i for i in items if i > pivot], key=lambda x: abs(x - pivot))
        timedelta_over = nearest_over - pivot
    # If there are no major data
    except ValueError:
        nearest_over = min([i for i in items if i <= pivot], key=lambda x: abs(x - pivot))
        timedelta_over = nearest_under - pivot
        flag = -1

    # Return nearest date over pivot
    if flag == -1 or abs(timedelta_under) < abs(timedelta_over):
        return nearest_under, timedelta_under
    elif flag == 1 or abs(timedelta_under) > abs(timedelta_over):
        return nearest_over, timedelta_over
    else:
        return nearest_over, timedelta_over


def update_dict(p_dict, p_list):
    dict_keys = list(p_dict)

    for i in range(0, len(p_dict)):
        for j in range(0, len(p_list[0])):
            if dict_keys[i] == p_list[0][j]:
                p_dict[dict_keys[i]] = j
                break

    return p_dict


def add_index(row_ref, rws_index):
    val_ind = []
    if len(rws_index) > 0:
        # Get the nearest date into rows index array
        nearest, timedelta = near_date([row[1] for row in rws_index],
                                       to_date(row_ref[pci_columns["SURVEY_DATE"]], "%m/%d/%Y"))
        for rw_ind in rws_index:
            # If row index date is the nearest, append to index value array
            if rw_ind[1] == nearest:
                val_ind.append(rw_ind[0])

        # Data append:
        # 1. Value
        # 2. Number of elements that match all conditions
        # 3. Time delta
        # 4. Check if all items in the array are the same

        row_ref.extend([val_ind[0].replace(".", ","), len(rws_index), timedelta, list_equals(val_ind)])
    else:
        row_ref.extend([None, len(rws_index), None, None])

    return row_ref


def def_char(row):
    values = [row[def_columns["PEAK_DEFL_1"]], row[def_columns["PEAK_DEFL_2"]], row[def_columns["PEAK_DEFL_3"]],
              row[def_columns["PEAK_DEFL_4"]], row[def_columns["PEAK_DEFL_5"]], row[def_columns["PEAK_DEFL_6"]],
              row[def_columns["PEAK_DEFL_7"]], row[def_columns["PEAK_DEFL_8"]], row[def_columns["PEAK_DEFL_9"]]]

    v_limit = len(values)

    for i in range(0, len(values)):
        if values[i] == "":
            v_limit = i
            break

    values = [us_is(float(v.replace(",", ".")), 25.4) for v in values[0:v_limit]]

    row_m = sum([float(v) for v in values])
    row_s = math.sqrt(sum((float(v) - row_m) ** 2 for v in values) / (len(values) - 1))

    return str(row_m + 2 * row_s)


if __name__ == '__main__':
    start_time = time.time()

    print("(i) Loading CSV files...")

    csv_pci = load_csv("./csv/pci.csv")
    csv_iri = load_csv("./csv/iri.csv")
    csv_def = load_csv("./csv/def.csv")
    csv_skn = load_csv("./csv/skn.csv")

    print(" ✓  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")

    sub_time = time.time()

    pci_columns = update_dict(pci_columns, csv_pci)
    iri_columns = update_dict(iri_columns, csv_iri)
    def_columns = update_dict(def_columns, csv_def)
    skn_columns = update_dict(skn_columns, csv_skn)

    print("- ", pci_columns)
    print("- ", iri_columns)
    print("- ", def_columns)
    print("- ", skn_columns)

    csv_pci[0].extend(["IRI", "IRI_N", "IRI_D", "IRI_E",
                       "DEF", "DEF_N", "DEF_D", "DEF_E",
                       "SKN", "SKN_N", "SKN_D", "SKN_E"])

    limit = 100

    table_csv = [csv_pci[0]]

    count = 0

    for row_pci in csv_pci[1:]:

        if count == limit:
            break

        if row_pci[pci_columns["STATE_CODE"]] != "1":
            continue

        # =======================================================================================

        rws_ind = []

        for row_iri in csv_iri[1:]:
            if [row_pci[pci_columns["STATE_CODE"]],
                row_pci[pci_columns["SHRP_ID"]],
                row_pci[pci_columns["CONSTRUCTION_NO"]]] == [row_iri[iri_columns["STATE_CODE"]],
                                                             row_iri[iri_columns["SHRP_ID"]],
                                                             row_iri[iri_columns["CONSTRUCTION_NO"]]] \
                    and row_iri[iri_columns["MRI"]] != "":
                rws_ind.append([us_is(row_iri[iri_columns["MRI"]].replace(",", "."), 1.609 / 39.37),
                                to_date(row_iri[iri_columns["VISIT_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        # =======================================================================================

        rws_ind = []

        for row_def in csv_def[1:]:
            if [row_pci[pci_columns["STATE_CODE"]],
                row_pci[pci_columns["SHRP_ID"]],
                row_pci[pci_columns["CONSTRUCTION_NO"]]] == [row_def[def_columns["STATE_CODE"]],
                                                             row_def[def_columns["SHRP_ID"]],
                                                             row_def[def_columns["CONSTRUCTION_NO"]]] \
                    and row_def[def_columns["PEAK_DEFL_1"]] != "":
                rws_ind.append([def_char(row_def), to_date(row_def[def_columns["TEST_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        # =======================================================================================

        rws_ind = []

        for row_skn in csv_skn[1:]:
            if [row_pci[pci_columns["STATE_CODE"]],
                row_pci[pci_columns["SHRP_ID"]],
                row_pci[pci_columns["CONSTRUCTION_NO"]]] == [row_skn[skn_columns["STATE_CODE"]],
                                                             row_skn[skn_columns["SHRP_ID"]],
                                                             row_skn[skn_columns["CONSTRUCTION_NO"]]] \
                    and row_skn[skn_columns["FRICTION_NO_BEGIN"]] != "":
                rws_ind.append([row_skn[skn_columns["FRICTION_NO_BEGIN"]].replace(",", "."),
                                to_date(row_skn[skn_columns["FRICTION_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        if len(row_pci) != len(csv_pci[0]):
            print("x", end="")
        else:
            print("|", end="")

        count += 1

        if count % 10 == 0 or count == len(csv_pci[1:limit]):
            print("", round(count * 100 / len(csv_pci[1:limit]), 2), "%")

        table_csv.append(row_pci)

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + "_PCI-IRI-DEF-SK" + ".csv"
    save_csv(save_path, table_csv)

    print(" ✓  ", str(len(table_csv[1:])), "entries saved to", save_path)
    print(" ✓  Program finished in", '%.3f' % (time.time() - start_time), "seconds")

    exit(0)
