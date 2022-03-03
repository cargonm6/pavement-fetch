import csv


def row_to_str(p_row):
    for j in range(0, len(p_row)):
        p_row[j] = str(p_row[j])  # Convert data to string
        p_row[j] = p_row[j].replace(".", ",")  # Replace dots with commas
        p_row[j] = p_row[j].replace("nan", "")  # Replace "nan" with void
    return p_row


def save_csv(p_path, p_data):
    for i in range(1, len(p_data)):
        p_data[i] = row_to_str(p_data[i])

        # Fix zero prefix in SHRP_ID
        if "SHRP_ID" in p_data[0] and len(p_data[i][p_data[0].index("SHRP_ID")]) < 4:
            p_data[i][p_data[0].index("SHRP_ID")] = "0" + p_data[i][p_data[0].index("SHRP_ID")]

    with open(p_path, 'w', newline='') as f:
        write = csv.writer(f, delimiter=';')
        write.writerows(p_data)

    print("\n\U0001F5AB Data saved")


def load_csv(p_file):
    with open(p_file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader)
    return data
