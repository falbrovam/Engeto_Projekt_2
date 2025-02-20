import mysql.connector
import komunikace_s_db
import pytest

ukoly_platna_data = [
        ('Ukol 1', 'Popis ukolu 1'),
        ('Ukol 2', 'Popis ukolu 2'),
        ('Ukol 3', 'Popis ukolu 3'),
        ('Ukol 4', 'Popis ukolu 4'),
        ('Ukol 5', 'Popis ukolu 5'),
    ]
data_nespravna_ukoly = [
        ('Ukol 1', 'Popis ukolu 1'),
        ('Ukol 2', 'Toto je velmi dlouhy popis ukolu....a jeste delsi'),
        ('Ukol 3', 'Popis ukolu 3'),
        ('Ukol 4', 'Popis ukolu 4'),
        ('Ukol 5', 'Popis ukolu 5'),
    ]

#pomocna funkce pro pridani ukolu
def pridej_ukoly_do_tabulky(cursor, pripojeni, data):
    try:
        cursor.executemany(f"INSERT INTO {komunikace_s_db.nazev_tab_automat} (nazev, popis, stav, datumVytvoreni) VALUES (%s, %s, 'Nezahájeno', CURDATE())", data)
        pripojeni.commit()
        print("Úkoly vloženy do databáze")
    except mysql.connector.Error as err:
        ukonci_test_pri_ostatnich_chybach(cursor, pripojeni, err)

#pomocna funkce pro uklid testovacich dat a nucene ukonceni testu pri chybe, ktera nemela nastat
def ukonci_test_pri_ostatnich_chybach(cursor, pripojeni, chyba):
        #uklid testovacich dat a ukonceni testu
        komunikace_s_db.uklid_smazat_db(cursor, pripojeni, komunikace_s_db.nazev_db_automat) 
        pytest.fail(f"Chyba při práci s daty: {chyba}")

#pozitivni test pridani noveho ukolu
def test_pridani_ukolu_s_platnymi_daty():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #pridej ukoly do databaze          
    pridej_ukoly_do_tabulky(mycursor, pripojeni_k_db, ukoly_platna_data)
    #zkontroluj, ze jsou ukoly v databazi
    for ukol in ukoly_platna_data:
        mycursor.execute(f"SELECT * FROM {komunikace_s_db.nazev_tab_automat} WHERE nazev = '{ukol[0]}';")
        result = mycursor.fetchall()
        try:
            prvni_radek = result[0]
            print("Úkol nalezen")
        except IndexError:
            print("Úkol nenalezen")
            #uklid testovacich dat a ukonceni testu
            komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat)
            pytest.fail(f"Zalozeny ukol: {ukol[0]} v databazi nebyl nalezen")
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat)         

#negativni test pridani noveho ukolu s prilis dlouhym retezcem
def test_pridani_ukolu_s_neplatnymi_daty():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #pridej ukoly do databaze          
    try:
        mycursor.executemany(f"INSERT INTO {komunikace_s_db.nazev_tab_automat} (nazev, popis, stav, datumVytvoreni) VALUES (%s, %s, 'Nezahájeno', CURDATE())", data_nespravna_ukoly)
        pripojeni_k_db.commit()
        print("Úkoly vloženy do databáze")
        #uklid testovacich dat a ukonceni testu
        komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 
        pytest.fail(f"Data byla vložena do databáze i s nesprávnou délkou hodnoty")
    except mysql.connector.Error as err:
        print(f"Data nebyla vložena: ", err)
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat)     

#pozitivni test aktualizace stavajiciho ukolu
def test_aktualizace_ukolu():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #vloz data
    pridej_ukoly_do_tabulky(mycursor, pripojeni_k_db, ukoly_platna_data)
    id_ukolu_k_updatu = 3
    novy_stav = "Probíhá"
    try:
        mycursor.execute(f"UPDATE {komunikace_s_db.nazev_tab_automat} SET stav = '{novy_stav}' WHERE id = '{id_ukolu_k_updatu}'")
        pripojeni_k_db.commit()
    except mysql.connector.Error as err:
        ukonci_test_pri_ostatnich_chybach(mycursor, pripojeni_k_db, err)
    mycursor.execute(f"SELECT * FROM {komunikace_s_db.nazev_tab_automat} WHERE stav = '{novy_stav}';")
    result = mycursor.fetchall()
    try:
        prvni_radek = result[0]
        print(f"Úkol se stavem {novy_stav} byl nalezen")
    except IndexError:
        #uklid testovacich dat a ukonceni testu
        komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 
        pytest.fail(f"Nový stav úkolu {novy_stav} v databázi nebyl nalezen")
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 

#negativni test aktualizace ukolu, ktery neexistuje
def test_aktualizace_neexistujiciho_ukolu():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #vloz data
    pridej_ukoly_do_tabulky(mycursor, pripojeni_k_db, ukoly_platna_data)
    id_ukolu_k_updatu = 7
    novy_stav = "Probíhá"
    try:
        mycursor.execute(f"UPDATE {komunikace_s_db.nazev_tab_automat} SET stav = '{novy_stav}' WHERE id = '{id_ukolu_k_updatu}'")
        pripojeni_k_db.commit()
    except mysql.connector.Error as err:
        ukonci_test_pri_ostatnich_chybach(mycursor, pripojeni_k_db, err)
    
    mycursor.execute(f"SELECT * FROM {komunikace_s_db.nazev_tab_automat} WHERE stav = '{novy_stav}';")
    result = mycursor.fetchall()
    try:
        prvni_radek = result[0]
        print(f"Úkol se stavem {novy_stav} byl nalezen")
        #uklid testovacich dat a ukonceni testu
        komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 
        pytest.fail(f"Nový stav úkolu {novy_stav} v databázi nebyl nalezen")
    except IndexError:
        print(f"Úkol se stavem {novy_stav} nebyl nalezen")
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 

#pozitivni test odstraneni ukolu
def test_odstraneni_ukolu():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #vloz data
    pridej_ukoly_do_tabulky(mycursor, pripojeni_k_db, ukoly_platna_data)
    id_ukolu_k_ke_smazani = 3
    try:
        mycursor.execute(f"DELETE FROM {komunikace_s_db.nazev_tab_automat} WHERE id = '%s'" % (id_ukolu_k_ke_smazani))
        pripojeni_k_db.commit()
        print(f"\nÚkol s id {id_ukolu_k_ke_smazani} byl smazán")
    except mysql.connector.Error as err:
        ukonci_test_pri_ostatnich_chybach(mycursor, pripojeni_k_db, err)
    #overeni, ze radek uz neexistuje
    mycursor.execute(f"SELECT * FROM {komunikace_s_db.nazev_tab_automat} WHERE id = '{id_ukolu_k_ke_smazani}';")
    result = mycursor.fetchall()
    try:
        prvni_radek = result[0]
        #uklid testovacich dat a ukonceni testu
        komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 
        pytest.fail(f"\nÚkol s id: {id_ukolu_k_ke_smazani} po pokusu o smazání byl v databázi nalezen")
    except IndexError:
        print("\nSmazaný úkol v databázi nebyl nalezen")
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat)

#negativni test odstraneni ukolu, ktery neexistuje    
def test_odstraneni_neexistujiciho_ukolu():
    #Vytvor spojeni se serverem a zaloz databazi
    komunikace_s_db.vytvor_databazi(komunikace_s_db.nazev_db_automat)
    #Vytvor nove spojeni serverem a kontrektni databazi
    pripojeni_k_db = komunikace_s_db.pripojeni_k_databazi(komunikace_s_db.nazev_db_automat)
    mycursor = pripojeni_k_db.cursor()
    #Vytvor tabulku
    komunikace_s_db.vytvor_tabulku(mycursor, komunikace_s_db.nazev_db_automat, komunikace_s_db.nazev_tab_automat)
    #vloz data
    pridej_ukoly_do_tabulky(mycursor, pripojeni_k_db, ukoly_platna_data)
    id_ukolu_k_ke_smazani = 7
    try:
        count = mycursor.execute(f"DELETE FROM {komunikace_s_db.nazev_tab_automat} WHERE id = '%s'" % (id_ukolu_k_ke_smazani))
        pripojeni_k_db.commit()
        if count==None:
            print(f"\nŽádný záznam nebyl smazán")
        else:
            #uklid testovacich dat a ukonceni testu
            komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat) 
            pytest.fail(f"\nDošlo ke smazání záznamu")
    except mysql.connector.Error as err:
        ukonci_test_pri_ostatnich_chybach(mycursor, pripojeni_k_db, err)
    #uklid testovacich dat
    komunikace_s_db.uklid_smazat_db(mycursor, pripojeni_k_db, komunikace_s_db.nazev_db_automat)

