import re, json
import pandas as pd
import numpy as np
from gensim import corpora
from gensim.models import LdaModel
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.corpus import stopwords  
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# nltk.download("punkt")
# nltk.download("wordnet")
# nltk.download("stopwords")
stop_words = list(stopwords.words("english"))


TOPICS_NUMBER = 5

# SUMMARY_JSON =""
# CSV_FILE = ""
CLUSTERS = "./commit_clusters.csv"
TOPICS_DOC = "./lda_results/topics"+(str)(TOPICS_NUMBER)+".txt" 
DELIMITER = "#"
chunk_size = 100

class Classifier:
    def __init__(self, repo):
        SUMMARY_JSON = f"./{repo}_commits_summary.json"
        CSV_FILE =f"./{repo}_commits.csv"
        self.cluster_centroids = []
        print("Classifier object created")
        print(SUMMARY_JSON)
        self.create_csv(SUMMARY_JSON, CSV_FILE)
        print("CSV file created")
        self.topic_modeling(CSV_FILE)
        print("Topic modeling done")


        ######
        #Below code is for classification based on the new prompt without using LDA
        # self.classify_commits2()
        # print("Classification done")
    
    def create_csv(self, SUMMARY_JSON, CSV_FILE):
        print(SUMMARY_JSON)
        with open(SUMMARY_JSON, "r") as file:
            data = json.load(file)
            with open(CSV_FILE, "w", newline='') as file:
                file.write("commitId#comment\n")
                for commit in data:
                    commit_hash = commit["commit_hash"]
                    # clean the text
                    summary = self.clean_text(commit["summary"])
                    file.write(commit_hash + DELIMITER + summary + "\n")
        file.close()

    def clean_text(self, text):
        # print(text)
        #Getting the parts of text inside the hash symbols for new commit structures
        text = text.split("#")
        cleaned_text = ""
        for i in range(1, len(text), 2):
            cleaned_text += text[i]+" "
        #ignore any numbers in the text
        cleaned_text = re.sub(r"\d+", "", cleaned_text)
        #ignore any floating point numbers in the text
        cleaned_text = re.sub(r"\d+\.\d+", "", cleaned_text)
        cleaned_text = cleaned_text.replace("\n", " ")
        # #remove data before the first semicolon if any
        # cleaned_text = cleaned_text.split(":", 1)[-1]
        cleaned_text = cleaned_text.replace("$", "")
        cleaned_text = cleaned_text.replace(":", "")
        cleaned_text = cleaned_text.replace("*", "")
        cleaned_text = re.sub(r"`.*?`", "", cleaned_text)
        cleaned_text = re.sub(r"'.*?'","", cleaned_text)
        cleaned_text = cleaned_text.replace("'", "")
        cleaned_text = cleaned_text.replace(".", " ")
        cleaned_text = cleaned_text.replace(",", "")
        cleaned_text = cleaned_text.replace("-", " ")
        cleaned_text = cleaned_text.replace("!", "")
        cleaned_text = cleaned_text.replace("\"", "")
        cleaned_text = cleaned_text.replace("#", "")
        cleaned_text = cleaned_text.replace("(", "")
        cleaned_text = cleaned_text.replace("<", "")
        cleaned_text = cleaned_text.replace(">", "")
        #convert all the text to lowercase
        cleaned_text = cleaned_text.lower()
        cleaned_text = cleaned_text.replace("=", "")
        cleaned_text = cleaned_text.replace(")", "")
        cleaned_text = re.sub(r"\b\w{1,2}\b", "", cleaned_text)
        cleaned_text = re.sub(r"\d+(?:\.\d*(?:[eE]\d+))?", " ", cleaned_text)
        cleaned_text = cleaned_text.replace("_", " ")
        cleaned_text = cleaned_text.lower()
        return cleaned_text
    
    # def topic_modeling(self):
    #     file_path = CSV_FILE
    #     vect = TfidfVectorizer(stop_words="english", max_features=1000)
    #     lda_model = LatentDirichletAllocation(
    #         n_components=TOPICS_NUMBER, learning_method="online", max_iter=10
    #     )

    #     # Dataframe to store the cluster information for each commit
    #     cluster_data = pd.DataFrame(columns=["commitId", "cleaned_text", "clusters"])

    #     for rev in pd.read_csv(file_path, chunksize=chunk_size, delimiter=DELIMITER):
    #         # rev["cleaned_text"] = rev["comment"].apply(self.clean_text)  # Clean the text
            
    #         rev["cleaned_text"] = rev["comment"]
    #         vect_text = vect.fit_transform(rev["cleaned_text"])

    #         lda_top = lda_model.fit_transform(vect_text)
    #         # print(lda_top.shape)
    #         # Find the clusters (topics) for each commit based on the threshold
    #         topics = []
    #         for row in lda_top:
    #             topic_indices = [i for i, val in enumerate(row) if val > 0.4]
    #             topics.append(topic_indices)
                
    #         # Add cluster information to the overall dataframe
    #         rev["clusters"] = topics
    #         rev["topic_relevance"] = [np.round(row, 4) for row in lda_top]
    #         cluster_data = pd.concat([cluster_data, rev[["commitId", "cleaned_text", "clusters", "topic_relevance"]]])
            
    #         ##Below code is to print the topics and their relevance to the words
    #         # for i in range (TOPICS_NUMBER):
    #         #     print("Topic", i, ":")
    #         #     #print words with their relevance to the topic
    #         #     zip_data = zip(vect.get_feature_names_out(), lda_model.components_[i])
    #         #     sorted_components = sorted(zip_data, key=lambda x: x[1], reverse=True)
    #         #     for t in sorted_components:
    #         #         print(t[0], ":",t[1],"," ,end=" ")
    #         #     print("\n")
            
    #         # vocab = vect.get_feature_names_out()
    #         # for i, comp in enumerate(lda_model.components_):
    #         #     vocab_comp = zip(vocab, comp)
    #         #     sorted_words = sorted(vocab_comp, key=lambda x: x[1], reverse=True)[:10]
    #         #     print("Topic", i, ":")
    #         #     for t in sorted_words:
    #         #         print(t[0], end=" ")
    #         #     print("\n")
        
    #     ##Save the above printed data into a file
    #     # with open(TOPICS_DOC, "w") as f:
    #     #     for i, comp in enumerate(lda_model.components_):
    #     #         vocab_comp = zip(vocab, comp)
    #     #         sorted_words = sorted(vocab_comp, key=lambda x: x[1], reverse=True)[:10]
    #     #         f.write("Topic " + str(i) + ":\n")
    #     #         for t in sorted_words:
    #     #             f.write(t[0] + " ")
    #     #         f.write("\n\n")
    #     # # Store the cluster information to a CSV file
    #     # cluster_data.to_csv(CLUSTERS, index=False)

    def preprocess(self, text):
        text = str(text)
        # print(text)
        if isinstance(text, str):  
            text = re.sub(r"\d+", "", text)
            text = re.sub(r"\d+\.\d+", "", text)
            tokens = simple_preprocess(text)
            tokens = [token for token in tokens if token not in STOPWORDS]
            return tokens
        else:
            return []  # Return an empty list if text is not a string

    def preprocess(self,text):
        #wite code such that text doesnt contain any numbers and nan values
        # text = text.replace("nan", "")
        # text = re.sub(r"\d+", "", text)
        # text = re.sub(r"\d+\.\d+", "", text)
        tokens = simple_preprocess(text)
        tokens = [token for token in tokens if token not in STOPWORDS]
        return tokens
    
    def topic_modeling(self, CSV_FILE):
        file_path = CSV_FILE
        data = pd.read_csv(file_path, delimiter=DELIMITER)
        # data["cleaned_text"] = data["comment"].apply(self.clean_text)
        data["cleaned_text"] = data["comment"]
        data["tokens"] = data["cleaned_text"].apply(self.preprocess)
        # data["tokens"] = data["cleaned_text"]
        
        dictionary = corpora.Dictionary(data["tokens"])
        corpus = [dictionary.doc2bow(text) for text in data["tokens"]]
        lda_model = LdaModel(corpus, num_topics=TOPICS_NUMBER, id2word=dictionary, passes=15)
        
        # coherence_model_lda = CoherenceModel(model=lda_model, texts=data["tokens"], dictionary=dictionary, coherence='c_v')
        # coherence_lda = coherence_model_lda.get_coherence()
        # print("Coherence Score: ", coherence_lda)
        
        # topics = lda_model.print_topics()
        # print("Topics: ")
        # for topic in topics:
        #     print(topic)

        # for i, row in data.iterrows():
            
        #     print("Commit", i, ":", row["comment"])
        #     print("Fitting: ", lda_model.get_document_topics(dictionary.doc2bow(row["tokens"])))
        #     print("Words: ")
        #     for word in row["tokens"]:
        #         if(lda_model.get_term_topics(dictionary.token2id[word]) != []):
        #             print(word, ":", lda_model.get_term_topics(dictionary.token2id[word]), end=", ")
        #     print("\n")

        # cluster_data = pd.DataFrame(columns=["commitId", "clusters_list", "topics", "cleaned_text"])
        # with open(CLUSTERS, "w") as f:
        #     for i, row in data.iterrows():
        #         topics = lda_model.get_document_topics(dictionary.doc2bow(row["tokens"]))
        #         relevante_topics = [i for i in range (TOPICS_NUMBER) if topics[i][1] > 0.3]
        #         for topic in relevante_topics:
        #             topic_list = []
        #             topic_list.append(topic)
        #             cluster_data = pd.concat([cluster_data, pd.DataFrame({"commitId": [data["commitId"][i]], "clusters_list": [topic_list], "topics": [topics], "cleaned_text": [row["cleaned_text"]]})])
        #         # cluster_data = pd.concat([cluster_data, pd.DataFrame({"commitId": data["commitId"][i], "clusters_list": [relevante_topics], "topics": [(topics)], "cleaned_text": [row["cleaned_text"]]})])
        #     f.write(str(i) + DELIMITER + str(topics) + "\n")
        # cluster_data.to_csv(CLUSTERS, index=False, sep=DELIMITER)

        cluster_data = pd.DataFrame(columns=["commitId", "clusters_list", "cleaned_text"])
        with open(CLUSTERS, "w") as f:
            for i, row in data.iterrows():
                topics = lda_model.get_document_topics(dictionary.doc2bow(row["tokens"]))
                relevante_topics = [i for i in range (len(topics)) if topics[i][1] > 0.3]
                for topic in relevante_topics:
                    topic_list = []
                    topic_list.append(topic)
                    cluster_data = pd.concat([cluster_data, pd.DataFrame({"commitId": [data["commitId"][i]], "clusters_list": [topic_list], "cleaned_text": [row["cleaned_text"]]})])
                # cluster_data = pd.concat([cluster_data, pd.DataFrame({"commitId": data["commitId"][i], "clusters_list": [relevante_topics], "topics": [(topics)], "cleaned_text": [row["cleaned_text"]]})])
            f.write(str(i) + DELIMITER + str(topics) + "\n")
        cluster_data.to_csv(CLUSTERS, index=False, sep=DELIMITER)


    def make_cluster_centroids(self):
        cluster_data = pd.read_csv(CLUSTERS, delimiter = DELIMITER)
        self.vect = TfidfVectorizer(stop_words="english", max_features = 1000)
        self.existing_commit_vectors = self.vect.fit_transform(cluster_data["cleaned_text"])
        cluster_centroids = []
        for cluster_id in sorted(cluster_data["clusters_list"].unique()):
            cluster_subset = self.existing_commit_vectors [
                cluster_data["clusters_list"] == cluster_id
            ]
            cluster_centroids.append(cluster_subset.mean(axis=0))

        cluster_centroids = np.array(cluster_centroids)
        self.cluster_centroids = cluster_centroids
        
    def classify_commit(self, new_commit_summary):
        # cluster_data = pd.read_csv(CLUSTERS, delimiter=DELIMITER)

        # vect = TfidfVectorizer(stop_words="english", max_features=1000)
        # existing_commit_vectors = vect.fit_transform(cluster_data["cleaned_text"])

        # new_commit_vector = vect.transform([self.clean_text(new_commit_summary)])

        # cluster_centroids = []
        # for cluster_id in sorted(cluster_data["clusters_list"].unique()):
        #     cluster_subset = existing_commit_vectors[
        #         cluster_data["clusters_list"] == cluster_id
        #     ]
        #     cluster_centroids.append(cluster_subset.mean(axis=0))

        # # Convert cluster_centroids to NumPy array
        # cluster_centroids = np.asarray(cluster_centroids)

        if(len(self.cluster_centroids) == 0):
            self.make_cluster_centroids()
        
        cluster_centroids = self.cluster_centroids
        
        new_commit_vector = self.vect.transform([self.clean_text(new_commit_summary)])

        # Calculate cosine similarity between the new commit and each cluster centroid
        similarities = [
            cosine_similarity(new_commit_vector, np.asarray(centroid))
            for centroid in cluster_centroids
        ]

        # If similarity is greater than 0.3 for any cluster, return those clusters
        most_similar_cluster = []
        # print(similarities)
        for i, similarity in enumerate(similarities):
            if similarity > 0.15:
                most_similar_cluster.append(i)
        return most_similar_cluster


    def print_all_clusters(self):
        cluster_data = pd.read_csv("commit_clusters.csv")
        for cluster_id in sorted(cluster_data["cluster"].unique()):
            print(f"Cluster {cluster_id}:")
            print(
                cluster_data[cluster_data["cluster"] == cluster_id]["commitId"].values
            )
    
    def classify_commits2(self, SUMMARY_JSON):
        with open(SUMMARY_JSON, "r") as file:
            data = json.load(file)
            with open("commit_clusters.csv", "w", newline='') as file:
                file.write("summary_class#commit_hash\n")
                for commit in data:
                    commit_hash = commit["commit_hash"]
                    summary = commit["summary"]
                    summary = summary.split(", ")
                    for word in summary:
                        file.write(word + DELIMITER + commit_hash + "\n")
        file.close()


# #Uncomment the below line to test the classifier
# c=Classifier()
# new_commit_summaries = ["Updated the argument's short name from -d to -dir for better readability.","Node.js package is bumped from 14.2.0 to 16.1.0","Changed the 'start' script to 'start2' for starting the app."]
# categories = []
# for summary in new_commit_summaries:
#     categories.append(c.classify_commit(summary))
# print(categories)


# if __name__ == "__main__":
#     c = Classifier()
#     while(True):
#         print("Enter the new commit summary: ")
#         summary = input()
#         category = c.classify_commit(summary)
#         print("The category of the commit is: ", category)
#         print("Do you want to continue? (y/n)")
#         choice = input()
#         if(choice == "n"):
#             break
    