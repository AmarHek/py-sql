import os
import prettytable as pt
import operator
import copy


def is_number(s):
    """checks if a string can be converted to float"""
    if '_' in s:
        return False
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False


# TODO: Add 'In' functionality
def convert_to_operator(op_string) -> operator:
    """
    Converts a string to an operator

    Args:
        op_string: operator to be converted

    Returns:
        operator: the corresponding operator object
    """
    operator_dict = {'>': operator.gt,
                     '<': operator.lt,
                     '>=': operator.ge,
                     '<=': operator.le,
                     '=': operator.eq,
                     '<>': operator.ne,
                     '!=': operator.ne}
    return operator_dict[op_string]


def join(table1, field1, table2, field2):
    """
    joins two table objects

    Args:
        table1 (Table): first table to be joined
        field1 (str): field of the first table at which to join
        table2 (Table): second table to be joined
        field2 (str): field of the second table at which to join

    Returns:
        joined (Table): the joined super-table
    """

    # joins this table with a specified second table at the given fields and returns the joined super-table
    # extract indexes of given fields
    index1 = table1.index(field1)
    index2 = table2.index(field2)
    # create empty table for joining
    joined = Table('joined')
    # copy fields of table1, but only add prefixes if fields of table1 do not have them, i.e. no '.' present
    if '.' not in table1.fields[0]:
        for field in table1.fields:
            joined.fields.append(table1.name + '.' + field)
    else:
        joined.fields = copy.deepcopy(table1.fields)
    for field in table2.fields:
        joined.fields.append(table2.name + '.' + field)
    # create arrays (= columns) of first and second fields to make things easier below
    first_field_as_column = []
    for row in table1.data:
        first_field_as_column.append(row[index1])
    second_field_as_column = []
    for row in table2.data:
        second_field_as_column.append(row[index2])
    # copy data from first table to temporary list
    joined.data = copy.deepcopy(table1.data)
    # loop through first_field_as_column (= rows of first table)
    for row, value in enumerate(first_field_as_column):
        # omit rows without corresponding value in other table
        # values must be unique in table2, otherwise only first row with the same value is joined
        # TODO: Make non-unique rows joinable
        if value in second_field_as_column:
            # check, where value is the same as in second_field_as_column (= corresponding row in second_table)
            second_table_row = second_field_as_column.index(value)
            # loop through the corresponding row of second table and append values to joined_data
            for column, second_value in enumerate(table2.data[second_table_row]):
                joined.data[row].append(second_value)
    return joined


class Table:
    """creates a simple table and offers some functions for table handling

    Args:
        name (str): the name of the table

    Attributes:
        name (str): the name of the table
        fields (list): a list of all field names of the table, the name of the columns
        data (list): contains all data of the table
                     Each entry is a row of the table, represented by a list
                     order is the same as in fields
    """

    def __init__(self, name):
        self.name = name
        self.fields = []
        self.data = []

    # Kommentar zur load-Funktion: Es ist in größeren Projekten üblicher und sinnvoller, solche allgemeinen Funktionen
    # wie das Laden einer .csv-Datei auf allgemeine Module auszulagern. Da wir es in unserem Programm nur für die
    # Tabellen an wenigen Stellen nutzen, belassen wir es aber bei dieser Implementierung.
    def load_from_csv(self, csv_file, delimiter=';'):
        """
        loads fields and data from a csv-file into a table object

        Args:
            csv_file (str): the path to the file
            delimiter (str): the symbol used to divide each entry on the csv-file, ';' by default

        """
        # reset previous attributes
        self.data = []
        self.fields = []

        if os.path.isfile(csv_file):
            with open(csv_file, 'r', encoding="utf-8-sig") as f:
                for idx, line in enumerate(f):
                    # remove trailing new line, split by delimiter and set to lowercase
                    line = line.rstrip("\n").lower()
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

    def copy(self, original_table):
        """
        copies the fields and data of an existing table into this one

        Args:
            original_table (Table): the table to copy from

        """
        self.fields = copy.deepcopy(original_table.fields)
        self.data = copy.deepcopy(original_table.data)

    def length(self):
        """returns the number of table columns"""
        return len(self.fields)

    def index(self, field_name):
        """ returns the column number of the given field_name
        Args:
            field_name (str): name of the required field
        """
        if self.is_valid_field(field_name):
            index = self.fields.index(field_name)
            return index

    def is_valid_field(self, field):
        """checks if a table has a given field"""
        return field in self.fields

    def present(self):
        """prints the table"""
        pretty = pt.PrettyTable()
        pretty.field_names = self.fields
        for line in self.data:
            pretty.add_row(line)
        print(pretty)

    def project(self, fields_list):
        """
        selects the specified columns of a table and deletes the others, directly alters the table

        Args:
            fields_list (list): all fields that should not be removed
        """
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
        """deletes a column from a table
        Args:
            field (str): name of the column to be deleted
        """
        idx = self.index(field)
        for row in self.data:
            del row[idx]
        del self.fields[idx]

    # deletes all rows from data that do not match condition
    def select(self, cond):
        """
        removes all rows of a table that do not fit the condition
        Args:
            cond (list): condition from which to select rows - a list with three entries: [field, operator, value]
        """
        field = cond[0]
        op = convert_to_operator(cond[1])
        value = cond[2]
        junk_rows = []
        column = self.index(field)
        for idx, row in enumerate(self.data):
            if not op(row[column], value):
                junk_rows.append(row)
        for row in junk_rows:
            self.data.remove(row)

    def reduce(self):
        """deletes all duplicate rows in a table"""

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
