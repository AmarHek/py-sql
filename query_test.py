import unittest
from query import *
import database as db


class QueryTest(unittest.TestCase):

    def testQuery(self):
        operators = ['=', '<', '>', '<=', '>=', '<>', '!=']
        myquery = Query()
        self.assertListEqual(myquery.select, [])
        self.assertListEqual(myquery.from_, [])
        self.assertListEqual(myquery.where_join, [])
        self.assertListEqual(myquery.where_cond, [])
        self.assertListEqual(myquery.operators, operators)

    def testCheckKeywords(self):
        myquery = Query()
        query = "select table1.field1 from table1"
        self.assertEqual(myquery.check_keywords(query), True)
        query = "select table1.field1 from table1 where table1.field1 = 10"
        self.assertEqual(myquery.check_keywords(query), True)
        query = 'select table1.field1 from table1 whr table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'select table1.field1 fRm table1 where table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'slct table1.field1 from table1 where table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'slct table1.field1 from table1 table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'select table1.field1, table2.field2 from table1, table2 join table1 on table1.field1 = table2.field2'
        self.assertEqual(myquery.check_keywords(query), True)
        query = 'select table1.field1, table2.field2 from table1, table2 join table1 on table1.field1 = table2.field2' \
                'where table1.field1 > 2'
        self.assertEqual(myquery.check_keywords(query), True)

    def testCheckDatabase(self):
        myquery = Query()
        data = db.Database()
        data.add_table('raum', 'raum.csv')
        data.add_table('belegung', 'belegung.csv')
        query = 'select raum.kuerzel, belegung.kuerzel from raum, belegung where raum.kuerzel = belegung.raum'
        myquery.build_syntax(query)
        self.assertEqual(myquery.check_database(data.tables), True)
        query = 'select raum.kuerzel, belegung.kuerzel from rum, belegung where raum.kuerzel = belegung.raum'
        myquery.build_syntax(query)
        self.assertEqual(myquery.check_database(data.tables), False)
        query = 'select raum.kuerzel, belegung.kuerzel from raum, belegung where raum.raum = belegung.raum'
        myquery.build_syntax(query)
        self.assertEqual(myquery.check_database(data.tables), False)
        query = 'select raum.raum, belegung.kuerzel from raum, belegung where raum.kuerzel = belegung.raum'
        myquery.build_syntax(query)
        self.assertEqual(myquery.check_database(data.tables), False)

    def testParse(self):
        myquery = Query()
        data = db.Database()
        data.add_table('raum', 'raum.csv')
        data.add_table('belegung', 'belegung.csv')
        query = "select raum.kuerzel, belegung.kuerzel " \
                "from raum, belegung " \
                "where raum.kuerzel = belegung.raum" \
                "and raum.groesse > 300"
        self.assertEqual(myquery.parse(query, data.tables), True)

    def testBuildSyntax(self):
        myquery = Query()
        query = "select table1, table2.field2 from table1, table2"
        self.assertEqual(myquery.build_syntax(query), False)
        query = "select table1.field1, table2.field2 from table1, table2" \
                "where table1 = 300"
        self.assertEqual(myquery.build_syntax(query), False)
        query = "select table1.field1, table2.field2 from table1, table2 where table1.field1 < jung"
        self.assertEqual(myquery.build_syntax(query), False)

        query = "select table1.field1, table2.field2, table3.field3 " \
                "from table1, table2, table3 " \
                "join table1 on table1.field1 = table2.field2" \
                "join table2 on table3.field3 = table2.field2" \
                "where table1.field1 = z6" \
                "and table2.field2 < 10" \
                "and table3.field3 = 50"
        self.assertEqual(myquery.build_syntax(query), True)
        self.assertListEqual(myquery.select, ['table1.field1', 'table2.field2', 'table3.field3'])
        self.assertListEqual(myquery.from_, ['table1', 'table2', 'table3'])
        self.assertListEqual(myquery.where_cond, [['table1.field1', '=', 'z6'], ['table2.field2', '<', 10],
                                                  ['table3.field3', '=', 50]])
        self.assertListEqual(myquery.where_join, [['table1', 'field1', 'table2', 'field2'],
                                                  ['table2', 'field2', 'table3', 'field3']])

        myquery = Query()
        query = "select table1.field1, table2.field2, table3.field3 " \
                "from table1, table2, table3 " \
                "join table1 on table1.field1 = table2.field2" \
                "join table2 on table3.field3 = table2.field2"
        self.assertEqual(myquery.build_syntax(query), True)
        self.assertListEqual(myquery.select, ['table1.field1', 'table2.field2', 'table3.field3'])
        self.assertListEqual(myquery.from_, ['table1', 'table2', 'table3'])
        self.assertListEqual(myquery.where_join, [['table1', 'field1', 'table2', 'field2'],
                                                  ['table2', 'field2', 'table3', 'field3']])

        myquery = Query()
        query = "select table1.field1, table2.field2, table3.field3 " \
                "from table1, table2, table3 " \
                "where table1.field1 = z6" \
                "and table2.field2 < 10" \
                "and table3.field3 = 50"
        self.assertEqual(myquery.build_syntax(query), True)
        self.assertListEqual(myquery.select, ['table1.field1', 'table2.field2', 'table3.field3'])
        self.assertListEqual(myquery.from_, ['table1', 'table2', 'table3'])
        self.assertListEqual(myquery.where_cond, [['table1.field1', '=', 'z6'], ['table2.field2', '<', 10],
                                                  ['table3.field3', '=', 50]])


if __name__ == "__main__":
    unittest.main()

