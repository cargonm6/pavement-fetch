import os
import sys

from shared import load_csv, save_csv


def csv_group(p_code, p_path="./csv/", p_path_res="./csv/00_All_States/"):
    if not os.path.isdir(p_path_res):
        try:
            print("\U000026A0 The output directory \"%s\" does not exist and will be created. " % p_path_res)
            os.mkdir(p_path_res)
        except OSError:
            print("\U000026D4 The output directory \"%s\" does not exist and could not be created. " % p_path_res)
            exit(1)
    else:
        print("\U0001F6C8 Output directory: \"%s\"" % p_path_res)

    print("\n\U0001F6C8 Finding \"" + p_code + "\" files under path \"" + p_path + "\"")
    p_list = []
    for root, dirs, files in os.walk(p_path):
        for f in files:
            p_list.append((os.path.join(root, f)).replace("\\", "/")) if f.startswith(p_code) else 0

    if len(p_list) == 0:
        print("(!) Code \"%s\" was not found under path \"%s\"" % (p_code, p_path))
        return

    p_result = None

    for n in range(0, len(p_list)):
        if p_result is None:
            p_result = load_csv(p_list[n])
        else:
            [p_result.append(p_row) for p_row in load_csv(p_list[n])[1:]]
        sys.stdout.write("\r- %d/%d files joined" % (n + 1, len(p_list)))

    save_csv(p_path_res + p_code + "_join.csv", p_result)


if __name__ == '__main__':
    # Join CSV files
    for code in ["cnd", "def", "iri", "skn", "snu", "trf", "vws"]:
        csv_group(code)

        save_path = "./csv/00_All_States/" + code + ".csv"
