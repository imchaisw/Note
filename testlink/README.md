# 用不到 200 行的 Python 代码编写一个批量检测 URL 是否可以访问的脚本

### 用不到 200 行的 Python 代码编写一个批量检测 URL 是否可以访问的脚本

最近有一个批量检测 URL 是否可以访问的需求，于是找了一个 Python 脚本来实现这个需求（ Python 2.7+ 测试有效）。

> 参考原文
> https://ccie.lol/knowledge-base/python-testing-url-2/

这个脚本会对每个 URL 检测四次，其中 http 检测两次，https 检测两次。之所以是各两次是因为会使用两个包来检测（ urllib 和 urllib2 ）。即：

- urllib 检测 http
- urllib 检测 https
- urllib2 检测 http
- urllib2 检测 https 

共四次。

首先是包的导入和浏览器所使用的 User-Agent 的定义：

```python
# coding=utf-8

import httplib, urllib, urllib2, ssl, time, os, threading

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3298.4 Safari/537.36'}
```

因为增加了多线程，所以多引入了一个名为 threading 的包。

紧接着是 `show_status_urllib(url)` 和 `show_status_urllib2(url)` 两个检测方法，这里面捕获了大量的异常；以及一个用于处理所返回的网页状态码的函数 `return_code(function_name, response)` ：

```python
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
```
这三个方法与之前脚本里的基本一致。

接下来是一个用于格式化日志的函数，以及一个对 URL 进行四次检测的函数：

```python
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
```

接下来是一个对日志进行分类并将日志保存到文本文件的函数：

```python
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
```

`log_of_list` 是一个列表，里面存放了四个打开的 `log` 文件，这四个 log 文件会在 `main()` 主函数里自动创建，存放路径是在 `logs/` 文件夹下（相对路径），具体如下图所示：

![用不到 200 行的 Python 代码编写一个批量检测 URL 是否可以访问的脚本 - 目录结构（1）](https://pic.chaishiwei.com/images/2020/08/20/20200820105836.png)

![用不到 200 行的 Python 代码编写一个批量检测 URL 是否可以访问的脚本 - 目录结构（2）](https://pic.chaishiwei.com/images/2020/08/20/20200820105854.png)

简单地说明下这四个 log 文件具体是存放什么的（XXX 为日期，精确到秒）：

 1) log-XXX.txt ：存放所有检测结果；
 2) log-XXX-http-no-and-https-no.txt ：存放 http 和 https 均无法访问的检测结果；
 3) log-XXX-http-no-but-https-yes.txt ：存放 https 可以访问但 http 无法访问的检测结果；
 4) log-XXX-http-yes-but-https-no.txt ：存放 http 可以访问但 https 无法访问的检测结果；

接下来是在每个进程里执行的函数 `use_thread(thread_total_number, thread_number, url_of_list, log_of_list)` ：

```python
def use_thread(thread_total_number, thread_number, url_of_list, log_of_list):
    i = -1
    for url in url_of_list:
        i += 1
        if i % thread_total_number == thread_number:
            line = request_url(url)
            save_log(log_of_list, line)
            print 'thread_number = ' + str(thread_number) + '\n' + line + '\n'   # 查看当前是哪个进程在运行
    # print 'thread_number EXIT = ' + str(thread_number) + '\n'      # 查看当前是哪个进程已经运行结束
```

和启动进程的函数 `open_thread(thread_total_number, url_of_list, log_of_list)` ：

```python
def open_thread(thread_total_number, url_of_list, log_of_list):
    threads_for_list = []
    for thread_number in range(thread_total_number):
        thread = threading.Thread(target=use_thread, args=(thread_total_number, thread_number, url_of_list, log_of_list))
        thread.start()
        threads_for_list.append(thread)

    # 等待所有进程全部退出
    for t in threads_for_list:
        t.join()
```

最后是主函数，主函数这里也提供了两种检测方法：一种是通过列表来读取出需要检测的 URL ，另一种是通过文本文件 `url.txt` 来读取出需要检测的 URL ：

```python
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
    url_of_list = ['www.baidu.com', 'news.baidu.com/guonei', 'www.qq.com', 'www.taobao.com']

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
```

### 示例

`url.txt` 文件里有如下内容：

```
chaisw.cn
www.taobao.com
```

`url.py` 脚本里有如下内容：

```python
print 'URL Testing For List :\n'
    url_of_list = ['www.baidu.com', 'www.qq.com', 'chaishiwei.com']
```

脚本执行结果如下：

![image-20200820114710346](https://pic.chaishiwei.com/images/2020/08/20/20200820114710.png)

其中 `thread_number = X`，`x` 为当前启动的第几个进程的进程号，可根据自身需要修改代码来决定是否要打印该日志。

![image-20200820115213337](https://pic.chaishiwei.com/images/2020/08/20/20200820115213.png)

代码下载：

```bash
git clone https://github.com/imchaisw/Note/tree/master/testlink testlink
```


