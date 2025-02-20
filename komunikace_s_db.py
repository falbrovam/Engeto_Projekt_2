from datetime import datetime
import mysql.connector

nazev_db_manual = "Database_Falbrova_manual"
nazev_db_automat = "Database_Falbrova_automat"
nazev_tab_manual = "ukoly_manual"
nazev_tab_automat = "ukoly_automat"

# pripojeni na server bez databaze
def prvni_pripojeni_na_server():   
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",    #doplnte vlastni heslo
        )
        if connection.is_connected():
            print("Připojení k databázi je úspěšné!")
            db_info = connection.get_server_info()
            print(f"MySQL verze: {db_info}")
            return connection
    except mysql.connector.Error as e:
        print(f"Chyba při připojení: {e}")
        return None

# pripojeni na konkretni databazi
def pripojeni_k_databazi(nazevDatabaze):    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="drvostepec87",
            database=nazevDatabaze
        )
        if connection.is_connected():
            print("Připojení k databázi je úspěšné!")
            db_info = connection.get_server_info()
            print(f"MySQL verze: {db_info}")
            return connection
    except mysql.connector.Error as e:
        print(f"Chyba při připojení: {e}")
        return None

#vytvori databazi pro manualni nebo automaticke testovani
def vytvor_databazi(nazevDatabaze):
    pripojeni = prvni_pripojeni_na_server()
    mycursor = pripojeni.cursor()
    
    mycursor.execute(f"CREATE DATABASE {nazevDatabaze}")
    mycursor.execute("SHOW DATABASES")
    db_list = mycursor.fetchall()
    if(nazevDatabaze, ) in db_list:
        print("Databaze byla vytvorena")
    else:
        print("Databaze nebyla vytvorena")
    mycursor.close()

#vytvori tabulku pro manualni nebo automaticke testovani
def vytvor_tabulku(mycursor, nazevDatabaze, nazevTabulky):
    mycursor.execute(f'''CREATE TABLE {nazevDatabaze}.{nazevTabulky} (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nazev VARCHAR(30) NOT NULL,
        popis VARCHAR(30) NOT NULL,
        stav VARCHAR(30),
        datumVytvoreni DATE
      )
    ''')
    mycursor.execute("SHOW TABLES")
    seznamTabulek = mycursor.fetchall()
    if(nazevTabulky, ) in seznamTabulek:
        print(f"Tabulka {nazevTabulky} byla vytvořena")
        print("")
    else:
        print(f"Tabulka {nazevTabulky} nebyla vytvořena")

#uklid testovacich dat - smazani databaze
def uklid_smazat_db(mycursor, connection, nazevDatabaze):
    
    mycursor.execute(f"DROP DATABASE {nazevDatabaze}")
    connection.commit()
    mycursor.execute("SHOW DATABASES")
    db_list = mycursor.fetchall()
    if(nazevDatabaze, ) in db_list:
        print("\nDatabáze nebyla odstraněna")
    else:
        print("\nDatabáze byla odstraněna")
    connection.close()
    mycursor.close()

#vlozeni ukolu do databaze
def create_tableRow(mycursor, nazevTabulky, connection, nazev, popis):
    try:
        mycursor.execute (f"INSERT INTO {nazevTabulky} (nazev, popis, stav, datumVytvoreni) VALUES ('{nazev}','{popis}','Nezahájeno',CURDATE());")
        connection.commit()        
    except mysql.connector.Error as err:
        print(f"Chyba při vkládání dat: {err}")

#zobrazeni vsech ukolu v databazi se stavem nezahajeno nebo probiha
def zobraz_ukoly(mycursor, nazevTabulky):
    try:
        mycursor.execute(f"SELECT * FROM {nazevTabulky} WHERE stav = 'Nezahájeno' OR stav = 'Probíhá'")
        return mycursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Chyba při načítání dat: {err}")

#aktualizace ukolu s prislusnym id
def update_ukol(mycursor, connection, nazevTabulky, idUkolu, stav):
    try:
        mycursor.execute(f"UPDATE {nazevTabulky} SET stav = '{stav}' WHERE id = '%s'" % (idUkolu))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Chyba při práci s daty: {err}")
    
    try:
        mycursor.execute(f"SELECT * FROM {nazevTabulky} WHERE id = '%s'" % (idUkolu))
        return mycursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Chyba při načítání dat: {err}")

#smazani ukolu dle zadaneho id
def smaz_radek(mycursor, connection, nazevTabulky, idUkolu):
    try:
        mycursor.execute(f"DELETE FROM {nazevTabulky} WHERE id = '%s'" % (idUkolu))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Chyba při práci s daty: {err}")
