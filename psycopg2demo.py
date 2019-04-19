#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Osnovna uporaba psycopg2
========================

Uporaba je prakticno enaka uporabi SQLite-a; bistveno drugacna je le
inicializacija, opisana spodaj.
"""

# Podobno kot bi se priklopili na sqlite:
#   import sqlite3
#   cur = sqlite3.connect('imenik.db', isolation_level=None)
# se priklopimo tudi na postgres (le da bolj na dolgo vklopimo se nekaj prakticnih razsiritev):

import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database='banka', host='audrey.fmf.uni-lj.si', user='student', password='telebajsek')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# Nadaljni ukazi so enaki ne glede na to, ali "cur" prihaja iz sqlite ali psycopg2 knjiznice:

# Preberi vse osebe ...
cur.execute("SELECT * FROM oseba")
# ... in za vsako vrstico iz tabele izpisi vrednost stolpcev ime in priimek
print('Imena vseh komitentov:')
for vrstica in cur:
  print("%s %s" % (vrstica['ime'], vrstica['priimek']))
  
# POZOR! Majhna razlika je le v nacinu posredovanja parametrov.
# V SQLite prostor za parametre oznacimo z "?":
#  cur.execute("SELECT * FROM transakcija WHERE znesek > ?", [x])
# V psycopg jih oznacimo z "%s", vendar potem NE uporabimo operatorja "%". 
#  cur.execute("SELECT * FROM transakcija WHERE znesek > %s" % [x])  # NAROBE!
x = 10000
cur.execute("SELECT * FROM transakcija WHERE znesek > %s", [x])  # Pravilno
print('\nPodatki o transakcijah nad %d evri:' % x)
for vrstica in cur:
  print(vrstica)