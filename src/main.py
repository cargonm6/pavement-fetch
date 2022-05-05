from src.modules import module_xls_csv, module_join_csv, module_master, module_interpolate, module_excel


def main(project_root):
    """
    Main function
    :param project_root: project root path
    :return:
    """

    if input("(0) Interpolate Distress CSV? [Y/y] ... ") in ["Y", "y"]:
        module_interpolate.main(project_root)
    if input("(1) Calculate PCI? [Y/y] ... ") in ["Y", "y"]:
        module_excel.main(project_root)
    if input("(2) Convert XLS files to CSV? [Y/y] ... ") in ["Y", "y"]:
        module_xls_csv.main(project_root)
    if input("(3) Join CSV files? [Y/y] ............. ") in ["Y", "y"]:
        module_join_csv.main(project_root)
    if input("(4) Generate master tables? [Y/y] ..... ") in ["Y", "y"]:
        module_master.main(project_root)
