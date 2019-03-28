import operator


# auxiliary function to check if string can be converted to float
def is_number(s):
    if '_' in s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

# TODO: add unit tests


class Query:

    def __init__(self):
        # generate an empty instance of a query
        self.select = []
        self.from_ = []
        self.where = []
        self.where_join = []
        self.where_cond = []

    def parse(self, cmd_query):
        # interpret command line string correctly and fill query attributes
        # TODO: Add check for valid query syntax
        # generate list of fields to select from
        select, rest = cmd_query.split(' From ')
        select = select.replace('Select ', '').split(', ')

        # check if query contains where conditions and generate where and from accordingly
        if 'Where' in rest:
            from_, where = rest.split(' Where ')
            from_ = from_.split(', ')
            where = where.split(' And ')
        else:
            # blank space at the end of from must be removed first
            from_ = rest[:-1].split(', ')
            where = []
        # only fill condition lists if conditions are given in the query
        where_join = []
        where_cond = []
        if len(where) > 0:
            for cond in where:
                cond = cond.split(' ')
                # join condition if first and last argument contain '.' (table.field) and if operator is '='
                if ('.' in cond[0]) and ('.' in cond[2]) and (cond[1] == '='):
                    where_join.append(cond[0].split('.') + cond[2].split('.'))
                # else is regular condition and is split into table.column, operator and value
                else:
                    # check if value for comparison is float and convert
                    if is_number(cond[2]):
                        cond[2] = float(cond[2])
                    where_cond.append(cond)

        # finally assign temporary variables to query attributes
        self.select = select
        self.from_ = from_
        self.where = where
        self.where_join = where_join
        self.sort_reorder_join()
        self.where_cond = where_cond

    def sort_reorder_join(self):

        def reorder_join_element(table_order, join_element):
            index1 = table_order.index(join_element[0])
            index2 = table_order.index(join_element[2])
            if index1 < index2:
                return join_element
            else:
                return [join_element[2], join_element[3], join_element[0], join_element[1]]

        join_list = self.where_join
        result = [join_list[0]]
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
        if len(rest) != 0:
            raise Exception('Unsorted join conditions left, something went wrong')
        self.where_join = join_list
