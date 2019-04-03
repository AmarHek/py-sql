import table as tbl
import query as qy


class Database:
    def __init__(self):
        self.tables = {}

    def add_table(self, name, file):
        if name in self.tables.keys():
            print("Table '{}' already exists.".format(name))
        else:
            table = tbl.Table(name)
            table.load_from_csv(file)
            if not table.data:
                print("No table created")
            else:
                self.tables[name] = table
                print("Added table '{}' from '{}' to the database".format(name, file))

    def delete_table(self, name):
        # TODO: Check for need of deleting table object
        del self.tables[name]

    # TODO: Add save
    def save_database(self):
        pass

    def show_table(self, name):
        if name in self.tables.keys():
            self.tables[name].present()

    def list_tables(self):
        tables = list(self.tables.keys())
        output = ''
        if not tables:
            output = 'Database is empty'
        else:
            for idx, name in enumerate(tables):
                if idx == 0:
                    output += name
                else:
                    output += ', ' + name
        print(output)

    def perform_query(self, query_string):
        # parse the query
        my_query = qy.Query()
        my_query.parse(query_string)

        # check if all required tables are in our database
        for tables in my_query.from_:
            if tables not in self.tables.keys():
                print("Error: One or more of the queried tables do not exist in your database")
                return

        # Create instance of query_table
        query_table = tbl.Table('query')

        # tracker to see, which tables are contained in joined super table at the current time
        joined_tables = []

        # only do joins if where_join is not emtpy, otherwise make copy of queried table
        if not my_query.where_join:
            query_table.copy(self.tables[my_query.from_[0]])
        else:
            for join_cond in my_query.where_join:
                table1, field1, table2, field2 = join_cond
                # make a copy of the very first join-table
                if not joined_tables:
                    query_table.copy(self.tables[table1])
                # if the requested first field is not in our joined super table, then it most likely
                # got prefixed with its table name from a previous loop
                # in that case, add the table name as a prefix
                if not query_table.is_valid_field(field1):
                    field1 = table1 + '.' + field1
                query_table = query_table.join(field1, self.tables[table2], field2)
                joined_tables.extend([table1, table2])

        # filter rows that do not fit conditions
        for cond in my_query.where_cond:
            # adjust field names in cond to field names in table
            table, field = cond[0].split('.')
            if not query_table.is_valid_field(cond[0]):
                if not query_table.is_valid_field(field):
                    print("Error: One or more field names in the query are invalid")
                    return
                else:
                    cond[0] = field
            query_table.select(cond)

        # first adjust field names in select-list to field names in table like before
        select = my_query.select
        for idx, column in enumerate(select):
            table, field = column.split('.')
            # check if 'table.field' is valid. if not, check if just the field is valid
            if query_table.is_valid_field(column):
                select[idx] = column
            elif query_table.is_valid_field(field):
                select[idx] = field
            else:
                print("Error: One or more field names in the query are invalid")
                return
        # reduce to only selected columns with adjusted selects-list
        query_table.project(select)

        # delete duplicates
        query_table.reduce()

        # print out the resulting table to the console
        query_table.present()
