import os
import prettytable as pt
import operator


# auxiliary function to check if string can be converted to float
def is_number(s):
    if '_' in s:
        return False
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False


def convert_to_operator(op_string):
    operator_dict = {'>': operator.gt,
                     '<': operator.lt,
                     '>=': operator.ge,
                     '<=': operator.le,
                     '=': operator.eq,
                     '<>': operator.ne,
                     '!=': operator.ne}
    return operator_dict[op_string]


class Table:
    # specify name and file from which to load the data
    # optional: specify delimiter used in the file, default is ';'
    def __init__(self, name, csv_file, delimiter=';'):
        self.name = name
        self.fields = []
        self.data = []
        # check if file exists, raise error if not
        if os.path.isfile(csv_file):
            with open(csv_file, 'r', encoding="utf-8-sig") as f:
                for idx, line in enumerate(f):
                    # remove trailing new line and split by delimiter
                    line = line.rstrip("\n")
                    line = line.split(delimiter)
                    # first line in file is treated as list of fields
                    if idx == 0:
                        self.fields = line
                    else:
                        self.data.append(line)
        else:
            raise FileNotFoundError

        # convert all number strings to floats
        for n_row, row in enumerate(self.data):
            for n_column, elem in enumerate(row):
                if is_number(elem):
                    self.data[n_row][n_column] = float(elem)

    def length(self):
        return len(self.fields)

    def index(self, field_name):
        try:
            index = self.fields.index(field_name)
            return index
        except ValueError:
            print("Specified field name does not exist.")

    # plot the table in terminal
    def present(self):
        pretty = pt.PrettyTable()

        pretty.field_names = self.fields

        for line in self.data:
            pretty.add_row(line)

        print(pretty)

    # check if a given field name exists in the table
    def is_valid_field(self, field):
        return field in self.fields

    # delete all columns of a table specified in fields_list
    def project(self, fields_list):
        if type(fields_list) == str:
            if self.is_valid_field(fields_list):
                self.delete_column(fields_list)
            else:
                raise Warning("%s is an invalid field, skipping" % fields_list)
        else:
            for field in fields_list:
                if self.is_valid_field(field):
                    self.delete_column(field)
                else:
                    raise Warning("%s is an invalid field, skipping" % field)

    # delete single column of table
    def delete_column(self, field):
        idx = self.index(field)
        for row in self.data:
            del row[idx]
        del self.fields[idx]

    # deletes all rows from data that do not match condition
    def select(self, condition):
        # TODO: Perhaps change to condition[0] is just field and name will be parsed in upper database class
        field = condition[0]
        op = convert_to_operator(condition[1])
        junk_data = []
        value = condition[2]
        if not self.is_valid_field(field):
            raise Warning('Table does not have specified field name')
        else:
            column = self.index(field)
            for idx, row in enumerate(self.data):
                if not op(row[column], value):
                    junk_data.append(row)
            for row in junk_data:
                self.data.remove(row)

    def join(self, field, table, other_field):
        