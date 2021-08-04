import json
import matplotlib.pyplot as plt
import numpy as np
import analyzation_helpers


class PlotterUebung6():
    """
    Holds methods for analyzing the tweet dataset and plotting its data in various charts.
    """

    def __init__(self, infile_path:str) -> None:
        self.infile_path = infile_path

        with open(infile_path, mode="r", encoding="utf-8") as fin:
            self.tweets_list = json.load(fin)

        self.most_active_users_sentiments, \
        self.most_active_users_tweet_days = analyzation_helpers.analyze_most_active_users(self.tweets_list)

        self.most_frequent_hashtags, \
        self.most_frequent_hashtags_sentiments = analyzation_helpers.analyze_most_frequent_hashtags(self.tweets_list)

        self.weekday_frequency = analyzation_helpers.get_tweet_weekday_frequency(self.tweets_list)

    def sentiment_distribution(self):
        """
        Plots the numbers of negative, neutral and positive tweets in tweets list.
        Plot will be a simple bar chart.
        :return: None
        """
        negative = neutral = positive = 0
        total = 0
        for tweet in self.tweets_list:
            prediction = tweet["predicted-sentiment"]
            if prediction == 0:
                negative += 1
            elif prediction == 1:
                neutral += 1
            else:
                positive += 1
            total += 1

        print("Sentiment distribution of", total, "tweets:")
        print("---> negative:", negative, "neutral:", neutral, "positive:", positive)

        labels = ["Negative", "Neutral", "Positive"]
        counts = [negative, neutral, positive]
        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        rect = ax.bar(x, counts, width, label=labels)

        ax.set_ylabel('Number of tweets')
        ax.set_title('Sentiment distribution of dataset')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.bar_label(rect) # you might need to update to latest version: conda install -c conda-forge matplotlib==3.4.2
        fig.tight_layout()
        plt.show()

    def token_distribution(self):
        """
        Plots the distribution of POS used in tokenized tweets.
        Plot will be a pie chart.
        :return: None
        """
        tokens = {}
        for tweet in self.tweets_list:
            token_list = tweet["tokens-pos-attributes"]
            for token in token_list:
                pos_token = token.get("pos")
                try:
                    pos_value = tokens.get(pos_token)
                    pos_value += 1
                    tokens[pos_token] = pos_value

                except Exception:
                    tokens[pos_token] = 1

        pos = tokens.keys()
        pos_counts = tokens.values()
        fig, ax = plt.subplots()
        ax.set_title('POS distribution of dataset')
        ax.pie(pos_counts, labels=pos, autopct='%1.1f%%')
        ax.axis("equal")
        plt.show()

    def top10_hashtags(self):
        """
        Plots the top 10 used hashtags in a dataset.
        Plot will be a bar chart.
        :return: None
        """
        hashtags, counts = [], []

        for hashtag, count in self.most_frequent_hashtags:
            hashtags.append(hashtag)
            counts.append(count)

        x = np.arange(len(hashtags))

        fig, ax = plt.subplots()
        rect = ax.bar(x, counts, label=hashtags)

        ax.set_ylabel('Number of occasions')
        ax.set_title('Top 10 used hashtags in dataset')
        ax.set_xticks(x)
        ax.set_xticklabels(hashtags, rotation="vertical")

        ax.bar_label(rect)  # for using bar_label() you might need to update to latest version: conda install -c conda-forge matplotlib==3.4.2
        fig.tight_layout()
        plt.show()

    def top10_hashtags_sentiments(self):
        """
        Plots the top 10 used hashtags in a dataset and distribution of their sentiment.
        Plot will be a stacked bar chart.
        :return: None
        """
        hashtags, sentiment_distributions = [], []

        for hashtag, sentiment_distribution in self.most_frequent_hashtags_sentiments:
            hashtags.append(hashtag)
            sentiment_distributions.append(sentiment_distribution)

        negative_list, neutral_list, positive_list = [], [], []

        for [negative, neutral, positive] in sentiment_distributions:
            negative_list.append(negative)
            neutral_list.append(neutral)
            positive_list.append(positive)

        negative_array = np.array(negative_list)
        neutral_array = np.array(neutral_list)
        positive_array = np.array(positive_list)

        x = np.arange(len(hashtags))

        fig, ax = plt.subplots()

        ax.set_ylabel('Number of hashtags')
        ax.set_title('Top 10 hashtags and distribution of their sentiment')
        ax.set_xticks(x)
        ax.set_xticklabels(hashtags, rotation="vertical")

        ax.bar(hashtags, negative_array, label="Negative")
        ax.bar(hashtags, neutral_array, bottom=negative_array, label="Neutral")
        ax.bar(hashtags, positive_array, bottom=neutral_array + negative_array, label="Positive")

        # Adding text to bars telling the exact numbers for the sentiments and total tweet number of user
        for xpos, ypos, yval in zip(x, negative_array / 2, negative_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, negative_array + neutral_array / 2, neutral_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, negative_array + neutral_array + positive_array / 2, positive_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        total = negative_array + neutral_array + positive_array
        for xpos, ypos, yval in zip(x, negative_array + neutral_array + positive_array, total):
            plt.text(xpos, ypos, "N=" + str(yval), ha="center", va="bottom")

        ax.legend()
        plt.show()

    def top10_users_sentiments(self):
        """
        Plots the top 10 most active users in a dataset and distribution of their tweets sentiments.
        Plot will be a stacked bar chart.
        :return: None
        """
        users, sentiment_distributions = [], []

        for user, sentiment_distribution in self.most_active_users_sentiments:
            users.append(user)
            sentiment_distributions.append(sentiment_distribution)

        negative_list, neutral_list, positive_list = [], [], []

        for [negative, neutral, positive] in sentiment_distributions:
            negative_list.append(negative)
            neutral_list.append(neutral)
            positive_list.append(positive)

        negative_array = np.array(negative_list)
        neutral_array = np.array(neutral_list)
        positive_array = np.array(positive_list)

        # Plot Users and their tweet number
        x = np.arange(len(users))

        fig, ax = plt.subplots()

        ax.set_ylabel('Number of tweets')
        ax.set_title('Top 10 users and distribution of sentiment of their tweets')
        ax.set_xticks(x)
        ax.set_xticklabels(users, rotation="vertical")

        ax.bar(users, negative_array, label="Negative")
        ax.bar(users, neutral_array, bottom=negative_array, label="Neutral")
        ax.bar(users, positive_array, bottom=neutral_array + negative_array, label="Positive")

        # Adding text to bars telling the exact numbers for the sentiments and total tweet number of user
        for xpos, ypos, yval in zip(x, negative_array / 2, negative_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, negative_array + neutral_array / 2, neutral_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, negative_array + neutral_array + positive_array / 2, positive_array):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        total = negative_array + neutral_array + positive_array
        for xpos, ypos, yval in zip(x, negative_array + neutral_array + positive_array, total):
            plt.text(xpos, ypos, "N=" + str(yval), ha="center", va="bottom")

        ax.legend()
        plt.show()

    def top10_users_weekdays(self):
        """
        Plots the top 10 most active users in a dataset and distribution of their tweets over a week.
        Plot will be a stacked bar chart.
        :return: None
        """
        users, weekdays_distributions = [], []

        for user, weekday_distribution in self.most_active_users_tweet_days:
            users.append(user)
            weekdays_distributions.append(weekday_distribution)

        monday, tuesday, wednesday, thursday, friday, saturday, sunday = [], [], [], [], [], [], []

        for [mo, tu, we, th, fr, sa, su] in weekdays_distributions:
            monday.append(mo)
            tuesday.append(tu)
            wednesday.append(we)
            thursday.append(th)
            friday.append(fr)
            saturday.append(sa)
            sunday.append(su)

        mo_arr = np.array(monday)
        tu_arr = np.array(tuesday)
        we_arr = np.array(wednesday)
        th_arr = np.array(thursday)
        fr_arr = np.array(friday)
        sa_arr = np.array(saturday)
        su_arr = np.array(sunday)

        # Plot top 10 Users and their tweets weekday distribution
        x = np.arange(len(users))

        fig, ax = plt.subplots()

        ax.set_ylabel('Number of tweets')
        ax.set_title('Top 10 users and distribution of daily tweets')
        ax.set_xticks(x)
        ax.set_xticklabels(users, rotation="vertical")

        ax.bar(users, mo_arr, label="Monday")
        ax.bar(users, tu_arr, bottom=mo_arr, label="Tuesday")
        ax.bar(users, we_arr, bottom=mo_arr + tu_arr, label="Wednesday")
        ax.bar(users, th_arr, bottom=mo_arr + tu_arr + we_arr, label="Thursday")
        ax.bar(users, fr_arr, bottom=mo_arr + tu_arr + we_arr + th_arr, label="Friday")
        ax.bar(users, sa_arr, bottom=mo_arr + tu_arr + we_arr + th_arr + fr_arr, label="Saturday")
        ax.bar(users, su_arr, bottom=mo_arr + tu_arr + we_arr + th_arr + fr_arr + sa_arr, label="Sunday")

        # Adding text to bars telling the exact numbers for the sentiments and total tweet number of user
        for xpos, ypos, yval in zip(x, mo_arr / 2, mo_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr / 2, tu_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr + we_arr / 2, we_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr + we_arr + th_arr / 2, th_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr + we_arr + th_arr + fr_arr / 2, fr_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr + we_arr + th_arr + fr_arr + sa_arr / 2, sa_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        for xpos, ypos, yval in zip(x, mo_arr + tu_arr + we_arr + th_arr + fr_arr + sa_arr + su_arr / 2, su_arr):
            plt.text(xpos, ypos, yval, ha="center", va="center")

        total = mo_arr + tu_arr + we_arr + th_arr + fr_arr + sa_arr + su_arr
        for xpos, ypos, yval in zip(x,total, total):
            plt.text(xpos, ypos, "N=" + str(yval), ha="center", va="bottom")

        ax.legend()
        plt.show()

    def hourly_tweets(self):
        pass

    def daily_tweets(self):
        print("Average Tweets on a Monday: ", self.weekday_frequency.get(0))
        print("Average Tweets on a Tuesday: ", self.weekday_frequency.get(1))
        print("Average Tweets on a Wednesday: ", self.weekday_frequency.get(2))
        print("Average Tweets on a Thursday: ", self.weekday_frequency.get(3))
        print("Average Tweets on a Friday: ", self.weekday_frequency.get(4))
        print("Average Tweets on a Saturday: ", self.weekday_frequency.get(5))
        print("Average Tweets on a Sunday: ", self.weekday_frequency.get(6))

        weekdays = self.weekday_frequency.keys()
        tweets = self.weekday_frequency.values()

        labels = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        counts = tweets
        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        rect = ax.bar(x, counts, width, label=labels)

        ax.set_ylabel('Number of tweets')
        ax.set_title('Daily average tweets')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.bar_label(rect)
        fig.tight_layout()
        plt.show()