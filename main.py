# uvozimo bottle.py
import bottle

# uvozimo podarke za povezavo
import auth_public
import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import hashlib # računanje MD5 kriptografski hash za gesla


secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"
adminGeslo = "1111"

###############################################

# Prijave

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def get_user(auto_login = True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        c = baza.cursor()
        c.execute("SELECT username, ime FROM uporabnik WHERE username=%s",
                  [username])
        r = c.fetchone()
        c.close ()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
    # Če pridemo do sem, uporabnik ni http://localhost:8010/prijavljen, naredimo redirect
    if auto_login:
        bottle.redirect('/login/')
    else:
        return None


@bottle.route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return bottle.static_file(filename, root=static_dir)

#############################################################################################################

@bottle.route("/")
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
    (username, ime) = get_user()
    # Morebitno sporočilo za uporabnika
    sporocilo = get_sporocilo()
    dodeli_pravice()
    # Seznam zadnjih 10 tračev
    ts = traci()
    # Vrnemo predlogo za glavno stran
    return bottle.template("main.html",
                           ime=ime,
                           username=username,
                           traci=ts,
                           sporocilo=sporocilo)

#############################################################################################################

@bottle.get("/login/")
def login_get():
    """Serviraj formo za login."""
    return bottle.template("login.html",
                           napaka=None,
                           username='')

@bottle.get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('username')
    bottle.redirect('/login/')

@bottle.post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    c = baza.cursor()
    c.execute("SELECT 1 FROM uporabnik WHERE username=? AND password=?",
              [username, password])
    if c.fetchone() is None:
        # Username in geslo se ne ujemata
        return bottle.template("login.html",
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/")

@bottle.get("/register/")
def register_get():
    """Prikaži formo za registracijo."""
    return bottle.template("register.html", 
                           username='',
                           ime=None,
                           napaka=None)

@bottle.post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    username = bottle.request.forms.username
    ime = bottle.request.forms.ime
    password1 = bottle.request.forms.password1
    password2 = bottle.request.forms.password2
    # Ali uporabnik že obstaja?
    c = baza.cursor()
    c.execute("SELECT 1 FROM uporabnik WHERE username=%s", [username])
    if c.fetchone():
        # Uporabnik že obstaja
        return bottle.template("register.html",
                               username=username,
                               ime=ime,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return bottle.template("register.html",
                               username=username,
                               ime=ime,
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        print('tukaj sem')
        c.execute("INSERT INTO uporabnik (username, ime, password) VALUES (%s, %s, %s)",
                  (username, ime, password))
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/")


###############################################

@bottle.get('/ekipe/')
def ekipe_get():
    cur.execute("SELECT ime, zmage, porazi FROM ekipa ORDER BY zmage DESC")
    ekipe = cur.fetchall()
    napaka='napaka'

    return bottle.template('ekipe.html', seznam_ekip= ekipe, napaka=None)

@bottle.post("/ekipe/")
def ekipe_post():
    username=get_user()

@bottle.get('/igralci/')
def igralci_get():
    cur.execute("SELECT ime, pozicija, starost FROM igralec")
    igralci = cur.fetchall()
    napaka='napaka'
    # return bottle.template('ekipe.html', ekipe=ekipe, napaka0=None, napaka=napaka, username=username)
    return bottle.template('igralci.html', seznam_igralcev=igralci, napaka=None)

@bottle.post("/igralci/")
def igralci_post():
    username=get_user()

@bottle.get('/trenerji/')
def trenerji_get():
    cur.execute("SELECT ime, ekipa, zmage, porazi FROM trener")
    trenerji = cur.fetchall()
    napaka='napaka'
    return bottle.template('trenerji.html', seznam_trenerjev = trenerji, napaka=None)

@bottle.post("/ekipe/")
def trenerji_post():
    username=get_user()

@bottle.get('/lastniki/')
def lastniki_get():
    cur.execute("SELECT ime, ekipa, premozenje FROM lastnik")
    lastniki = cur.fetchall()
    napaka='napaka'
    return bottle.template('lastniki.html', seznam_lastnikov=lastniki, napaka=None)

@bottle.post("/ekipe/")
def lastniki_post():
    username=get_user()

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
    

###############################################

# GLAVNI PROGRAM

# priklopimo se na bazo
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na portu 8010, glej http://localhost:8010/
bottle.run(host='localhost', port=8010)
