from git import Repo
import os, subprocess

class RM_Lines_map:
    def __init__(self, path):
        self.lines = []
        self.repo = Repo(path)
        self.readme_path = self.find_readme_file(self.repo.working_dir)
        self.lines = self.readme_lines(self.readme_path)
        self.hashes_list = self.get_last_commit_per_line()
        self.print_rm_lines_map()
    
    def find_readme_file(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == 'readme.md':
                    return os.path.join(root, file)
        return None
    
    def readme_lines(self, path):
        lines = []
        with open(path, 'r', encoding='utf-8') as file:
            readme_content = file.read()
            lines = readme_content.split("\n")
        # for i in range(len(lines)):
        #     print(f"{i+1}: {lines[i]}")

        with open("rm_lines.txt", "w", encoding='utf-8') as f:
            for i in range(len(lines)-1):
                # f.write(i, lines[i]+"/n")
                f.write(str(i)+"   ::"+lines[i]+"\n")
        return lines
    

    def get_last_commit_per_line(self):
        commit_hases_list = []
        for i in range(len(self.lines)-1):
            parts =(self.repo.git.log("-L", f"{i+1},{i+1}:"+self.readme_path, "-p", "-1")).split("\n")
            commit_hash = parts[0].split(" ")[1]
            commit_hases_list.append(commit_hash)
            # print(f"{i}: {commit_hash}")
        return commit_hases_list

    def print_rm_lines_map(self):
        with open("rm_lines_list.txt", "w", encoding='utf-8') as f:
            for i in range(len(self.lines)-1):
                f.write(self.hashes_list[i]+",")

# RmMap = RM_Lines_map("./OpenDevin")

