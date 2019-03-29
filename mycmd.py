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

    def do_tables(self, arg):
        # lists the names of all tables in the database
        db.list_tables()

    def do_help(self, arg):
        print('...')

    def do_exit(self, args):
        raise SystemExit()


if __name__ == '__main__':
    db = database.Database()

    app = MyCmd()
    app.cmdloop("New Database created. Enter a command to do something, "
                "e.g. 'add [table name] [csv-file], [table name] [csv-file], etc.'.")

