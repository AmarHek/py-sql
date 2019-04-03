from cmd import Cmd
import database


class MyCmd(Cmd):

    prompt = "> "

    def do_add(self, args):
        # adds the specified tables and files to the database
        tables = args.split(', ')
        for table in tables:
            nameandfile = table.split(' ')
            if len(nameandfile) == 2:
                name, file = nameandfile
                db.add_table(name, file)
            else:
                print("Wrong syntax, failed creating table")

    def do_del(self, args):
        # delete the specified tables, separated by commas
        tables = args.split(', ')
        for table in tables:
            db.delete_table(table)
            print("Deleted table '{}' from the database".format(table))

    def do_show(self, args):
        if args == '':
            pass
        else:
            # presents the tables specified in args
            tables = args.split(', ')
            for table in tables:
                db.show_table(table)

    def do_Select(self, query):
        db.perform_query(query)

    def do_SELECT(self, query):
        db.perform_query(query)

    def do_select(self, query):
        db.perform_query(query)

    def do_tables(self, args):
        # lists the names of all tables in the database
        db.list_tables()

    def do_save(self, args):
        db.save_database()

    def do_help(self, arg):
        print('Here is a list of possible commands:')
        print('add [name1] [file1], [name2] [file2], etc.')
        print('\t  - adds a new table with to the database with the given name(s) (must be unique),')
        print('\t    where the data is loaded from the given file(s).')
        print('del [name1], [name2], etc.')
        print('\t - deletes the specified tables from the database.')
        print('show [name1], [name2], etc.')
        print('\t - prints the contents of the specified tables')
        print('tables')
        print('\t - lists the names of all tables in the database')
        print('Select/SELECT/select')
        print('\t - initiates an SQL-style query')
        print('exit')
        print('\t - exits the program.')

    def do_exit(self, args):
        raise SystemExit()


if __name__ == '__main__':
    db = database.Database()

    app = MyCmd()
    app.cmdloop("New Database created. Enter a command to do something. "
                "Enter help to see a list of commands with explanations.")

