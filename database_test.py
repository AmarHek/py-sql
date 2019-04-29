import unittest
from database import *
import table as tbl
import os


class DatabaseTest(unittest.TestCase):

    def testDatabase(self):
        db = Database()
        keys = db.tables.keys()
        self.assertEqual(not keys, True)
        self.assertEqual(db.query_table.name, 'query_table')
        self.assertListEqual(db.query_table.fields, [])
        self.assertListEqual(db.query_table.data, [])

    def testAddTable(self):
        db = Database()
        db.add_table('raum', 'raum.csv')
        self.assertEqual(len(db.tables.keys()), 1)
        raum = tbl.Table('raum')
        raum.load_from_csv('raum.csv')
        self.assertEqual(db.tables['raum'].name, raum.name)
        self.assertListEqual(db.tables['raum'].fields, raum.fields)
        self.assertListEqual(db.tables['raum'].data, raum.data)

        db.add_table('belegung', 'belegung.csv')
        self.assertEqual(len(db.tables.keys()), 2)

    def testPerformQuery(self):



if __name__ == "__main__":
    unittest.main()