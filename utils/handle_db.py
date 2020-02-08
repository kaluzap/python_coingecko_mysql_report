import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
from dateutil import tz
import matplotlib.pyplot as plt

import sys
sys.path.append("./utils")
import config


def start_mysql_connection(in_database):
    """starting mysql with the info of the dictionary in_database"""
    try:
        cnx = mysql.connector.connect(
            user=in_database["user"],
            password=in_database["password"],
            host=in_database["host"],
            port=in_database["port"],
            database=in_database["database"],
        )
    except Exception as e:
        print(f"Error in start_mysql_connection()")
        print(f'Message: "{e}"')
    return cnx


def create_table(cursor, cnx, simbol):
    command = "CREATE TABLE " + simbol.upper() + ' '
    command += "(time_re INT, price_usd DOUBLE, volume_usd DOUBLE, price_btc DOUBLE, volume_btc DOUBLE, time_lu INT, PRIMARY KEY (time_re));"
    try:
        cursor.execute(command)
        cnx.commit()
    except:
        return False
    return True


def write_a_line(cursor, cnx, symbol, data):
    """data is a dict with keys as COLUMNS_NAMES"""
    command = "INSERT INTO " + symbol + " (time_re, price_usd, volume_usd, price_btc, volume_btc, time_lu) VALUES ("
    command += "\"" + str(round(data['time_re'], 0)) + "\", "
    command += "\"" + str(data['price_usd']) + "\", "
    command += "\"" + str(data['volume_usd']) + "\", "
    command += "\"" + str(data['price_btc']) + "\", "
    command += "\"" + str(data['volume_btc']) + "\", "
    command += "\"" + str(round(data['time_lu'], 0)) + "\");"
    try:
        cursor.execute(command)
        cnx.commit()
    except:
        print("Error: some problems adding data for ", symbol)
        return False
    return True
    
    
def read_crypto_data(symbol, initial_date, final_date=None):
    """initial_date and final_date are datetime objects
    If final_date is ignored, the actual time is considered."""

    # empty dataframe with the requered columns
    df_results = pd.DataFrame(columns=config.COLUMN_NAMES)

    # looping over the databases
    for db in list(config.DATABASES.keys()):
        try:
            cnx = start_mysql_connection(config.DATABASES[db])
            cursor = cnx.cursor(buffered=True)
        except:
            continue

        if cnx.is_connected() == False:
            continue

        stamp_ini = initial_date.timestamp()
        if final_date is None:
            stamp_fin = datetime.now().timestamp()
        else:
            stamp_fin = final_date.timestamp()

        command = f"SELECT * FROM {symbol} WHERE time_re >= {stamp_ini} AND time_re <= {stamp_fin};"
        try:
            cursor.execute(command)
            results = cursor.fetchall()
        except:
            continue

        cursor.close()

        df_temp = pd.DataFrame(results)

        if df_temp.shape[0] == 0:  # there are any row
            continue

        df_temp.columns = config.COLUMN_NAMES
        df_results = pd.concat([df_results, df_temp], ignore_index=True)

    df_results = df_results.drop_duplicates(subset="time_re", keep="last")
    df_results = df_results.sort_values(["time_re"])
    df_results = df_results.reset_index()

    df_results['time_re'] = df_results['time_re'].astype('int64')
    df_results["price_usd"] = df_results["price_usd"].astype('float64')
    df_results["price_btc"] = df_results["price_btc"].astype('float64')
    df_results["volume_usd"] = df_results["volume_usd"].astype('float64')
    df_results["volume_btc"] = df_results["volume_btc"].astype('float64')
    
    return df_results


if __name__ == "__main__":

    df = read_crypto_data(
        "LTC", datetime.now() - timedelta(days=700), datetime.now()
    )
    df['date'] = pd.to_datetime(df['time_re'],unit='s')
    plt.plot(df["date"], df["price_usd"], "red")

    plt.show()
