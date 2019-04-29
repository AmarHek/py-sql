import table as tbl
import query as qy


class Database:
    """
    class to manage a database of tables
    Attributes:
        tables: dictionary with table names as keys and Table objects as values
        query_table: variable to save the most recent queried table
    """

    tables = {}
    query_table = tbl.Table('query_table')

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
                self.tables[name] = table
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
        success = my_query.parse(query_string, self.tables)
        # stop if something is wrong with the query
        if not success:
            return

        # if there are no conditions in where_join, just make a copy of the table in my_query.from_
        if not my_query.where_join:
            self.query_table.copy(self.tables[my_query.from_[0]])
            # since we only select from a pure table, all field names must be un-prefixed
            select = my_query.select
            # convert all table.field selects to just field
            for idx, sel in enumerate(select):
                _, field = sel.split('.')
                select[idx] = field
        # otherwise perform the joins
        else:
            for join_cond in my_query.where_join:
                # split up join_cond
                table1, field1, table2, field2 = join_cond
                # perform the first join
                if my_query.where_join.index(join_cond) == 0:
                    self.query_table.copy(tbl.join(self.tables[table1], field1, self.tables[table2], field2))
                else:
                    self.query_table.copy(tbl.join(self.query_table, table1+'.'+field1, self.tables[table2], field2))
            select = my_query.select

        # remove rows that do not fit the given conditions
        for cond in my_query.where_cond:
            self.query_table.select(cond)

        # reduce to only selected columns with adjusted selects-list
        self.query_table.project(select)

        # delete duplicates
        self.query_table.reduce()
        # print out the resulting table to the console
        self.query_table.present()

    if __name__ == '__main__':
        pass
