import requests
import json
import threading
import pickle
import time
import sys
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from model import Repo, AccessToken, AccessTokenPool
from config import *


def get_repo_stars_forks(repo):
    global repos, repos_num

    url = repo.get_repo_url()
    headers = {
        'Authorization': '',
        'User-Agent': USER_AGENT,
        'Host': 'api.github.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    while True:
        # get token
        with token_pool_lock:
            is_success, value = access_token_pool.get_token()
        if not is_success:
            print('Get Rate Limit. Sleep %ds...' % value)
            time.sleep(value)
            continue
        headers['Authorization'] = 'token %s' % value
        try:
            r = requests.get(url=url, headers=headers, timeout=(15, 20))
            if r.status_code == 200:
                r.encoding = 'utf-8'
                data = json.loads(r.text)
                if 'id' in data:
                    with repos_lock:
                        repo.stars = data['stargazers_count']
                        repo.forks = data['forks']
                        repo.size = data['size']
                    with repo_num_lock:
                        sys.stdout.write('[%.2f%s] %s/%s\r' % (repos_num / len_repos * 100, '%', repos_num, len_repos))
                        repos_num += 1
                    break
                else:
                    print('Some Wrong Happened.')
                    return
            elif r.status_code == 403:
                print('Abuse Rate Limit. Sleep %ds...' % ABUSE_RATE_LIMIT_SLEEP_TIME)
                time.sleep(ABUSE_RATE_LIMIT_SLEEP_TIME)
            else:
                print('Connecting Github API Error. Response HTTP Status Code: %d' % r.status_code)
                return
        except:
            print('Connection Has Been Reset. Sleep %ds...' % CONNECTION_RESET_SLEEP_TIME)
            time.sleep(CONNECTION_RESET_SLEEP_TIME)


if __name__ == '__main__':
    # unserialize repos
    with open(SERIALIZATION_REPOS_INFO_FILE_WITH_MAVEN, 'rb') as f:
        repos = pickle.load(f)
    print('Unserializing Repos Info Success!\n')

    # get repos stars and forks
    print('Starting Get Repos Stars and Forks...')
    repos_num = 1
    len_repos = len(repos)
    token_pool_lock = threading.Lock()
    repos_lock = threading.Lock()
    repo_num_lock = threading.Lock()
    access_tokens = [AccessToken(value, GITHUB_API_CORE_RATE_LIMIT) for value in GITHUB_API_ACCESS_TOKENS]
    access_token_pool = AccessTokenPool(access_tokens)
    executor = ThreadPoolExecutor(CORE_THREAD_NUM)
    tasks = []
    for repo in repos:
        tasks.append(executor.submit(get_repo_stars_forks, repo))
    wait(tasks, return_when=ALL_COMPLETED)
    print('Getting All Completed!\n')

    # filter repos too large
    tmp_repos = []
    for repo in repos:
        if repo.size <= MAX_REPOS_SIZE:
            tmp_repos.append(repo)
    repos = tmp_repos
    print('Filter %d Repos Which Are Too Large.\nRemaining %d Repos.\n' % (len_repos-len(repos), len(repos)))

    # serialize repos
    with open(SERIALIZATION_REPOS_INFO_FILE_FULL, 'wb') as f:
        pickle.dump(repos, f)
    print('Serializing Repos Info Success!')
