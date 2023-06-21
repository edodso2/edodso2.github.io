import os
import openai
from git import Repo
from pathlib import Path

openai.api_key = os.getenv('OPENAI_API_KEY')

PATH_TO_BLOG = Path(os.getcwd())
PATH_TO_BLOG_REPO = PATH_TO_BLOG/".git"
PATH_TO_CONTENT = PATH_TO_BLOG/"content"

PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

def update_blog(commit_message='Updates blog'):
    # Reports repository location to GitPython
    repo = Repo(PATH_TO_BLOG_REPO)

    # Git Add
    repo.git.add(all=True)

    # Git Commit
    repo.index.commit(commit_message)

    # Git Push
    origin = repo.remote(name='origin')
    origin.push()

with open(PATH_TO_BLOG/"index.html", 'w') as f:
    f.write('test 2')

update_blog()