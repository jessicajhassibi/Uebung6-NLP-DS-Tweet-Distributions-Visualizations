import json
import krippendorff_alpha_impl

class DisambiguationAnalyzer():

    def __init__(self, infile_path: str):

        with open(infile_path, mode="r", encoding="utf-8") as fin:
            self.tweets_list = json.load(fin)

        self.annotations_array = self.get_annotations()
        self.calculate_iaa()

    def get_annotations(self) -> list:
        max_annotations = 0
        for tweet in self.tweets_list:
            num_annotators = len(tweet["annotations"])
            if num_annotators > max_annotations:
                max_annotations = num_annotators

        annotations_array = []

        for i in range(max_annotations):
            annotations_array.append([])

        for tweet in self.tweets_list:
            try:
                word = tweet["verb"]
            except Exception:
                try:
                    word = tweet["noun"]
                except Exception:
                    try:
                        word = tweet["adjective"]
                    except Exception:
                        pass

            word_annotations = tweet["annotations"]

            num_word_annotators = len(word_annotations)
            total_annotators = max_annotations
            missing_annotators = total_annotators - num_word_annotators

            i = 0
            for annotation in word_annotations:
                value = annotation.get("value").get("$numberLong")
                annotations_array[i].append(value)
                i+=1

            for missing_value in range(missing_annotators):
                annotations_array[i].append('*')
                i+=1

        return annotations_array

    def get_annotations2(self) -> list:
        max_annotations = 0
        for tweet in self.tweets_list:
            num_annotators = len(tweet["annotations"])
            if num_annotators > max_annotations:
                max_annotations = num_annotators

        annotations_array = []

        for i in range(max_annotations):
            annotations_array.append({})

        j= 0
        for tweet in self.tweets_list:
            try:
                word = tweet["verb"]
            except Exception:
                try:
                    word = tweet["noun"]
                except Exception:
                    try:
                        word = tweet["adjective"]
                    except Exception:
                        pass

            word_annotations = tweet["annotations"]

            num_word_annotators = len(word_annotations)
            total_annotators = max_annotations
            missing_annotators = total_annotators - num_word_annotators

            i = 0
            for annotation in word_annotations:
                value = annotation.get("value").get("$numberLong")
                annotations_array[i]["unit"+str(j)] = value
                i+=1

            j+=1
        return annotations_array

    def calculate_iaa(self):
        #print("nominal metric: %.3f" % krippendorff_alpha_impl.krippendorff_alpha(self.annotations_array, krippendorff_alpha_impl.nominal_metric, missing_items='*'))
        print("interval metric: %.3f" % krippendorff_alpha_impl.krippendorff_alpha(self.annotations_array, krippendorff_alpha_impl.interval_metric, missing_items='*'))