# coding=utf-8

import httplib, urllib, urllib2, ssl, time, os, threading

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3298.4 Safari/537.36'}

def show_status_urllib(url):
    function_name = 'urllib'
    try:
        response = urllib.urlopen(url)
    except IOError, e:
        return False, function_name + ' : IOError - ' + e.message
    except ssl.CertificateError, e:
        return False, function_name + ' : CertificateError - ' + e.message
    except httplib.BadStatusLine, e:
        return False, function_name + ' : httplib.BadStatisLine - ' + e.message
    else:
        return return_code(function_name, response)


def show_status_urllib2(url):
    function_name = 'urllib2'
    try:
        # request = urllib2.Request(url)
        request = urllib2.Request(url, '', HEADERS)
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        return False, function_name + ' : HTTPError code ' + str(e.code)
    except urllib2.URLError, e:
        return False, function_name + ' : URLError - ' + str(e.reason)
    except IOError, e:
        return False, function_name + ' : IOError - ' + e.message
    except ssl.CertificateError, e:
        return False, function_name + ' : CertificateError - ' + e.message
    except httplib.BadStatusLine, e:
        return False, function_name + ' : httplib.BadStatisLine - ' + e.message
    else:
        return return_code(function_name, response)


def return_code(function_name, response):
    code = response.getcode()
    if code == 404:
        return False, function_name + ' : code 404 - Page Not Found !'
    elif code == 403:
        return False, function_name + ' : code 403 - Forbidden !'
    elif code == 200:
        return True, function_name + ' : code 200 - OK !'
    else:
        return False, function_name + ' : code ' + str(code)


def return_log(protocol, is_true, url, urllib_log, urllib2_log):
    if is_true:
        return '### ' + protocol + '_YES ### ' + url + ' → （' + urllib_log + ' ）（ ' + urllib2_log + '）'
    else:
        return '### ' + protocol + '_NO ### ' + url + ' → （' + urllib_log + ' ）（ ' + urllib2_log + '）'


def request_url(url):
    url = url.strip().replace(" ", "").replace("\n", "").replace("\r\n", "")

    http_url = 'http://' + url
    is_http_urllib_true, http_urllib_log = show_status_urllib(http_url)
    is_http_urllib2_true, http_urllib2_log = show_status_urllib2(http_url)

    https_url = 'https://' + url
    is_https_urllib_true, https_urllib_log = show_status_urllib(https_url)
    is_https_urllib2_true, https_urllib2_log = show_status_urllib2(https_url)

    return return_log('HTTP', is_http_urllib_true and is_http_urllib2_true, http_url, http_urllib_log, http_urllib2_log)\
           + '\n' + return_log('HTTPS', is_https_urllib_true and is_https_urllib2_true, https_url, https_urllib_log, https_urllib2_log)


LOG_FILE = 0
LOG_HTTP_NO_AND_HTTPS_NO_FILE = 1
LOG_HTTP_NO_BUT_HTTPS_YES_FILE = 2
LOG_HTTP_YES_BUT_HTTPS_NO_FILE = 3


def save_log(log_of_list, line):
    line += '\n'
    log_of_list[LOG_FILE].write(line)
    if '### HTTP_NO ###' in line:
        if '### HTTPS_NO ###' in line:
            log_of_list[LOG_HTTP_NO_AND_HTTPS_NO_FILE].write(line)
        elif '### HTTPS_YES ###' in line:
            log_of_list[LOG_HTTP_NO_BUT_HTTPS_YES_FILE].write(line)
    elif '### HTTP_YES ###' in line and '### HTTPS_NO ###' in line:
        log_of_list[LOG_HTTP_YES_BUT_HTTPS_NO_FILE].write(line)


def use_thread(thread_total_number, thread_number, url_of_list, log_of_list):
    i = -1
    for url in url_of_list:
        i += 1
        if i % thread_total_number == thread_number:
            line = request_url(url)
            save_log(log_of_list, line)
            print 'thread_number = ' + str(thread_number) + '\n' + line + '\n'   # 查看当前是哪个进程在运行
    # print 'thread_number EXIT = ' + str(thread_number) + '\n'      # 查看当前是哪个进程已经运行结束


def open_thread(thread_total_number, url_of_list, log_of_list):
    threads_for_list = []
    for thread_number in range(thread_total_number):
        thread = threading.Thread(target=use_thread, args=(thread_total_number, thread_number, url_of_list, log_of_list))
        thread.start()
        threads_for_list.append(thread)

    # 等待所有进程全部退出
    for t in threads_for_list:
        t.join()


def main():
    if not os.path.exists('logs'):
        os.mkdir('logs')

    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_of_list = [None, None, None, None]
    log_of_list[LOG_FILE] = open('logs/log-' + now_time + '.txt', 'a')
    log_of_list[LOG_HTTP_NO_AND_HTTPS_NO_FILE] = open('logs/log-' + now_time + '-http-no-and-https-no.txt', 'a')
    log_of_list[LOG_HTTP_NO_BUT_HTTPS_YES_FILE] = open('logs/log-' + now_time + '-http-no-but-https-yes.txt', 'a')
    log_of_list[LOG_HTTP_YES_BUT_HTTPS_NO_FILE] = open('logs/log-' + now_time + '-http-yes-but-https-no.txt', 'a')

    # 1、检测 list 里的链接
    print 'URL Testing For List :\n'
    url_of_list = ['www.baidu.com', 'www.qq.com', 'chaishiwei.com']

    # 2、开启线程
    thread_total_number = 8  # 默认开启 8 个线程，这里可以根据实际情况修改
    open_thread(thread_total_number, url_of_list, log_of_list)

    # 1、检测 txt file 里的链接
    print '\nURL Testing For TXT File :\n'

    # 2、读取文本文件到列表
    url_of_list = []
    url_file = open("url.txt", 'r')
    for url in url_file.readlines():
        url_of_list.append(url)
    url_file.close()

    # 3、开启线程
    thread_total_number = 8  # 默认开启 8 个线程，这里可以根据实际情况修改
    open_thread(thread_total_number, url_of_list, log_of_list)

    # 4、将文件缓存写入磁盘，并关闭文件的读写
    log_of_list[LOG_FILE].flush()
    log_of_list[LOG_HTTP_NO_AND_HTTPS_NO_FILE].flush()
    log_of_list[LOG_HTTP_NO_BUT_HTTPS_YES_FILE].flush()
    log_of_list[LOG_HTTP_YES_BUT_HTTPS_NO_FILE].flush()

    log_of_list[LOG_FILE].close()
    log_of_list[LOG_HTTP_NO_AND_HTTPS_NO_FILE].close()
    log_of_list[LOG_HTTP_NO_BUT_HTTPS_YES_FILE].close()
    log_of_list[LOG_HTTP_YES_BUT_HTTPS_NO_FILE].close()


if __name__ == "__main__":
    main()