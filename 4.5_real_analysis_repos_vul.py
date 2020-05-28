import pymysql
import re
import sys
import os
from model import CVE, Vul
from config import *


def analyze_repo_files(udb_file):
    udb_file_path = os.path.join(UDB_FILE_ROOT, udb_file)
    understand_file = understand.open(udb_file_path)
    functions = understand_file.ents("function, method, procedure")
    len_functions = len(functions)
    vuls = []
    for n, func in enumerate(functions):
        sys.stdout.write('[%.2f%s] %s/%s\r' % ((n+1)/len_functions*100, '%', n+1, len_functions))
        cve_indexes = [i for i in range(len(cve)) if cve_method_name[i] == func.longname()]
        for i in cve_indexes:
            vul = Vul(cve[i].no, cve[i].level, cve[i].jar_name, cve[i].method_longname, cve[i].vulnerable_line)
            have_java_file = False
            for ref in func.refs(refkindstring='Callby'):
                if re.match(r'.*\.java', ref.file().name()):
                    vul.add_vul_file(ref.file().relname(), ref.line(), ref.column())
                    have_java_file = True
            if have_java_file:
                vuls.append(vul)
    return vuls


def format_report(vuls):
    s = '-------------------- Vulnerabilities Report --------------------\n\n'
    s += 'Found %d vulnerabilities in target JAVA project\n\n' % len(vuls)
    for i, vul in enumerate(vuls):
        s += '[%d]\n' % (i + 1)
        s += '- CVE No:              %s\n' % vul.cve_no
        s += '- CVE Level:           %s\n' % vul.cve_level
        s += '- CVE Jar Name:        %s\n' % vul.cve_jar_name
        s += '- CVE Method Name:     %s\n' % vul.cve_method_name
        s += '- CVE Vulnerable Line: %s\n' % vul.cve_vulnerable_line
        s += '- File Containing This CVE in Project:\n'
        for j, file in enumerate(vul.vul_file):
            s += '  (%d)\n' % (j + 1)
            s += '  - File Name: %s\n' % file[0]
            s += '  - Line:      %s\n' % file[1]
            s += '  - Column:    %s\n' % file[2]
        s += '\n\n'
    s += '--------------------                        --------------------\n\n\n'
    return s


def check_is_analyze(file_name):
    for file in all_report_files:
        if file.find('__%s.txt' % file_name) != -1:
            return True
    return False


if __name__ == '__main__':
    sys.path.append(UNDERSTAND_PYTHON_API_ROOT)
    import understand

    # init mysql
    mysql = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DB,
                            port=MYSQL_PORT, charset='utf8mb4')
    # get cve
    sql = "SELECT cve_no, cve_level, jar_name, git_repository, commitid, file_name, class_name, method_name, " \
          "isPublic, vulnerable_line, file_longname, method_longname FROM apis;"
    cursor = mysql.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    mysql.close()
    cve = [CVE(*x) for x in res]
    cve_method_name = [x.method_longname for x in cve]
    print('Getting CVEs From Database Success!\n')

    # load udb files
    udbs = [x for x in os.listdir(UDB_FILE_ROOT)
            if os.path.isfile(os.path.join(UDB_FILE_ROOT, x)) and re.match(r'.*\.udb', x)]
    len_udbs = len(udbs)
    print('Found %d udb files.\n' % len_udbs)

    # analyze udb files
    print('Staring Analyze Repos Vulnerabilities...')
    all_report_files = [x for x in os.listdir(REPORT_FILES_ROOT)
                        if os.path.isfile(os.path.join(REPORT_FILES_ROOT, x)) and os.path.splitext(x)[1] == '.txt']
    for i, udb in enumerate(udbs):
        print('Analyzing %d/%d Repos: %s\n' % (i+1, len_udbs, udb[:-4]))
        # if is analyzed
        if check_is_analyze(udb[:-4]):
            print('This repo has already analyzed!')
            continue
        vuls = analyze_repo_files(udb)
        report_contents = format_report(vuls)
        print(report_contents)
        # save report
        report_file = os.path.join(REPORT_FILES_ROOT, '%d__%s.txt' % (len(vuls), udb[:-4]))
        with open(report_file, 'w') as f:
            f.write(report_contents)

    print('Analysis All Completed!')
