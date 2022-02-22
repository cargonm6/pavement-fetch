import os
# import shutil
import sys
import time
from datetime import datetime

import csv
import xls2csv


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


def csv_group(p_code, p_path="./csv/", p_path_res="./res/csv/"):
    print("\n\U0001F6C8 Finding \"" + p_code + "\" files under path \"" + p_path + "\"")
    p_list = []
    for root, dirs, files in os.walk(p_path):
        for f in files:
            p_list.append((os.path.join(root, f)).replace("\\", "/")) if f.startswith(p_code) else 0

    if len(p_list) == 0:
        print("(!) Code \"%s\" was not found under path \"%s\"" % (p_code, p_path))
        return

    p_result = None

    for i in range(0, len(p_list)):
        if p_result is None:
            p_result = load_csv(p_list[i])
        else:
            [p_result.append(p_row) for p_row in load_csv(p_list[i])[1:]]
        sys.stdout.write("\r- %d/%d files joined" % (i + 1, len(p_list)))

    save_csv(p_path_res + p_code + "_join.csv", p_result)


if __name__ == '__main__':

    start_time = time.time()

    xls_list = []

    for file in os.listdir("./xls"):
        if file.endswith(".xlsx"):
            xls_list.append(os.path.join("./xls", file).replace("\\", "/"))

    for k in range(0, len(xls_list)):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("(%s/%s) Current file: \"%s\"" % (k + 1, len(xls_list), xls_list[k]))

        csv_path = "./csv/" + os.path.basename(xls_list[k])[0:-5] + "/"

        try:
            xls2csv.main(xls_list[k], csv_path, True)
        except BaseException as e:
            print("(!) Error with file: ", e)
            continue

    # Join CSV files
    for code in ["cnd", "def", "iri", "skn", "snu", "trf", "vws"]:
        csv_group(code)

    exit(0)

    #     save_path = "./res/" + os.path.basename(xls_list[k])[0:-5] + ".csv"
    #     shutil.copyfile("./csv/pci.csv", save_path)
    #
    # for
    #
    #     print("(i) Loading CSV files...")
    #
    #     csv_pci = load_csv(save_path)  # (PCI) Pavement Condition Index
    #     csv_iri = load_csv(csv_path + "/iri.csv")  # (IRI) International Roughness Index
    #     csv_def = load_csv(csv_path + "/def.csv")  # (DEF) Deflections
    #     csv_skn = load_csv(csv_path + "/skn.csv")  # (SKN) Skid Number
    #
    #     csv_cnd = load_csv(csv_path + "/cnd.csv")  # (CND) Construction Number Date
    #     csv_trf = load_csv(csv_path + "/trf.csv")  # (TRF) Traffic
    #     csv_snu = load_csv(csv_path + "/snu.csv")  # (SNU) Structural Number
    #     csv_vws = load_csv(csv_path + "/vws.csv")  # (VWS) Virtual Weather Station
    #
    #     print(" ✓  CSV files loaded in", '%.3f' % (time.time() - start_time), "seconds\n")
    #
    #     # == PCI ==
    #
    #     csv_pci = [csv_pci[0]] + (list(filter(lambda x:
    #                                           x[csv_pci[0].index("STATE_CODE")] ==
    #                                           csv_iri[1][csv_iri[0].index("STATE_CODE")], csv_pci)))
    #
    #     limit = len(csv_pci)
    #
    #     for i in range(1, limit):
    #
    #         if len(csv_pci[i][csv_pci[0].index("SHRP_ID")]) < 4:
    #             csv_pci[i][csv_pci[0].index("SHRP_ID")] = "0" + csv_pci[i][csv_pci[0].index("SHRP_ID")]
    #
    #     # == IRI ==
    #
    #     csv_pci[0].extend(["IRI", "IRI_YEAR_DIF"])
    #     count = 0
    #
    #     for i in range(1, limit):
    #         # Lista ordenada de valores por diferencia de fechas
    #         nearest = sorted(list(filter(lambda x:
    #                                      [x[csv_iri[0].index("SHRP_ID")],
    #                                       x[csv_iri[0].index("STATE_CODE")],
    #                                       x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
    #                                          csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                          csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                          csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_iri)),
    #                          key=lambda x: abs(date_diff(x[csv_iri[0].index("VISIT_DATE")],
    #                                                      csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))
    #
    #         # Añade el índice y diferencia de fechas del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].append(nearest[0][csv_iri[0].index("MRI")])
    #             csv_pci[i].append(date_diff(nearest[0][csv_iri[0].index("VISIT_DATE")],
    #                                         csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) / 365)
    #             count += 1
    #         else:
    #             csv_pci[i].extend([""] * 2)
    #         sys.stdout.write("\r- IRI %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == DEF ==
    #
    #     csv_pci[0].extend(csv_def[0][4:len(csv_def[0])])
    #     csv_pci[0].append("DEF_YEAR_DIF")
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista ordenada de valores por diferencia de fechas
    #         nearest = sorted(list(filter(lambda x:
    #                                      [x[csv_def[0].index("SHRP_ID")],
    #                                       x[csv_def[0].index("STATE_CODE")],
    #                                       x[csv_def[0].index("CONSTRUCTION_NO")]] == [
    #                                          csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                          csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                          csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_def)),
    #                          key=lambda x: abs(date_diff(x[csv_def[0].index("TEST_DATE")],
    #                                                      csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))
    #
    #         # Añade el índice y diferencia de fechas del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].extend(nearest[0][4:len(nearest[0])])
    #             csv_pci[i].append(date_diff(nearest[0][csv_def[0].index("TEST_DATE")],
    #                                         csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) / 365)
    #             count += 1
    #         else:
    #             csv_pci[i].extend([""] * 7)
    #         sys.stdout.write("\r- DEF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == SKN ==
    #
    #     csv_pci[0].extend(["SKID_NUMBER", "SKN_YEAR_DIF"])
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista ordenada de valores por diferencia de fechas
    #         nearest = sorted(list(filter(lambda x:
    #                                      [x[csv_skn[0].index("SHRP_ID")],
    #                                       x[csv_skn[0].index("STATE_CODE")],
    #                                       x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
    #                                          csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                          csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                          csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_skn)),
    #                          key=lambda x: abs(date_diff(x[csv_skn[0].index("FRICTION_DATE")],
    #                                                      csv_pci[i][csv_pci[0].index("SURVEY_DATE")])))
    #
    #         # Añade el índice y diferencia de fechas del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].append(nearest[0][csv_skn[0].index("FRICTION_NO_END")])
    #             csv_pci[i].append(date_diff(nearest[0][csv_skn[0].index("FRICTION_DATE")],
    #                                         csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) / 365)
    #             count += 1
    #         else:
    #             csv_pci[i].extend([""] * 2)
    #         sys.stdout.write("\r- SKN %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == CND ==
    #
    #     csv_pci[0].append("Pa")
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista de valores
    #         nearest = list(filter(lambda x:
    #                               [x[csv_cnd[0].index("SHRP_ID")],
    #                                x[csv_cnd[0].index("STATE_CODE")],
    #                                x[csv_cnd[0].index("CONSTRUCTION_NO")]] == [
    #                                   csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                   csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                   csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_cnd))
    #
    #         # Añade la diferencia de fechas del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].append(date_diff(csv_pci[i][csv_pci[0].index("SURVEY_DATE")],
    #                                         nearest[0][csv_cnd[0].index("CN_ASSIGN_DATE")]) / 365)
    #             count += 1
    #         else:
    #             csv_pci[i].append("")
    #
    #         sys.stdout.write("\r- CND %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == TRF ==
    #
    #     csv_pci[0].extend(csv_trf[0][3:6])
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista de valores
    #         nearest = list(filter(lambda x:
    #                               [x[csv_trf[0].index("SHRP_ID")],
    #                                x[csv_trf[0].index("STATE_CODE")],
    #                                int(x[csv_trf[0].index("YEAR_MON_EST")])] == [
    #                                   csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                   csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                   int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")])], csv_trf[1:]))
    #
    #         # Añade el índice del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].extend(nearest[0][3:6])
    #             count += 1
    #         else:
    #             csv_pci[i].extend([""] * 3)
    #
    #         sys.stdout.write("\r- TRF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == SNU ==
    #
    #     csv_pci[0].append("SN")
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista de valores
    #         nearest = list(filter(lambda x:
    #                               [x[csv_snu[0].index("SHRP_ID")],
    #                                x[csv_snu[0].index("STATE_CODE")],
    #                                x[csv_snu[0].index("CONSTRUCTION_NO")]] == [
    #                                   csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                   csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                   csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]], csv_snu))
    #
    #         # Añade el índice del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].append(nearest[0][csv_snu[0].index("SN_VALUE")])
    #             count += 1
    #         else:
    #             csv_pci[i].append("")
    #
    #         sys.stdout.write("\r- SNU %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     # == VWS ==
    #
    #     csv_pci[0].extend(csv_vws[0][4:len(csv_vws[0])])
    #     count = 0
    #
    #     for i in range(1, limit):
    #
    #         # Lista de valores
    #         nearest = list(filter(lambda x:
    #                               [x[csv_vws[0].index("SHRP_ID")],
    #                                x[csv_vws[0].index("STATE_CODE")],
    #                                int(x[csv_vws[0].index("YEAR")]),
    #                                int(x[csv_vws[0].index("MONTH")])] == [
    #                                   csv_pci[i][csv_pci[0].index("SHRP_ID")],
    #                                   csv_pci[i][csv_pci[0].index("STATE_CODE")],
    #                                   int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
    #                                   int_month(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
    #                               ], csv_vws[1:]))
    #
    #         # Añade el índice del primer valor de la lista
    #         if len(nearest) > 0:
    #             csv_pci[i].extend(nearest[0][4:len(nearest[0])])
    #             count += 1
    #         else:
    #             csv_pci[i].extend([""] * 16)
    #
    #         sys.stdout.write("\r- VWS %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    #     print("")
    #
    #     save_csv(save_path, csv_pci)
    #
    # print(" ✓  xls2csv finished in", '%.3f' % (time.time() - start_time), "seconds")
    #
    # exit(0)
