import sys
import time
from datetime import datetime

import csv
import xls2csv


# from operator import itemgetter


def load_csv(file):
    with open(file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data


def save_csv(p_path, p_data):
    for k in range(1, len(p_data)):
        p_data[k] = row_to_str(p_data[k])

        # Fix zero prefix in SHRP_ID
        if "SHRP_ID" in p_data[0] and len(p_data[k][p_data[0].index("SHRP_ID")]) < 4:
            p_data[k][p_data[0].index("SHRP_ID")] = "0" + p_data[k][p_data[0].index("SHRP_ID")]

    with open(p_path, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(p_data)

    print("\n\U0001F5AB Data saved")


def row_to_str(p_row):
    for k in range(0, len(p_row)):
        p_row[k] = str(p_row[k])  # Convert data to string
        p_row[k] = p_row[k].replace(".", ",")  # Replace dots with commas
        p_row[k] = p_row[k].replace("nan", "")  # Replace "nan" with void
    return p_row


def int_month(date):
    if str(date)[2:3] == "/":
        # Format: dd/mm/aaaa
        return int(str(date)[3:5])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[5:7])


def int_year(date):
    if str(date)[2:3] == "/":
        # Format: dd/mm/aaaa
        return int(str(date)[6:10])
    else:
        # Format: yyyy-mm-dd
        return int(str(date)[0:4])


def date_diff(d1, d2):
    if str(d1)[2:3] == "/":
        # Format: dd/mm/aaaa
        d1 = datetime(int(str(d1)[6:10]), int(str(d1)[3:5]), int(str(d1)[0:2]))
    else:
        # Format: yyyy-mm-dd
        d1 = datetime(int(str(d1)[0:4]), int(str(d1)[5:7]), int(str(d1)[8:10]))

    if str(d2)[2:3] == "/":
        # Format: dd/mm/aaaa
        d2 = datetime(int(str(d2)[6:10]), int(str(d2)[3:5]), int(str(d2)[0:2]))
    else:
        # Format: yyyy-mm-dd
        d2 = datetime(int(str(d2)[0:4]), int(str(d2)[5:7]), int(str(d2)[8:10]))

    return (d1 - d2).days


if __name__ == '__main__':
    start_time = time.time()

    # xls2csv.main()

    print("(i) Loading CSV files...")

    csv_pci = load_csv("./csv/pci.csv")  # (PCI) Pavement Condition Index
    csv_iri = load_csv("./csv/iri.csv")  # (IRI) International Roughness Index
    csv_def = load_csv("./csv/def.csv")  # (DEF) Deflections
    csv_skn = load_csv("./csv/skn.csv")  # (SKN) Skid Number

    csv_cnd = load_csv("./csv/cnd.csv")  # (CND) Construction Number Date
    csv_trf = load_csv("./csv/trf.csv")  # (TRF) Traffic
    csv_snu = load_csv("./csv/snu.csv")  # (SNU) Structural Number
    csv_vws = load_csv("./csv/vws.csv")  # (VWS) Virtual Weather Station

    print(" ✓  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")

    limit = len(csv_pci)

    # == PCI ==

    for i in range(1, limit):

        if len(csv_pci[i][csv_pci[0].index("SHRP_ID")]) < 4:
            csv_pci[i][csv_pci[0].index("SHRP_ID")] = "0" + csv_pci[i][csv_pci[0].index("SHRP_ID")]

    # == IRI ==

    csv_pci[0].extend(["IRI", "IRI_YEAR_DIF"])
    count = 0

    for i in range(1, limit):
        # Lista ordenada de valores por diferencia de fechas
        nearest = sorted(list(filter(lambda x:
                                     [x[csv_iri[0].index("SHRP_ID")],
                                      x[csv_iri[0].index("STATE_CODE")],
                                      x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
                                         csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                         csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                         csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_iri)),
                         key=lambda x: abs(date_diff(x[csv_iri[0].index("VISIT_DATE")],
                                                     csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))

        # Añade el índice y diferencia de fechas del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].append(nearest[0][csv_iri[0].index("MRI")])
            csv_pci[i].append(date_diff(nearest[0][csv_iri[0].index("VISIT_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")])/365)
            count += 1
        else:
            csv_pci[i].extend([""] * 2)
        sys.stdout.write("\r- IRI %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == DEF ==

    csv_pci[0].extend(csv_def[0][4:len(csv_def[0])])
    csv_pci[0].append("DEF_YEAR_DIF")
    count = 0

    for i in range(1, limit):

        # Lista ordenada de valores por diferencia de fechas
        nearest = sorted(list(filter(lambda x:
                                     [x[csv_def[0].index("SHRP_ID")],
                                      x[csv_def[0].index("STATE_CODE")],
                                      x[csv_def[0].index("CONSTRUCTION_NO")]] == [
                                         csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                         csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                         csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_def)),
                         key=lambda x: abs(date_diff(x[csv_def[0].index("TEST_DATE")],
                                                     csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))

        # Añade el índice y diferencia de fechas del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].extend(nearest[0][4:len(nearest[0])])
            csv_pci[i].append(date_diff(nearest[0][csv_def[0].index("TEST_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")])/365)
            count += 1
        else:
            csv_pci[i].extend([""] * 7)
        sys.stdout.write("\r- DEF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == SKN ==

    csv_pci[0].extend(["SKID_NUMBER", "SKN_YEAR_DIF"])
    count = 0

    for i in range(1, limit):

        # Lista ordenada de valores por diferencia de fechas
        nearest = sorted(list(filter(lambda x:
                                     [x[csv_skn[0].index("SHRP_ID")],
                                      x[csv_skn[0].index("STATE_CODE")],
                                      x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
                                         csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                         csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                         csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_skn)),
                         key=lambda x: abs(date_diff(x[csv_skn[0].index("FRICTION_DATE")],
                                                     csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))

        # Añade el índice y diferencia de fechas del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].append(nearest[0][csv_skn[0].index("FRICTION_NO_END")])
            csv_pci[i].append(date_diff(nearest[0][csv_skn[0].index("FRICTION_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")])/365)
            count += 1
        else:
            csv_pci[i].extend([""] * 2)
        sys.stdout.write("\r- DEF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == CND ==

    csv_pci[0].append("Pa")
    count = 0

    for i in range(1, limit):

        # Lista de valores
        nearest = list(filter(lambda x:
                              [x[csv_cnd[0].index("SHRP_ID")],
                               x[csv_cnd[0].index("STATE_CODE")],
                               x[csv_cnd[0].index("CONSTRUCTION_NO")]] == [
                                  csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                  csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                  csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_cnd))

        # Añade la diferencia de fechas del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].append(date_diff(csv_pci[i][csv_pci[0].index("SURVEY_DATE")],
                                        nearest[0][csv_cnd[0].index("CN_ASSIGN_DATE")]) / 365)
            count += 1
        else:
            csv_pci[i].append("")

        sys.stdout.write("\r- CND %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == TRF ==

    csv_pci[0].extend(csv_trf[0][3:6])
    count = 0

    for i in range(1, limit):

        # Lista de valores
        nearest = list(filter(lambda x:
                              [x[csv_trf[0].index("SHRP_ID")],
                               x[csv_trf[0].index("STATE_CODE")],
                               int(x[csv_trf[0].index("YEAR_MON_EST")])] == [
                                  csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                  csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                  int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")])], csv_trf[1:]))

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].extend(nearest[0][3:6])
            count += 1
        else:
            csv_pci[i].extend([""] * 3)

        sys.stdout.write("\r- TRF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == SNU ==

    csv_pci[0].append("SN")
    count = 0

    for i in range(1, limit):

        # Lista de valores
        nearest = list(filter(lambda x:
                              [x[csv_snu[0].index("SHRP_ID")],
                               x[csv_snu[0].index("STATE_CODE")],
                               x[csv_snu[0].index("CONSTRUCTION_NO")]] == [
                                  csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                  csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                  csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_snu))

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].append(nearest[0][csv_snu[0].index("SN_VALUE")])
            count += 1
        else:
            csv_pci[i].append("")

        sys.stdout.write("\r- SNU %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # == VWS ==

    csv_pci[0].extend(csv_vws[0][4:len(csv_vws[0])])
    count = 0

    for i in range(1, limit):

        # Lista de valores
        nearest = list(filter(lambda x:
                              [x[csv_vws[0].index("SHRP_ID")],
                               x[csv_vws[0].index("STATE_CODE")],
                               int(x[csv_vws[0].index("YEAR")]),
                               int(x[csv_vws[0].index("MONTH")])] == [
                                  csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                  csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                  int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
                                  int_month(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
                              ], csv_vws[1:]))

        # Añade el índice del primer valor de la lista
        if len(nearest) > 0:
            csv_pci[i].extend(nearest[0][4:len(nearest[0])])
            count += 1
        else:
            csv_pci[i].extend([""] * 16)

        sys.stdout.write("\r- VWS %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + ".csv"
    save_csv(save_path, csv_pci)

    print(" ✓  Program finished in", '%.3f' % (time.time() - start_time), "seconds")

    exit(0)
