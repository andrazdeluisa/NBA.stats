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


# Funkcija, ki v cookie spravi sporocilo
def set_sporocilo(tip, vsebina):
    bottle.response.set_cookie('message', (tip, vsebina), path='/', secret=secret)

# Funkcija, ki iz cookija dobi sporočilo, če je
def get_sporocilo():
    sporocilo = bottle.request.get_cookie('message', default=None, secret=secret)
    bottle.response.delete_cookie('message')
    return sporocilo



def get_user(auto_login = False):
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


@bottle.route("/")
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
    dodeli_pravice()
    #(username, ime) = get_user()
    # Morebitno sporočilo za uporabnika
    #sporocilo = get_sporocilo()
    # Seznam zadnjih 10 tračev
    #ts = traci()
    # Vrnemo predlogo za glavno stran
    return bottle.template("login.html", napaka=None, username='uporabnik')

@bottle.get("/login/")
def login_get():
    """Serviraj formo za login."""
    return bottle.template("login.html",
                           napaka=None,
                           username='uporabnik')

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
                           username=None,
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
        c.execute("INSERT INTO uporabnik (username, ime, password) VALUES (?, ?, ?)",
                  (username, ime, password))
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/")

###############################################

def pretty_date(time):
    """
    Predelaj čas (v formatu Unix epoch) v opis časa, na primer
    'pred 4 minutami', 'včeraj', 'pred 3 tedni' ipd.
    """

    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "zdaj"
        if second_diff < 60:
            return "pred " + str(second_diff) + " sekundami"
        if second_diff < 120:
            return  "pred minutko"
        if second_diff < 3600:
            return "pred " + str( second_diff // 60 ) + " minutami"
        if second_diff < 7200:
            return "pred eno uro"
        if second_diff < 86400:
            return "pred " + str( second_diff // 3600 ) + " urami"
    if day_diff == 1:
        return "včeraj"
    if day_diff < 7:
        return "pred " + str(day_diff) + " dnevi"
    if day_diff < 31:
        return "pred " + str(day_diff//7) + " tedni"
    if day_diff < 365:
        return "pred " + str(day_diff//30) + " meseci"
    return "pred " + str(day_diff//365) + " leti"


@bottle.post("/trac/new/")
def new_trac():
    """Ustvari nov trač."""
    # Kdo je avtor trača?
    (username, ime) = get_user()
    # Vsebina trača
    trac = bottle.request.forms.trac
    c = baza.cursor()
    c.execute("INSERT INTO trac (avtor, vsebina) VALUES (?,?)",
              [username, trac])
    # Presumerimo na glavno stran
    return bottle.redirect("/")


@bottle.post("/komentar/<tid:int>/")
def komentar(tid):
    """Vnesi nov komentar."""
    (username, ime) = get_user()
    komentar = bottle.request.forms.komentar
    baza.execute("INSERT INTO komentar (vsebina, trac, avtor) VALUES (?, ?, ?)",
                 [komentar, tid, username])
    bottle.redirect("/#trac-{0}".format(tid))

@bottle.route("/trac/<tid:int>/delete/")
def komentar_delete(tid):
    """Zbriši komentar."""
    (username, ime) = get_user()
    # DELETE napišemo tako, da deluje samo, če je avtor komentarja prijavljeni uporabnik
    r = baza.execute("DELETE FROM trac WHERE id=? AND avtor=?", [tid, username]).rowcount
    if not r == 1:
        return "Vi ste hacker."
    else:
        set_sporocilo('alert-success', "Vaš komentar je IZBRISAN.")
        return bottle.redirect("/")

###############################################

@bottle.get('/ekipe/')
def ekipe_get():
    cur.execute("SELECT ime, zmage, porazi FROM ekipa")
    ekipe = cur.fetchall()
    napaka='napaka'
    # return bottle.template('ekipe.html', ekipe=ekipe, napaka0=None, napaka=napaka, username=username)
    return bottle.template('ekipe.html', seznam_ekip=ekipe, napaka=None)

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

def dodeli_pravice():
    cur.execute("GRANT CONNECT ON DATABASE sem2019_sarabi TO andrazdl; GRANT CONNECT ON DATABASE sem2019_sarabi TO tadejm; GRANT CONNECT ON DATABASE sem2019_sarabi TO javnost;")
    cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO andrazdl; GRANT ALL ON ALL TABLES IN SCHEMA public TO tadejm; GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;")
    baza.commit()

###############################################

# GLAVNI PROGRAM

# priklopimo se na bazo
baza = psycopg2.connect(database=auth.db, host=auth.host, user='sarabi', password='fhx7lo1l')
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na portu 8010, glej http://localhost:8010/
bottle.run(host='localhost', port=8010)
