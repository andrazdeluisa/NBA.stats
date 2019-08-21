# uvozimo bottle.py
import bottle

# uvozimo podarke za povezavo
import auth_public as auth
#import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import hashlib # računanje MD5 kriptografski hash za gesla

from urllib.parse import urlencode

prijavljen = None

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

@bottle.route('/')
@bottle.route('/?username="username"')
def main():
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template("zacetna_stran.html", username=username)
    else:
        return bottle.template("zacetna_stran.html", username=None)
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
        mydict = {'username': '{}'.format(username)}
        qstr = urlencode(mydict)
        global prijavljen
        prijavljen = username
        print(prijavljen)
        bottle.redirect('/?' + qstr)

@bottle.get("/odjava/")
def logout():
    global prijavljen
    prijavljen = None
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
@bottle.get('/ekipe/?username="username"')
def ekipe_get():
    cur.execute("SELECT ime, zmage, porazi, ROUND(100.0*zmage/82, 2), kratica FROM ekipa ORDER BY zmage DESC")
    ekipe = cur.fetchall()    
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('ekipe.html', seznam_ekip=ekipe, username=username, napaka=None)
    else:
        return bottle.template('ekipe.html', seznam_ekip=ekipe, username=None, napaka=None)





@bottle.get('/igralci/')
@bottle.get('/igralci/?username="username"')
def igralci_get():
    #if searchon:
    #    
    cur.execute("SELECT ime, pozicija, starost FROM igralec")
    igralci = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('igralci.html', seznam_igralcev=igralci, username=username, napaka=None)
    else:
        return bottle.template('igralci.html', seznam_igralcev=igralci, username=None, napaka=None)

@bottle.post("/igralci/")
def igralci_post():
    # username=get_user()
    # Search bar bo implementiran tako, da bo probalo samo popravit, če se uporabnik zmoti v par črkah
    iskana_beseda = bottle.request.forms.search
    c = baza.cursor()
    c.execute("SELECT * FROM igralec WHERE ime=%s", [iskana_beseda])
    igralci = c.fetchall()
    username = bottle.request.query.username
    if igralci != []:
        # Našli smo igralca
        if check_user(username, prijavljen):
            return bottle.template('igralci.html', seznam_igralcev=igralci, username=username, napaka=None)
        else:
            return bottle.template('igralci.html', seznam_igralcev=igralci, username=None, napaka=None)
    else:
        popravljena_beseda = popravi_besedo(iskana_beseda)
        if popravljena_beseda != False:
            c.execute("SELECT * FROM igralec WHERE ime=%s", [popravljena_beseda])
            igralci = c.fetchall()
            if check_user(username, prijavljen):
                return bottle.template('igralci.html', seznam_igralcev=igralci, username=username, napaka="Verjetno ste mislili {}".format(popravljena_beseda))
            else:
                return bottle.template('igralci.html', seznam_igralcev=igralci, username=None, napaka="Verjetno ste mislili {}".format(popravljena_beseda))
        else:
            c.execute("SELECT ime, pozicija, starost FROM igralec")
            igralci = c.fetchall()
            if check_user(username, prijavljen):
                return bottle.template('igralci.html', seznam_igralcev=igralci, username=username, napaka="Burek si")
            else:
                return bottle.template('igralci.html', seznam_igralcev=igralci, username=None, napaka="Burek si")
    # if popravi_besedo(iskana_beseda):





@bottle.get('/trenerji/')
@bottle.get('/trenerji/?username="username"')
def trenerji_get():
    cur.execute("SELECT ime, ekipa, zmage, porazi FROM trener")
    trenerji = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('trenerji.html', seznam_trenerjev=trenerji, username=username, napaka=None)
    else:
        return bottle.template('trenerji.html', seznam_trenerjev=trenerji, username=None, napaka=None)





@bottle.get('/lastniki/')
@bottle.get('/lastniki/?username="username"')
def lastniki_get():
    cur.execute("SELECT ime, ekipa, premozenje FROM lastnik")
    lastniki = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('lastniki.html', seznam_lastnikov=lastniki, username=username, napaka=None)
    else:
        return bottle.template('lastniki.html', seznam_lastnikov=lastniki, username=None, napaka=None)






@bottle.get('/ekipa/:x/')
@bottle.get('ekipa/:x/?username="username"')
def ekipa_get(x):
    cur.execute("SELECT * FROM statistika WHERE statistika.ekipa = %s", [str(x)])
    stat = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('ekipa.html', x=x, statistika=stat, username=username, napaka=None)
    else:
        return bottle.template('ekipa.html',x=x, statistika=stat, username=None, napaka=None)





@bottle.get('/igralec/:x/')
@bottle.get('/igralec/:x/?username="username"')
def igralec_get(x):
    cur.execute("SELECT ekipa, stevilo_tekem, zacetna_postava, minutaza, tocke, osebne_napake, izgubljene_zoge, blokade, ukradene_zoge, podaje, skoki_v_obrambi, skoki_v_napadu, stevilo_prostih_metov, stevilo_zadetih_prostih_metov, stevilo_trojk, stevilo_zadetih_trojk, stevilo_metov_iz_igre, stevilo_zadetih_metov_iz_igre, placa FROM statistika WHERE statistika.ime = %s", [str(x)])
    stat = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('igralec.html', x=x, statistika=stat, username=username, napaka=None)
    else:
        return bottle.template('igralec.html',x=x, statistika=stat, username=None, napaka=None)


###


# ZANIMIVOSTI


@bottle.get('/razvrsti/')
@bottle.get('/razvrsti/?username="username"')
def urazvrsti_get():
    cur.execute("SELECT ime, ekipa, stevilo_tekem, tocke, blokade, podaje, skoki_v_obrambi, skoki_v_napadu, stevilo_zadetih_prostih_metov, stevilo_prostih_metov, stevilo_zadetih_metov_iz_igre, stevilo_metov_iz_igre, stevilo_zadetih_trojk, stevilo_trojk FROM statistika ORDER BY tocke/stevilo_tekem DESC")
    razvrsti = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('razvrsti.html', razvrsti=razvrsti, username=username, napaka=None)
    else:
        return bottle.template('razvrsti.html', razvrsti=razvrsti, username=None, napaka=None)




    
@bottle.get('/uspesni_lastniki/')
@bottle.get('uspesni_lastniki/?username="username"')
def uspesni_lastniki_get():
    cur.execute("SELECT lastnik.ime, lastnik.premozenje, ekipa.zmage, ekipa.ime as ekipa FROM lastnik JOIN ekipa ON lastnik.ekipa=ekipa.kratica WHERE ekipa.zmage>42 ORDER BY ekipa.zmage desc;")
    lastniki = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('uspesni_lastniki.html', seznam_lastnikov=lastniki, username=username, napaka=None)
    else:
        return bottle.template('uspesni_lastniki.html', seznam_lastnikov=lastniki, username=None, napaka=None)





@bottle.get('/uspesni_igralci/')
@bottle.get('/uspesni_igralci/?username="username"')
def uspesni_igralci_get():
    cur.execute("SELECT ime, ekipa, stevilo_tekem, tocke, blokade, podaje, skoki_v_obrambi, skoki_v_napadu, stevilo_zadetih_prostih_metov, stevilo_prostih_metov, stevilo_zadetih_metov_iz_igre, stevilo_metov_iz_igre, stevilo_zadetih_trojk, stevilo_trojk FROM statistika WHERE tocke/stevilo_tekem > 15 ORDER BY tocke/stevilo_tekem DESC")
    igralci = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('uspesni_igralci.html', seznam_igralcev=igralci, username=username, napaka=None)
    else:
        return bottle.template('uspesni_igralci.html', seznam_igralcev=igralci, username=None, napaka=None)





@bottle.get('/dvojni_dvojcki/')
@bottle.get('/dvojni_dvojcki/?username="username"')
def lastniki_get():
    cur.execute("SELECT ime, ekipa, ROUND(1.0*tocke / stevilo_tekem, 2), ROUND(1.0*podaje / stevilo_tekem, 2), ROUND(1.0*(skoki_v_napadu + skoki_v_obrambi) / stevilo_tekem, 2) FROM statistika WHERE tocke/stevilo_tekem >= 10 AND podaje/stevilo_tekem >= 10 OR tocke/stevilo_tekem >= 10 AND (skoki_v_obrambi + skoki_v_napadu)/stevilo_tekem >=10 OR podaje/stevilo_tekem >= 10 AND (skoki_v_obrambi + skoki_v_napadu)/stevilo_tekem >=10 ORDER BY tocke/stevilo_tekem DESC")
    dvojcek = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('dvojni_dvojcki.html', dvojni_dvojcek=dvojcek, username=username, napaka=None)
    else:
        return bottle.template('dvojni_dvojcki.html', dvojni_dvojcek=dvojcek, username=None, napaka=None)





@bottle.get('/trojni_dvojcki/')
def lastniki_get():
    cur.execute("SELECT ime, ekipa, ROUND(1.0*tocke / stevilo_tekem, 2), ROUND(1.0*podaje / stevilo_tekem, 2), ROUND(1.0*(skoki_v_napadu + skoki_v_obrambi) / stevilo_tekem, 2) FROM statistika WHERE tocke/stevilo_tekem >= 10 AND podaje/stevilo_tekem >= 10 AND (skoki_v_obrambi + skoki_v_napadu)/stevilo_tekem >=10 ORDER BY tocke/stevilo_tekem DESC")
    trojni = cur.fetchall()
    username = bottle.request.query.username
    if check_user(username, prijavljen):
        return bottle.template('trojni_dvojcki.html', trojni_dvojcek=trojni, username=username, napaka=None)
    else:
        return bottle.template('trojni_dvojcki.html', trojni_dvojcek=trojni, username=None, napaka=None)

##################################################################



def popravi_besedo(beseda):
    username = beseda
    c = baza.cursor()
    c.execute("SELECT ime, pozicija, starost FROM igralec")
    seznam = c.fetchall()
    imena = []
    for igralec in seznam:
        imena.append(igralec[0])
    # Ustvarili bomo slovar, v katerem bo stevilo razlicnih znakov, glede na podano besedo
    slovar_diferenc = {}
    for ime in imena:
        slovar_diferenc[ime] = diference_crk(ime, beseda)
    najmanjsa = min(slovar_diferenc, key=slovar_diferenc.get)
    # Program bo vrnil False, če bo razlika prevelika
    if slovar_diferenc[najmanjsa] <= 3:
        return najmanjsa
    else:
        return False

def diference_crk(beseda1, beseda2):
    # Funkcija izracuna stevilo znakov, v katerih se crki razlikujeta
    dolzina = min(len(beseda1), len(beseda2))
    diferenca = 0
    for i in range(dolzina):
        if beseda1[i] != beseda2[i]:
            diferenca+=1
    return diferenca


###############################################

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
