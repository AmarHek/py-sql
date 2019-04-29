import unittest
from table import *


class TableTest(unittest.TestCase):

    def testTable(self):
        belegung = Table('belegung')
        self.assertEqual(belegung.name, 'belegung')
        self.assertListEqual(belegung.data, [])
        self.assertListEqual(belegung.fields, [])
        raum = Table('raum')
        self.assertEqual(raum.name, 'raum')

    def testLoad(self):
        fields = ['kuerzel', 'gebaeude', 'groesse']
        data = [['z6_hs4', 'z6', 600], ['z6_hs1', 'z6', 200]]
        raum = Table('raum')
        raum.load_from_csv('raum.csv')
        self.assertListEqual(raum.fields, fields)
        self.assertListEqual(raum.data, data)

        leer = Table('leer')
        leer.load_from_csv('leer.csv')
        self.assertListEqual(leer.fields, [])
        self.assertListEqual(leer.data, [])


if __name__ == "__main__":
    unittest.main()
