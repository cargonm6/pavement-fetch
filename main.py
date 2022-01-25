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


def save_csv(file, data):
    with open(file, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(data)
    print("Data saved")


def int_month(date):
    if str(date)[2:3] == "/":
        # Formato dd/mm/aaaa
        return int(str(date)[3:5])
    else:
        # Formato yyyy-mm-dd
        return int(str(date)[5:7])


def int_year(date):
    if str(date)[2:3] == "/":
        # Formato dd/mm/aaaa
        return int(str(date)[6:10])
    else:
        # Formato yyyy-mm-dd
        return int(str(date)[0:4])


def biggest_date(d1, d2):
    if str(d1)[2:3] == "/":
        # Formato dd/mm/aaaa
        d1 = datetime(int(str(d1)[6:10]), int(str(d1)[3:5]), int(str(d1)[0:2]))
    else:
        # Formato yyyy-mm-dd
        d1 = datetime(int(str(d1)[0:4]), int(str(d1)[5:7]), int(str(d1)[8:10]))

    if str(d2)[2:3] == "/":
        # Formato dd/mm/aaaa
        d2 = datetime(int(str(d2)[6:10]), int(str(d2)[3:5]), int(str(d2)[0:2]))
    else:
        # Formato yyyy-mm-dd
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
    print(csv_pci[0], "\n", print(csv_pci[1]), "\n")

    for i in range(1, limit):

        if len(csv_pci[i][csv_pci[0].index("SHRP_ID")]) < 4:
            csv_pci[i][csv_pci[0].index("SHRP_ID")] = "0" + csv_pci[i][csv_pci[0].index("SHRP_ID")]

        sys.stdout.write("\r- PCI %d/%d" % (i, limit - 1))
    print("")

    # TODO : IRI
    print(csv_iri[0], "\n", print(csv_iri[1]), "\n")

    csv_pci[0] = csv_pci[0] + ["MRI"]

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
        else:
            csv_pci[i].append("")
        sys.stdout.write("\r- IRI %d/%d" % (i, limit - 1))
    print("")

    # TODO : DEF
    print(csv_def[0], "\n", print(csv_def[1]), "\n")

    csv_pci[0] = csv_pci[0] + csv_def[0][4:len(csv_def[0])]

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
        else:
            csv_pci[i] = csv_pci[i] + [""] * 6
        sys.stdout.write("\r- DEF %d/%d" % (i, limit - 1))
    print("")

    # TODO : SKN
    print(csv_skn[0], "\n", print(csv_skn[1]), "\n")

    csv_pci[0] = csv_pci[0] + ["FRICTION"]

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
        else:
            csv_pci[i].append("")
        sys.stdout.write("\r- SKN %d/%d" % (i, limit - 1))
    print("")

    # TODO : CND
    print(csv_cnd[0], "\n", print(csv_cnd[1]), "\n")

    csv_pci[0] = csv_pci[0] + ["Pa"]

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
                status = True
                break
        if not status:
            csv_pci[i].append("")

        sys.stdout.write("\r- CND %d/%d" % (i, limit - 1))
    print("")

    # TODO : TRF
    print(csv_trf[0], "\n", print(csv_trf[1]), "\n")

    csv_pci[0] = csv_pci[0] + csv_trf[0][3:6]

    for i in range(1, limit):
        status = False
        # Coge la fecha inferior inmediatamente más cercana
        for j in range(1, len(csv_trf)):
            if [csv_trf[csv_trf[0].index("SHRP_ID")],
                csv_trf[csv_trf[0].index("STATE_CODE")],
                csv_trf[csv_trf[0].index("YEAR_MON_EST")]] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                               csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                               int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")])]:
                csv_pci[i] = csv_pci[i] + csv_trf[j][3:6]
                status = True
                break

        if not status:
            csv_pci[i] = csv_pci[i] + [""] * 16

        sys.stdout.write("\r- TRF %d/%d" % (i, limit - 1))
    print("")

    # TODO : SNU
    print(csv_snu[0], "\n", print(csv_snu[1]), "\n")

    csv_pci[0] = csv_pci[0] + ["SN"]

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
                status = True
                break
        if not status:
            csv_pci[i].append("")

        sys.stdout.write("\r- SNU %d/%d" % (i, limit - 1))
    print("")

    # TODO : VWS
    print(csv_vws[0], "\n", print(csv_vws[1]), "\n")

    csv_pci[0] = csv_pci[0] + csv_vws[0][4:len(csv_vws[0])]

    for i in range(1, limit):
        status = False
        # Coge la fecha inferior inmediatamente más cercana
        for j in range(1, len(csv_vws)):
            if [csv_vws[csv_vws[0].index("SHRP_ID")],
                csv_vws[csv_vws[0].index("STATE_CODE")],
                csv_vws[csv_vws[0].index("YEAR")],
                csv_vws[csv_vws[0].index("MONTH")], ] == [csv_pci[i][csv_pci[0].index("SHRP_ID")],
                                                          csv_pci[i][csv_pci[0].index("STATE_CODE")],
                                                          int_year(csv_pci[i][csv_pci[0].index("SURVEY_DATE")]),
                                                          int_month(csv_pci[i][csv_pci[0].index("SURVEY_DATE")])]:
                csv_pci[i] = csv_pci[i] + csv_vws[j][4:len(csv_vws[j])]
                status = True
                break

        if not status:
            csv_pci[i] = csv_pci[i] + [""] * 16

        sys.stdout.write("\r- VWS %d/%d" % (i, limit - 1))
    print("")

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + ".csv"
    save_csv(save_path, csv_pci)

    print(" ✓  Program finished in", '%.3f' % (time.time() - start_time), "seconds")

    exit(0)
