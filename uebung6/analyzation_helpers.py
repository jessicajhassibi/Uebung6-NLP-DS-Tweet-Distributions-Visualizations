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
                #print("Don't count stop word: '" + token_text + "'")
                pass

            elif token_text in string.punctuation:
                #print("Don't count punctuation mark: ", token_text)
                pass

            elif token_text.isspace():
                #print("Don't count white space.")
                pass

            elif not token_text.isalpha():
                #print("Don't count if not a word: ", token_text)
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
            incorrect_percentage = incorrect_num/total_frequency
            most_frequent_hashtags_wrongly_classified.append(
                (hashtag, total_frequency, incorrect_num, incorrect_percentage))
            print("-> Tweets mit dem Hashtag", hashtag, "werden mit", round(incorrect_percentage*100),
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


def get_tweet_weekday_frequency(tweets_list: list) -> dict:
    """
    Returns the average tweet frequencies for each weekday as a list.
    :param tweets_list: list
    :return: dictionary with weekdays as keys and daily tweet numbers as values
    """
    # For the average tweet occcurences of each weekday:
    day_keys = [0,1,2,3,4,5,6] # Monday = 0 ...Sunday = 6
    weekday_tweet_avg = dict.fromkeys(day_keys)

    days = {} # holds each mentioned day in tweet_list
    for tweet in tweets_list:
        date = tweet["created_at"]
        date = date[:10] # just leave year, month, day value
        day = datetime.datetime.fromisoformat(date)
        try:
            current_day_frequency = days.get(day)
            new_current_day_frequency = current_day_frequency + 1
            days[day] = new_current_day_frequency
        except Exception:
            days[day] = 1

    # saving daily tweet numbers for each weekday
    weekday_tweet_lists = {0: [],  # Monday = 0 ...
                         1: [],
                         2: [],
                         3: [],
                         4: [],
                         5: [],
                         6: []}  # Sunday = 6

    # iterate through day dict and calc
    for day in days:
        weekday = day.weekday()
        weekday_tweet_lists[weekday].append(days[day])

    for weekday in range(7):
        weekday_numbers = weekday_tweet_lists.get(weekday)
        weekday_total = len(weekday_numbers) # total occurrences of certain weekday
        # calc avg
        weekday_avg = round(sum(weekday_numbers)/weekday_total)
        weekday_tweet_avg[weekday] = weekday_avg

    return weekday_tweet_avg
