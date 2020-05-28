import requests
import json
import threading
import pickle
import pymysql
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from model import Repo, CVE, AccessToken, AccessTokenPool
from config import *


def get_repo_info(file_name, method_name):
    global repos, cve_num

    current_count = 0
    total_count = 1
    is_first_page = True

    # get html
    url = 'https://api.github.com/search/code'
    params = {
        'q': 'language:java filename:%s %s' % (file_name, method_name),
        'sort': GITHUB_API_SORT,
        'order': GITHUB_API_ORDER,
        'per_page': PER_PAGE_NUM,
        'page': 1
    }
    headers = {
        'Authorization': '',
        'User-Agent': USER_AGENT,
        'Host': 'api.github.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    while current_count < total_count:
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
                r = requests.get(url=url, params=params, headers=headers, timeout=(15, 20))
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    data = json.loads(r.text)
                    if 'total_count' in data:
                        if is_first_page:
                            total_count = min(data['total_count'], SEARCH_REPOS_NUM, 1000)
                            with cve_num_lock:
                                print('(%d/%d) CVE Method Name: %s.%s\nFound %d Repos About This CVE.' %
                                      (cve_num, len_cve, file_name[:-5], method_name, total_count))
                                cve_num += 1
                            is_first_page = False
                        params['page'] += 1
                        current_count += PER_PAGE_NUM
                        with repos_lock:
                            for item in data['items']:
                                repo = Repo(name=item['repository']['name'], owner=item['repository']['owner']['login'])
                                repos.append(repo)
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
    # init mysql
    mysql = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DB,
                            port=MYSQL_PORT, charset='utf8mb4')
    # get cve
    sql = "SELECT cve_no, cve_level, file_name, file_longname, class_name, method_name, method_longname, " \
          "vulnerable_line FROM api;"
    cursor = mysql.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    mysql.close()
    cve = [CVE(*x) for x in res]
    len_cve = len(cve)

    # get repos info
    print('Starting Get Repos Info by CVE...')
    cve_num = 1
    repos = []
    token_pool_lock = threading.Lock()
    repos_lock = threading.Lock()
    cve_num_lock = threading.Lock()
    access_tokens = [AccessToken(value, GITHUB_API_SEARCH_RATE_LIMIT) for value in GITHUB_API_ACCESS_TOKENS]
    access_token_pool = AccessTokenPool(access_tokens)
    executor = ThreadPoolExecutor(SEARCH_THREAD_NUM)
    tasks = []
    for item in cve:
        tasks.append(executor.submit(get_repo_info, item.file_name, item.method_name))
    wait(tasks, return_when=ALL_COMPLETED)
    print('Getting All Completed!\n')
    print('Found %d Repos.\n' % len(repos))

    # distinct repos
    tmp_repos = []
    for repo in repos:
        if repo not in tmp_repos:
            tmp_repos.append(repo)
    repos = tmp_repos
    print('Found %d Repos Distinct.\n' % len(repos))

    # serialize repos
    with open(SERIALIZATION_REPOS_INFO_FILE, 'wb') as f:
        pickle.dump(repos, f)
    print('Serializing Repos Info Success!')
