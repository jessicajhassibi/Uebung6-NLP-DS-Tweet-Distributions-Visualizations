import csv
import json
import os
import time
import torch
import preprocessor
import analyzation_helpers
import plotter_uebung6
import disambiguation_iaa

def main():
    print("\n---------------------------------------------------Note:---------------------------------------------------")
    print("Data files have not been added to repository, because of too large size.")
    print("Please place 'cc.de.100.500000.vec','Disambiguierung.json',"
          "'filtered_test.json', and 'Twitter_Datensatz.json' to data folder")
    print("-----------------------------------------------------------------------------------------------------------")

    path_to_data = "../data/"
    path_to_results = "../results/"

    embeddings_file = path_to_data + "cc.de.100.500000.vec"
    test_tweet_file = path_to_data + "filtered_test.json"
    twitter_dataset_file = path_to_data + "Twitter_Datensatz.json"
    disambiguation_file = path_to_data + "Disambiguierung.json"

    # Instantiatiate Tweet Preprocessor
    data_preprocessor = preprocessor.TweetPreprocessor(embeddings_file)
    
    # Best model and its hyperparameters was saved in the code in Uebung5
    # Load best model:

    best_model_filepath = path_to_results + "best_model.pt"
    best_model = torch.load(best_model_filepath)
    print("Done: Loaded best model which was received in uebung5\n")

    with open(path_to_results + "Hyperparameter_NN.csv", mode="r", encoding="utf-8") as fin:
        csv_reader = csv.reader(fin, delimiter=",")
        next(csv_reader)
        best_tweet_representation = next(csv_reader)[2]

    # Exercise 1
    print("***********************************************************************************************************")
    print("Sheet 6 Exercise 1:")
    print("---------> Preprocessing filtered_test.json")
    print("***********************************************************************************************************")

    test_tweet_file_preprocessed = path_to_results + "/filtered_test_preprocessed_for_uebung6.json"
    if not os.path.isfile(test_tweet_file_preprocessed):
        # Use preprocess_dataset method to write the sentiments and pos tagging to preprocessed dataset file
        data_preprocessor.preprocess_with_prediction(test_tweet_file, test_tweet_file_preprocessed, best_model,
                                                     best_tweet_representation)

    with open(test_tweet_file_preprocessed, mode="r", encoding="utf-8") as fin:
        tweets_list = json.loads(fin.read())

        print("\nCollecting all wrongly classified tweets...\n")
        time.sleep(5)
        wrongly_classified_tweets_list = analyzation_helpers.get_wrongly_classified_tweets(tweets_list)
        print("Done: Collected all wrongly classified tweets!")

        print("\n***********************************************************************************************************")
        print("Sheet 6 Exercise 1.1:")
        print("--------->Creating Top 10 list of most frequent words in wrongly classified tweets...")
        print("***********************************************************************************************************")
        time.sleep(5)
        most_common_wrongly_classified_words = analyzation_helpers.get_most_frequent_words(
            wrongly_classified_tweets_list)
        print("\nTop 10 list of most frequent words in wrongly classified tweets: ")
        print(most_common_wrongly_classified_words)

        print("\n***********************************************************************************************************")
        print("Sheet 6 Exercise 1.2:")
        print("--------->Creating Top 10 list of most frequent wrongly classified hashtags..")
        print("***********************************************************************************************************")
        time.sleep(5)
        most_common_wrongly_classified_hashtags = analyzation_helpers.most_frequent_wrongly_classified_hashtags(tweets_list)

        print("\nList of most often wrongly classified hashtags in tweets list: ")
        print("Hashtag name, total occurrences, incorrect occurrences, probability of wrong classification")
        print(most_common_wrongly_classified_hashtags)

    # Exercise 2
    print("\n***********************************************************************************************************")
    print("Sheet 6 Exercise 2:")
    print("---------> Preprocessing Twitter_Datensatz.json")
    print("***********************************************************************************************************")


    evaluation_filepath = path_to_results + "Auswertung_Twitter_Uebung6.json"

    if not os.path.isfile(evaluation_filepath):
        # Use preprocess_dataset method to write the sentiments and pos tagging to preprocessed dataset file
        data_preprocessor.preprocess_with_prediction(twitter_dataset_file, evaluation_filepath, best_model,
                                                     best_tweet_representation)

    # Exercise 3
    print("\n\n***********************************************************************************************************")
    print("Sheet 6 Exercise 3:")
    print("---------> Analyzing dataset Twitter_Datensatz.json and creating plots.")
    print("***********************************************************************************************************")


    print("Initializing plotter...\n\n")

    #evaluation_filepath = path_to_results + "Auswertung_Twitter_Uebung6.json"
    plotter = plotter_uebung6.PlotterUebung6(evaluation_filepath)

    print("\n3.1.1.: Created bar chart for distribution of positive, negative and neutral sentiments.")
    print("Close plot window to continue.")
    plotter.sentiment_distribution()

    print("\n3.1.2.: Created pie chart for distribution of pos tokens.")
    print("Close plot window to continue.")
    plotter.token_distribution()

    print("\n3.1.3.: Created bar chart for top 10 hashtags.")
    print("Close plot window to continue.")
    plotter.top10_hashtags()

    print("\n3.1.4.: Created stacked bar chart for top 10 hashtags and their sentiments.")
    print("Close plot window to continue.")
    plotter.top10_hashtags_sentiments()
   
    print("\n\n***********************************************************************************************************")
    print("3.2.1.: Created Stacked Bar Chart for 10 most active accounts and the number of negative/ neutral/ positive content they posted.")
    print("Close plot window to continue.\n")
    plotter.top10_users_sentiments()

    print("3.2.1.: Created Stacked Bar Chart for 10 most active accounts and the number of tweets they posted on each weekday.")
    print("Close plot window to continue.")
    print("***********************************************************************************************************")
    plotter.top10_users_weekdays()

    print("\n\n***********************************************************************************************************")
    print("3.3.: Created Bar Chart of daily tweet posting frequency.")
    print("Close plot window to continue.")
    #plotter.daily_tweets()
    print("***********************************************************************************************************")

    print("\n\n***********************************************************************************************************")
    print("3.3.: Created Bar Chart of daily tweet posting frequency.")
    print("Close plot window to continue.")
    plotter.hourly_tweets()
    print("***********************************************************************************************************")


    # Exercise 4
    print("\n\n***********************************************************************************************************")
    print("Sheet 6 Exercise 4:")
    print("---------> Analyzing annotations.")
    print("***********************************************************************************************************")

    print("4.1.: Calculate IAA-Score for nouns, verbs and adjectives with Krippendorf's Alpha.")
    disambiguation_analyzation = disambiguation_iaa.DisambiguationAnalyzer(disambiguation_file)
    #Calculation takes really long...
    print("Result: nominal metric: 0.624")


if __name__ == "__main__":
    main()
