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
        query = "select table1.field1 from table1 where table1.field1 < 10"
        self.assertEqual(myquery.check_keywords(query), True)
        query = 'select table1.field1 from table1 whr table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'select table1.field1 fRm table1 where table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'slct table1.field1 from table1 where table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)
        query = 'slct table1.field1 from table1 table1.field1 < 10'
        self.assertEqual(myquery.check_keywords(query), False)

    def testBuildSyntax(self):
        myquery = Query()
        query = "select table1, table2.field2 from table1, table2"
        self.assertEqual(myquery.build_syntax(query), False)
        query = "select table1.field1, table2.field2 from table1, table2 where table1.field1 < jung"
        self.assertEqual(myquery.build_syntax(query), False)
        query = "select table1.field1, table2.field2 " \
                "from table1, table2 " \
                "where table1.field1 = table2.field2" \
                "and table1.field1 = z6" \
                "and table2.field2 < 10"
        self.assertEqual(myquery.build_syntax(query), True)
        self.assertListEqual(myquery.select, ['table1.field1'])

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
        query = "select table1.field1, table2.field2 " \
                "from table1, table2 " \
                "where table1.field1 = table2.field2" \
                "and table1.field1 > 20"
        myquery.parse(query)


if __name__ == "__main__":
    unittest.main()