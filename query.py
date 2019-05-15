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

    def parse(self, query_string, tables):
        """
        parses a query string from the command line and fills out the attributes of the Query object

        Args:
            query_string (str): an SQL-query of the form SELECT ... FROM ... WHERE ...
            tables (Dict): Dictionary/database of tables to assert table names and fields

        Returns:
            bool: False if the query fails due to an error
        """

        # convert all to lowercase first
        query_string = query_string.lower()

        # check keywords
        if not self.check_keywords(query_string):
            print('Keyword Error')
            return False

        # check query syntax
        if not self.build_syntax(query_string):
            print('Syntax Error')
            return False

        if not self.check_database(tables):
            print('Database Error')
            return False

        # reorder join conditions
        if len(self.where_join) > 0:
            if not self.sort_reorder_join():
                # if something went from during reordering, abort query
                return False

        return True

    def check_keywords(self, query_string):
        # Check if at least one where-condition is given
        is_cond = False
        for operator in self.operators:
            if operator in query_string:
                is_cond = True
        # syntax check and abort if something is wrong
        # basic typo check
        if 'select' not in query_string or 'from' not in query_string or \
                (is_cond and (('join' not in query_string or 'on' not in query_string) and 'where' not in query_string)):
            print("Syntax error in query, stopping query")
            return False
        return True

    def build_syntax(self, query_string):
        """
        function to check the query syntax and fill in the attributes of the query object

        Args:
            query_string: the query in question

        Returns:
            bool: False (+ prints error messages) if something went wrong, True if everything is fine
        """

        # Select is removed from the string and split into two halves at 'From'
        select, rest = split_and_strip(query_string, 'from')
        select = select.replace('select', '')
        select = split_and_strip(select, ',')
        # check if every select is of form table.field
        for sel in select:
            if len(sel.split('.')) != 2:
                print('Syntax error in SELECT, stopping query')
                return False
        self.select = select

        # split the rest up depending on keywords
        if 'join' in rest and 'where' in rest:
            rest, where = split_and_strip(rest, 'where')
            rest = split_and_strip(rest, 'join')
            from_ = rest[0]
            joins = rest[1:]
        elif 'join' in rest:
            rest = split_and_strip(rest, 'join')
            from_ = rest[0]
            joins = rest[1:]
            where = ''
        elif 'where' in rest:
            from_, where = rest.split('where')
            joins = ''
        else:
            from_ = rest
            joins = ''
            where = ''

        # fill up from-list
        self.from_ = split_and_strip(from_, ',')

        # fill up join conditions of not empty
        if joins != '':
            for join in joins:
                if (len(join.split('on')) != 2) or (len(join.split('=')) != 2):
                    print('Wrong number of join operator(s), stopping query')
                    return False
                else:
                    # separate table name and actual join condition
                    table, join = split_and_strip(join, 'on')
                    # separate into first and second table.column
                    join = split_and_strip(join, '=')
                    # check if both conditions are of form table.column
                    if (len(join[0].split('.')) != 2) or (len(join[1].split('.')) != 2):
                        print('Syntax error in join conditions, stopping query')
                        return False
                    else:
                        # create list of join condition with order depending on called table
                        if table in join[0]:
                            join_cond = join[0].split('.') + join[1].split('.')
                            self.where_join.append(join_cond)
                        elif table in join[1]:
                            join_cond = join[1].split('.') + join[0].split('.')
                            self.where_join.append(join_cond)
                        else:
                            print('Table name and join condition do not match.')
                            return False

        # fill up where conditions if not empty
        if where != '':
            where = split_and_strip(where, 'and')
            # only fill condition lists if conditions are given in the query
            for cond in where:
                # extract operator:
                operator = ''
                for op in self.operators:
                    if op in cond:
                        operator = op
                if operator == '':
                    print('Syntax error in conditions, stopping query')
                    return False
                cond = split_and_strip(cond, operator)
                # check if the left-side of a condition is of form table.field
                if len(cond[0].split('.')) != 2:
                    print('Syntax error in conditions, stopping query')
                    return False
                # check that right-side strings only come with '=' and no other operator
                if not is_number(cond[1]) and operator != '=':
                    print('Cannot use comparison operators with strings')
                    return False
                # check if value for comparison is float and convert
                elif is_number(cond[1]):
                    cond[1] = float(cond[1])
                self.where_cond.append([cond[0], operator, cond[1]])

        return True

    def check_database(self, tables):
        """
        Function to check if every field and table in the query exists

        Returns:
            bool: False (+ prints error messages) if something is wrong, True otherwise
        """

        # check if every table in from_ exists:
        for name in self.from_:
            if name not in tables.keys():
                print("Table '{}' does not exist.".format(name))
                return False

        # check if every field and table in select exist
        for sel in self.select:
            name, field = sel.split('.')
            if name not in self.from_:
                print("Table '{}' found in select, but not in from.".format(name))
                return False
            elif not tables[name].is_valid_field(field):
                print("Table '{}' does not have the field '{}'.".format(name, field))
                return False

        # check the regular conditions
        if len(self.where_cond) > 0:
            for cond in self.where_cond:
                name, field = cond[0].split('.')
                if name not in tables.keys():
                    print("Table '{}' does not exist.".format(name))
                    return False
                elif not tables[name].is_valid_field(field):
                    print("Table '{}' does not have the field '{}'.".format(name, field))
                    return False

        # check the join conditions
        if len(self.where_join) > 0:
            for cond in self.where_join:
                #if cond[0] not in self.from_:
                #    print("Table '{}' found in conditions, but not in from.".format(cond[0]))
                #    return False
                #elif cond[2] not in self.from_:
                #    print("Table '{}' found in conditions, but not in from.".format(cond[2]))
                #    return False
                if not tables[cond[0]].is_valid_field(cond[1]):
                    print("Table '{}' does not have the field '{}'.".format(cond[0], cond[1]))
                    return False
                elif not tables[cond[2]].is_valid_field(cond[3]):
                    print("Table '{}' does not have the field '{}'.".format(cond[2], cond[3]))
                    return False
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


