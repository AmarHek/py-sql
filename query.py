# auxiliary function to check if string can be converted to float
def is_number(s):
    if '_' in s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


# splits a string with the splitter and removes spaces
def split_and_strip(expr, splitter):
    expr = expr.split(splitter)
    expr = [a.strip(' ') for a in expr]
    return expr

# TODO: add unit tests


class Query:

    operators = ['=', '<', '>', '<=', '>=', '<>', '!=']

    def __init__(self):
        # generate an empty instance of a query
        self.select = []
        self.from_ = []
        self.where = []
        self.where_join = []
        self.where_cond = []

    def parse(self, cmd_query):
        # interpret command line string correctly and fill query attributes
        # generate list of fields to select from
        # All caps, all lowercase and only first uppercase are valid syntax
        # , but all caps and lowercase are converted first
        cmd_query = cmd_query.replace('SELECT', 'Select').replace('select', 'Select')\
            .replace('FROM', 'From').replace('from', 'From')\
            .replace('WHERE', 'Where').replace('where', 'Where')\
            .replace('AND', 'And').replace('and', 'And')

        # Check if at least one where-condition is given
        iswhere = False
        for operator in self.operators:
            if operator in cmd_query:
                iswhere = True

        # syntax check and abort if something is wrong
        if 'Select' not in cmd_query or 'From' not in cmd_query or (iswhere and 'Where' not in cmd_query):
            print("Syntax error in query, stopping query")
            return False

        # Select is removed from the string and split into two halves at 'From'
        select, rest = cmd_query.split('From')
        select = split_and_strip(select, 'Select')
        # check if every element of select has the format 'table.field'
        if sum(['.' not in sel for sel in select]) > 0:
            print("One or more selects are not of the format 'table.field', stopping query")
            return False

        # Fill out from and fill where if conditions are given
        if iswhere:
            from_, where = rest.split('Where')
            from_ = split_and_strip(from_, ',')
            where = split_and_strip(where, 'And')
        else:
            from_ = split_and_strip(rest, ',')
            where = []

        where_join = []
        where_cond = []
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
                    where_join.append(cond[0].split('.') + cond[1].split('.'))
                # otherwise is regular condition and split into table.column, operator and value
                else:
                    # check if value for comparison is float and convert
                    if is_number(cond[1]):
                        cond[1] = float(cond[1])
                    where_cond.append([cond[0], operator, cond[1]])

        # finally assign temporary variables to query attributes
        self.select = select
        self.from_ = from_
        self.where = where
        self.where_join = where_join
        # reorder join conditions
        if len(where_join) > 0:
            success = self.sort_reorder_join()
            # if something went from during reordering, abort query
            if not success:
                return False
        self.where_cond = where_cond
        return True

    def sort_reorder_join(self):

        def reorder_join_element(table_order, join_element):
            # reorders a join-condition-list to fit the given table order
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
        if len(rest) != 0:
            print('Unsorted join conditions left, something went wrong, stopping query')
            return False
        self.where_join = join_list


