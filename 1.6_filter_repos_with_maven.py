import requests
import json
import threading
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from model import Repo, AccessToken, AccessTokenPool
from config import *


def filter_repo_with_maven(repo):
    global new_repos, repos_num

    url = 'https://api.github.com/search/code'
    headers = {
        'Authorization': '',
        'User-Agent': USER_AGENT,
        'Host': 'api.github.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    proxies = {
        'http': 'http://127.0.0.1:8000',
        'https': 'http://127.0.0.1:8000'
    }
    params = {
        'q': 'repo:%s/%s filename:pom.xml' % (repo.owner, repo.name)
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
            r = requests.get(url=url, params=params, headers=headers, proxies=proxies, timeout=(15, 20))
            if r.status_code == 200:
                r.encoding = 'utf-8'
                data = json.loads(r.text)
                if 'total_count' in data:
                    if data['total_count'] > 0:
                        with repos_lock:
                            new_repos.append(repo)
                            print('Found a repo with maven! Total: %d.' % len(new_repos))
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
    with open(SERIALIZATION_REPOS_INFO_FILE, 'rb') as f:
        repos = pickle.load(f)
    print('Unserializing Repos Info Success!\n')

    # filter repos with maven
    print('Starting Get Repos Stars and Forks...')
    repos_num = 1
    len_repos = len(repos)

    new_repos = []

    token_pool_lock = threading.Lock()
    repos_lock = threading.Lock()
    repo_num_lock = threading.Lock()

    access_tokens = [AccessToken(value, GITHUB_API_SEARCH_RATE_LIMIT) for value in GITHUB_API_ACCESS_TOKENS]
    access_token_pool = AccessTokenPool(access_tokens)

    executor = ThreadPoolExecutor(SEARCH_THREAD_NUM)
    tasks = []
    for repo in repos:
        tasks.append(executor.submit(filter_repo_with_maven, repo))
    wait(tasks, return_when=ALL_COMPLETED)

    print('Getting All Completed!\n')
    print('Found %d Repos With Maven.\n' % len(new_repos))

    # serialize repos
    with open(SERIALIZATION_REPOS_INFO_FILE_WITH_MAVEN, 'wb') as f:
        pickle.dump(new_repos, f)
    print('Serializing Repos Info Success!')
