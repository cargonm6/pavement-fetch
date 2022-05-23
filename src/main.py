from copy import deepcopy

from src.modules import module_xls_csv, module_join_csv, module_master, module_interpolate, module_excel
from src.modules.module_common import load_csv, save_csv


def main(project_root):
    """
    Main function
    :param project_root: project root path
    :return:
    """

    tests = [0]  # , 30 * 1, 30 * 3, 30 * 6, 30 * 12
    # TODO: restore process
    for k, test in enumerate(tests):
        print("=== test %s (%s days intervals)" % (k + 1, test))
        if input("(0) Interpolate Distress CSV? [Y/y] ... ") in ["Y", "y"]:
            print("(0) Interpolate Distress")
            module_interpolate.main(project_root, test)
        if input("(1) Calculate PCI? [Y/y] ... ") in ["Y", "y"]:
            print("(1) Calculate PCI")
            module_excel.main(project_root)
        if input("(1.1) Mark PCI error rows [Y/y] ... ") in ["Y", "y"]:
            print("Marking...")
            pci_csv = load_csv(project_root + '/res/csv/ready/pci.csv')
            pci_csv[0].append("PCI_SLOPE")
            pci_csv[1].append(0.0)
            for i in range(2, len(pci_csv)):
                if [pci_csv[i][pci_csv[0].index("STATE_CODE")],
                    pci_csv[i][pci_csv[0].index("SHRP_ID")],
                    pci_csv[i][pci_csv[0].index("CONSTRUCTION_NO")]] == \
                        [pci_csv[i - 1][pci_csv[0].index("STATE_CODE")],
                         pci_csv[i - 1][pci_csv[0].index("SHRP_ID")],
                         pci_csv[i - 1][pci_csv[0].index("CONSTRUCTION_NO")]]:

                    pci_csv[i].append(
                        float(pci_csv[i][pci_csv[0].index("PCI")]) - float(pci_csv[i - 1][pci_csv[0].index("PCI")])
                    )
                else:
                    pci_csv[i].append(0.0)
            pci_csv_fixed = [pci_csv[0][0:-1]]
            for i in range(1, len(pci_csv)):
                if pci_csv[i][pci_csv[0].index("PCI_SLOPE")] <= 0.0:
                    pci_csv_fixed.append(pci_csv[i][0:-1])

            save_csv(project_root + '/res/csv/ready/pci_slope.csv', pci_csv)
            save_csv(project_root + '/res/csv/ready/pci_fixed.csv', pci_csv_fixed)

        # if input("(2) Convert XLS files to CSV? [Y/y] ... ") in ["Y", "y"]:
        #     module_xls_csv.main(project_root)
        # if input("(3) Join CSV files? [Y/y] ............. ") in ["Y", "y"]:
        #     module_join_csv.main(project_root)
        if input("(4) Generate master tables? [Y/y] ..... ") in ["Y", "y"]:
            print("(4) Generate master tables")
            module_master.main(project_root)
