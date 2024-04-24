import os
import pandas
CLUSTERS = "./commit_clusters.csv"
RM_LINES_LIST = "./rm_lines_list.txt"

class Suggest_lines:
    def __init__(self, belonging_cluster):
        self.clusters = {}
        self.create_clusters()
        self.readme_hashes = {}
        self.get_readme_hashes()
        self.readme_clusters = {}
        self.get_readme_clusters()
        self.belonging_cluster = belonging_cluster
    
    def create_clusters(self):
        df = pandas.read_csv(CLUSTERS, sep="#")
        for index, row in df.iterrows():
            clusters_list = row['clusters_list'][1:-1].split(", ")
            for cluster in clusters_list:
                cluster_int = int(cluster)
                if cluster_int not in self.clusters:
                    self.clusters[cluster_int] = []
                self.clusters[cluster_int].append(row['commitId'])
               
    def get_readme_clusters(self):
        for cluster in self.clusters:
            self.readme_clusters[cluster] = []
            for commit in self.clusters[cluster]:
                if commit in self.readme_hashes:
                    self.readme_clusters[cluster].append(commit)

    def get_readme_hashes(self):
        #self.readme_hashes has key as index and value as hash
        with open(RM_LINES_LIST, 'r') as f:
            for line in f:
                line = line.strip().split(",")
                for i in range(0, len(line)-1):    
                    if line[i] not in self.readme_hashes:
                        self.readme_hashes[line[i]] = [i]
                    # self.readme_hashes[line[i]].append(i)
                    # self.readme_hashes[line[i]] = i

    def suggest_lines(self):
        suggestions_map = {}
        for single_belonging_cluster in self.belonging_cluster:
            for commit in self.readme_clusters[single_belonging_cluster]:
                # print(commit)
                # if commit in self.readme_hashes:
                #     suggestions_map[self.readme_hashes[commit]] = commit
                if commit in self.readme_hashes:
                    for index in self.readme_hashes[commit]:
                        suggestions_map[index] = commit    
        # print(suggestions_map) 
        return suggestions_map

# sgl = Suggest_lines([1])
# suggested = sgl.suggest_lines()
# lines = []


# with open("./OpenDevin/README.md",encoding='utf-8') as f:
#     lines = f.readlines()
# # print(lines)
# for keys in suggested:
#     print("Suggested line: ", lines[suggested[keys]])