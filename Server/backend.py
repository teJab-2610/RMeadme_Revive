from flask import Flask, request, jsonify
from pydriller_commit_store import CommitStore
from git import Repo
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from flask_cors import CORS
from datetime import datetime
from classifier import Classifier
from utility import last_readme_modified_hash
from RM_Lines_map import RM_Lines_map
from Suggest_lines import Suggest_lines
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

class FileChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print("Restarting server...")
            os.system("pkill -f 'python backend.py'")

event_handler = FileChangeHandler()
observer = Observer()
observer.schedule(event_handler, '.')

observer.start()
commit_list = []

def write_info(repo_url):
    flag = 1
    owner = repo_url.split('/')[3]
    repo = repo_url.split('/')[4]
    repo = repo.split('?')[0]
    repo_id = owner.strip() + '/'+repo.strip()
    current_time = datetime.now().isoformat()
    with open ("info.json", 'r') as f:
        data = json.load(f)
        for repo in data:
            if repo["repo_name"] == repo_id:
                flag = 0
                repo["last_revised_on"] = current_time
    if flag == 1:
        data.append({"repo_name": repo_id, "last_revised_on": current_time})
    with open ("info.json", 'w') as f:
        json.dump(data, f, indent=4)

def split_summaries(repo, new_commits_set):
    latest_summaries = []
    with open(f"{repo}_commits_summary.json", 'r') as f:
        commits_summary = json.load(f)

    for summary in reversed(commits_summary):
        if summary["commit_hash"] in new_commits_set:
            latest_summaries.append(summary)
    return latest_summaries
        
def convert_readme_date(readme_date_str):
    readme_datetime = datetime.strptime(readme_date_str, '%a %b %d %H:%M:%S %Y %z')
    readme_datetime_utc = readme_datetime.astimezone(timezone.utc)
    readme_datetime_local = readme_datetime_utc.astimezone()
    return readme_datetime_local.strftime('%Y-%m-%dT%H:%M:%S%z')


@app.route('/process_repo', methods=['POST'])
def direct_route():
    data = request.json
    repo_url = data.get('repo_url')
    # print(repo_url)
    if not repo_url:
        return jsonify({'error': 'Repository URL not provided in request body'}), 400

    owner = repo_url.split('/')[3]
    repo = repo_url.split('/')[4]
    repo = repo.split('?')[0]

    with open(f"info.json", 'r') as f:
        json_data = json.load(f)
        for repo_info in json_data:
            # print(repo_info["repo_name"], (owner+'/'+repo))
            # print(repo_info["repo_name"].strip() == (owner+'/'+repo).strip())
            if repo_info["repo_name"].strip() == (owner+'/'+repo).strip(): 
                print("Found repo info in info.json")
                last_revised_on = repo_info["last_revised_on"]
                print("Going into new commits method")
                return new_commits(repo_url, last_revised_on)
    
    print("Going into process repo method")
    return process_repo(repo_url)
                

def process_repo(repo_url):
    if not repo_url:
        return jsonify({'error': 'Repository URL not provided in request body'}), 400

    owner = repo_url.split('/')[3]
    repo = repo_url.split('/')[4]
    repo = repo.split('?')[0]
    repo_dir = f"./{repo}"

    if os.path.exists(repo_dir):
        print("\nRepository folder exists. Removing...")        
        # for root, dirs, files in os.walk(repo_dir):
        #     for file in files:
        #         try:
        #             os.remove(os.path.join(root, file))
        #             print(f"Removed file: {os.path.join(root, file)}")
        #         except OSError as e:
        #             print(f"Error: {os.path.join(root, file)} : {e.strerror}")
        
        # for root, dirs, _ in os.walk(repo_dir, topdown=False):
        #     for dir in dirs:
        #         try:
        #             os.rmdir(os.path.join(root, dir))
        #             print(f"Removed directory: {os.path.join(root, dir)}")
        #         except OSError as e:
        #             print(f"Error: {os.path.join(root, dir)} : {e.strerror}")
        # try:
        #     os.rmdir(repo_dir)
        #     print(f"Folder '{repo_dir}' removed successfully.")
        # except OSError as e:
        #     print(f"Error: {repo_dir} : {e.strerror}")
    else:
        print("Repository folder does not exist.")


    print("\nCloning the repository....")
    repo_dir = f"./{repo}"
    os.makedirs(repo_dir, exist_ok=True) 
    # Repo.clone_from("https://github.com/"+owner+"/"+repo+".git", repo_dir)
    print("\nRepository cloned successfully.\n")

    commit_store = CommitStore("./" + repo)
    commit_list = commit_store.get_hash_and_commit()
    print("Total ",len(commit_list)," commmits inside the repo")
    
    #Preprocess everything since it is the first time we are processing the repo
    #pre_processing(commit_store,commit_list,repo)

    #Get the commits that are not reflected in the ReadMe
    readme_hash = last_readme_modified_hash(repo)
    commits_to_process = commit_store.commits_only_after(readme_hash)
    
    #Right now we only have the commit hashes that are not reflected in the ReadMe
    #We need to get the summaries of those commit hashes present in the commit_summary.json
    new_commits_set = set()
    for commit in commits_to_process:
        new_commits_set.add(commit[1].hash)
    newsummaries = split_summaries(repo, new_commits_set)
    print("Found ",len(commits_to_process), "new commits to be summarised out of which, we have ", len(newsummaries), "summaries")

    RM_Lines_map(f"./{repo}") 

    c = Classifier(repo)

    suggestions = []
    for new_summary in newsummaries :
        category = c.classify_commit(new_summary["summary"])
        hash = new_summary["commit_hash"]
        
        sgl = Suggest_lines(category)
        suggested = sgl.suggest_lines()
        lines = []
        for line in suggested :
            lines.append(line)
        suggestions.append({"commit_hash": hash, "summary":new_summary["summary"],"lines" : lines})
    print(suggestions)

    write_info(repo_url)
    with open("results_"+repo+".json", "w") as f:
        json.dump(suggestions, f, indent=4)
    return jsonify(suggestions), 200


def new_commits(repo_url, last_revised_date):
    if not repo_url:
        return jsonify({'error': 'Repository URL not provided in request body'}), 400

    owner = repo_url.split('/')[3]
    repo = repo_url.split('/')[4]
    repo = repo.split('?')[0]
    repo_dir = f"./{repo}"

    print("\nCloning the repository....")
    os.makedirs(repo_dir, exist_ok=True) 
    # Repo.clone_from("https://github.com/"+owner+"/"+repo+".git", repo_dir)
    print("\nRepository cloned successfully.\n")

    commit_store = CommitStore("./" + repo)
    
    commits_after_last_revised_dates = commit_store.commits_after_date(last_revised_date)
    #Get the summaries for these new commits
    #pre_processing(commit_store, commits_after_last_revised_dates, repo)

    #Get the commits that are not reflected in the Readme
    readme_hash = last_readme_modified_hash(repo)
    commits_to_process = commit_store.commits_only_after(readme_hash)

    #We only have the commits but not the summaries, so get those
    new_commits_set = set()
    for commit in commits_to_process:
        new_commits_set.add(commit[1].hash)
    newsummaries = split_summaries(repo, new_commits_set)
    print("Found ",len(commits_to_process), "new commits to be summarised out of which, we have ", len(newsummaries), "summaries")

    ###################################
    # Another approach to do this is to reflect the commits  
    # after the last usage of the tool. Below is the code for that:

    # new_commits_set = set()
    # for commit in commits_after_last_revised_dates:
    #     new_commits_set.add(commit[1].hash)
    # newsummaries = split_summaries(repo, new_commits_set)
    # print("Found ",len(commits_after_last_revised_dates), "new commits to be summarised out of which, we have ", len(newsummaries), "summaries")

    ###################################
    
    RM_Lines_map(f"./{repo}") 

    c = Classifier(repo)

    suggestions = []
    for new_summary in newsummaries :
        category = c.classify_commit(new_summary["summary"])
        hash = new_summary["commit_hash"]
        # print("The category of the commit is: ", category)
        sgl = Suggest_lines(category)
        suggested = sgl.suggest_lines()
        lines = []
        for line in suggested :
            lines.append(line)
        suggestions.append({"commit_hash": hash, "summary":new_summary["summary"],"lines" : lines})
    
    #Update the info.json for future
    write_info(repo_url)
    with open("results_"+repo+"_.json", "w") as f:
        json.dump(suggestions, f, indent=4)
    return jsonify(suggestions), 200
    
def pre_processing(commit_store, commit_list,repo):
    merge_commit_shas =[]
    commit_msgs=[]

    COMMIT_SUMMARY_FILE = f"{repo}_commits_summary.json"

    if os.path.exists(COMMIT_SUMMARY_FILE):
        with open(COMMIT_SUMMARY_FILE, "r") as f:
            existing_commits_summary = json.load(f)
    else:
        existing_commits_summary = []

    for merge_commit_sha, commit in commit_list:
        merge_commit_shas.append(merge_commit_sha)
        commit_msgs.append(commit.msg)
        summaries = []
        
    c = 0
    commits_summary = []
    for merge_commit_sha, commit in commit_list:
        try:
            if len(commit.modified_files) > 3:
                print(f"Skipping commit {merge_commit_sha} with commit number {c} as it has {len(commit.modified_files)} files")
                c += 1
                continue
            
            summary = commit_store.get_files_summarise_code_2(merge_commit_sha, commit.msg, summaries)
            commits_summary.append({"commit_hash": merge_commit_sha, "summary": summary})
            print(f"Summary generated for COMMIT NUMBER {c} with commit hash {merge_commit_sha}")

        except Exception as e:
            print(f"Error processing commit {merge_commit_sha}: {e}")
        c += 1
    all_commits_summary = existing_commits_summary + commits_summary
    with open(COMMIT_SUMMARY_FILE, "w") as f:
        json.dump(all_commits_summary, f)

    print("Summary of commits written to commits_summary.json")
    

if __name__ == '__main__':
    app.run(port=5000)
