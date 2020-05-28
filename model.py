import time


class AccessToken(object):
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit  # per min
        self.remaining = limit
        self.reset_time = -1

    def is_available(self):
        return False if self.remaining == 0 else True

    def reduce(self):
        self.remaining -= 1

    def reset(self):
        self.reset_time = int(time.time() + 60) + 1
        self.remaining = self.limit


class AccessTokenPool(object):
    def __init__(self, access_tokens):
        assert isinstance(access_tokens, list)
        self.access_tokens = access_tokens
        for item in access_tokens:
            assert isinstance(item, AccessToken)
            item.reset_time = time.time()

    def get_token(self):
        current_time = int(time.time()) + 1
        min_waiting_time = 61
        for item in self.access_tokens:
            if item.reset_time < current_time:
                item.reset()
                item.reduce()
                return True, item.value
            else:
                if item.is_available():
                    item.reduce()
                    return True, item.value
                else:
                    waiting_time = item.reset_time - current_time + 1
                    min_waiting_time = waiting_time if waiting_time < min_waiting_time else min_waiting_time
        return False, min_waiting_time


class Repo(object):
    def __init__(self, name='', owner='', size=-1, stars=-1, forks=-1):
        self.name = name
        self.owner = owner
        self.size = size
        self.stars = stars
        self.forks = forks

    def __eq__(self, other):
        return self.name == other.name and self.owner == other.owner

    def get_clone_url(self):
        return 'https://github.com/%s/%s.git' % (self.owner, self.name)

    def get_repo_url(self):
        return 'https://api.github.com/repos/%s/%s' % (self.owner, self.name)


class CVE(object):
    def __init__(self, no, level, jar_name, git_repository, commitid, file_name, class_name, method_name, is_public,
                 vulnerable_line, file_longname, method_longname):
        self.no = no
        self.level = level
        self.jar_name = jar_name
        self.git_repository = git_repository
        self.commitid = commitid
        self.file_name = file_name
        self.class_name = class_name
        self.method_name = method_name
        self.isPublic = True if is_public == '1' else False
        self.vulnerable_line = vulnerable_line
        self.file_longname = file_longname
        self.method_longname = method_longname


class Vul(object):
    def __init__(self, cve_no, cve_level, cve_jar_name, cve_method_name, cve_vulnerable_line):
        self.cve_no = cve_no
        self.cve_level = cve_level
        self.cve_jar_name = cve_jar_name
        self.cve_method_name = cve_method_name
        self.cve_vulnerable_line = cve_vulnerable_line
        self.vul_file = []

    def add_vul_file(self, name, line, column):
        self.vul_file.append((name, line, column))
