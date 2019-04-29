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
        """
        # create an empty query
        my_query = qy.Query()
        # parse the input string to the query and check if there were any errors
        success = my_query.parse(query_string, self.tables)
        if not success:
            return
        self.answer_query(my_query)

    def answer_query(self, my_query):
        """builds the final answer table from a given query
        Args:
            my_query (Query): Query object with filled attributes
        """
        # create a temporary table from join conditions
        self.build_query_table(my_query)
        # remove rows that do not fit the given conditions
        for cond in my_query.where_cond:
            self.query_table.select(cond)
        # reduce to only selected columns with adjusted selects-list
        self.query_table.project(my_query.select)
        # delete duplicates
        self.query_table.reduce()
        # print out the resulting table to the console
        self.query_table.present()

    def build_query_table(self, my_query):
        """builds a temporary super-table from join conditions
        Args:
            my_query (Query):
        """
        # if there are no conditions in where_join, just make a copy of the table in my_query.from_
        # and change field names
        if not my_query.where_join:
            requested_table = self.tables[my_query.from_[0]]
            self.query_table.copy(requested_table)
            # adjust the field names to convention
            for i in range(self.query_table.length()):
                self.query_table.fields[i] = requested_table.name + self.query_table.fields[i]
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

    if __name__ == '__main__':
        pass
