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

    #adding the neede columns with zeros.
    totals_btc['total_all'] = 0.0
    totals_btc['total_fiat'] = 0.0
    totals_btc['total_crypto'] = 0.0
    totals_btc['inv_all'] = 0.0
    totals_btc['inv_fiat'] = 0.0
    totals_btc['inv_crypto'] = 0.0
    totals_usd['total_all'] = 0.0
    totals_usd['total_fiat'] = 0.0
    totals_usd['total_crypto'] = 0.0
    totals_usd['inv_all'] = 0.0
    totals_usd['inv_fiat'] = 0.0
    totals_usd['inv_crypto'] = 0.0
    #col_names_totals = ['total_all', 'total_fiat', 'total_crypto', 'inv_all', 'inv_fiat', 'inv_crypto']
    
    # creatin list with mean values for inversion dataframe
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
        
        #We need to know when the invesment is actived in order to add the initial amount
        totals_usd['when_active'] = totals_usd['value_usd'].apply(lambda x: 0 if np.isnan(x) else 1.0)
        totals_btc['when_active'] = totals_btc['value_btc'].apply(lambda x: 0 if np.isnan(x) else 1.0)
        
        totals_usd = totals_usd.fillna(0.0)
        totals_btc = totals_btc.fillna(0.0)
        
        totals_usd['total_all'] = totals_usd['total_all'] + totals_usd['value_usd']
        totals_usd['inv_all'] = totals_usd['inv_all'] + totals_usd['when_active']*row['start_value_usd']
        totals_btc['total_all'] = totals_btc['total_all'] + totals_btc['value_btc']
        totals_btc['inv_all'] = totals_btc['inv_all'] + totals_btc['when_active']*row['start_value_btc']
        
        if row["type"] == "fiat":
            totals_usd['total_fiat'] = totals_usd['total_fiat'] + totals_usd['value_usd']
            totals_usd['inv_fiat'] = totals_usd['inv_fiat'] + totals_usd['when_active']*row['start_value_usd']
            totals_btc['total_fiat'] = totals_btc['total_fiat'] + totals_btc['value_btc']
            totals_btc['inv_fiat'] = totals_btc['inv_fiat'] + totals_btc['when_active']*row['start_value_btc']
        elif row["type"] == "crypto":
            totals_usd['total_crypto'] = totals_usd['total_crypto'] + totals_usd['value_usd']
            totals_usd['inv_crypto'] = totals_usd['inv_crypto'] + totals_usd['when_active']*row['start_value_usd']
            totals_btc['total_crypto'] = totals_btc['total_crypto'] + totals_btc['value_btc']
            totals_btc['inv_crypto'] = totals_btc['inv_crypto'] + totals_btc['when_active']*row['start_value_btc']
            

        totals_usd.drop(columns=['value_usd', 'when_active'], inplace=True)
        totals_btc.drop(columns=['value_btc', 'when_active'], inplace=True)
        
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

    df_inv.to_csv("out_investments_report.csv")

    print_report_totals(df_inv, totals_usd, totals_btc)


def print_report_totals(df_inv, totals_usd, totals_btc):
    #write html

    make_a_plot_totals(totals_usd, "Totals_in_USD_small", "usd", "small")
    make_a_plot_totals(totals_usd, "Totals_in_USD_big", "usd", "big")
    make_a_plot_totals(totals_btc, "Totals_in_BTC_small", "btc", "small")
    make_a_plot_totals(totals_btc, "Totals_in_BTC_big", "btc", "big")
    
    report_file = open("report_totals.html", "w")
    
    #initial links
    text = '<a href="#usd_short">[Totals USD 24hs]</a>'
    report_file.write(text + "\n")
    text = '<a href="#usd_long">[Totals USD all]</a>'
    report_file.write(text + "\n")
    text = '<a href="#btc_short">[Totals BTC 24hs]</a>'
    report_file.write(text + "\n")
    text = '<a href="#btc_long">[Totals BTC all]</a>'
    report_file.write(text + "\n")


    text = df_inv.to_html()
    report_file.write(text)
    
    text = '<p></p>\n<p></p>\n<p></p>\n'
    report_file.write(text)
    
    
    text = '<a name="usd_short"></a>'
    report_file.write(text + "\n")
    
    text = '<p><font size="6" color="black"> Totals in USD 24hs</font></p>'
    report_file.write(text + "\n")

    text = '<figure> <img src = "./img/Totals_in_USD_small.jpg"> </figure>'
    report_file.write(text + "\n\n")
    
    text = '<a name="usd_long"></a>'
    report_file.write(text + "\n")
    
    text = '<p><font size="6" color="black"> Totals in USD all</font></p>'
    report_file.write(text + "\n")
    
    text = '<figure> <img src = "./img/Totals_in_USD_big.jpg"> </figure>'
    report_file.write(text + "\n\n")

    
    text = '<p></p>\n<p></p>\n<p></p>\n'
    report_file.write(text)
    
    
    text = '<a name="btc_short"></a>'
    report_file.write(text + "\n")
    
    text = '<p><font size="6" color="black"> Totals in BTC 24hs</font></p>'
    report_file.write(text + "\n")
    
    text = '<figure> <img src = "./img/Totals_in_BTC_small.jpg"> </figure>'
    report_file.write(text + "\n\n")
    
    text = '<a name="btc_long"></a>'
    report_file.write(text + "\n")
    
    text = '<p><font size="6" color="black"> Totals in BTC all</font></p>'
    report_file.write(text + "\n")
    
    text = '<figure> <img src = "./img/Totals_in_BTC_big.jpg"> </figure>'
    report_file.write(text + "\n\n")
    

def make_a_plot_totals(data, file_name, what, how):
    
    fig = plt.figure(figsize=(13, 10))  # tight_layout=True)#figsize=(600,300))
    plt.subplots_adjust(
        left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.35
    )
    ax = fig.subplots(nrows=3, ncols=1)

    # new column with datetime values
    data["date"] = pd.to_datetime(data["time_re"], unit="s")

    if how == "small":
        data = data[data["date"] >= (datetime.now() - timedelta(days=2))]

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
    
    ax[0].set_ylabel(f"Total All Investments [{what}]", size=10)
    ax[0].plot(data["date"], data["total_all"], label=change_all, color="black")
    if how == "big":
        ax[0].plot(data["date"], data['inv_all'], "--", label="Initial", color="black")
    my_color = "red" if change_all[0] == "-" else "green"
    ax[0].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[1].set_ylabel(f"Total Crypto Investments [{what}]", size=10)
    ax[1].plot(data["date"], data["total_crypto"], label=change_crypto, color="red")
    if how == "big":
        ax[1].plot(data["date"], data['inv_crypto'], "--", label="Initial", color="black")
    my_color = "red" if change_crypto[0] == "-" else "green"
    ax[1].legend(prop={"size": 10}).texts[0].set_color(my_color)

    ax[2].set_ylabel(f"Total Fiat Investments [{what}]", size=10)
    ax[2].plot(data["date"], data["total_fiat"], label=change_fiat, color="blue")
    if how == "big":
        ax[2].plot(data["date"], data['inv_fiat'], "--", label="Initial", color="black")
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
