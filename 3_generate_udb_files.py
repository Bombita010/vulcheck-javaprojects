import os
import subprocess
import sys
from config import *


if __name__ == '__main__':
    # load repos
    repos = [x for x in os.listdir(REPO_FILE_ROOT) if os.path.isdir(os.path.join(REPO_FILE_ROOT, x))]
    len_repos = len(repos)
    print('Found %d repos.\n' % len_repos)

    # generate understand udb files
    print('Starting Generate Understand UDB Files...')
    for i, repo in enumerate(repos):
        und_path = os.path.join(UNDERSTAND_ROOT, 'und')
        udb_file_path = os.path.join(UDB_FILE_ROOT, '%s.udb' % repo)
        repo_file_path = os.path.join(REPO_FILE_ROOT, repo)
        if os.path.isfile(udb_file_path):
            continue
        cmd1 = '%s create -languages java %s' % (und_path, udb_file_path)
        cmd2 = '%s add %s -db %s' % (und_path, repo_file_path, udb_file_path)
        cmd3 = '%s analyze %s' % (und_path, udb_file_path)
        cmds = (cmd1, cmd2, cmd3)
        for cmd in cmds:
            res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.stderr:
                print(res.stderr.decode('utf-8'))
                exit()
        sys.stdout.write('[%.2f%s] %s/%s\r' % ((i+1) / len_repos * 100, '%', i+1, len_repos))
    print('Generating All Completed!')
