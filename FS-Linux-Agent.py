#!/usr/bin/python
# -*- coding: utf-8 -*-
#Version=<<version-info>>
import sys, getopt

is_python2 = (sys.version_info[0] == 2)

ProxyServerAdditional = ""
ProxyUserNameAdditional = ""
ProxyPasswordAdditional = ""
ProxyPortAdditional = ""
try:
    opts, args = getopt.getopt(sys.argv[1:],"hs:u:k:p:",["server=","username=","password=","port="])
except getopt.GetoptError:
    print('FS-Linux-Agent.py -i <inputfile> -o <outputfile>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('FS-Linux-Agent.py --server <host_address> --username <username> --password <password> --port <port>')
        sys.exit()
    elif opt in ("-s", "--server"):
        ProxyServerAdditional = arg
    elif opt in ("-u", "--username"):
        ProxyUserNameAdditional = arg
    elif opt in ("-k", "--password"):
        ProxyPasswordAdditional = arg
    elif opt in ("-p", "--port"):
        ProxyPortAdditional = arg

AccountURI = "https://iamgroot.freshservice.com"
ProbeKey = ""
RegistrationKey="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwb3J0YWxfdXJsIjoiaHR0cHM6Ly9pYW1ncm9vdC5mcmVzaHNlcnZpY2UuY29tIn0.MRpI8Sq292t_3Buagj97zJceshXZ32RtU596ETVtvUU"
ProxyServer = ""
ProxyUserName = ""
ProxyPassword = ""
ProxyPort = ""
ForcePushInterval = 7  #days
PeriodicScanInterval = 30  #minutes
ScheduleInterval = 7 #days

if is_python2:
    from urlparse import urlparse
    from urllib2 import build_opener, ProxyHandler, HTTPSHandler
else:
    from urllib.parse import urlparse
    from urllib.request import build_opener, ProxyHandler, HTTPSHandler

Proxy = {}
Opener = build_opener(HTTPSHandler)

def get_proxy_config(server,port,username,password):
    if server and port and username and password:
        return {"https" : "https://{}:{}@{}:{}".format(username, password, server, port)}
    elif server and port:
        return {"https" : "https://{}:{}".format(server, port)}
    else:
        print("Provided proxy information is not sufficient so proceeding instalation without proxy settings")
        return {}

def open_url(url):
    try:
        return Opener.open(url)
    except Exception as e:
        print(e.args[0])
        # log valid message
        if Proxy:
            print("Exception occured while trying to download with Proxy")
            print("Try to download without proxy")
            globals()["Proxy"] = {}
            globals()["Opener"] = build_opener(HTTPSHandler)
            return open_url(url)
        else:
            sys.exit(0)

if ProxyServerAdditional: Proxy = get_proxy_config(ProxyServerAdditional, ProxyPortAdditional, ProxyUserNameAdditional, ProxyPasswordAdditional)
if Proxy: Opener = build_opener(ProxyHandler(Proxy))

account_domain = urlparse(AccountURI)
cdn_url = "https://fstools.freshservice.com"
manifest_url = cdn_url + "/agent/linux-manifest.json"
print("Please read the License Agreement in the following location")
print("https://s3.amazonaws.com/fs-probe-production/FreshserviceEULA.pdf")
eula_statement = "Do you Accept the End User License Agreement linked above type yes/no : "
accept = raw_input(eula_statement) if is_python2 else input(eula_statement)
if accept=="no":
    print("you need to Accept the EULA to proceed further")
    sys.exit(0)
elif accept!="yes":
    print("invalid choice type yes/no")
    sys.exit(0)
try:
    ProxyServer
except NameError:
    ProxyServer = ""
try:
    ProxyUserName
except NameError:
    ProxyUserName = ""
try:
    ProxyPassword
except NameError:
    ProxyPassword = ""
try:
    ProxyPort
except NameError:
    ProxyPort = ""

try:
    AccountURI
except NameError:
    sys.stderr.write(
        "\"AccountURI\" is a mandatory field don't remove it from the script, you can find it from configuration.json. "
        "\nRefer solution manual for further information")
    exit(1)
try:
    ProbeKey
except NameError:
    sys.stderr.write(
         "\"ProbeKey\" is a mandatory field don't remove it from the script, you can find it from configuration.json."
         "\nRefer solution manual for further information")
    exit(1)
import os
curr_dir = os.path.dirname(os.path.realpath(__file__))
manifest = open_url(manifest_url).read()
import json
manifest = json.loads(manifest.decode('utf-8'))
prod_version = ""
if manifest["AvailableTo"] == "*" or account_domain.netloc.split('.')[0] in manifest["AvailableTo"]:
    prod_version = manifest["ProductVersion"]
else:
    prod_version = manifest["OldVersion"]
url = cdn_url + "/agent/linux-installer-"+prod_version+".tar.gz"

file_name = url.split('/')[-1]
u = open_url(url)
f = open(os.path.join(curr_dir, file_name), 'wb')
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0]) if is_python2 else int(meta.get("Content-Length"))
print("Downloading: %s Bytes: %s" % (file_name, file_size))
file_size_dl = 0
block_sz = 4096
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status += chr(8)*(len(status)+1)
    print(status,)
f.close()

import subprocess

class ShellScriptException(Exception):
    def __init__(self, return_code, std_out, std_err):
        self.return_code = return_code
        self.std_out = std_out
        self.std_err = std_err
        self.message = "return_code"+str(return_code)+"\nstd_out : "+str(std_out)+"\nstd_err : "+str(std_err)

def execute_shell_command_ex_handled(ShellCommand, silent=False):
    if not silent:
        print("Executing ShellCommand : "+ShellCommand)
    process = subprocess.Popen(ShellCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = process.communicate()
    if not silent:
        print("stdout : "+ str(out[0]))
        print("stderr : "+ str(out[1]))
    if process.returncode != 0:
        raise ShellScriptException(process.returncode, out[0], out[1])

    return out[0].strip()

def write_file(content, path):
    with open(path, "w") as text_file:
        print("file opened successfully")
        text_file.write(content)
    return True

config = {
    "AccountURI": AccountURI,
    "AgentKey": "",
    "ProbeKey": ProbeKey,
    "ProxyPassword": ProxyPassword,
    "ProxyPort": ProxyPort,
    "ProxyServer": ProxyServer,
    "ProxyUserName": ProxyUserName,
    "ForcePushInterval": ForcePushInterval,
    "PeriodicScanInterval": PeriodicScanInterval,
    "ScheduleInterval": ScheduleInterval,
    "VersionInfo": prod_version
}
additional_configuration = {
    "ProxyServer": ProxyServerAdditional,
    "ProxyUserName": ProxyUserNameAdditional,
    "ProxyPassword": ProxyPasswordAdditional,
    "ProxyPort": ProxyPortAdditional
}
if RegistrationKey!="<<registration_key>>":
    config["RegistrationKey"] = RegistrationKey

if AccountURI == "<<account_uri>>" \
        or ProbeKey == "<<probe_key>>" \
        or ProxyPassword == "<<proxy_password>>" \
        or ProxyPort == "<<proxy_port>>" \
        or ProxyServer == "<<proxy_server>>" \
        or ProxyUserName == "<<proxy_user_name>>":
    print(json.dumps(config, indent=4))
    print("configuration not properly entered Exiting")
    sys.exit(1)
try:
    import shutil
    shutil.rmtree(os.path.join(curr_dir, "Freshservice"))
except Exception as e:
    print(e)
execute_shell_command_ex_handled('tar -zxvf "{1}/{0}" -C "{1}"'.format(file_name, curr_dir))
write_file(json.dumps(config), os.path.join(curr_dir, "Freshservice-Discovery-Agent", "conf", "Configuration.json"))
if ProxyServerAdditional != "":
    write_file(json.dumps(additional_configuration), os.path.join(curr_dir, "Freshservice-Discovery-Agent", "conf", "AdditionalConfiguration.json"))
print("\n\n\n Installing Freshservice Agent ...\n\n")
execute_shell_command_ex_handled('/bin/bash "{0}" "{1}" "{2}" "{3}" "{4}"'.format(os.path.join(curr_dir, "Freshservice-Discovery-Agent", "setup.sh"), ProxyServerAdditional, ProxyPortAdditional, ProxyUserNameAdditional, ProxyPasswordAdditional))
try:
    import shutil
    shutil.rmtree(os.path.join(curr_dir, "Freshservice-Discovery-Agent"))
except Exception as e:
    print(e)
try:
    os.remove(os.path.join(curr_dir, file_name))
except Exception as e:
    print(e)