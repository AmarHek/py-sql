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

    def testInsert(self):
        raum = Table('raum')
        raum.load_from_csv('raum.csv')
        raum2 = Table('raum2')
        raum2.copy(raum)
        # row too short / false length
        row = ['info_turing', 'turing']
        self.assertFalse(raum.insert(row))
        # false data type in first entry
        row = ['500', 'turing', 500]
        self.assertFalse(raum.insert(row))
        # should return True if successful
        row = ['info_turing', 'turing', 500]
        self.assertTrue(raum.insert(row))
        # last data entry must be row
        self.assertListEqual(raum.data[-1], row)
        # data length must increase by one
        self.assertEqual(len(raum.data), len(raum2.data)+1)
        # row length must stay the same
        self.assertEqual(len(raum.data[0]), len(raum2.data[0]))
        # previous data must stay the same
        self.assertListEqual(raum2.data, raum.data[:-1])
        # successful test
        row = ['info_zuse', 'zuse', '500']
        self.assertTrue(raum.insert(row))


if __name__ == "__main__":
    unittest.main()
