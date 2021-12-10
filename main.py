import csv
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
        timedelta_under = abs(nearest_under - pivot)
    # If there are no minor or equal data
    except ValueError:
        nearest_under = min([i for i in items if i > pivot], key=lambda x: abs(x - pivot))
        timedelta_under = abs(nearest_under - pivot)
        flag = 1

    # Nearest date major than pivot, and difference
    try:
        nearest_over = min([i for i in items if i > pivot], key=lambda x: abs(x - pivot))
        timedelta_over = abs(nearest_over - pivot)
    # If there are no major data
    except ValueError:
        nearest_over = min([i for i in items if i <= pivot], key=lambda x: abs(x - pivot))
        timedelta_over = abs(nearest_under - pivot)
        flag = -1

    # If deltas are not equal, gives a sign. Return nearest date over pivot
    if flag == -1 or timedelta_under < timedelta_over:
        return nearest_under, -1
    elif flag == 1 or timedelta_under > timedelta_over:
        return nearest_over, 1
    else:
        return nearest_over, 0


def put_index(row_ref, csv_ind, p1, p2, p3, p4, p5, date_f):
    # p1 STATE CODE, p2 SECTION, p3 CONSTRUCTION, p4 VALUE OF INTEREST, p5 DATE

    rws_ind = []
    for row_ind in csv_ind[1:]:
        if [row_ref[0], row_ref[2], row_ref[4]] == [row_ind[p1], row_ind[p2], row_ind[p3]] and row_ind[p4] != "":
            # If it matches all conditions, append a row with VALUE and DATE
            rws_ind.append([row_ind[p4], to_date(row_ind[p5], date_f)])

    val_ind = []
    if len(rws_ind) > 0:
        # Get the nearest date into rows index array
        near, flag = near_date([row[1] for row in rws_ind], to_date(row_ref[3], '%d/%m/%Y'))
        for rw_ind in rws_ind:
            # If row index date is the nearest, append to index value array
            if rw_ind[1] == near:
                val_ind.append(rw_ind[0])

        # Data append:
        # 1. Value
        # 2. Number of elements that match all conditions
        # 3. Nearest date flag
        # 4. Check if all items in the array are the same

        row_ref.extend([val_ind[0], len(rws_ind), flag, list_equals(val_ind)])

        # Mean of all values
        # row_ref.append(sum([float(i.replace(",", ".")) for i in rws_ind]) / len(rws_ind))
    else:
        row_ref.extend([None, len(rws_ind), None, None])

    return row_ref


if __name__ == '__main__':
    csv_pci = load_csv("./csv/pci.csv")
    csv_iri = load_csv("./csv/iri.csv")
    csv_def = load_csv("./csv/deflection.csv")
    csv_skn = load_csv("./csv/sn.csv")

    tables = [
        ["PCI", "IRI", "DEF", "SKN"],
        [0, 1, 0, 1],  # STATE CODE COLUMN
        [2, 3, 1, 0],  # SECTION COLUMN
        [4, 10, 8, 3],  # CONSTRUCTION COLUMN
        [58, 9, 21, 10],  # VALUE OF INTEREST COLUMN
        [3, 0, 2, 4],  # DATE COLUMN
        ['%m/%d/%Y', '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%Y'],  # DATE FORMAT
    ]

    for table in tables[0][1:]:
        csv_pci[0].extend([table, table + " Number", table + " Dates", table + " Equal"])

    # print("IRI:", len(csv_iri), "x", len(csv_iri[0]))
    # print("PCI:", len(csv_pci), "x", len(csv_pci[0]))
    # print("DEF:", len(csv_def), "x", len(csv_def[0]))

    limit = 100  # len(csv_pci)

    count = 0

    for row_pci in csv_pci[1:limit]:

        row_pci = put_index(row_pci, csv_iri, 1, 2, 9, 8, 0, '%m/%d/%Y')
        row_pci = put_index(row_pci, csv_def, 0, 1, 8, 21, 2, '%d/%m/%Y')
        row_pci = put_index(row_pci, csv_skn, 1, 0, 3, 10, 4, '%m/%d/%Y')

        if len(row_pci) != len(csv_pci[0]):
            print("x", end="")
        else:
            print("|", end="")

        count += 1

        if count % 10 == 0 or count == len(csv_pci[1:limit]):
            print("", round(count * 100 / len(csv_pci[1:limit]), 2), "%")

    save_path = "./res/" + datetime.now().strftime("(%d-%m-%Y_%H-%M-%S)") + "_PCI-IRI-DEF-SK" + ".csv"
    save_csv(save_path, csv_pci)

    exit(0)
