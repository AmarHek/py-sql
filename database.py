import table as tbl
import query as qy


class Database:
    """
    module to manage several tables
    Attributes:
        tables: dictionary with table names as keys and Table objects as values
        query_table: variable to save the most recent queried table
    """

    tables = {}
    query_table = tbl.Table('Query Table')

    def add_table(self, name: str, file: str):
        """adds a new table to the database

        Args:
            name (str): name of the table
            file (str): path to the file

        Returns:
            Nothing if an error occurs
        """
        if name in self.tables.keys():
            print("Table '{}' already exists.".format(name))
        else:
            table = tbl.Table(name)
            table.load_from_csv(file)
            if not table.data:
                return
            else:
                tables[name] = table
                print("Added table '{}' from '{}' to the database".format(name, file))

    def clear(self):
        """deletes all existing tables from the database"""
        self.tables = {}
        self.query_table = tbl.Table('Query Table')

    # TODO: Add save
    def save_database(self):
        pass

    def show_table(self, name: str):
        """
        prints a table from the database
        Args:
            name (str): name of the table
        """
        if name in self.tables.keys():
            self.tables[name].present()

    def list_tables(self):
        """prints the names of all tables in the database"""
        tables = list(self.tables.keys())
        if not tables:
            print('Database is empty')
        else:
            for name in tables:
                print(name)

    def perform_query(self, query_string):
        """parses a given query and prints the resulting table to the console

        Args:
            query_string: an SQL-query of the form SELECT ... FROM ... WHERE ...

        Returns:
            Nothing if an error occurs
        """

        if not self.tables:
            print("Database empty, cannot perform query")
            return
        # parse the query
        my_query = qy.Query()
        success = my_query.parse(query_string)
        # stop if something is wrong with the query
        if not success:
            return

        # if there are no conditions in where_join, just make a copy of the table in my_query.from_
        if not my_query.where_join:
            self.query_table.copy(self.tables[my_query.from_[0]])
        # otherwise perform the joins
        else:
            for join_cond in my_query.where_join:
                # split up join_cond
                table1, field1, table2, field2 = join_cond
                # make a copy of the very first join-table
                if my_query.where_join.index(join_cond) == 0:
                    self.query_table.copy(self.tables[table1])
                self.query_table = tbl.join(self.query_table, table1+field1, self.tables[table2], field2)
                # If something went wrong during join, abort query
                if not self.query_table:
                    return
        # remove rows that do not fit the given conditions
        for cond in my_query.where_cond:
            _, field = cond[0].split('.')
            self.query_table.select(cond)
        # first adjust field names in select-list to field names in table like before
        select = my_query.select
        # TODO: Add check for join select or regular select
        for idx, column in enumerate(select):
            table, field = column.split('.')
            # check if 'table.field' is valid. if not, check if just the field is valid
            if query_table.is_valid_field(column):
                select[idx] = column
            else:
                select[idx] = field
        # reduce to only selected columns with adjusted selects-list
        self.query_table.project(select)
        # delete duplicates
        self.query_table.reduce()
        # print out the resulting table to the console
        self.query_table.present()

    if __name__ == '__main__':
        pass
