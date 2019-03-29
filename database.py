import table as tbl
import query as qy

class Database:
    def __init__(self):
        self.tables = {}

    def add_table(self, name, file):
        if name in self.tables.keys():
            print("Table '{}' already exists.".format(name))
        else:
            table = tbl.Table(name, file)
            if not table.data:
                print("No table created")
            else:
                self.tables[name] = tbl.Table(name, file)
                print("Added table '{}' from '{}' to the database".format(name, file))

    def delete_table(self, name):
        del self.tables[name]

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

        # TODO: Join

        # tracker to see, which tables are contained in joined super table at the current time
        tables_in_join = []

        # only do joins if where_join is not emtpy, otherwise make copy of queried table
        if not my_query.where_join:
            query_table = tbl.Table(name='query', copy_table=self.tables[my_query.from_[0]])
        else:
            for join in my_query.where_join:
                pass

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
            if not query_table.is_valid_field(column):
                if not query_table.is_valid_field(field):
                    print("Error: One or more field names in the query are invalid")
                    return
                else:
                    select[idx] = field
        # reduce to only selected columns with adjusted selects-list
        query_table.project(select)

        # delete duplicates
        query_table.reduce()

        # print out the resulting table to the console
        query_table.present()
