import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import tz
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates

import make_report_evolutions as mre


def read_investments_file(name):

    # loading file
    df_inv = pd.read_csv(name, skipinitialspace=True)

    # Removing missing time values
    df_inv["start_date"] = df_inv["start_date"].fillna(datetime.now())
    df_inv["end_date"] = df_inv["end_date"].fillna(datetime.now())

    # Fixing data types
    df_inv["start_date"] = pd.to_datetime(df_inv["start_date"])
    df_inv["end_date"] = pd.to_datetime(df_inv["end_date"])

    # Time differences
    df_inv["delta_t"] = df_inv["end_date"] - df_inv["start_date"]

    # removinf white spaces
    df_inv["type"] = df_inv["type"].apply(lambda x: x.replace(" ", ""))
    df_inv["coin"] = df_inv["coin"].apply(lambda x: x.replace(" ", ""))

    return df_inv


def load_usd_btc_prices_for_one_investment(coin, date_start, date_end):

    seconds_in_the_past = (datetime.now() - date_start).total_seconds()

    df_temp = mre.read_crypto_data(coin, seconds_in_the_past)[
        ["time_re", "price_usd", "price_btc"]
    ]

    return df_temp[df_temp["time_re"] <= date_end.timestamp()]


def load_one_investment(df_investments):

    coin = df_investments["coin"]
    start_date = df_investments["start_date"]
    end_date = df_investments["end_date"]
    amount = df_investments["amount"]
    # print(coin)
    df_temp = load_usd_btc_prices_for_one_investment(coin, start_date, end_date)

    df_temp.columns = ["time_re", "value_usd", "value_btc"]

    df_temp["value_usd"] = df_temp["value_usd"].apply(lambda x: x * amount)
    df_temp["value_btc"] = df_temp["value_btc"].apply(lambda x: x * amount)

    return df_temp


def main(args):

    # loading investments
    df_inv = read_investments_file(args.investments)

    # crating totals dataframes
    seconds_in_the_past = (datetime.now() - df_inv["start_date"].min()).total_seconds()
    totals_btc = mre.read_crypto_data("BTC", seconds_in_the_past)[["time_re"]]
    totals_usd = mre.read_crypto_data("BTC", seconds_in_the_past)[["time_re"]]

    # creatin list with mean values
    active_investments = []
    actual_value_usd = []
    actual_value_btc = []
    change_usd = []
    change_btc = []
    col_names_fiat = []
    col_names_crypto = []

    # running over investments
    for index, row in df_inv.iterrows():

        is_active = True if np.isnan(row["end_value_usd"]) else False
        active_investments.append(is_active)

        df_temp = load_one_investment(row)

        if is_active:
            final_value_usd = df_temp["value_usd"].iloc[-1]
            final_value_btc = df_temp["value_btc"].iloc[-1]
            actual_value_usd.append(final_value_usd)
            actual_value_btc.append(final_value_btc)
        else:
            final_value_usd = row["end_value_usd"]
            final_value_btc = row["end_value_btc"]
            actual_value_usd.append(final_value_usd)
            actual_value_btc.append(final_value_btc)

        change_usd_here = (
            100.0 * (final_value_usd - row["start_value_usd"]) / row["start_value_usd"]
        )
        change_btc_here = (
            100.0 * (final_value_btc - row["start_value_btc"]) / row["start_value_btc"]
        )
        change_btc.append(change_btc_here)
        change_usd.append(change_usd_here)

        totals_usd = totals_usd.merge(
            df_temp[["time_re", "value_usd"]],
            left_on="time_re",
            right_on="time_re",
            how="left",
        )
        totals_btc = totals_btc.merge(
            df_temp[["time_re", "value_btc"]],
            left_on="time_re",
            right_on="time_re",
            how="left",
        )

        colnames = [x.replace(" ", "") for x in totals_btc.columns]
        new_col_name = row["coin"].replace(" ", "") + f"{index}"
        colnames = colnames[:-1] + [new_col_name]
        totals_btc.columns = colnames
        totals_usd.columns = colnames

        if row["type"] == "fiat":
            col_names_fiat.append(new_col_name)
        elif row["type"] == "crypto":
            col_names_crypto.append(new_col_name)

        # print only if we want active investments
        if (args.status == "active") and (is_active == False):
            continue

        if (args.status == "inactive") and (is_active == True):
            continue

        print(f"Investment {index+1}")
        print("Coin: ", row["coin"])
        print("Investment type: ", row["type"])
        print("Amount: ", row["amount"])
        if is_active:
            print("Status: ACTIVE")
        else:
            print("Status: ENDED")
        print("Initial date: ", row["start_date"])
        if is_active:
            print("End date    :  running now!")
        else:
            print("End date    : ", row["end_date"])

        print(f"Duration: {row['delta_t'].days} days")

        print(f"Initial value (usd): {row['start_value_usd']:.2f}")
        print(f"Final value   (usd): {final_value_usd:.2f}")
        print(
            f"Delta usd: {final_value_usd-row['start_value_usd']:.2f} ({change_usd_here:.2f})%"
        )

        print(f"Initial value (btc): {row['start_value_btc']:.5f}")
        print(f"Final value   (btc): {final_value_btc:.5f}")
        print(
            f"Delta btc: {final_value_btc-row['start_value_btc']:.5f} ({change_btc_here:.2f})%"
        )
        print(" ")

    df_inv["active"] = active_investments
    df_inv["actual_value_usd"] = actual_value_usd
    df_inv["actual_value_btc"] = actual_value_btc
    df_inv["change_usd"] = change_usd
    df_inv["change_btc"] = change_btc

    totals_usd = totals_usd.fillna(0.0)
    totals_btc = totals_btc.fillna(0.0)

    colnames = [x for x in totals_btc.columns][1:]

    totals_usd["total_all"] = totals_usd[colnames].sum(axis=1)
    totals_usd["total_fiat"] = totals_usd[col_names_fiat].sum(axis=1)
    totals_usd["total_crypto"] = totals_usd[col_names_crypto].sum(axis=1)
    totals_usd = totals_usd[["time_re", "total_all", "total_fiat", "total_crypto"]]

    totals_btc["total_all"] = totals_btc[colnames].sum(axis=1)
    totals_btc["total_fiat"] = totals_btc[col_names_fiat].sum(axis=1)
    totals_btc["total_crypto"] = totals_btc[col_names_crypto].sum(axis=1)
    totals_btc = totals_btc[["time_re", "total_all", "total_fiat", "total_crypto"]]

    # totals_usd.plot('time_re', 'total_all')
    print(totals_usd.tail())
    print(totals_btc.tail())
    df_inv.to_csv("out_investments_report.csv")

    print_report_totals(df_inv, totals_usd, totals_btc)


def print_report_totals(df_inv, totals_usd, totals_btc):

    make_a_plot_totals(df_inv, totals_usd, "Totals_in_USD_small", "usd", "small")
    make_a_plot_totals(df_inv, totals_usd, "Totals_in_USD_big", "usd", "big")
    make_a_plot_totals(df_inv, totals_btc, "Totals_in_BTC_small", "btc", "small")
    make_a_plot_totals(df_inv, totals_btc, "Totals_in_BTC_big", "btc", "big")


def make_a_plot_totals(df_inv, data, file_name, what, how):

    fig = plt.figure(figsize=(13, 10))  # tight_layout=True)#figsize=(600,300))
    plt.subplots_adjust(
        left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.35
    )
    ax = fig.subplots(nrows=3, ncols=1)

    # new column with datetime values
    data["date"] = pd.to_datetime(data["time_re"], unit="s")

    if how == "small":
        data = data[data["date"] >= (datetime.now() - timedelta(days=2))]
        print(data.shape)

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

    change_all = mre.percent_change(
        data["total_all"].iloc[0], data["total_all"].iloc[-1]
    )
    change_crypto = mre.percent_change(
        data["total_crypto"].iloc[0], data["total_crypto"].iloc[-1]
    )
    change_fiat = mre.percent_change(
        data["total_fiat"].iloc[0], data["total_fiat"].iloc[-1]
    )

    if what == "usd":
        ini_val_all = df_inv[df_inv["active"] == True]["start_value_usd"].sum()
        ini_val_cry = df_inv[(df_inv["active"] == True) & (df_inv["type"] == "crypto")][
            "start_value_usd"
        ].sum()
        ini_val_fia = df_inv[(df_inv["active"] == True) & (df_inv["type"] == "fiat")][
            "start_value_usd"
        ].sum()
    else:
        ini_val_all = df_inv[df_inv["active"] == True]["start_value_btc"].sum()
        ini_val_cry = df_inv[(df_inv["active"] == True) & (df_inv["type"] == "crypto")][
            "start_value_btc"
        ].sum()
        ini_val_fia = df_inv[(df_inv["active"] == True) & (df_inv["type"] == "fiat")][
            "start_value_btc"
        ].sum()

    ax[0].set_ylabel(f"Total All Investments [{what}]", size=10)
    ax[0].plot(data["date"], data["total_all"], label=change_all, color="black")
    if how == "big":
        ax[0].plot(
            [data["date"].iloc[0], data["date"].iloc[-1]],
            [ini_val_all, ini_val_all],
            "--",
            label="Initial",
            color="black",
        )
    my_color = "red" if change_all[0] == "-" else "green"
    ax[0].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[1].set_ylabel(f"Total Crypto Investments [{what}]", size=10)
    ax[1].plot(data["date"], data["total_crypto"], label=change_crypto, color="red")
    if how == "big":
        ax[1].plot(
            [data["date"].iloc[0], data["date"].iloc[-1]],
            [ini_val_cry, ini_val_cry],
            "--",
            label="Initial",
            color="red",
        )
    my_color = "red" if change_crypto[0] == "-" else "green"
    ax[1].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[2].set_ylabel(f"Total Fiat Investments [{what}]", size=10)
    ax[2].plot(data["date"], data["total_fiat"], label=change_fiat, color="blue")
    if how == "big":
        ax[2].plot(
            [data["date"].iloc[0], data["date"].iloc[-1]],
            [ini_val_fia, ini_val_fia],
            "--",
            label="Initial",
            color="blue",
        )
    my_color = "red" if change_fiat[0] == "-" else "green"
    ax[2].legend(prop={"size": 10}).texts[0].set_color(my_color)
    ax[2].set_xlabel("Time", size=10)

    plt.savefig("./img/" + file_name + ".jpg", dpi=100, bbox_inches="tight")

    plt.close()


if __name__ == "__main__":

    import argparse

    # Adding command line options
    parser = argparse.ArgumentParser(
        description="Make Report Investments V 1.0 (2020-01-26)",
        epilog="Example: python make_report_investments.py --investments list_of_investments.csv --status active",
    )

    parser.add_argument(
        "--investments", "-i", required=True, help="specify the list of investments."
    )

    parser.add_argument(
        "--status",
        "-s",
        required=False,
        default="active",
        help="specify active or inactive investments.",
    )

    print("Evolutions of the investments as function of time in usd and BTC.")
    print("The dataset is taken from the local MySQL database.\n\n")

    # Computing command line arguments
    args = parser.parse_args()
    main(args)
