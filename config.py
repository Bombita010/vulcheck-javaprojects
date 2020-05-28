# mysql
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASS = 'root'
MYSQL_DB = 'vulnerable_apis'

# understand
UNDERSTAND_ROOT = '/Applications/Understand.app/Contents/MacOS'
UNDERSTAND_PYTHON_API_ROOT = '/Applications/Understand.app/Contents/MacOS/Python'
UDB_FILE_ROOT = './udb_files'

# github API
GITHUB_API_QUERY = 'language:java stars:100..1000'
GITHUB_API_SORT = 'stars'  # best match, stars, forks, help-wanted-issues, updated. Default: best match
GITHUB_API_ORDER = 'desc'  # desc OR asc. Default: desc
GITHUB_API_ACCESS_TOKENS = ['15d06bd59cf2ed73b5558848c25e3b58016bfa16']
PER_PAGE_NUM = 100  # 1<=n<=100
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'

GITHUB_API_SEARCH_RATE_LIMIT = 30  # per min
GITHUB_API_CORE_RATE_LIMIT = 83  # per min

SEARCH_THREAD_NUM = 8
CORE_THREAD_NUM = 16

ABUSE_RATE_LIMIT_SLEEP_TIME = 15  # seconds
CONNECTION_RESET_SLEEP_TIME = 300  # seconds

# repo
SERIALIZATION_REPOS_INFO_FILE = './repos_info'
SERIALIZATION_REPOS_INFO_FILE_WITH_MAVEN = './repos_info_with_maven'
SERIALIZATION_REPOS_INFO_FILE_FULL = './repos_info_full'
REPO_FILE_ROOT = './repos'
SEARCH_REPOS_NUM = 300  # 1<=n<=1000. Because only the first 1000 search results are available in github.
MAX_REPOS_SIZE = 20480  # KB

# report
REPORT_FILES_ROOT = './report'
