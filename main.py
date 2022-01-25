import sys
import time
from datetime import datetime
from operator import itemgetter

import csv


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


def biggest_date(d1, d2):
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

    if d1 > d2:
        value = 1
    elif d1 < d2:
        value = 2
    else:
        value = 0

    return value


if __name__ == '__main__':
    start_time = time.time()

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

    # TODO : PCI

    for i in range(1, limit):

        if len(csv_pci[i][csv_pci[0].index("SHRP_ID")]) < 4:
            csv_pci[i][csv_pci[0].index("SHRP_ID")] = "0" + csv_pci[i][csv_pci[0].index("SHRP_ID")]

    # TODO : IRI

    csv_pci[0] = csv_pci[0] + ["MRI"]

    count = 0

    for i in range(1, limit):

        # Coge la fecha inferior inmediatamente más cercana
        if len(list(filter(lambda x:
                           [x[csv_iri[0].index("SHRP_ID")],
                            x[csv_iri[0].index("STATE_CODE")],
                            x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
                               csv_pci[i][csv_pci[0].index("SHRP_ID")],
                               csv_pci[i][csv_pci[0].index("STATE_CODE")],
                               csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                           biggest_date(x[csv_iri[0].index("VISIT_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_iri))) > 0:
            last_value = max(filter(lambda x:
                                    [x[csv_iri[0].index("SHRP_ID")],
                                     x[csv_iri[0].index("STATE_CODE")],
                                     x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_iri[0].index("VISIT_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_iri),
                             key=itemgetter(csv_iri[0].index("VISIT_DATE")))
            csv_pci[i].append(last_value[csv_iri[0].index("MRI")])
            count += 1

        # Coge la fecha inferior inmediatamente más cercana
        elif len(list(filter(lambda x:
                             [x[csv_iri[0].index("SHRP_ID")],
                              x[csv_iri[0].index("STATE_CODE")],
                              x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
                                 csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                 csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                 csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                             biggest_date(x[csv_iri[0].index("VISIT_DATE")],
                                          csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_iri))) > 0:
            last_value = min(filter(lambda x:
                                    [x[csv_iri[0].index("SHRP_ID")],
                                     x[csv_iri[0].index("STATE_CODE")],
                                     x[csv_iri[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_iri[0].index("VISIT_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_iri),
                             key=itemgetter(csv_iri[0].index("VISIT_DATE")))
            csv_pci[i].append(last_value[csv_iri[0].index("MRI")])
            count += 1
        else:
            csv_pci[i].append("")
        sys.stdout.write("\r- IRI %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : DEF

    csv_pci[0] = csv_pci[0] + csv_def[0][4:len(csv_def[0])]

    count = 0

    for i in range(1, limit):

        # Coge la fecha inferior inmediatamente más cercana
        if len(list(filter(lambda x:
                           [x[csv_def[0].index("SHRP_ID")],
                            x[csv_def[0].index("STATE_CODE")],
                            x[csv_def[0].index("CONSTRUCTION_NO")]] == [
                               csv_pci[i][csv_pci[0].index("SHRP_ID")],
                               csv_pci[i][csv_pci[0].index("STATE_CODE")],
                               csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                           biggest_date(x[csv_def[0].index("TEST_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_def))) > 0:
            last_value = max(filter(lambda x:
                                    [x[csv_def[0].index("SHRP_ID")],
                                     x[csv_def[0].index("STATE_CODE")],
                                     x[csv_def[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_def[0].index("TEST_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_def),
                             key=itemgetter(csv_def[0].index("TEST_DATE")))
            csv_pci[i] = csv_pci[i] + last_value[4:len(last_value)]
            count += 1
        # Coge la fecha inferior inmediatamente más cercana
        elif len(list(filter(lambda x:
                             [x[csv_def[0].index("SHRP_ID")],
                              x[csv_def[0].index("STATE_CODE")],
                              x[csv_def[0].index("CONSTRUCTION_NO")]] == [
                                 csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                 csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                 csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                             biggest_date(x[csv_def[0].index("TEST_DATE")],
                                          csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_def))) > 0:
            last_value = min(filter(lambda x:
                                    [x[csv_def[0].index("SHRP_ID")],
                                     x[csv_def[0].index("STATE_CODE")],
                                     x[csv_def[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_def[0].index("TEST_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_def),
                             key=itemgetter(csv_def[0].index("TEST_DATE")))
            csv_pci[i] = csv_pci[i] + last_value[4:len(last_value)]
            count += 1
        else:
            csv_pci[i] = csv_pci[i] + [""] * 6
        sys.stdout.write("\r- DEF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : SKN

    csv_pci[0] = csv_pci[0] + ["FRICTION"]

    count = 0

    for i in range(1, limit):

        # Coge la fecha inferior inmediatamente más cercana
        if len(list(filter(lambda x:
                           [x[csv_skn[0].index("SHRP_ID")],
                            x[csv_skn[0].index("STATE_CODE")],
                            x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
                               csv_pci[i][csv_pci[0].index("SHRP_ID")],
                               csv_pci[i][csv_pci[0].index("STATE_CODE")],
                               csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                           biggest_date(x[csv_skn[0].index("FRICTION_DATE")],
                                        csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_skn))) > 0:
            last_value = max(filter(lambda x:
                                    [x[csv_skn[0].index("SHRP_ID")],
                                     x[csv_skn[0].index("STATE_CODE")],
                                     x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_skn[0].index("FRICTION_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 2, csv_skn),
                             key=itemgetter(csv_skn[0].index("FRICTION_DATE")))
            csv_pci[i].append(last_value[csv_skn[0].index("FRICTION_NO_END")])
            count += 1

        # Coge la fecha inferior inmediatamente más cercana
        elif len(list(filter(lambda x:
                             [x[csv_skn[0].index("SHRP_ID")],
                              x[csv_skn[0].index("STATE_CODE")],
                              x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
                                 csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                 csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                 csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                             biggest_date(x[csv_skn[0].index("FRICTION_DATE")],
                                          csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_skn))) > 0:
            last_value = min(filter(lambda x:
                                    [x[csv_skn[0].index("SHRP_ID")],
                                     x[csv_skn[0].index("STATE_CODE")],
                                     x[csv_skn[0].index("CONSTRUCTION_NO")]] == [
                                        csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                        csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                        csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]] and
                                    biggest_date(x[csv_skn[0].index("FRICTION_DATE")],
                                                 csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) == 1, csv_skn),
                             key=itemgetter(csv_skn[0].index("FRICTION_DATE")))
            csv_pci[i].append(last_value[csv_skn[0].index("FRICTION_NO_END")])
            count += 1

        else:
            csv_pci[i].append("")
        sys.stdout.write("\r- SKN %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : CND

    csv_pci[0] = csv_pci[0] + ["Pa"]

    count = 0

    for i in range(1, limit):
        status = False
        for j in range(1, len(csv_cnd)):
            if [csv_cnd[j][csv_cnd[0].index("SHRP_ID")],
                csv_cnd[j][csv_cnd[0].index("STATE_CODE")],
                csv_cnd[j][csv_cnd[0].index("CONSTRUCTION_NO")]] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                                     csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                                     csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]]:
                # Cálculo de p_a
                csv_pci[i].append(int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]) - int_year(
                    csv_cnd[j][csv_cnd[0].index("CN_ASSIGN_DATE")]))
                count += 1
                status = True
                break
        if not status:
            csv_pci[i].append("")

        sys.stdout.write("\r- CND %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : TRF

    csv_pci[0] = csv_pci[0] + csv_trf[0][3:6]

    count = 0

    for i in range(1, limit):
        status = False
        # Coge la fecha inferior inmediatamente más cercana
        for j in range(1, len(csv_trf)):
            if [csv_trf[j][csv_trf[0].index("SHRP_ID")],
                csv_trf[j][csv_trf[0].index("STATE_CODE")],
                int(csv_trf[j][csv_trf[0].index("YEAR_MON_EST")])] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                                       csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                                       int_year(csv_pci[i][
                                                                                    csv_pci[0].index("SURVEY_DATE")])]:
                csv_pci[i] = csv_pci[i] + csv_trf[j][3:6]
                count += 1
                status = True
                break

        if not status:
            csv_pci[i] = csv_pci[i] + [""] * 3

        sys.stdout.write("\r- TRF %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : SNU

    csv_pci[0] = csv_pci[0] + ["SN"]

    count = 0

    for i in range(1, limit):
        status = False
        for j in range(1, len(csv_snu)):
            if [csv_snu[j][csv_snu[0].index("SHRP_ID")],
                csv_snu[j][csv_snu[0].index("STATE_CODE")],
                csv_snu[j][csv_snu[0].index("CONSTRUCTION_NO")]] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                                     csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                                     csv_pci[i][csv_pci[0].index("CONSTRUCTION_NO")]]:
                #
                csv_pci[i].append(csv_snu[j][csv_snu[0].index("SN_VALUE")])
                count += 1
                status = True
                break
        if not status:
            csv_pci[i].append("")

        sys.stdout.write("\r- SNU %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    # TODO : VWS

    csv_pci[0] = csv_pci[0] + csv_vws[0][4:len(csv_vws[0])]

    count = 0

    for i in range(1, limit):
        status = False
        # Coge la fecha inferior inmediatamente más cercana
        for j in range(1, len(csv_vws)):
            if [csv_vws[j][csv_vws[0].index("SHRP_ID")],
                csv_vws[j][csv_vws[0].index("STATE_CODE")],
                int(csv_vws[j][csv_vws[0].index("YEAR")]),
                int(csv_vws[j][csv_vws[0].index("MONTH")])] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                                csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                                int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
                                                                int_month(csv_pci[i][csv_pci[0].index("SURVEY_DATE")])]:
                csv_pci[i] = csv_pci[i] + csv_vws[j][4:len(csv_vws[j])]
                count += 1
                status = True
                break

        if not status:
            csv_pci[i] = csv_pci[i] + [""] * 16

        sys.stdout.write("\r- VWS %d/%d: añadidas %s entradas" % (i, limit - 1, count))
    print("")

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + ".csv"
    save_csv(save_path, csv_pci)

    print(" ✓  Program finished in", '%.3f' % (time.time() - start_time), "seconds")

    exit(0)
