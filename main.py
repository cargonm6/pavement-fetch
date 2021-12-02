import csv
import numpy as np
from scipy.stats import pearsonr
from datetime import datetime


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


def calc_correlation(data1, data2):
    data_cov = np.cov(data1, data2)
    data_cor, _ = pearsonr(data1, data2)
    return [data_cov, data_cor]


if __name__ == '__main__':
    csv_iri = load_csv("./csv/iri.csv")
    csv_def = load_csv("./csv/deflection.csv")
    csv_pci = load_csv("./csv/pci.csv")
    csv_skn = load_csv("./csv/sn.csv")

    csv_pci[0].append("IRI")
    csv_pci[0].append("IRI N")
    csv_pci[0].append("DEFLECTION")
    csv_pci[0].append("DEFLECTION N")
    csv_pci[0].append("SKID NUM")
    csv_pci[0].append("SKID NUM N")

    # print("IRI:", len(csv_iri), "x", len(csv_iri[0]))
    # print("PCI:", len(csv_pci), "x", len(csv_pci[0]))
    # print("DEF:", len(csv_def), "x", len(csv_def[0]))

    limit = len(csv_pci)

    count = 0
    count2 = 0

    for row_pci in csv_pci[1:limit]:

        # STATE CODE:   PCI[0], IRI[1], DEF[0], SKN[1]
        # SECTION:      PCI[2], IRI[2], DEF[1], SKN[0]
        # CONSTRUCTION: PCI[4], IRI[9], DEF[8], SKN[3]

        rws_iri = []
        for row_iri in csv_iri[1:]:
            # PCI-IRI: Check State, Section and Construction Number
            if [row_pci[0], row_pci[2], row_pci[4]] == [row_iri[1], row_iri[2], row_iri[9]] and row_iri[8] != "":
                rws_iri.append(row_iri[8])
        if len(rws_iri) > 0:
            row_pci.append(sum([float(i.replace(",", ".")) for i in rws_iri]) / len(rws_iri))
        else:
            row_pci.append("-1")
        row_pci.append(len(rws_iri))

        rws_def = []
        for row_def in csv_def[1:]:
            # PCI-DEF: Check State, Section and Construction Number
            if [row_pci[0], row_pci[2], row_pci[4]] == [row_def[0], row_def[1], row_def[8]] and row_def[21] != "":
                rws_def.append(row_def[21])
        if len(rws_def) > 0:
            row_pci.append(sum([float(i.replace(",", ".")) for i in rws_def]) / len(rws_def))
        else:
            row_pci.append("-1")
        row_pci.append(len(rws_def))

        rws_skn = []
        for row_skn in csv_skn[1:]:
            # PCI-DEF: Check State, Section and Construction Number
            if [row_pci[0], row_pci[2], row_pci[4]] == [row_skn[1], row_skn[0], row_skn[3]] and row_skn[10] != "":
                rws_skn.append(row_skn[10])
        # Evaluate the average SN of all measures
        if len(rws_skn) > 0:
            row_pci.append(sum([float(i.replace(",", ".")) for i in rws_skn]) / len(rws_skn))
        else:
            row_pci.append("-1")
        row_pci.append(len(rws_skn))

        if len(row_pci) != len(csv_pci[0]):
            print("x", end="")
        else:
            print("|", end="")

        count += 1
        count2 += 1

        if count2 == 10 or count == len(csv_pci[1:limit]):
            count2 = 0
            print("", round(count * 100 / len(csv_pci[1:limit]), 2), "%")

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + "_PCI-IRI-DEF-SK" + ".csv"
    save_csv(save_path, csv_pci)

    exit(0)
