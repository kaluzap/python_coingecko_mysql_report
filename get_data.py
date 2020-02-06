import sys
import time
import datetime
import mysql.connector
import requests
import csv


def read_id_symbol_name(file_name):
    #open the file
    try:
        file_data = open(file_name,"r")    
    except FileNotFoundError:
        print("The file \"%s\" is missing" % sys.argv[1])
        return None
    #read csv
    reader = csv.reader(file_data)
    next(reader, None)
    your_list = list(reader)
    file_data.close()
    #print coin list
    print("My coin list (id, symbol, name):")
    for i in range(len(your_list)):
        print(i+1, " - ", 
              "\"" + your_list[i][0] + "\"",
              "\"" + your_list[i][1] + "\"",
              "\"" + your_list[i][2] + "\"")
    return your_list


def start_mysql_connection():
    #starting mysql
    try:
        cnx = mysql.connector.connect(user='crypto_loader', 
                                password='12345678',
                                host='localhost',
                                database='cryptos')
    except:
        print("Error I connecting MySQL database")
        quit()
    cursor = cnx.cursor()
    if(cnx.is_connected()):
        print("MySQL connection is open!")
    else:
        print("Error II connecting MySQL database")
        quit()
    return cursor, cnx
    

def get_one_request(my_coin_list):
    #creating the request line
    linea = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids="
    linea += "bitcoin"
    for x in my_coin_list:
        if x[0] == 'bitcoin':
            continue
        linea += "%2C" + x[0]
    linea += "&order=market_cap_desc&per_page=250&page=1&sparkline=false"
    try:
        r = requests.get(linea)
    except:
        print("Error in request")
        return None
    
    try:
        data = r.json()
    except:
        print("Error in json")
        return None
    
    if len(data) == 0:
        return None
    return data


def create_tables(cursor, cnx, my_coin_list):
    #CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20), species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);
    #CREATE TABLE Persons (ID int NOT NULL, LastName varchar(255) NOT NULL, FirstName varchar(255),Age int,PRIMARY KEY (ID));
    new_tables = 0
    for x in my_coin_list:
        command = "CREATE TABLE " + x[1].upper() + ' '
        command += "(time_re INT, price_usd DOUBLE, volume_usd DOUBLE, price_btc DOUBLE, volume_btc DOUBLE, time_lu INT, PRIMARY KEY (time_re));"
        try:
            cursor.execute(command)
            cnx.commit()
            new_tables += 1
        except:
            pass
    return new_tables
    
    
#######################################    
#the main function
#######################################

if(len(sys.argv) != 2): 
    print("Tomar datos! V 3.0 (26.07.2019)")
    print("The dataset is taken from CoinGecko plus MySQL and request.")
    print("Usar: python3 tomar_datos.py list_id_symbol_name_coingecko.csv")
    quit()


#file with coin ids, symbols, names
#my_coin_list is a list of list. Each elemen has a list with [id, symbol, name]
my_coin_list = read_id_symbol_name(sys.argv[1])
if my_coin_list == None:
    quit()


#starting mysql connection    
cursor, cnx = start_mysql_connection()


#create tables if there do not exist
create_tables(cursor, cnx, my_coin_list)


BTC_price = 1.0


#main loop
while True:
    
    data = get_one_request(my_coin_list)
    
    date_time_obj = datetime.datetime.now()
    time_re = date_time_obj.timestamp()
    
    if data == None:
        continue
    
    for one_coin in data:
        
        the_price_usd = float(one_coin['current_price'])
        the_symbol = one_coin['symbol'].upper()
        
        if the_symbol == 'BTC':
            BTC_price = the_price_usd
                    
        date_time_obj = datetime.datetime.strptime(one_coin['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")
        time_lu = date_time_obj.timestamp()
        
        the_price_btc = the_price_usd/BTC_price
        volume_24h_usd = float(one_coin['total_volume'])
        volume_24h_btc = volume_24h_usd/BTC_price
        
        #to MySQL
        command = "INSERT INTO " + the_symbol + " (time_re, price_usd, volume_usd, price_btc, volume_btc, time_lu) VALUES ("
        command += "\"" + str(round(time_re, 0)) + "\", "
        command += "\"" + str(the_price_usd) + "\", "
        command += "\"" + str(volume_24h_usd) + "\", "
        command += "\"" + str(the_price_btc) + "\", "
        command += "\"" + str(volume_24h_btc) + "\", "
        command += "\"" + str(round(time_lu, 0)) + "\");"
        
        try:
            cursor.execute(command)
            cnx.commit()
        except:
            print("Error: some problems adding data for ", one_coin[2])
        
    time.sleep(300) #300 it takes like 20seg to do a cycle
cnx.close()



