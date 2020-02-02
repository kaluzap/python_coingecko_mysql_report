import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import tz
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import sys


def read_crypto_data(symbol, past_hours=48):

    cnx = mysql.connector.connect(
        user="pablo",
        password="12345678",
        host="192.168.0.13",
        port="3306",
        database="cryptos",
    )

    cursor = cnx.cursor(buffered=True)

    if cnx.is_connected() == False:
        return None

    date_time_obj = datetime.now()
    time_linux_now = date_time_obj.timestamp()
    time_start = time_linux_now - past_hours * 3600

    command = "SELECT * FROM " + symbol + " WHERE time_re > " + str(time_start) + ";"
    # print(command)
    try:
        cursor.execute(command)
        # cnx.commit()
        results = cursor.fetchall()
    except:
        return None

    cursor.close()

    # if(cnx.is_connected()):
    #    cursor.close()

    results = pd.DataFrame(results)

    if results.shape[0] == 0:  # there are any row
        return None

    results.columns = [
        "time_re",
        "price_usd",
        "volume_usd",
        "price_btc",
        "volume_btc",
        "time_lu",
    ]

    return results


def percent_change(initial_value, final_value):
    change = 100.0 * (final_value - initial_value) / initial_value
    return f"{change:.2f}%"


def nice_str(num):
    if num == 0:
        return f"{num:.2f}"
    if num >= 1.0:
        return f"{num:.2f}"
    my_str = f"{num:.40f}"[2:]
    for i in range(len(my_str)):
        if my_str[i] != "0":
            break
    if i > 35:
        return f"{num}"
    return f"{num:.40f}"[: i + 3 + 2]


def make_a_plot_1(data, symbol, name):

    fig = plt.figure(figsize=(13, 10))  # tight_layout=True)#figsize=(600,300))
    plt.subplots_adjust(
        left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.35
    )
    ax = fig.subplots(nrows=4, ncols=1)

    # time = list(data["time_re"])
    # time = [(x - time[-1]) / 3600 for x in time]

    # new column with datetime values
    data["date"] = pd.to_datetime(data["time_re"], unit="s")

    # time Format
    delta_time = data["date"].iloc[-1] - data["date"].iloc[0]

    if delta_time.days <= 2:
        myFmt = mdates.DateFormatter("%a-%H:%M")  # ('%d')
    elif delta_time.days <= 30:
        myFmt = mdates.DateFormatter("%d%b-%Hhs")  # ('%d')
    else:
        myFmt = mdates.DateFormatter("%Y%b%d")  # ('%d')

    ax[0].xaxis.set_major_formatter(myFmt)
    ax[1].xaxis.set_major_formatter(myFmt)
    ax[2].xaxis.set_major_formatter(myFmt)
    ax[3].xaxis.set_major_formatter(myFmt)

    title_str = name + ": " + str(data["price_usd"][len(data) - 1]) + " [usd]"

    change_usd = percent_change(data["price_usd"][0], data["price_usd"][len(data) - 1])
    change_btc = percent_change(data["price_btc"][0], data["price_btc"][len(data) - 1])

    ax[0].set_ylabel("Price [usd]", size=10)
    # ax[0].set_xlabel("Time", size=8)
    # ax[0].plot(time, data["price_usd"], label=change_usd)
    ax[0].plot(data["date"], data["price_usd"], label=change_usd)
    my_color = "red" if change_usd[0] == "-" else "green"
    ax[0].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[1].set_ylabel("Volume [usd]", size=10)
    ax[1].ticklabel_format(style="sci", axis="y")
    # ax[1].set_xlabel("Time", size=8)
    ax[1].plot(data["date"], data["volume_usd"], color="red")
    ax[1].yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1e"))

    ax[2].set_ylabel("Price [btc]", size=10)
    # ax[2].set_xlabel("Time", size=8)
    ax[2].plot(data["date"], data["price_btc"], label=change_btc)
    ax[2].ticklabel_format(style="sci", axis="y")
    my_color = "red" if change_btc[0] == "-" else "green"
    ax[2].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[3].set_ylabel("Volume [btc]", size=10)
    ax[3].ticklabel_format(style="sci", axis="y")
    ax[3].set_xlabel("Time", size=10)
    ax[3].plot(data["date"], data["volume_btc"], color="red")
    ax[3].yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1e"))

    plt.savefig("./img/" + symbol + ".jpg", dpi=100, bbox_inches="tight")

    plt.close()


def main(args):

    try:
        list_of_coins = pd.read_csv(args.coins)
    except:
        print("Error reading file ", args.coins)
        return

    list_of_coins.columns = ["id", "symbol", "name"]

    time_period = eval(args.time)

    report_file = open("report_evolutions.html", "w")

    # printing the links to the different coins
    for i in range(list_of_coins.shape[0]):
        text = (
            '<a href="#'
            + list_of_coins["symbol"][i].upper()
            + '">['
            + list_of_coins["name"][i]
            + "]</a>"
        )
        report_file.write(text + "\n")

    for i in range(list_of_coins.shape[0]):

        print(i, " -> ", flush=True)
        print("\t id: ", list_of_coins["id"][i], flush=True)
        print("\t Symbol: ", list_of_coins["symbol"][i].upper(), flush=True)
        print("\t Name: ", list_of_coins["name"][i], flush=True)

        try:
            data = read_crypto_data(list_of_coins["symbol"][i].upper(), time_period)

            if data is None:
                print("Error reading data from MySQL database")
                continue

            make_a_plot_1(
                data, list_of_coins["symbol"][i].upper(), list_of_coins["name"][i]
            )
        except Exception as e:
            print("\tError!\n\t", e)
            continue

        # links to jump to this coin
        text = '<a name="' + list_of_coins["symbol"][i].upper() + '"></a>'
        report_file.write(text + "\n")

        text = (
            '<p><font size="9" color="black">'
            + str(i + 1)
            + ") "
            + list_of_coins["name"][i]
            + "</font></p>"
        )
        report_file.write(text + "\n")

        change_usd = percent_change(
            data["price_usd"][0], data["price_usd"][len(data) - 1]
        )
        change_btc = percent_change(
            data["price_btc"][0], data["price_btc"][len(data) - 1]
        )

        text = (
            '<p><font size="6" color="black"> Price (usd) ['
            + str(change_usd)
            + "]: "
            + nice_str(data["price_usd"][len(data) - 1])
            + "</font></p>"
        )
        report_file.write(text + "\n")

        text = (
            '<p><font size="6" color="black"> Price (btc) ['
            + str(change_btc)
            + "]: "
            + nice_str(data["price_btc"][len(data) - 1])
            + "</font></p>"
        )
        report_file.write(text + "\n")

        text = (
            '<figure> <img src = "./img/'
            + list_of_coins["symbol"][i].upper()
            + '.jpg"> </figure>'
        )
        report_file.write(text + "\n")

        report_file.write("<p></p>\n" * 3)

    report_file.close()

    print(
        "\nLast database actualization (UTC): ",
        datetime.utcfromtimestamp(data["time_re"].iloc[-1]).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        flush=True,
    )

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = datetime.utcfromtimestamp(data["time_re"].iloc[-1])
    utc = utc.replace(tzinfo=from_zone)

    my_zone = utc.astimezone(to_zone)

    print(
        "Last database actualization (Berlin): ", my_zone.strftime("%Y-%m-%d %H:%M:%S"),
    )


if __name__ == "__main__":

    import argparse

    # Adding command line options
    parser = argparse.ArgumentParser(
        description="Make Report V 2.0 (2020-01-16)",
        epilog="Example: python make_report.py --coins list_id_symbol_name_coingecko.csv --time num_hours",
    )

    parser.add_argument(
        "--coins", "-c", required=True, help="specify the list of coins."
    )

    parser.add_argument(
        "--time",
        "-t",
        required=False,
        default="24",
        help="specify the time period in hours.",
    )

    print("Evolutions of the price as function of time in usd and BTC.")
    print("The dataset is taken from the local MySQL database.")

    # Computing command line arguments
    args = parser.parse_args()
    main(args)
