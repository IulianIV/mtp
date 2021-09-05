import pandas as pd
import tkinter as tk
from tkinter import filedialog
from mtp import db_manager


# TODO create new and separate view for importer

class Import:

    def __init__(self):

        root = tk.Tk()
        root.withdraw()

        prompt = """
        To import successfully, the name of the imported file must match the name of the table
        you wish to import into. If there is no such table an error will be thrown.
        If you accidentally import with another database name, there is a possibility to have 
        wrong data imported.
        """

        print(prompt)

        cont = input('Do you want to continue? [y/n]')

        if cont == 'y':
            self.file_path = filedialog.askopenfilename()
        else:
            print('Stopped.')

    def import_validation_items(self):
        with open(self.file_path, 'r') as import_file:
            file_name_len = len(self.file_path)
            file_extensions = file_name_len[file_name_len-3:file_name_len]

            if file_extensions != 'csv':
                pass
            elif file_extensions == 'csv':
                imported_df = pd.read_csv(self.file_path)

                for i, j in zip(imported_df['items'], imported_df['category']):
                    print(f'Key: {i} with value: {j}')


if __name__ == '__main__':
    importer = Import()
    importer.import_validation_items()
