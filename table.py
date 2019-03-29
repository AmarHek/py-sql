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

# TODO: reorder, i.e. constructor makes empty table, load_csv loads from csv, make_copy copys from another table and
#       join takes two tables to create one. Perhaps add prefix to all columns to make things easier

class Table:
    # specify name and file from which to load the data
    # optional: specify delimiter used in the file, default is ';'
    def __init__(self, name: str, csv_file=None, delimiter=';', copy_table=None):
        self.name = name
        self.fields = []
        self.data = []

        # only load from csv if specified
        if csv_file is not None:
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
                print("File not found")
                return

            # convert all number strings to floats
            for n_row, row in enumerate(self.data):
                for n_column, elem in enumerate(row):
                    if is_number(elem):
                        self.data[n_row][n_column] = float(elem)

        # if copy_table exists, create a copy of it
        elif copy_table is not None:
            self.fields = copy_table.fields[:]
            self.data = copy_table.data[:][:]

        # otherwise the created table is empty, only a name is assigned

    def set_fields(self, fields):
        self.fields = fields

    def set_data(self, data):
        self.data = data

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
        # check if all entered fields are valid
        for field in fields_list:
            if not self.is_valid_field(field):
                print("One or more of the selected fields are invalid")
                return
        # make list of all fields that need to be removed
        to_delete = []
        for field in self.fields:
            if field not in fields_list:
                to_delete.append(field)
        # finally remove all unnecessary columns
        for field in to_delete:
            self.delete_column(field)

    # delete single column of table
    def delete_column(self, field):
        idx = self.index(field)
        for row in self.data:
            del row[idx]
        del self.fields[idx]

    # deletes all rows from data that do not match condition
    def select(self, condition):
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

    def reduce(self):
        # make copy of data (needed for proper looping)
        junk_row_index = []
        for idx, row in enumerate(self.data):
            for idx2, row2 in enumerate(self.data):
                if idx != idx2 and row == row2:
                    junk_row_index.append(idx2)
        for row_index in junk_row_index[::-1]:
            del self.data[row_index]

    def join(self, self_field, second_table, second_field):
        index1 = self.index(self_field)
        index2 = second_table.index(second_field)
        if index1 is None or index2 is None:
            raise ValueError("One or more fields are invalid")

        # create empty table for joining
        joined = Table('joined')

        # create joined fields
        join_fields = []
        for field in self.fields:
            join_fields.append(field)
        for field in second_table.fields:
            # ignore second field since self_field is already in joined_fields
            if field != second_field:
                # if column names are duplicates, then add table name as prefix
                if field in join_fields:
                    field = second_table.name + '.' + field
                join_fields.append(field)

        # create column of first and second fields to make things easier below
        first_field_as_column = []
        for row in self.data:
            first_field_as_column.append(row[index1])
        second_field_as_column = []
        for row in second_table.data:
            second_field_as_column.append(row[index2])

        # copy data from first table to temporary list
        joined_data = self.data[:][:]

        # loop through first_field_as_column (= rows of first table)
        for row, value in enumerate(first_field_as_column):
            # check, where this value is the same as in second_field_as_column (= corresponding row in second_table)
            try:
                second_table_row = second_field_as_column.index(value)
                # loop through the corresponding row of second table and append values to joined_data
                for column, second_value in enumerate(second_table.data[second_table_row]):
                    # skip value of second_field
                    if not column == index2:
                        joined_data[row].append(second_value)
            except ValueError:
                print("No matching value found in second table")

        # set temporary lists to joined table object and return
        joined.set_fields(join_fields)
        joined.set_data(joined_data)

        return joined
