import os
import prettytable as pt


class table:
    def __init__(self, name, csvfile):
        self.name = name
        self.fields = []
        self.data = []
        if os.path.isfile(csvfile):
            with open(csvfile, 'r', encoding="utf-8-sig") as f:
                for idx, line in enumerate(f):
                    line = line.rstrip("\n")
                    line = line.split(";")
                    if idx == 0:
                        self.fields = line
                    else:
                        self.data.append(line)
        else:
            raise FileNotFoundError

    def length(self):
        return len(self.fields)

    def index(self, field_name):
        try:
            index = self.fields.index(field_name)
            return index
        except ValueError:
            print("Specified field name does not exist.")

    def present(self):
        pretty = pt.PrettyTable()

        pretty.field_names = self.fields

        for line in self.data:
            pretty.add_row(line)

        print(pretty)
