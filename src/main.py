from src.modules import module_xls_csv, module_join_csv, module_master


def main(project_root):
    if input("(1) Convert XLS files to CSV? [Y/y] ... ") in ["Y", "y"]:
        module_xls_csv.main(project_root)
    if input("(2) Join CSV files? [Y/y] ............. ") in ["Y", "y"]:
        module_join_csv.main(project_root)
    if input("(3) Generate master tables? [Y/y] ..... ") in ["Y", "y"]:
        module_master.main(project_root)
