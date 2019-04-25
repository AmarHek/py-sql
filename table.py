import os
import prettytable as pt
import operator
import copy


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


# TODO: Add 'In' functionality
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
    """
    Test
    """

    def __init__(self, name: str):
        # create an empty Table object with only a name
        self.name = name
        self.fields = []
        self.data = []

    def load_from_csv(self, csv_file, delimiter=';'):
        # specify name and file from which to load the data
        # optional: specify delimiter used in the file, default is ';'
        # only load from csv if specified
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
        for i, row in enumerate(self.data):
            for j, entry in enumerate(row):
                if is_number(entry):
                    self.data[i][j] = float(entry)

    # copies the contents of one table to another
    def copy(self, original_table):
        self.fields = copy.deepcopy(original_table.fields)
        self.data = copy.deepcopy(original_table.data)

    # returns the number of columns of the table
    def length(self):
        return len(self.fields)

    # returns the index of a field
    def index(self, field_name):
        if self.is_valid_field(field_name):
            index = self.fields.index(field_name)
            return index
        else:
            print("Table '{}' does not have a field named '{}'").format(self.name, field_name)
            return None

    # check if a given field name exists in the table
    def is_valid_field(self, field):
        return field in self.fields

    # plot the table in terminal
    def present(self):
        pretty = pt.PrettyTable()
        pretty.field_names = self.fields
        for line in self.data:
            pretty.add_row(line)
        print(pretty)

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
    def select(self, cond):
        field = cond[0]
        op = convert_to_operator(cond[1])
        value = cond[2]
        junk_rows = []
        if not self.is_valid_field(field):
            print("Warning: Table does not have the field '{}'").format(field)
        else:
            column = self.index(field)
            for idx, row in enumerate(self.data):
                if not op(row[column], value):
                    junk_rows.append(row)
            for row in junk_rows:
                self.data.remove(row)

    def reduce(self):
        # make copy of data (needed for proper looping)
        junk_row_index = []
        # loop twice through the data to compare each row to the rest
        # second loop always starts at the current index of first loop
        for i in range(len(self.data)):
            for j in range(i, len(self.data)):
                if i != j and self.data[i] == self.data[j] and j not in junk_row_index:
                    junk_row_index.append(j)
        junk_row_index.sort()
        # running backwards to avoid index confusion
        for row_index in junk_row_index[::-1]:
            del self.data[row_index]

    def join(self, self_field, second_table, second_field):
        # joins this table with a specified second table at the given fields and returns the joined super-table
        # extract indexes of given fields
        index1 = self.index(self_field)
        index2 = second_table.index(second_field)
        if index1 is None or index2 is None:
            return None

        # create empty table for joining
        joined = Table('joined')
        # create joined fields
        join_fields = []

        # TODO: convention: name.field for all fields
        for field in self.fields:
            join_

        # create arrays (= columns) of first and second fields to make things easier below
        first_field_as_column = []
        for row in self.data:
            first_field_as_column.append(row[index1])
        second_field_as_column = []
        for row in second_table.data:
            second_field_as_column.append(row[index2])

        # copy data from first table to temporary list
        joined_data = copy.deepcopy(self.data)

        # loop through first_field_as_column (= rows of first table)
        for row, value in enumerate(first_field_as_column):
            # if value is not in second table, add blank spaces as values
            if value not in second_field_as_column:
                joined_data[row].append([' ']*len(second_table.length()))
            else:
                # check, where value is the same as in second_field_as_column (= corresponding row in second_table)
                second_table_row = second_field_as_column.index(value)
                # loop through the corresponding row of second table and append values to joined_data
                for column, second_value in enumerate(second_table.data[second_table_row]):
                    joined_data[row].append(second_value)

        # set temporary lists to joined table object and return
        joined.fields = copy.deepcopy(join_fields)
        joined.data = copy.deepcopy(joined_data)

        return joined
