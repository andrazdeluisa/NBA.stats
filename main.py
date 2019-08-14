# uvozimo bottle.py
import bottle

# uvozimo podarke za povezavo
import auth_public
import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import hashlib # računanje MD5 kriptografski hash za gesla

from urllib.parse import urlencode

secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"
adminGeslo = "1111"

###############################################

bottle.debug(True)

# Prijave

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def check_user(username, prijavljen):
    return username == prijavljen


@bottle.route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    static_dir = '/Static'
    return bottle.static_file(filename, root=static_dir)

#############################################################################################################

@bottle.route("/")
def main():
    username = get_user()
    return bottle.template("zacetna_stran.html", username=username)

#############################################################################################################

@bottle.get("/prijava/")
def login_get():
    """Serviraj formo za login."""
    return bottle.template("prijava.html",
                           napaka=None,
                           username='')


@bottle.post("/prijava/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    c = baza.cursor()
    c.execute("SELECT 1 FROM uporabnik WHERE username=%s AND password=%s",
              [username, password])
    if c.fetchone() is None:
        # Username in geslo se ne ujemata
        return bottle.template("prijava.html",
                               napaka="Nepravilna prijava",
                               username='')
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie("username", username, secret=secret, path='/')
        # PROBLEM: bottle.redirect zbriše cookie
        bottle.redirect('/')

@bottle.get("/odjava/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('username')
    bottle.redirect('/')
        
    

@bottle.get("/registracija/")
def register_get():
    """Prikaži formo za registracijo."""
    return bottle.template("registracija.html", 
                           username='',
                           napaka=None)

@bottle.post("/registracija/")
def register_post():
    """Registriraj novega uporabnika."""
    username = bottle.request.forms.username
    password1 = bottle.request.forms.password1
    password2 = bottle.request.forms.password2
    # Ali uporabnik že obstaja?
    c = baza.cursor()
    c.execute("SELECT 1 FROM uporabnik WHERE username=%s", [username])
    if c.fetchone():
        # Uporabnik že obstaja
        return bottle.template("registracija.html",
                               username='',
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Gesli se ne ujemata
        return bottle.template("registracija.html",
                               username='',
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        print('tukaj sem')
        c.execute("INSERT INTO uporabnik (username, password) VALUES (%s, %s)",
                  (username, password))
        bottle.redirect("/prijava/")


###############################################


@bottle.get('/ekipe/')
def ekipe_get():
    cur.execute("SELECT ime, zmage, porazi FROM ekipa ORDER BY zmage DESC")
    ekipe = cur.fetchall()
    napaka='napaka'

    return bottle.template('ekipe.html', seznam_ekip=ekipe, username='', napaka=None)

@bottle.post("/ekipe/")
def ekipe_post():
    username=get_user()


@bottle.get('/igralci/')
def igralci_get():
    cur.execute("SELECT ime, pozicija, starost FROM igralec")
    igralci = cur.fetchall()
    napaka='napaka'
    # return bottle.template('ekipe.html', ekipe=ekipe, napaka0=None, napaka=napaka, username=username)
    return bottle.template('igralci.html', seznam_igralcev=igralci, username='', napaka=None)

@bottle.post("/igralci/")
def igralci_post():
    username=get_user()



@bottle.get('/trenerji/')
def trenerji_get():
    cur.execute("SELECT ime, ekipa, zmage, porazi FROM trener")
    trenerji = cur.fetchall()
    napaka='napaka'
    return bottle.template('trenerji.html', seznam_trenerjev = trenerji, username = '', napaka=None)

@bottle.post("/trenerji/")
def trenerji_post():
    username=get_user()

"""

@bottle.get('/lastniki/')
def lastniki_get():
    cur.execute("SELECT ime, ekipa, premozenje FROM lastnik")
    lastniki = cur.fetchall()
    napaka='napaka'
    return bottle.template('lastniki.html', seznam_lastnikov=lastniki, napaka=None)

@bottle.post("/ekipe/")
def lastniki_post():
<style type="text/css">
    body {
        margin: 0px 0px 0px 0px;
        padding: 0px 0px 0px 0px;
        background-image: url('bg.jpg');
    }
    #wrapper {
        width: 80%;
        margin: 60px auto 0px auto;
        padding: 20px 20px 20px 20px;
</style>    username=get_user()

@bottle.get('/uspesni-lastniki/')
def lastniki_get():
    cur.execute("SELECT lastnik.ime, lastnik.premozenje, ekipa.zmage, ekipa.ime as ekipa FROM lastnik JOIN ekipa ON lastnik.ekipa=ekipa.kratica WHERE ekipa.zmage>42 ORDER BY ekipa.zmage desc;")
    lastniki = cur.fetchall()
    napaka='napaka'
    return bottle.template('uspesni-lastniki.html', seznam_lastnikov=lastniki, napaka=None)

@bottle.post("/ekipe/")
def lastniki_post():
    username=get_user()
    
def dodeli_pravice():
    cur.execute("GRANT CONNECT ON DATABASE sem2019_sarabi TO andrazdl; GRANT CONNECT ON DATABASE sem2019_sarabi TO tadejm; GRANT CONNECT ON DATABASE sem2019_sarabi TO javnost;")
    cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO andrazdl; GRANT ALL ON ALL TABLES IN SCHEMA public TO tadejm; GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;")
    baza.commit()
     """

###############################################

# GLAVNI PROGRAM

# priklopimo se na bazo
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na portu 8010, glej http://localhost:8010/
bottle.run(host='localhost', port=8010)
