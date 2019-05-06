from cmd import Cmd
import database

# TODO: Document classes (what they do etc.)
# TODO: Write out non-simple statements (split, enumerate, dicts, etc.)


class PySQL(Cmd):

    prompt = "> "

    def do_add(self, args):
        """adds a table to the database, table name is derived from the file"""
        files = args.split(',')
        files = [file.strip(' ') for file in files]
        for file in files:
            # TODO: Add automatic name extraction from path
            # works only if file in same directory as of now
            name = file.replace('.csv', '').lower()
            db.add_table(name, file)

    def do_clear(self, args):
        """clears all loaded tables"""
        db.clear()

    def do_show(self, args):
        """prints specified tables to the console"""
        if args == '':
            pass
        else:
            tables = args.lower().split(', ')
            for table in tables:
                db.show_table(table)

    def do_select(self, query):
        """initiates a query"""
        if not db.tables:
            print("Database empty, cannot perform query")
            return
        query = 'select ' + query
        db.perform_query(query)

    def do_tables(self, args):
        """lists the names of all tables in the database"""
        db.list_tables()

    def do_save(self, args):
        """saves the database"""
        db.save_database()

    def do_help(self, arg):
        print('Here is a list of possible commands:')
        print('add [file1], [file2], etc.')
        print('\t  - adds a new table to the database from the given file, table name is the same as the filename')
        print('clear')
        print('\t - deletes all tables from the database.\n')
        print('show [name1], [name2], etc.')
        print('\t - prints the contents of the specified tables\n')
        print('tables')
        print('\t - lists the names of all tables in the database\n')
        print('select')
        print('\t - initiates a query: ')
        print('\t   select ', '[table1].[column1], [table2].[column2] from [table1], [table2] '
                              '(Optional) where [...] And [...] \n')
        print('exit')
        print('\t - exits the program.\n')

    def do_exit(self, args):
        raise SystemExit()

    def do_insert(self, args):
        table, row = args.split('values')
        table = table.replace('into ', '').strip()
        row = row.strip('(').strip(')')
        row = row.split(',')
        db.insert(table, row)


if __name__ == '__main__':
    db = database.Database()

    app = PySQL()
    app.cmdloop("New Database created. Enter a command to do something. "
                "Enter help to see a list of commands with explanations.")

