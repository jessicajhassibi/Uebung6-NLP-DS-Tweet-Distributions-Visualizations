import io
import spacy
import numpy as np
import json

import torch
import re
import ffnetwork

class TweetPreprocessor():
    """
    Reads fastTextEmbeddings out of .vec file into dictionary when instantiated.
    Class methods implement further twitter data preprocessing.
    """

    def __init__(self, embeddings_path: str):
        self.embeddings_path = embeddings_path
        self.vocab = 0
        self.vecsize = 0
        self.vector_dict = self.load_vectors()

        self.embeddings = self.load_vectors()
        self.nlp = spacy.load("de_core_news_sm")

    def load_vectors(self):
        """
        Function to read fastText embeddings out of .vec file to a dictionary.
        Source: https://fasttext.cc/docs/en/crawl-vectors.html
        """
        fin = io.open(self.embeddings_path, 'r', encoding='utf-8', newline='\n', errors='ignore')
        n, d = map(int, fin.readline().split())
        self.vocab = n
        self.vecsize = d
        data = {}
        for line in fin:
            tokens = line.rstrip().split(' ')
            data[tokens[0]] = list(map(float, tokens[1:]))
        return data

    def convert_tweet(self, string: str) -> list():
        """
        Tokenizes twitter data via spacy and returns list of word vectors.
        """
        vectors = []  # List of word vectors of the string/ tweet

        try:
            for token in self.nlp(string):  # tokenizing via spacy
                value_list = self.vector_dict.get(token.text)
                if value_list is not None:  # ignore Vectors which are not in Fasttext
                    new_value_list = []
                    for value in value_list:
                        value_as_float = float(value)
                        new_value_list.append(value_as_float)
                    vectors.append(new_value_list)
        except Exception as e:
            print(e)
        return vectors

    def convert_dataset(self, infile_path: str, outfile_path: str):
        """
        Reads twitter dataset and preprocesses the tweets via convert_tweet method.
        Tweets are represented as max, min and avg vectors and saved with the other tweet data in the corresponding files.
        """
        with open(infile_path, mode="r", encoding="utf-8") as fin:
            tweets_list = json.load(fin)
            new_tweets_list = []
            for tweet in tweets_list:
                vector_list = self.convert_tweet(tweet["text"])

                if vector_list:  # if list not empty
                    max_vector = np.max(vector_list, 0)
                    min_vector = np.min(vector_list, 0)
                    avg_vector = np.average(vector_list, 0)
                    tweet["tweetmax"] = max_vector.tolist()
                    tweet["tweetmin"] = min_vector.tolist()
                    tweet["tweetavg"] = avg_vector.tolist()
                    new_tweets_list.append(tweet)

                else:  # no token in fasttext -> remove tweet from json file
                    pass

            with open(outfile_path, mode="w", encoding="utf-8") as fout:
                json_string = json.dumps(new_tweets_list, indent=4)
                fout.write(json_string)
                print("Wrote: ", outfile_path)
                fout.close()

    def preprocess_with_prediction(self, infile_path: str, outfile_path: str, model: ffnetwork.FeedForwardNetwork,
                                   tweet_representation: str):
        """
        Iterates through twitter data, tokenizes the tweets and performs POS tagging.
        Also finds all hashtags in a tweet.
        Then predicts sentiment with given model and writes preprocessed tweet to json file.
        """

        with open(infile_path, mode="r", encoding="utf-8") as fin:
            tweets_list = json.load(fin)
            new_tweets_list = []

            i = 0
            for tweet in tweets_list:
                print("Tokenizing and tagging tweet No. ", i)
                tweet_text_doc = self.nlp(tweet["text"])

                # Save hashtags of tweet in json
                hashtags = []
                indexes = [m.span() for m in re.finditer('#\w+', tweet["text"], flags=re.IGNORECASE)]
                for start, end in indexes:
                    hashtags.append(tweet["text"][start:end])
                tweet["hashtags"] = hashtags

                tokens_pos_attributes_list = []

                for token in tweet_text_doc:
                    token_pos_attributes = {"text": token.text, "lemma": token.lemma_, "pos": token.pos_,
                                            "tag": token.tag_, "dep": token.dep_, "shape": token.shape_,
                                            "alpha": token.is_alpha, "stop": token.is_stop}
                    tokens_pos_attributes_list.append(token_pos_attributes)

                tweet["tokens-pos-attributes"] = tokens_pos_attributes_list

                vector_list = self.convert_tweet(tweet["text"])

                if vector_list:  # if list not empty
                    if tweet_representation == "tweetmin":
                        vector = np.min(vector_list, 0)
                    elif tweet_representation == "tweetmax":
                        vector = np.max(vector_list, 0)
                    else:
                        vector = np.average(vector_list, 0)

                    with torch.no_grad():
                        model.to("cpu")

                        # set dropout and batch normalization layers to evaluation mode
                        model.eval()
                        # compute the prediction with the trained NN
                        processed_input = torch.FloatTensor([vector])

                        # 0 = negative, 1 = neutral, 2 = positive
                        model_pred = model(processed_input)
                        pred_class = torch.argmax(model_pred.data, 1)

                        tweet["predicted-sentiment"] = pred_class.item()

                        print("Text:", tweet["text"])
                        # Print Predicted Class
                        print("Label for Text:", str(pred_class.item()))

                    new_tweets_list.append(tweet)

                else:  # no token in fasttext -> remove tweet from json file
                    pass

                i += 1

            with open(outfile_path, mode="w", encoding="utf-8") as fout:
                json_string = json.dumps(new_tweets_list)
                fout.write(json_string)

            print("Wrote: ", outfile_path)

