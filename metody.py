from datetime import datetime
import komunikace_s_db
from tabulate import tabulate

aktualniPocetUkolu=0

#tato funkce vyvolá spusteni programu a zobrazeni hlavniho menu
def spustProgram():
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_manual)
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_manual)
    mycursor = pripojeni_k_db.cursor()
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_manual, komunikace_s_db.nazev_tab_manual)
    YELLOW = '\033[93m'
    END = '\033[0m'
    print(f"\n{YELLOW}*** Vítejte ve vylepšeném task manageru ***{END}")
    print("")
    hlavni_menu(mycursor, pripojeni_k_db)
    
#hlavni funkce = rozcestník
def hlavni_menu(mycursor, connection):
    volba = 0
    while volba==0:
        volba = volbyMenu()       
        if volba==1:
            pridat_ukol(mycursor, connection)
        elif volba==2:
            zobrazit_ukoly(mycursor, connection)
        elif volba==3:
            aktualizovat_ukol(mycursor, connection)
        elif volba==4:   
            odstranit_ukol(mycursor, connection)
        elif volba==5:
            ukoncit_program_a_uklidit(mycursor, connection)

#pomocna funkce - uzivatelsky vyber v hlavnim menu
def volbyMenu():
    print("Správce úkolů - Hlavní menu") 
    print("1. Přidat úkol") 
    print("2. Zobrazit úkoly") 
    print("3. Aktualizovat úkol")
    print("4. Odstranit úkol")
    print("5. Ukončit program")

    correctType = False
    userInput = 0
    while correctType==False or userInput==0:
        try:
            userInput = int(input("Vyberte možnost (1-5): "))   
            correctType = True
            while userInput>5:
                userInput=0
                print("\nZadaná hodnota je mimo rozsah menu, zadejte prosím číslo (1-5)\n")
                userInput = int(input("Vyberte možnost (1-5): ")) 
        except(ValueError):
            print("\nZadaná hodnota není číslo.\n")
            correctType==False
    return userInput

#pomocna funkce - dostava vyhodnocuje textovy vstup uzivatele
def dostanUzivatelskyVstup (zpravaUzivateli):
    vystup = ""
    while vystup=="":
        vystup = input(zpravaUzivateli)
        if vystup=="":
            print("Nebyl vložen žádný text.")
        if len(vystup)>30:
            print("Zadané slovní spojení je příliš dlouhé, vložte prosím znovu text (max 30 znaků)")
            vystup=""
    return vystup

#pomocna funkce - vytezi seznam ukolu z databaze
def seznamUkolu(mycursor, zprava_uzivateli):
    #dostan seznam ukolu z databaze
    ukoly = komunikace_s_db.zobraz_ukoly(mycursor, komunikace_s_db.nazev_tab_manual)
    #spocitej radky selectu
    global aktualniPocetUkolu
    aktualniPocetUkolu = len(ukoly)
    
    if aktualniPocetUkolu==0:   #pokud nejsou k dispozici radky s ukoly - informuj
        print("Nejsou k dispozici žádné rozpracované úkoly.")
        print("")

    else:   #pokud jsou k dispozici radky s ukoly = vytiskni seznam
        print(f"\n{zprava_uzivateli}")
        print(tabulate(ukoly, headers=['Id', 'Nazev', 'Popis', 'Stav', 'Datum vytvoreni'], tablefmt='psql'))
        print("")

#hlavni funkce - zalozi radek s ukolem v databazi        
def pridat_ukol(mycursor, connection):
    nazev = dostanUzivatelskyVstup("\nZadejte název úkolu: ")
    popis = dostanUzivatelskyVstup("Zadejte popis úkolu: ")
    komunikace_s_db.create_tableRow(mycursor, komunikace_s_db.nazev_tab_manual, connection, nazev, popis)
    print("\nÚkol \'" + nazev + "\' byl přidán.\n")
    hlavni_menu(mycursor, connection)

#hlavni funkce - zobrazi seznam ukolu
def zobrazit_ukoly(mycursor, connection):
    #zobraz ukoly
    seznamUkolu(mycursor, "Seznam úkolů: ")
    #vrat se do hlavniho menu
    hlavni_menu(mycursor, connection)

#pomocna funkce = dostane od uzivatele id ukolu a porovna jeho spravnost (zda id existuje v db...atd)
def dostan_id_ukolu_a_over_platnost_vstupu(mycursor, pocetUkolu, zprava_uzivateli):     # pozadej o uzivatelsky vstup a zkontroluj vlozena data - id ukolu
    zadana_validni_volba = False
    i=1
    id_ukolu_k_aktualizaci=0
    ukoly_z_db = komunikace_s_db.zobraz_ukoly(mycursor, komunikace_s_db.nazev_tab_manual)
    id_ukolu_k_aktualizaci_int=0
    while(zadana_validni_volba==False):
        if i<5:                
            try:
                uzivatelsky_vstup = dostanUzivatelskyVstup(f"{zprava_uzivateli} - doplňte id úkolu (pokus {i}/4): ")
                id_ukolu_k_aktualizaci_int = int(uzivatelsky_vstup)
                for ukol in ukoly_z_db:
                    if ukol[0]==id_ukolu_k_aktualizaci_int:
                        zadana_validni_volba=True
                        id_ukolu_k_aktualizaci=id_ukolu_k_aktualizaci_int
                        break
            except(ValueError):
                ("Vložená hodnota není číslo...")
            i=i+1
        else:
            id_ukolu_k_aktualizaci = 0
            break
    return id_ukolu_k_aktualizaci

#hlavni funkce - aktualizuje ukol v databazi
def aktualizovat_ukol(mycursor, connection):
    #zobraz ukoly
    seznamUkolu(mycursor, "Seznam úkolů: ")
    #dostan seznam ukolu z databaze
    ukoly = komunikace_s_db.zobraz_ukoly(mycursor, komunikace_s_db.nazev_tab_manual)
    #spocitej radky selectu
    global aktualniPocetUkolu
    aktualniPocetUkolu = len(ukoly)
    # pozadej o uzivatelsky vstup a zkontroluj vlozena data - id stavu
    def dostan_id_stavu_ukolu_a_over_platnost_vstupu(moznostiNabidky):
        zadana_validni_volba = False
        i=1
        id_stavu_k_aktualizaci=0
        print("\nStavy úkolů: ")
        print("1. Probíhá")
        print("2. Hotovo")
        print("")
        while(zadana_validni_volba==False):
            if i<5:
                uzivatelsky_vstup = dostanUzivatelskyVstup(f"Doplňte id nového stavu úkolu (pokus {i}/4): ")
                try:
                    id_stavu_int = int(uzivatelsky_vstup)
                    #assert(id_ukolu_k_aktualizaci_int is int)
                    assert(id_stavu_int in range(1, moznostiNabidky+1))
                    zadana_validni_volba==True
                    id_stavu_k_aktualizaci=id_stavu_int

                    break                  
                except(ValueError):
                    i=i+1
                except(AssertionError):
                    i=i+1
            else:
                id_stavu_k_aktualizaci = 0
                break
        return id_stavu_k_aktualizaci
    idUkolu = dostan_id_ukolu_a_over_platnost_vstupu(mycursor, aktualniPocetUkolu, "Aktualizace úkolu")
    if idUkolu==0:  #v pripade, ze ani po opakovanych pokusech neni vlozena spravna hodnota
        print("\nByl překročen počet pokusů, návrat do hlavní nabídky...")
        print("")
        hlavni_menu(mycursor, connection)
    idStavu = dostan_id_stavu_ukolu_a_over_platnost_vstupu(2)
    stav = ""
    if idStavu==0: #v pripade, ze ani po opakovanych pokusech neni vlozena spravna hodnota
        print("\nByl překročen počet pokusů, návrat do hlavní nabídky...")
        print("")
        hlavni_menu(mycursor, connection)
    elif idStavu==1:
        stav = "Probíhá"
    elif idStavu==2:
        stav = "Hotovo"
    novyStav = komunikace_s_db.update_ukol(mycursor, connection, komunikace_s_db.nazev_tab_manual, idUkolu, stav)
    print("\nÚkol byl aktualizován:")
    print(tabulate(novyStav, headers=['Id', 'Nazev', 'Popis', 'Stav', 'Datum vytvoreni'], tablefmt='psql'))
    print("")
    hlavni_menu(mycursor, connection)

#hlavni funkce - ukonci program a vycisti testovaci data
def ukoncit_program_a_uklidit(mycursor, connection):
    print("\nKonec programu.")
    komunikace_s_db.uklid_smazat_db(mycursor, connection, komunikace_s_db.nazev_db_manual)

#hlavni funkce - odstrani ukol z databaze
def odstranit_ukol(mycursor, connection):
    #zobraz ukoly
    seznamUkolu(mycursor, "Seznam úkolů: ")
    #dostan seznam ukolu z databaze
    ukoly = komunikace_s_db.zobraz_ukoly(mycursor, komunikace_s_db.nazev_tab_manual)
    #spocitej radky selectu
    global aktualniPocetUkolu
    aktualniPocetUkolu = len(ukoly)
    if aktualniPocetUkolu>0:
        idUkolu = dostan_id_ukolu_a_over_platnost_vstupu(mycursor, aktualniPocetUkolu, "Smazání úkolu")
        print("volba uzivatele: ", idUkolu)
        if idUkolu==0:  #v pripade, ze ani po opakovanych pokusech neni vlozena spravna hodnota
            print("\nByl překročen počet pokusů, návrat do hlavní nabídky...")
            print("")
            hlavni_menu(mycursor, connection)
        result = komunikace_s_db.smaz_radek(mycursor, connection, komunikace_s_db.nazev_tab_manual, idUkolu)
        print(f"\nÚkol s id {idUkolu} byl smazán.")
        seznamUkolu(mycursor, "Seznam zbývajících úkolů: ")
        hlavni_menu(mycursor, connection)
    else:
        print("")
        hlavni_menu(mycursor, connection)
    
    
