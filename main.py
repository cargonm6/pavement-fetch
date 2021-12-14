import time

import csv
import math
from datetime import datetime

pci_cols = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "SURVEY_DATE": None,  # Own parameters
    "PCI": None
}

iri_cols = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "VISIT_DATE": None,  # Own parameters
    "RUN_NUMBER": None,
    "MRI": None
}

def_cols = {
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

skn_cols = {
    "STATE_CODE": None,  # Common parameters
    "SHRP_ID": None,
    "CONSTRUCTION_NO": None,
    "FRICTION_DATE": None,  # Own parameters
    "FRICTION_NO_BEGIN": None,
    "FRICTION_NO_END": None
}

merra_grid_cols = {
    "MERRA_ID": None,
    "STATE_CODE": None,
    "SHRP_ID": None
}

merra_temp_cols = {
    "MERRA_ID": None,
    "YEAR": None,
    "TEMP_AVG": None,
    "FREEZE_INDEX": None,
    "FREEZE_THAW": None
}

merra_sola_cols = {
    "MERRA_ID": None,
    "YEAR": None,
    "CLOUD_COVER_AVG": None,
    "SHORTWAVE_SURFACE_AVG": None
}

merra_wind_cols = {
    "MERRA_ID": None,
    "YEAR": None,
    "WIND_VELOCITY_AVG": None
}

merra_prec_cols = {
    "MERRA_ID": None,
    "YEAR": None,
    "PRECIPITATION": None,
    "EVAPORATION": None,
    "PRECIP_DAYS": None
}

merra_humi_cols = {
    "MERRA_ID": None,
    "YEAR": None,
    "REL_HUM_AVG_AVG": None,
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
                                       to_date(row_ref[pci_cols["SURVEY_DATE"]], "%m/%d/%Y"))
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
    values = [row[def_cols["PEAK_DEFL_1"]], row[def_cols["PEAK_DEFL_2"]], row[def_cols["PEAK_DEFL_3"]],
              row[def_cols["PEAK_DEFL_4"]], row[def_cols["PEAK_DEFL_5"]], row[def_cols["PEAK_DEFL_6"]],
              row[def_cols["PEAK_DEFL_7"]], row[def_cols["PEAK_DEFL_8"]], row[def_cols["PEAK_DEFL_9"]]]

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

    csv_merra_humi = load_csv("./csv/merra_humi.csv")
    csv_merra_sola = load_csv("./csv/merra_sola.csv")
    csv_merra_prec = load_csv("./csv/merra_prec.csv")
    csv_merra_temp = load_csv("./csv/merra_temp.csv")
    csv_merra_wind = load_csv("./csv/merra_wind.csv")
    csv_merra_grid = load_csv("./csv/merra_grid.csv")

    print(" ✓  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")

    pci_cols = update_dict(pci_cols, csv_pci)
    iri_cols = update_dict(iri_cols, csv_iri)
    def_cols = update_dict(def_cols, csv_def)
    skn_cols = update_dict(skn_cols, csv_skn)

    merra_humi_cols = update_dict(merra_humi_cols, csv_merra_humi)
    merra_sola_cols = update_dict(merra_sola_cols, csv_merra_sola)
    merra_prec_cols = update_dict(merra_prec_cols, csv_merra_prec)
    merra_temp_cols = update_dict(merra_temp_cols, csv_merra_temp)
    merra_wind_cols = update_dict(merra_wind_cols, csv_merra_wind)
    merra_grid_cols = update_dict(merra_grid_cols, csv_merra_grid)

    csv_pci[0].extend(["IRI", "IRI_N", "IRI_D", "IRI_E",
                       "DEF", "DEF_N", "DEF_D", "DEF_E",
                       "SKN", "SKN_N", "SKN_D", "SKN_E",
                       "TEMP_AVG", "FREEZE_INDEX", "FREEZE_THAW", "CLOUD_COVER_AVG", "SHORTWAVE_SURFACE_AVG",
                       "REL_HUM_AVG_AVG", "PRECIP_DAYS", "PRECIPITATION", "EVAPORATION", "WIND_VELOCITY_AVG"])

    limit = 100

    table_csv = [csv_pci[0]]

    count = 0

    for row_pci in csv_pci[1:]:

        if count == limit:
            break

        if row_pci[pci_cols["STATE_CODE"]] != "1":
            continue

        # =======================================================================================

        rws_ind = []

        for row_iri in csv_iri[1:]:
            if [row_pci[pci_cols["STATE_CODE"]],
                row_pci[pci_cols["SHRP_ID"]],
                row_pci[pci_cols["CONSTRUCTION_NO"]]] == [row_iri[iri_cols["STATE_CODE"]],
                                                          row_iri[iri_cols["SHRP_ID"]],
                                                          row_iri[iri_cols["CONSTRUCTION_NO"]]] \
                    and row_iri[iri_cols["MRI"]] != "":
                rws_ind.append([us_is(row_iri[iri_cols["MRI"]].replace(",", "."), 1.609 / 39.37),
                                to_date(row_iri[iri_cols["VISIT_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        # =======================================================================================

        rws_ind = []

        for row_def in csv_def[1:]:
            if [row_pci[pci_cols["STATE_CODE"]],
                row_pci[pci_cols["SHRP_ID"]],
                row_pci[pci_cols["CONSTRUCTION_NO"]]] == [row_def[def_cols["STATE_CODE"]],
                                                          row_def[def_cols["SHRP_ID"]],
                                                          row_def[def_cols["CONSTRUCTION_NO"]]] \
                    and row_def[def_cols["PEAK_DEFL_1"]] != "":
                rws_ind.append([def_char(row_def), to_date(row_def[def_cols["TEST_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        # =======================================================================================

        rws_ind = []

        for row_skn in csv_skn[1:]:
            if [row_pci[pci_cols["STATE_CODE"]],
                row_pci[pci_cols["SHRP_ID"]],
                row_pci[pci_cols["CONSTRUCTION_NO"]]] == [row_skn[skn_cols["STATE_CODE"]],
                                                          row_skn[skn_cols["SHRP_ID"]],
                                                          row_skn[skn_cols["CONSTRUCTION_NO"]]] \
                    and row_skn[skn_cols["FRICTION_NO_BEGIN"]] != "":
                rws_ind.append([row_skn[skn_cols["FRICTION_NO_BEGIN"]].replace(",", "."),
                                to_date(row_skn[skn_cols["FRICTION_DATE"]], "%m/%d/%Y")])

        row_pci = add_index(row_pci, rws_ind)

        # =======================================================================================

        for row_grid in csv_merra_grid[1:]:
            if [row_pci[pci_cols["STATE_CODE"]],
                row_pci[pci_cols["SHRP_ID"]]] == [row_grid[merra_grid_cols["STATE_CODE"]],
                                                  row_grid[merra_grid_cols["SHRP_ID"]]]:
                for row_temp in csv_merra_temp[1:]:
                    if [row_grid[merra_grid_cols["MERRA_ID"]],
                        row_pci[pci_cols["SURVEY_DATE"]][6:10]] == [row_temp[merra_temp_cols["MERRA_ID"]],
                                                                    row_temp[merra_temp_cols["YEAR"]]]:
                        row_pci.extend(
                            [row_temp[merra_temp_cols["TEMP_AVG"]],
                             row_temp[merra_temp_cols["FREEZE_INDEX"]],
                             row_temp[merra_temp_cols["FREEZE_THAW"]]])
                        break

                for row_sola in csv_merra_sola[1:]:
                    if [row_grid[merra_grid_cols["MERRA_ID"]],
                        row_pci[pci_cols["SURVEY_DATE"]][6:10]] == [row_sola[merra_sola_cols["MERRA_ID"]],
                                                                    row_sola[merra_sola_cols["YEAR"]]]:
                        row_pci.extend(
                            [row_sola[merra_sola_cols["CLOUD_COVER_AVG"]],
                             row_sola[merra_sola_cols["SHORTWAVE_SURFACE_AVG"]]])
                        break

                for row_humi in csv_merra_humi[1:]:
                    if [row_grid[merra_grid_cols["MERRA_ID"]],
                        row_pci[pci_cols["SURVEY_DATE"]][6:10]] == [row_humi[merra_humi_cols["MERRA_ID"]],
                                                                    row_humi[merra_humi_cols["YEAR"]]]:
                        row_pci.append(
                            row_humi[merra_humi_cols["REL_HUM_AVG_AVG"]])
                        break

                for row_prec in csv_merra_prec[1:]:
                    if [row_grid[merra_grid_cols["MERRA_ID"]],
                        row_pci[pci_cols["SURVEY_DATE"]][6:10]] == [row_prec[merra_prec_cols["MERRA_ID"]],
                                                                    row_prec[merra_prec_cols["YEAR"]]]:
                        row_pci.extend(
                            [row_prec[merra_prec_cols["PRECIP_DAYS"]],
                             row_prec[merra_prec_cols["PRECIPITATION"]],
                             row_prec[merra_prec_cols["EVAPORATION"]]])
                        break

                for row_wind in csv_merra_wind[1:]:
                    if [row_grid[merra_grid_cols["MERRA_ID"]],
                        row_pci[pci_cols["SURVEY_DATE"]][6:10]] == [row_wind[merra_wind_cols["MERRA_ID"]],
                                                                    row_wind[merra_wind_cols["YEAR"]]]:
                        row_pci.append(
                            row_wind[merra_wind_cols["WIND_VELOCITY_AVG"]])
                        break

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
