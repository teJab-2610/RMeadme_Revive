import os

from git import Repo

def last_readme_modified_date(repo):
      repo = Repo(f"./{repo}")
      readme_file = find_readme_file(repo.working_dir)
      if readme_file:
          return repo.git.log('-1', '--format=%cd', '--', readme_file)
      return None

def last_readme_modified_hash(repo):
        repo = Repo(f"./{repo}")
        readme_file = find_readme_file(repo.working_dir)
        if readme_file:
            return repo.git.log('-1', '--format=%H', '--', readme_file)
        return None
    
    
def find_readme_file(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() == 'readme.md':
                return os.path.join(root, file)
    return None