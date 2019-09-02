import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import matplotlib.ticker as mtick

def read_crypto_data(symbol, past_hours = 48):
    
    cnx = mysql.connector.connect(user='pablo', 
                                  password='12345678',
                                  host='localhost',
                                  database='cryptos')

    cursor = cnx.cursor(buffered=True)

    if(cnx.is_connected() == False):
        return None
    
    date_time_obj = datetime.datetime.now()
    time_linux_now = date_time_obj.timestamp()
    time_start = time_linux_now - past_hours*3600;

    command = "SELECT * FROM " + symbol + " WHERE time_re > " + str(time_start) + ";"
    #print(command)
    try:
        cursor.execute(command)
        #cnx.commit()
        results = cursor.fetchall()
    except:
        return None
    
    if(cnx.is_connected()):
        cursor.close()
    
    results = pd.DataFrame(results)
    results.columns = ['time_re', 'price_usd', 'volume_usd', 'price_btc', 'volume_btc', 'time_lu']
    return results


def make_a_plot_1(data, symbol, name):
    
    fig = plt.figure(figsize=(13,10))#tight_layout=True)#figsize=(600,300))
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.35)
    ax = fig.subplots(nrows=4, ncols=1)
    
    time = list(data['time_re'])
    time = [(x-time[-1])/3600 for x in time]
    
    title_str = name + ': ' + str(data['price_usd'][len(data)-1]) + ' [usd]' 
    
    change_usd = str(round(100*((data['price_usd'][len(data)-1] - data['price_usd'][0])/data['price_usd'][0]), 2)) + '%'
    change_btc = str(round(100*((data['price_btc'][len(data)-1] - data['price_btc'][0])/data['price_btc'][0]), 2)) + '%'
    
    ax[0].set_ylabel('Price [usd]', size=8)
    ax[0].set_xlabel('Time [hs]', size=8)
    ax[0].plot(time,data['price_usd'], label= change_usd)
    my_color = 'red' if change_usd[0] == '-' else 'green'
    ax[0].legend(prop={'size': 10}).texts[0].set_color(my_color)

    ax[1].set_ylabel('Volume [usd]', size=8)
    ax[1].ticklabel_format(style='sci', axis='y')
    ax[1].set_xlabel('Time [hs]', size=8)
    ax[1].plot(time, data['volume_usd'], color='red')
    ax[1].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
    
    ax[2].set_ylabel('Price [btc]', size=8)
    ax[2].set_xlabel('Time [hs]', size=8)    
    ax[2].plot(time,data['price_btc'], label = change_btc)
    ax[2].ticklabel_format(style='sci', axis='y')
    my_color = 'red' if change_btc[0] == '-' else 'green'
    ax[2].legend(prop={'size': 10}).texts[0].set_color(my_color)
    
    ax[3].set_ylabel('Volume [btc]', size=8)
    ax[3].ticklabel_format(style='sci', axis='y')
    ax[3].set_xlabel('Time [hs]', size=8)
    ax[3].plot(time, data['volume_btc'], color='red')
    ax[3].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))

    plt.savefig( "./img/" + symbol + ".jpg", dpi=100, bbox_inches='tight')
    plt.close()


#main function

list_of_coins = pd.read_csv('list_id_symbol_name_coingecko.csv')
list_of_coins.columns = ['id', 'symbol', 'name']


report_file = open("report_evolutions.html","w")

for i in range(list_of_coins.shape[0]):

    print(i, " -> ")
    print("\t id: ", list_of_coins['id'][i])
    print("\t Symbol: ", list_of_coins['symbol'][i].upper())
    print("\t Name: ", list_of_coins['name'][i])

    data = read_crypto_data(list_of_coins['symbol'][i].upper(), 48)
    make_a_plot_1(data, list_of_coins['symbol'][i].upper(), list_of_coins['name'][i])

    text = '<p><font size="9" color="black">' + str(i+1) + ") " + list_of_coins['name'][i] + '</font></p>'
    report_file.write(text + '\n')
    
    
    change_usd = str(round(100*((data['price_usd'][len(data)-1] - data['price_usd'][0])/data['price_usd'][0]), 2)) + '%'
    change_btc = str(round(100*((data['price_btc'][len(data)-1] - data['price_btc'][0])/data['price_btc'][0]), 2)) + '%'
    
    text = '<p><font size="6" color="black"> Price (usd) [' + str(change_usd) + ']: ' + str(data['price_usd'][len(data)-1]) + '</font></p>'
    report_file.write(text + '\n')
    
    text = '<p><font size="6" color="black"> Price (btc) [' + str(change_btc) + ']: ' + str(data['price_btc'][len(data)-1]) + '</font></p>'
    report_file.write(text + '\n')
    
    text = '<figure> <img src = "./img/' + list_of_coins['symbol'][i].upper() + '.jpg"> </figure>'
    report_file.write(text + '\n')
    
    report_file.write('<p></p>\n'*3)
    
report_file.close()



