import pickle
import os
import subprocess
from model import Repo
from config import *


if __name__ == '__main__':
    # unserialize repos
    with open(SERIALIZATION_REPOS_INFO_FILE_FULL, 'rb') as f:
        repos = pickle.load(f)
    print('Unserializing Repos Info Success!\n')

    # download repo by git
    print('Starting Download Repos...')
    len_repos = len(repos)
    for i, repo in enumerate(repos):
        print('Downloading %d/%d repos.' % (i+1, len_repos))
        print('- Repo Name:  %s' % repo.name)
        print('- Repo Owner: %s' % repo.owner)
        print('- Repo Size:  %s' % repo.size)
        print('- Repo Stars: %s' % repo.stars)
        print('- Repo Forks: %s' % repo.forks)
        path = os.path.join(REPO_FILE_ROOT, '%s__%s' % (repo.owner, repo.name))
        if os.path.exists(path):
            print('This repos already exists!')
        else:
            cmd = 'git clone --depth=1 %s %s' % (repo.get_clone_url(), path)
            subprocess.call(cmd, shell=True)
        print()
    print('Downloading All Completed!')
