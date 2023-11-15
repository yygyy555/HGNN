import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta
import pickle

'''2023.11.15'''
def identify_EP_SL_TP_in_long_strategy():
    # Save the results
    long_total_entry_points = []
    long_total_stop_loss = []
    long_total_take_profit = []
    long_total_exit_market = []

    # Read Signal file
    file_path = 'E:/Dimtech实习/Project 2/Signaux1.xlsx'
    sheet_name = 'NQ'
    signal = pd.read_excel(file_path, sheet_name=sheet_name)
    # Change the data type of the 'Date' column to string
    signal['Date'] = signal['Date'].astype(str)

    # Time Series folder location
    path = "E:/Dimtech实习/Project 2/NQ_20230914-20231109(0-24)"
    filelist = os.listdir(path)
    for filename in filelist:
        data = pd.read_csv(path + "/" + filename)

        # Extract date
        date_str = filename.split("_")[1].split(".")[0]
        # Convert date string to date object
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        # Format date object to specified format
        date = date_obj.strftime("%Y-%m-%d")
        # Get entry point value
        entry_point = signal.loc[(signal['Date'] == date) & (signal['Side'] == 'Buy'), 'Stop (or better)'].values[0]
        # Get stoploss value
        stoploss = signal.loc[(signal['Date'] == date) & (signal['Side'] == 'Buy'), 'StopLoss'].values[0]
        # Get takeprofit value
        takeprofit = signal.loc[(signal['Date'] == date) & (signal['Side'] == 'Buy'), 'TakeProfit'].values[0]
        # Define exit market time
        exit_market_time = date + ' 16:50:00'

        # Find practical entry point
        entry_points = []
        count = 0
        previous_value = data.iloc[0]  # Take the first line and the result is a Series

        for index, row in data.iterrows():
            current_value = row  # row is a Series

            # The condition of being an entry point：1.From small to large to reach the entry point value; 2.The previous and current points are both entry points.
            if (previous_value['Close'] < entry_point and current_value['Close'] >= entry_point) or (
                    previous_value['Close'] == current_value['Close'] and (
                    previous_value['Date'], count) in entry_points):
                count += 1
                entry_points.append((current_value['Date'], count))

            previous_value = current_value

        # Find practical stoploss and takeprofit and exitmarket
        stop_loss = []
        take_profit = []
        exit_market = []

        for i in entry_points:  # For every entry point
            stop_loss_time = date + ' 17:00:00'
            take_profit_time = date + ' 17:00:00'
            time_series = data[data['Date'] > i[0]]

            previous_value = time_series['Close'].iloc[0]
            for index, row in time_series.iterrows():  # Find stoploss. Once find one, end the loop.
                current_value = row['Close']
                if previous_value > stoploss and current_value <= stoploss:
                    stop_loss_time = row['Date']
                    break
                previous_value = current_value

            previous_value = time_series['Close'].iloc[0]
            for index, row in time_series.iterrows():  # Find takeprofit. Once find one, end the loop.
                current_value = row['Close']
                if previous_value < takeprofit and current_value >= takeprofit:
                    take_profit_time = row['Date']
                    break
                previous_value = current_value

            if stop_loss_time < take_profit_time and stop_loss_time < exit_market_time:
                stop_loss.append((stop_loss_time, i[1]))
            elif take_profit_time < exit_market_time:
                take_profit.append((take_profit_time, i[1]))
            else:
                exit_market.append((exit_market_time, i[1]))  # Find exitmarket

        long_total_entry_points.append(entry_points)
        long_total_stop_loss.append(stop_loss)
        long_total_take_profit.append(take_profit)
        long_total_exit_market.append(exit_market)

    # Save the results
    long_total_entry_points_file = open('E:/Dimtech实习/Project 2/long_total_entry_points.pickle', 'wb')
    pickle.dump(long_total_entry_points, long_total_entry_points_file)
    long_total_entry_points_file.close()
    long_total_stop_loss_file = open('E:/Dimtech实习/Project 2/long_total_stop_loss.pickle', 'wb')
    pickle.dump(long_total_stop_loss, long_total_stop_loss_file)
    long_total_stop_loss_file.close()
    long_total_take_profit_file = open('E:/Dimtech实习/Project 2/long_total_take_profit.pickle', 'wb')
    pickle.dump(long_total_take_profit, long_total_take_profit_file)
    long_total_take_profit_file.close()
    long_total_exit_market_file = open('E:/Dimtech实习/Project 2/long_total_exit_market.pickle', 'wb')
    pickle.dump(long_total_exit_market, long_total_exit_market_file)
    long_total_exit_market_file.close()

identify_EP_SL_TP_in_long_strategy()



# read the file
list_file = open('E:/Dimtech实习/Project 2/long_total_entry_points.pickle','rb')
long_total_entry_points = pickle.load(list_file)
list_file = open('E:/Dimtech实习/Project 2/long_total_stop_loss.pickle','rb')
long_total_stop_loss = pickle.load(list_file)
list_file = open('E:/Dimtech实习/Project 2/long_total_take_profit.pickle','rb')
long_total_take_profit = pickle.load(list_file)
list_file = open('E:/Dimtech实习/Project 2/long_total_exit_market.pickle','rb')
long_total_exit_market = pickle.load(list_file)



'''2023.11.15'''
def cal_probability_of_win_loss_exit(total_entry_points, total_stop_loss, total_take_profit, total_exit_market):
    # Initialize a 15-minute sliding window and 1-minute step size
    window_size = timedelta(minutes=15)
    step_size = timedelta(minutes=1)
    # Set the start and end time of the sliding window
    start_time = datetime.strptime('00:00:00', '%H:%M:%S')
    end_time = datetime.strptime('23:59:59', '%H:%M:%S')
    # Iterate to calculate the number of data points in each sliding window
    current_time = start_time
    while current_time + window_size <= end_time:
        window_end_time = current_time + window_size
        count_entry_point = 0
        count_stop_loss = 0
        count_take_profit = 0
        count_exit_market = 0
        for i, entry_points in enumerate(total_entry_points):
            index_entry_point = []
            for date, index in entry_points:
                time = datetime.strptime(date.split()[1], '%H:%M:%S')
                if current_time <= time <= window_end_time:
                    count_entry_point += 1
                    index_entry_point.append(index)
            count_stop_loss += len([elem for elem in total_stop_loss[i] if elem[1] in index_entry_point])
            count_take_profit += len([elem for elem in total_take_profit[i] if elem[1] in index_entry_point])
            count_exit_market += len([elem for elem in total_exit_market[i] if elem[1] in index_entry_point])
        print(current_time.strftime('%H:%M:%S'), window_end_time.strftime('%H:%M:%S'))
        print("The number of entry points is: ", count_entry_point)
        print("The number of stoploss is: ", count_stop_loss)
        print("The number of takeprofit is: ", count_take_profit)
        print("The number of exitmarket is: ", count_exit_market, "\n")
        current_time += step_size

cal_probability_of_win_loss_exit(total_entry_points = long_total_entry_points, total_stop_loss = long_total_stop_loss, total_take_profit = long_total_take_profit, total_exit_market = long_total_exit_market)
