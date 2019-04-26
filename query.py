from database import *
from table import is_number


def split_and_strip(expr, splitter):
    """splits a string with the given splitter and removes blank spaces in front or end of the elements
    Args:
        expr (str): expression to be split
        splitter (str): character at which to split expr into a list
    Returns:
        expr (list): the initial expression divided into a list
    """
    expr = expr.split(splitter)
    expr = [a.strip(' ') for a in expr]
    return expr

# TODO: add unit tests


class Query:
    """
    a class designed to parse an input query into several lists to create the queried table in later operations

    Attributes:

        select: list of fields to be selected in format table.field
        from_: list of tables from which to select
        where_join: list of join conditions
        where_cond: list of all remaining conditions
    """

    operators = ['=', '<', '>', '<=', '>=', '<>', '!=']

    def __init__(self):
        """generates an empty instance of a query"""
        self.select = []
        self.from_ = []
        self.where_join = []
        self.where_cond = []

    def parse(self, cmd_query):
        """
        parses a query string from the command line and fills out the attributes of the Query object

        Args:
            cmd_query (str): an SQL-query of the form SELECT ... FROM ... WHERE ...

        Returns:
            bool: False if the query fails due to an error
        """

        # convert all to lowercase first
        cmd_query = cmd_query.lower()

        # check query syntax
        if not self.check_query_syntax(cmd_query):
            return False

        # Select is removed from the string and split into two halves at 'From'
        select, rest = cmd_query.split('from')
        select = split_and_strip(select, 'select')

        # Fill out from and fill where if conditions are given
        if 'where' in rest:
            from_, where = rest.split('where')
            from_ = split_and_strip(from_, ',')
            where = split_and_strip(where, 'and')
        else:
            from_ = split_and_strip(rest, ',')
            where = []

        # only fill condition lists if conditions are given in the query
        if len(where) > 0:
            for cond in where:
                # extract operator:
                operator = ''
                for op in self.operators:
                    if op in cond:
                        operator = op
                cond = split_and_strip(cond, operator)
                # join condition if first and last argument contain '.' (table.field) and if operator is '='
                if ('.' in cond[0]) and ('.' in cond[2]) and (operator == '='):
                    self.where_join.append(cond[0].split('.') + cond[1].split('.'))
                # otherwise is regular condition and split into table.column, operator and value
                else:
                    # check if value for comparison is float and convert
                    if is_number(cond[1]):
                        cond[1] = float(cond[1])
                    self.where_cond.append([cond[0], operator, cond[1]])

        # assign temporaries to attributes
        self.select = select
        self.from_ = from_

        # reorder join conditions
        if len(self.where_join) > 0:
            success = self.sort_reorder_join()
            # if something went from during reordering, abort query
            if not success:
                return False
        return True

    def check_query_syntax(self, query_string):
        """
        function to check the query syntax and if all requested tables and fields exist

        Args:
            query_string: the query in question

        Returns:
            bool: False (+ prints error messages) if something went wrong, True if everything is fine
        """

        # Check if at least one where-condition is given
        is_where = False
        for operator in self.operators:
            if operator in query_string:
                is_where = True

        # syntax check and abort if something is wrong
        if 'select' not in query_string or 'from' not in query_string or (is_where and 'where' not in query_string):
            print("Syntax error in query, stopping query")
            return False

        select, _ = query_string.split('from')

        # check if every element of select has the format 'table.field'
        if sum(['.' not in sel for sel in select]) > 0:
            print("One or more selects are not of the format 'table.field', stopping query")
            return False
        # check if every field and table exist
        for sel in select:
            name, field = sel.split('.')
            if name not in Database.tables.keys():
                print("Table '{}' does not exist").format(name)
                return False
            elif not Database.tables[name].is_valid_field(field):
                print("Table '{}' does not have the field '{}").format(name, field)
                return False
            else:
                return True

    def sort_reorder_join(self):
        """reorders the conditions in self.where_join so that the tables are joined in a set order"""

        def reorder_join_element(table_order, join_element):
            """
            reorders a join-condition-list to fit the given table order

            Args:
                table_order (list): hierarchy of the tables
                join_element (list): a single, unordered join condition
            """
            index1 = table_order.index(join_element[0])
            index2 = table_order.index(join_element[2])
            if index1 < index2:
                return join_element
            else:
                # [table1, field1, table2, field2]
                return [join_element[2], join_element[3], join_element[0], join_element[1]]

        join_list = self.where_join
        # Result is the ordered list of join-conditions
        result = [join_list[0]]
        # The list tables dictates the order in which the tables are joined together. The first two tables are
        # chosen as an arbitrary base
        tables = [join_list[0][0], join_list[0][2]]
        rest = join_list[1:]
        for i in range(len(join_list)):
            for elem in rest:
                if elem[0] in tables:
                    if not elem[2] in tables:
                        tables.append(elem[2])
                    elem_ordered = reorder_join_element(tables, elem)
                    result.append(elem_ordered)
                    rest.remove(elem)
                elif elem[2] in tables:
                    if not elem[0] in tables:
                        tables.append(elem[0])
                    elem_ordered = reorder_join_element(tables, elem)
                    result.append(elem_ordered)
                    rest.remove(elem)
                else:
                    print('The given conditions create more than one query-table, stopping query')
                    return False
        self.where_join = join_list
        return True


