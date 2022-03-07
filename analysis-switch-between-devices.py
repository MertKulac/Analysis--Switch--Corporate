def switch_connection(device_ip):

    bekci = "10.222.247.240"
    port = 2222
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    global vlan_list

    try:
        ssh.connect(bekci, port=2222, username=username, password=password, timeout=20)
        remote_connection = ssh.invoke_shell()
        print (colored ("connected_bekci", "green"))

        t = 0
        Err_ = ""
        remote_connection.send(device_ip + "\r")
        while True:
            time.sleep(5)
            t += 5
            if t > 60:
                print("timeout")
                Err_ = "TIMEOUT"
                break

            output3 = remote_connection.recv(65500)
            result3 = output3.decode('ascii').strip("\n")

            if result3[-1][-1] == ">":
                print (colored ("connected_Switch_"+ device_ip,"blue"))
                print("Connection_Time", t)
                break
            elif result3[-1][-1] in ["Do you want to proceed with Management IP Detection? [y/n]: ", "Type to search or select one:", "Press any key to continue...", " "]:
                Err_ = True
                with open("connection_problem.txt", "a") as f:
                    f.write(device_ip + "connection_problem" + "\n")
                    f.close()
                break

        if not Err_:
            remote_connection.send("terminal length 0 \r")
            time.sleep(1)
            remote_connection.send("show vlan " + " \r")
            time.sleep(2)
            output = remote_connection.recv(65500)
            result = output.decode('ascii').strip("\n")
            output_list_fnk1 = result.splitlines()

            time.sleep(2)
            remote_connection.send("s 0 t \r")
            time.sleep(1)
            remote_connection.send("display vlan " + " \r")
            time.sleep(2)
            output2 = remote_connection.recv(65500)
            result2 = output2.decode('ascii').strip("\n")
            output_list_fnk2 = result2.splitlines()

            vlan_list = []

            for line_fnk1 in output_list_fnk1:
                if("enet" in line_fnk1):
                    words1 = line_fnk1.split()
                    port_vlan = words1[0]

                    if int(port_vlan) > 200 and int(port_vlan) < 4096:
                        vlan_list.append(port_vlan)
                        print(vlan_list)

            for line_fnk2 in output_list_fnk2:
                if "enable" in line_fnk2 and "default" in line_fnk2:
                    words2 = line_fnk2.split()
                    port_vlan2 = words2[0]

                    if int(port_vlan2) > 200 and int(port_vlan2) < 4096:
                        vlan_list.append(port_vlan2)
                        print(vlan_list)
        else:
            with open("vlan.txt", "a") as f:
                f.write(device_ip + "_erisim veya farkli bir problem kontrol ediniz "+ "\n")
                f.close()

    except Exception as e:
        print(device_ip +"\n"+ "no connection_to_device " + str(e) + Err_, end=" ")
        time.sleep(2)
        with open("vlan.txt", "a") as f:
            f.write(device_ip + "_erisim veya farkli bir problem kontrol ediniz "+ "\n")
            f.close()

def connectionbekci(ip):

    bekci1 = "10.222.247.240"
    port = 2222
    bekci_prompt = ".*one: "
    UPE_prompt = ".*>"
    ASR_prompt = ".*#"
    PE_IP = "172.28.111.195"
    SSH = paramiko.SSHClient()
    SSH.load_system_host_keys()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    try:
        #Kartal UPE connection
        SSH.connect(hostname=bekci1, username=username, password=password, port=2222)
        with SSHClientInteraction(SSH, timeout=20, display=False, buffer_size=65535) as command:
            command.expect(bekci_prompt, timeout=2)

            if bekci_prompt == command.last_match:
                print("###########Connection to bekci1 was established.###########")

                command.send(PE_IP)
                command.expect(UPE_prompt, timeout=20) ###cause of bekci problem timeout set 10

                if command.last_match == UPE_prompt:
                    print("###########Connection to UPE was established.###########")
                    command.send("display ip routing-table {}".format(ip))
                    command.expect(UPE_prompt)
                    routing = command.current_output_clean
                    routing = routing.splitlines()
                    result = [x for x in routing if "RD" in x]
                    route = result[0].split(" ")
                    route.remove("RD")
                    IP = route[24] or route[25] or route[26] or route[27] or route[28]
                    hop = ''.join(IP)
                    print(hop)

                else:
                    print("###########Connection to UPE was NOT established.###########")
            else:
                print("##########Connection to bekci1 was NOT established, Please check your network connection and try again.###########")

    except Exception as Error:
        print(Error)

    return hop

def description(ip, vlan):

    bekci2 = "10.222.247.240"
    bekci_yedek2 = "bekci.superonline.net"
    port = 2222
    bekci_prompt = ".*one: "
    UPE_prompt = ".*>"
    SSH = paramiko.SSHClient()
    SSH.load_system_host_keys()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    try:
        SSH.connect(hostname=bekci2, username=username, password=password, port=2222)
        with SSHClientInteraction(SSH, timeout=20, display=False, buffer_size=65535) as command:
            command.expect(bekci_prompt, timeout=2)

            if bekci_prompt == command.last_match:
                print("###########Connection to bekci2 was established.###########")

                command.send(ip)
                command.expect(UPE_prompt, timeout=20) ###cause of bekci problem timeout set 10

                if command.last_match == UPE_prompt:
                    print (colored ("connected_Switch_Uplink_"+ ip,"red"))
                    command.send("display int des | i {}".format(vlan))
                    command.expect(UPE_prompt)
                    time.sleep(4)
                    routing = command.current_output_clean
                    routing = routing.splitlines()
                    result = [x for x in routing if "up" and "100" in x]
                    result2 = result[0]
                    sonuc = ''.join(result2)
                    print(sonuc)

                    with open('vlan.txt', 'a') as f:
                        f.write(str(sonuc) + "\n")

                else:
                    print("###########Connection to bekci_yedek2 established.###########")
                    try :
                        SSH.connect(hostname=bekci_yedek2, username=username, password=password, port=2222)
                        with SSHClientInteraction(SSH, timeout=20, display=False, buffer_size=65535) as command:
                            command.expect(bekci_prompt, timeout=2)

                            if bekci_prompt == command.last_match:
                                print("###########Connection to bekci2 was established.###########")

                                command.send(ip)
                                command.expect(UPE_prompt, timeout=20) ###cause of bekci problem timeout set 10

                                print (colored ("connected_Switch_Uplink_"+ ip,"red"))
                                command.send("display int des | i {}".format(vlan))
                                command.expect(UPE_prompt)
                                routing = command.current_output_clean
                                routing = routing.splitlines()
                                result = [x for x in routing if "up" in x]
                                result2 = result[2]

                                with open('vlan.txt', 'a') as f:
                                    f.write(str(result2) + "\n")

                    except Exception as Error:
                        print(Error)
            else:
                print("##########Connection to bekci2 was NOT established, Please check your network connection and try again.###########")


    except Exception as Error:
        print(Error)

hosts = []
f1 = open('Switch_Etki.txt', 'r')
devices = f1.readlines()

for i in devices:
    i = i.split()
    if len(i) != 0:
        #print(i)
        hosts.append(i[0])

#print (hosts)

for host in hosts:
    switch_connection(host)
    for vlan in vlan_list:
        description(connectionbekci(host),vlan)

host = 0
while host > 1:
    description(connectionbekci(host),vlan)
    host +=1
    break

    sys.exit()

#print (hosts)
