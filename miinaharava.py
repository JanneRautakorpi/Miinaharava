"""
Miinaharava kurssin lopputyönä.
Työssä käytetään Haravasto -moduulia, jonka on tehnyt Mika Oja.
Janne Rautakorpi, 2022.
Ohjelmoinnin alkeet, Oulun yliopisto.
"""

import time
import random as rnd
import datetime as dt
import haravasto as ha

# Visual -sanakirja kuvaa kenttää, jota näytetään ja päivitetään pelaajalle.
visual = {
    "kentta":[]
}

# Miina -sanakirja kuvaa ns. back-end kenttää, joka miinoitetaan ja jonka avulla tulvatäytetään ja tehdään voitto-häviö-ehtoja.
miina = {
    "kentta":[]
}

# Pelin tilaa sekä ominaisuuksia kuvaava sanakirja.
peli = {
    "miinojen_lkm":0,
    "leveys":0,
    "korkeus":0,
    "end":0,
    "start":0,
    "koko":0,
    "miinoitettavat":0,
    "tulos":" ",
    "klikkaukset":0,
    "ruutuja_jaljella":0
}

def tilastoi():
    """
    Tilastoidaan pelattujen pelien tuloksia *.txt -tiedostoon.
    """
    kulunut_aika = int(peli["end"] - peli["start"])
    try:
        with open("tulokset.txt", "a", encoding="utf-8") as t:
            t.write(f'Kentän koko: {peli["koko"]} - Miinojen lkm: {peli["miinojen_lkm"]} - Aikaa kului {dt.timedelta(seconds=kulunut_aika)} - Vuoroja yht. {peli["klikkaukset"]} kpl - Lopputulos: {peli["tulos"]} - Pvm: {dt.date.today()}\n')
    except IOError:
        print("Tiedoston avaaminen epäonnistui.")

def tarkastele_tuloksia():
    """
    Luetaan tekstitiedostoa, jossa tuloksia pelatuista peleistä.
    """
    try:
        with open("tulokset.txt", "r", encoding="utf-8") as file:
            for i in file.readlines():
                print(i)
    except IOError:
        print("Tiedoston avaaminen epäonnistui.")

def kasittele_hiiri(x, y, nappi, lisanappi):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Tarkistetaan myös mihin klikkaus osuu; miinasta häviää pelin ja 
    tyhjästä ruudusta kutsutaan tulvatäyttö -funktiota.
    """
    button = {
        "vasen": ha.HIIRI_VASEN,
        "keski": ha.HIIRI_KESKI,
        "oikea": ha.HIIRI_OIKEA
    }
    # Määritetään x- sekä y-koordinaatit painallyksille. Yksi ruudukko on 40px.
    x, y = int(x / 40), int(y / 40)
    
    # Tarkistetaan osuiko klikkaus miinaan vai tyhjään ruutuun.
    if nappi == button["vasen"]:

        if miina["kentta"][y][x] == "x":
            visual["kentta"] = "x"
            ha.aseta_piirto_kasittelija(piirra_kentta)
            peli["tulos"] = "häviö"
            peli["end"] = time.time()
            tilastoi()
            print("Hävisit pelin!")
            ha.lopeta()

        if miina["kentta"][y][x] == " ":
            tulvataytto(x, y)
            ha.aseta_piirto_kasittelija(piirra_kentta)
            peli["klikkaukset"] += 1
            if peli["ruutuja_jaljella"] == 0:
                peli["tulos"] = "voitto"
                peli["end"] = time.time()
                tilastoi()
                print("Voitit pelin!")
                ha.lopeta()

    # Liputusnappi.
    if nappi == button["oikea"]:
        """"
        Hiireän oikealla klikillä voidaan lisätä lippu.
        """
        if visual["kentta"][y][x] == "f":
            visual["kentta"][y][x] = " "
            ha.aseta_piirto_kasittelija(piirra_kentta)
        elif visual["kentta"][y][x] == " ":
            visual["kentta"][y][x] = "f"
            ha.aseta_piirto_kasittelija(piirra_kentta)

def tulvataytto(x, y):
    """
    Tulvatäyttöä miinoihin asti, merkataan ruutuun numero
    sen perusteella montako miinaa ruutua ympäröi.
    """
    pari = [(x, y)]
    while pari:
        x, y = pari.pop()
        miinat = 0
        x_min, x_max = x - 1, x + 1
        x_min = max(x_min, 0)
        if x_max >= peli["leveys"]:
            x_max = peli["leveys"] - 1
        y_min, y_max = y - 1, y + 1
        y_min = max(y_min, 0)
        if y_max >= peli["korkeus"]:
            y_max = peli["korkeus"] - 1
            
        for j in range(y_min, y_max + 1):
            for i in range(x_min, x_max + 1):
                if i == x and j == y:
                    continue
                if miina["kentta"][j][i] == "x":
                    miinat += 1
        
        for j in range(y_min, y_max + 1):
            for i in range(x_min, x_max + 1):
                if i == x and j == y:
                    continue
                if miina["kentta"][j][i] == " " and miinat == 0:
                    pari.append((i, j))
        if miina["kentta"][y][x] == " ":
            peli["ruutuja_jaljella"] -= 1

        miina["kentta"][y][x] = str(miinat)
        visual["kentta"][y][x] = str(miinat)

def kysy_koko():
    """"
    Kysytään käyttäjältä pelikentän kokoa ja tallennetaan koko sanakirjaan.
    """
    while True:
        try:
            vastaus1, vastaus2 = int(input("Anna kentän leveys: ")), int(input("Entäpä korkeus: "))
            peli["koko"] = f'{vastaus1}x{vastaus2}'
            return vastaus1, vastaus2
        except ValueError:
            print("Tarjoahan kokonaislukuja, kiitos.")

def kysy_miinojenlkm(width, height):
    """
    Kysyy käyttäjältä miinojen lukumäärän. Kysytään kunnes seuraava ehto täyttyy:
    Miinoja täytyy olla enemmän kuin 0 ja vähemmän kuin ruutuja kentällä.
    Tieto tallentuu sanakirjaan käytettäväksi koko ohjelmassa.
    """
    gridit = width * height
    while True:
        try:
            ans = int(input(f'Montako miinaa haluat {width}x{height} kentällesi? Max. {width*height-1}\n'))
            if 0 < ans < gridit:
                return ans
            print(f'Miinojen lukumäärän on oltava pienempää kuin {gridit} ja suurempaa kuin 0!')
        except ValueError:
            print("Hupsis! Vain kokonaislukuja, kiitos!")

def luo_kentta(width, height):
    """
    Luodaan pelikenttä käyttäjältä kysytyn leveyden ja korkeuden mukaisiksi.
    Myöskin muokataan sanakirjan "jaljella" -listaa, sitä käytetään myöhemmin miinoituksessa.
    """
    visuaalinenkentta = []
    miinakentta = []
    for _ in range(height):
        visuaalinenkentta.append([])
        miinakentta.append([])
        for _1 in range(width):
            miinakentta[-1].append(" ")
            visuaalinenkentta[-1].append(" ")
    visual["kentta"] = visuaalinenkentta
    miina["kentta"] = miinakentta

def miinoita(kentta, miinat):
    """
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin.
    """
    jaljella = []
    for x in range(peli["leveys"]):
        for y in range(peli["korkeus"]):
            jaljella.append((x, y))

    miinoitettu = 0
    while miinoitettu < miinat:
        x_coord = rnd.randint(0, len(kentta[0])-1)
        y_coord = rnd.randint(0, len(kentta)-1)
        if (x_coord, y_coord) in jaljella:
            jaljella.remove((x_coord, y_coord))
            kentta[y_coord][x_coord] = "x"
            miinoitettu += 1

def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    ha.tyhjaa_ikkuna()
    ha.aloita_ruutujen_piirto()
    for i, j in enumerate(visual["kentta"]):
        for k, kord in enumerate(j):
            ha.lisaa_piirrettava_ruutu(kord, k*40, i*40)
    ha.piirra_ruudut()

def menu():
    """"
    Kirjaimellisesti ohjelman main menu. Kysytään mitä tehdään.
    """
    print("\n\nSinulla on kolme vaihtoehtoa; pelata (1), lopettaa (2) tai tarkastella (3) tuloksia tekstitiedostossa")
    while True:
        try:
            vastaus = int(input("Mitä haluat tehdä? "))
        except ValueError:
            print("Valitse 1, 2 tai 3.")
        else:
            return vastaus

def main():
    """
    Main -funkkari, josta haaraudutaan pelaamaan, tilastoihin tai lopetetaan ohjelma.
    """
    print("-------------------------------------------------------------------------------")
    print(" ----------------------- Miinaharava, Janne Rautakorpi -----------------------")
    print("  ------------------------- 2022, Ohjelmoinnin alkeet -----------------------")

    while True:
        toiminto = menu()

        if toiminto == 1:
            peli["leveys"], peli["korkeus"] = kysy_koko()
            peli["miinojen_lkm"] = kysy_miinojenlkm(peli["leveys"], peli["korkeus"])
            luo_kentta(peli["leveys"], peli["korkeus"])
            miinoita(miina["kentta"], peli["miinojen_lkm"])
            peli["start"] = time.time()
            leveys = len(visual["kentta"][0])
            korkeus = len(visual["kentta"])
            peli["ruutuja_jaljella"] = leveys * korkeus - peli["miinojen_lkm"]
            ha.lataa_kuvat("spritet")
            ha.luo_ikkuna(leveys*40, korkeus*40)
            ha.aseta_piirto_kasittelija(piirra_kentta)
            ha.aseta_hiiri_kasittelija(kasittele_hiiri)
            ha.aloita()

        if toiminto == 2:
            print("Suljetaan ohjelma..")
            time.sleep(1)
            ha.lopeta()
            exit()

        if toiminto == 3:
            tarkastele_tuloksia()

if __name__ == "__main__":
    main()
