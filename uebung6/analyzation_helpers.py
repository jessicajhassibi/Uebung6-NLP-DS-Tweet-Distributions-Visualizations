import string
import datetime


def get_wrongly_classified_tweets(tweets_list: list) -> list:
    """
    Checks if tweet sentiment has been classified correctly.
    Returns list of all incorrect classified tweets.
    :param tweets_list: list
    :return: wrongly_classified_tweets: list
    """
    wrongly_classified_tweets = []

    for tweet in tweets_list:
        correct = tweet["annotation"]
        prediction = tweet["predicted-sentiment"]
        print("correct sentiment: ", correct)
        print("predicted sentiment: ", prediction)
        if correct != prediction:
            wrongly_classified_tweets.append(tweet)
            print("Classification wrong -> add to list\n")
        else:
            print("Yeay! Classification succeeded!\n")
    return wrongly_classified_tweets


def get_most_frequent_words(tweets_list: list) -> list:
    """
    Returns 10 most common words and number of their occasions (as tuple) in tweets list.
    :param tweets_list: list
    :return: most_frequent_words: list
    """

    words_frequency = {}
    for tweet in tweets_list:
        tokens_pos_attributes_list = tweet["tokens-pos-attributes"]
        for token in tokens_pos_attributes_list:
            token_text = token.get("text")
            if token.get("stop"):
                # print("Don't count stop word: '" + token_text + "'")
                pass

            elif token_text in string.punctuation:
                # print("Don't count punctuation mark: ", token_text)
                pass

            elif token_text.isspace():
                # print("Don't count white space.")
                pass

            elif not token_text.isalpha():
                # print("Don't count if not a word: ", token_text)
                pass

            else:

                try:
                    frequency = words_frequency.get(token_text)
                    frequency += 1
                    words_frequency[token_text] = frequency

                except Exception:
                    words_frequency[token_text] = 1

    print("\nMost frequent words in wrongly classified tweets:")
    most_frequent_words = get_top10(words_frequency)

    return most_frequent_words


def analyze_most_frequent_hashtags(tweets_list: list) -> (list, list):
    """
    Iterates through tweets in tweets_list, and saves all used hashtags.
    For each hashtag the sentiment counts (0: negative, 1: neutral, 2: positive) are saved
    and a list of [negative_frequency, neutral_frequency, positive_frequency].
    Returns tuple of (most_frequent_hashtags, most_frequent_hashtags_sentiments)
    :param tweets_list: list
    :return: (most_frequent_hashtags, most_frequent_hashtags_sentiments): tuple(list, list)
    """

    hashtags_frequency = {}
    hashtags_sentiments = {}  # saves list of ints [negative, neutral, positive] as sentiment count for each hashtag

    for tweet in tweets_list:
        hashtags = tweet["hashtags"]
        sentiment = tweet["predicted-sentiment"]

        if len(hashtags) != 0:
            for hashtag in hashtags:
                try:
                    frequency = hashtags_frequency.get(hashtag)
                    frequency += 1
                    hashtags_frequency[hashtag] = frequency

                    sentiments_frequency = hashtags_sentiments.get(hashtag)
                    negative_frequency = sentiments_frequency[0]
                    neutral_frequency = sentiments_frequency[1]
                    positive_frequency = sentiments_frequency[2]

                    if sentiment == 0:
                        negative_frequency += 1
                    elif sentiment == 1:
                        neutral_frequency += 1
                    else:
                        positive_frequency += 1

                except Exception:
                    # hashtag not in dict -> add user to dict and set frequency to 1
                    hashtags_frequency[hashtag] = 1

                    negative_frequency = 0
                    neutral_frequency = 0
                    positive_frequency = 0

                    if sentiment == 0:
                        negative_frequency = 1
                    elif sentiment == 1:
                        neutral_frequency = 1
                    else:
                        positive_frequency = 1

                # update sentiment frequencies for user
                hashtags_sentiments[hashtag] = [negative_frequency, neutral_frequency, positive_frequency]

    print("\nMost frequent hashtags in tweet list:")
    most_frequent_hashtags = get_top10(hashtags_frequency)
    most_frequent_hashtags_sentiments = []

    for hashtag, frequency in most_frequent_hashtags:
        sentiment = hashtags_sentiments.get(hashtag)
        most_frequent_hashtags_sentiments.append((hashtag, sentiment))

    return most_frequent_hashtags, most_frequent_hashtags_sentiments


def most_frequent_wrongly_classified_hashtags(tweets_list: list) -> list:
    """
    Returns List of 10 most often wrongly classified hashtags as 4 tuples:
    (hashtag, total_frequency, incorrect_num, incorrect_percentage)
    If hashtag appears only up to 2 times, it will not appear in list, even if it would be one of the top 10.
    :param tweets_list: list
    :return: most_frequent_hashtags_wrongly_classified: list
    """

    hashtags_frequency = {}
    hashtags_sentiments_incorrect = {}  # saves hashtags with number of incorrect classifications

    for tweet in tweets_list:
        hashtags = tweet["hashtags"]
        sentiment = tweet["predicted-sentiment"]

        if len(hashtags) != 0:
            for hashtag in hashtags:
                try:
                    frequency = hashtags_frequency.get(hashtag)
                    frequency += 1
                    hashtags_frequency[hashtag] = frequency

                    correct_sentiment = tweet["annotation"]
                    if sentiment != correct_sentiment:
                        incorrect_num = hashtags_sentiments_incorrect.get(hashtag)
                        incorrect_num += 1
                        hashtags_sentiments_incorrect[hashtag] = incorrect_num

                except Exception:
                    # hashtag not in dict -> add user to dict and set frequency to 1
                    hashtags_frequency[hashtag] = 1

                    correct_sentiment = tweet["annotation"]
                    if sentiment != correct_sentiment:
                        hashtags_sentiments_incorrect[hashtag] = 1
                    else:
                        hashtags_sentiments_incorrect[hashtag] = 0  # Initialize hashtag with incorrect number of 0

    print("\nMost frequent wrongly classified hashtags in tweet list and number of incorrect occasions:")
    most_frequent_wrongly_classified = get_top10(hashtags_sentiments_incorrect)
    most_frequent_hashtags_wrongly_classified = []

    for hashtag, incorrect_num in most_frequent_wrongly_classified:

        total_frequency = hashtags_frequency.get(hashtag)
        if total_frequency >= 3:
            incorrect_percentage = incorrect_num / total_frequency
            most_frequent_hashtags_wrongly_classified.append(
                (hashtag, total_frequency, incorrect_num, incorrect_percentage))
            print("-> Tweets mit dem Hashtag", hashtag, "werden mit", round(incorrect_percentage * 100),
                  "Prozent Wahrscheinlichkeit falsch klassifiziert.")
        else:
            break

    return most_frequent_hashtags_wrongly_classified


def analyze_most_active_users(tweets_list: list) -> (list, list):
    """
    Extracts the 10 users out of tweets_list who authored the highest numbers of tweets.
    Returns list of those users and the distribution of sentiments of their tweets.
    Second list returned holds the users and distribution of activity on the weekdays.
    :param tweets_list: list
    :return: (most_active_users_sentiments, most_active_users_tweet_days): tuple(list, list)
    """
    users_frequency = {}
    users_sentiments = {}
    users_tweet_days = {}

    for tweet in tweets_list:
        user = tweet["author_name"]
        sentiment = tweet["predicted-sentiment"]
        date = tweet["created_at"]
        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))  # convert to datetime.datetime object
        weekday = date.weekday()  # Monday = 0 -> Sunday = 6
        try:
            # update users_frequency dict
            frequency = users_frequency.get(user)
            frequency += 1
            users_frequency[user] = frequency

            sentiments_frequency = users_sentiments.get(user)
            negative_frequency = sentiments_frequency[0]
            neutral_frequency = sentiments_frequency[1]
            positive_frequency = sentiments_frequency[2]

            if sentiment == 0:
                negative_frequency += 1
            elif sentiment == 1:
                neutral_frequency += 1
            else:
                positive_frequency += 1

            # update number on weekday
            new_value = users_tweet_days[user][weekday]
            new_value += 1
            users_tweet_days[user][weekday] = new_value

        except Exception:
            # user not in dict -> add user to dict and set frequency to 1
            users_frequency[user] = 1

            negative_frequency = 0
            neutral_frequency = 0
            positive_frequency = 0

            if sentiment == 0:
                negative_frequency = 1
            elif sentiment == 1:
                neutral_frequency = 1
            else:
                positive_frequency = 1

            # create weekday counter list
            users_tweet_days[user] = [0, 0, 0, 0, 0, 0, 0]
            # update number on weekday
            users_tweet_days[user][weekday] = 1

        # update sentiment frequencies for user
        users_sentiments[user] = [negative_frequency, neutral_frequency, positive_frequency]

    print("Top 10 most active users:")
    most_active_users = get_top10(users_frequency)

    most_active_users_sentiments = []
    most_active_users_tweet_days = []

    for user, frequencies in most_active_users:
        user_sentiments = users_sentiments.get(user)
        most_active_users_sentiments.append((user, user_sentiments))

        user_weekdays = users_tweet_days.get(user)
        most_active_users_tweet_days.append((user, user_weekdays))

    return most_active_users_sentiments, most_active_users_tweet_days


def get_top10(frequency_dictionary: dict) -> list:
    """
    Returns list of 10 (key, value) tuples of the keys with highest values in dictionary.
    :param frequency_dictionary: dict
    :return: most_frequent_list: list
    """
    max_value = 0
    max_key = None
    most_frequent_list = []
    for i in range(10):
        for key in frequency_dictionary:
            if frequency_dictionary.get(key) > max_value:
                max_key = key
                max_value = frequency_dictionary.get(key)
        print("No.", i + 1, ": ", max_key, "with", max_value, "occurrences.")
        most_frequent_list.append((max_key, max_value))
        del frequency_dictionary[max_key]
        max_value = 0
        max_key = None
    print()
    return most_frequent_list


def get_tweet_daily_hourly_frequency(tweets_list: list) -> (dict, dict):
    """
    Fist dict returned holds the average tweet frequencies for each weekday
    -> weekdays as keys and daily tweet numbers as values
    Second dict returned holds the average number of tweets posted in each hour of a full week.
    -> all hours as keys and daily tweet numbers as values
    :param tweets_list: list
    :return: (weekday_tweet_avg, hour_tweet_avg): tuple(dict, dict):
    """

    tweets_days_hours = {}  # holds each day mentioned with hours list in tweet_list
    for tweet in tweets_list:
        date = tweet["created_at"]
        date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
        day = date.date()
        hour = date.hour

        try:
            day_hours_list = tweets_days_hours.get(day)
            new_hour_val = day_hours_list[hour] + 1
            day_hours_list[hour] = new_hour_val
            tweets_days_hours[day] = day_hours_list

        except Exception:
            init_day_hours_list = []
            for i in range(24):
                init_day_hours_list.append(0)  # initialze num of tweets for each hour of new day with 0
            init_day_hours_list[hour] = 1  # set tweet counter on the right hour of the day to 1
            tweets_days_hours[day] = init_day_hours_list

    weekday_tweet_lists = {0: [],  # save lists in a list for each weekday
                           1: [],
                           2: [],
                           3: [],
                           4: [],
                           5: [],
                           6: []}

    for day in tweets_days_hours:
        weekday = day.weekday()
        day_hours = tweets_days_hours.get(day)
        # weekday_day_hours = weekday_tweet_lists.get(weekday)
        # new_weekday_day_hours = [sum(x) for x in zip(day_hours, weekday_day_hours)]
        weekday_tweet_lists[weekday].append(day_hours)

    # For the average tweet occcurences of each hour:
    hour_keys = range(168)
    hour_tweet_avg = dict.fromkeys(hour_keys)

    # For the average tweet occcurences of each weekday:
    day_keys = range(7)  # Monday = 0 ...Sunday = 6
    weekday_tweet_avg = dict.fromkeys(day_keys)

    hour_of_168 = 0
    for weekday in weekday_tweet_lists:
        total_hour_tweets = []
        for i in range(24):
            total_hour_tweets.append(0)

        weekday_lists = weekday_tweet_lists.get(weekday)
        total_weekday_occurences = len(weekday_lists)
        total_weekday_tweets = 0

        for day_list in weekday_lists:
            total_weekday_tweets += sum(day_list)

            total_hour_tweets = [sum(x) for x in zip(day_list, total_hour_tweets)]

        for hour in total_hour_tweets:
            hour_avg = round(hour / total_weekday_occurences)
            hour_tweet_avg[hour_of_168] = hour_avg
            hour_of_168 += 1
            print(hour_of_168)

        average_tweets_weekday = round(total_weekday_tweets / total_weekday_occurences)
        weekday_tweet_avg[weekday] = average_tweets_weekday


    print(hour_tweet_avg)
    return weekday_tweet_avg, hour_tweet_avg
