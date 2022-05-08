from src.modules import module_xls_csv, module_join_csv, module_master, module_interpolate, module_excel


def main(project_root):
    """
    Main function
    :param project_root: project root path
    :return:
    """

    tests = [30 * 1, 30 * 3, 30 * 6, 30 * 12]
    # TODO: restore process
    for k, test in enumerate(tests):
        print("=== test %s (%s days intervals)" % (k + 1, test))
        # if input("(0) Interpolate Distress CSV? [Y/y] ... ") in ["Y", "y"]:
        print("(0) Interpolate Distress")
        module_interpolate.main(project_root, test)
        # if input("(1) Calculate PCI? [Y/y] ... ") in ["Y", "y"]:
        print("(1) Calculate PCI")
        module_excel.main(project_root)
        # if input("(2) Convert XLS files to CSV? [Y/y] ... ") in ["Y", "y"]:
        #     module_xls_csv.main(project_root)
        # if input("(3) Join CSV files? [Y/y] ............. ") in ["Y", "y"]:
        #     module_join_csv.main(project_root)
        # if input("(4) Generate master tables? [Y/y] ..... ") in ["Y", "y"]:
        print("(4) Generate master tables")
        module_master.main(project_root)
