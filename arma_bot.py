import os
import datetime
from time import sleep
from threading import Thread

from arma_model import AVDataStream, StatsModel, TwitterOutput, main
from bot import Bot


def get_timings(is_first_iter=True):
    # Get current time
    time = datetime.datetime.now()

    # Get target time in US/Eastern
    target_time = time + datetime.timedelta(hours=3, minutes=5)
    if is_first_iter:
        hour = time.hour
        minute = time.minute + 1
        # Check whether we're at the end of the hour
        if (minute % 60) < time.minute:
            hour = time.hour + 1
            minute = 0

        # Number of seconds after the minute to wait
        n_past = 1

        # Time at which loop will be run
        check_next = time.replace(hour=hour, minute=minute, second=n_past)

        delta_t = check_next - time

        secs = delta_t.seconds

    else:
        secs = 60
        
    return (secs, target_time)


def run_loop(bot):
    # First loop we only wait until n_past the next minute
    secs, target_time = get_timings(is_first_iter=True)
    main(bot, target_time)
    sleep(secs)

    while True:
        secs, target_time = get_timings(is_first_iter=False)
        main(bot, target_time)
        sleep(secs)


if __name__ == '__main__':
    # Get keys
    ALPHAVANTAGE_API_KEY = os.environ['ALPHAVANTAGE_API_KEY']
    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    ACCESS_KEY = os.environ['ACCESS_KEY'] 
    ACCESS_SECRET = os.environ['ACCESS_SECRET']
    
    # Create DataStream
    datastream = AVDataStream(api_key=ALPHAVANTAGE_API_KEY)

    # Create Model
    model = StatsModel()

    # Create Output
    output = TwitterOutput(consumer_key=CONSUMER_KEY,
                           consumer_secret=CONSUMER_SECRET,
                           access_key=ACCESS_KEY,
                           access_secret=ACCESS_SECRET)

    # Create Bot
    bot = Bot(datastream, model, output)

    # Start datastream
    bot.start_stream()

    # Start Twitter output
    bot.start_output()
    
    thread = Thread(target=run_loop,args=[bot])
    thread.start()   
