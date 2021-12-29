#!usr/bin/python3 
# -*- coding:UTF-8 -*-

import json
import configparser
import argparse
from colorama import Fore,Style
from typing import Mapping
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client 
from tencentcloud.cvm.v20170312 import models as cvm_models
from tencentcloud.tat.v20201028 import tat_client, models
import pandas as pd
import base64




try:
    cf = configparser.ConfigParser()
    cf.read('./config.ini', encoding='UTF-8')
    SecretId = cf.get("config", "SecretId")
    SecretKey = cf.get("config", "SecretKey")

except:
    print(Fore.YELLOW + "[+] 请填写config.ini文件 [+]" + Style.RESET_ALL)
    exit(0)

cred = credential.Credential(SecretId,SecretKey)
httpProfile = HttpProfile()
httpProfile.endpoint = "cvm.tencentcloudapi.com"
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile



def banner():
    print(Fore.YELLOW + '''
 _____                                   _  __   __              
|_   _|___    __ _  ___   ___    __ _  _| | \ \ / /_   _   __ _  
  | | / _ \  / _` ||__ \ / _ \  / _` ||__ |  \ V /| | | | / _` | 
  | | \__  || | | | __) |\__  || | | | _| |   | | | |_| || | | | 
  |_| |___/ |_| |_||___/ |___/ |_| |_||__/    |_| |_.__/ |_| |_|  by K1p2y3
                        
    ''' + Style.RESET_ALL)


def Tencent_get_Regions():
    try:
        client = cvm_client.CvmClient(cred, "", clientProfile)
        req = models.DescribeRegionsRequest()
        params = {

        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeRegions(req).to_json_string()
        s = json.loads(resp)
        RegionSet = s["RegionSet"]
        Region_list = []
        RegionName_list = []
        for i in RegionSet:
            Region_list.append(i["Region"])
            RegionName_list.append(i["RegionName"])
        a_dict = dict(zip(Region_list,RegionName_list))
        return a_dict
    except TencentCloudSDKException:
        print("获取地域信息失败，请确认Accesskey是否有效")
        exit(0)

def Tencent_scan(regions):
    InstanceId_list = []
    CPU_list = []
    Memory_list = []
    InstanceName_list = []
    OSname_list = []
    PrivateIpAddresses_list = []
    PublicIpAddresses_list = []
    InstanceName_list = []
    CreatedTime_list = []
    ExpiredTime_list = []
    Regions_list = []
    for key in regions:
        client = cvm_client.CvmClient(cred,key, clientProfile)
        req = cvm_models.DescribeInstancesRequest()
        params = {}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req).to_json_string()
        s = json.loads(resp)
        TotalCount = s["TotalCount"]
        if TotalCount != 0:
            print(Fore.GREEN + "[+] 正在扫描" + str(regions[key]) + "主机 : " + str(TotalCount) + Style.RESET_ALL)
            for i in range(0,TotalCount):
                InstanceId_list.append(str(s["InstanceSet"][i]["InstanceId"]))
                InstanceName_list.append(str(s["InstanceSet"][i]["InstanceName"]))
                OSname_list.append(str(s["InstanceSet"][i]["OsName"]))
                CPU_list.append(str(s["InstanceSet"][i]["CPU"]))
                Regions_list.append(str(key))
                Memory_list.append(str(s["InstanceSet"][i]["Memory"]))
                PrivateIpAddresses_list.append(str(s["InstanceSet"][i]["PrivateIpAddresses"]))
                PublicIpAddresses_list.append(str(s["InstanceSet"][i]["PublicIpAddresses"]))
                CreatedTime_list.append(str(s["InstanceSet"][i]["CreatedTime"]))
                ExpiredTime_list.append(str(s["InstanceSet"][i]["ExpiredTime"]))

            dataframe = pd.DataFrame({'InstanceId':InstanceId_list,
                                      '实例名称':InstanceName_list,
                                      '操作系统':OSname_list,
                                      '地域名称':Regions_list,
                                      'CPU核数':CPU_list,
                                      '内存大小':Memory_list,
                                      '内网地址':PrivateIpAddresses_list,
                                      '公网地址':PublicIpAddresses_list,
                                      '创建时间':CreatedTime_list,
                                      '到期时间':ExpiredTime_list})
            dataframe.to_csv("主机信息.csv",index=False,sep=',')          
        else:
            print("[+] 正在扫描" + str(regions[key]) + "主机 : " + str(TotalCount))

def Tencent_command(id,regions,command):
    str1 = command.encode('utf-8')
    command_str = base64.b64encode(str1).decode('utf-8')
    httpProfile.endpoint = "tat.tencentcloudapi.com"
    client = tat_client.TatClient(cred, regions, clientProfile)    
    req = models.RunCommandRequest()
    params = {
        "Content": command_str,
        "InstanceIds": [ id ]
    }
    print(params)
    req.from_json_string(json.dumps(params))
    resp = client.RunCommand(req)
    print(resp.to_json_string())

def main():
    banner()
    parser = argparse.ArgumentParser(description='python3 Tencent_rce.py -i InstanceId -r ap-beijing -c "whoami"')
    parser.add_argument('-s','--scan',action='store_true',required=False,help='Scan Virtual Machine ')
    parser.add_argument('-i','--instanceid',required=False,help='Scan Virtual Machine ')
    parser.add_argument('-r','--regions',required=False,type=str,help='Specified region information ')
    parser.add_argument('-c','--command',required=False,type=str,help='Commands to execute ')
    args = parser.parse_args()

    if args.scan == True:
        regions = Tencent_get_Regions()
        Tencent_scan(regions)

    if args.regions and args.command and args.instanceid:
        Tencent_command(args.instanceid,args.regions,args.command)
    else:
        exit(0)


if __name__=="__main__":
    main()
