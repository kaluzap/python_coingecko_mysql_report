import mysql.connector
import pandas as pd
from datetime import datetime
from dateutil import tz

import matplotlib.pyplot as plt


databases = {
    "rp3": {
        "user": "pablo",
        "password": "12345678",
        "host": "192.168.0.13",
        "port": "3306",
        "database": "cryptos",
    },
    "grande": {
        "user": "pablo",
        "password": "12345678",
        "host": "127.0.0.1",
        "port": "3306",
        "database": "cryptos",
    },
}


def read_crypto_data(symbol, past_hours=48):

    columns_names = [
        "time_re",
        "price_usd",
        "volume_usd",
        "price_btc",
        "volume_btc",
        "time_lu",
    ]

    df_results = pd.DataFrame(columns=columns_names)

    for db in list(databases.keys()):

        try:
            cnx = mysql.connector.connect(
                user=databases[db]["user"],
                password=databases[db]["password"],
                host=databases[db]["host"],
                port=databases[db]["port"],
                database=databases[db]["database"],
            )
        except:
            continue

        cursor = cnx.cursor(buffered=True)

        if cnx.is_connected() == False:
            continue

        date_time_obj = datetime.now()
        time_linux_now = date_time_obj.timestamp()
        time_start = time_linux_now - past_hours * 3600

        command = (
            "SELECT * FROM " + symbol + " WHERE time_re > " + str(time_start) + ";"
        )

        try:
            cursor.execute(command)
            results = cursor.fetchall()
        except:
            continue

        cursor.close()

        df_temp = pd.DataFrame(results)

        if df_temp.shape[0] == 0:  # there are any row
            continue

        df_temp.columns = columns_names
        df_results = pd.concat([df_results, df_temp], ignore_index=True)

    df_results = df_results.drop_duplicates(subset="time_re", keep="last")
    df_results = df_results.sort_values(["time_re"])
    df_results = df_results.reset_index()

    return df_results


if __name__ == "__main__":

    df = read_crypto_data("LTC", 400008)

    print(df.head())

    plt.plot(df["time_re"], df["price_usd"])
    plt.show()
