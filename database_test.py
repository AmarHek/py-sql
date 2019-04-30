import unittest
from database import *
import table as tbl


class DatabaseTest(unittest.TestCase):

    def testDatabase(self):
        db = Database()
        db.clear()
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
        db = Database()
        db.add_table('raum', 'raum.csv')
        db.add_table('belegung', 'belegung.csv')
        db.add_table('veranstaltung', 'veranstaltung.csv')
        query = "SELECT belegung.raum, belegung.uhrzeit, raum.gebaeude, raum.groesse, veranstaltung.modul" \
                "FROM belegung, raum, veranstaltung " \
                "WHERE belegung.raum = raum.kuerzel" \
                "AND belegung.semester = veranstaltung.semester" \
                "AND veranstaltung.modul = swt"
        fields = ['belegung.raum', 'belegung.uhrzeit', 'raum.gebaeude', 'raum.groesse', 'veranstaltung.modul']
        data = [['z6_hs4', '10_12', 'z6', 600, 'swt'], ['z6_hs4', '8_10', 'z6', 600, 'swt']]
        db.perform_query(query)
        self.assertEqual(db.query_table.name, 'query_table')
        self.assertListEqual(db.query_table.fields, fields)
        self.assertListEqual(db.query_table.data, data)

    def testAnswerQuery(self):
        pass

    def testBuildQueryTable(self):
        pass


if __name__ == "__main__":
    unittest.main()
