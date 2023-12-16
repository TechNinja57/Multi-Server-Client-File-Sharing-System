from socket import *
import sys
import threading
import time
import os
from threading import current_thread
import itertools
import math
import shutil

NUMBER_OF_THREADS = 0       # A variable to store how many threads will be created. One thread for one server

files_folder=os.path.abspath(os.getcwd())           # Gets the client file path

files_folder = os.path.join(files_folder,"files")

file_dir_further_seg = os.path.join(files_folder, "further_seg_files")

lists_created_names_dir = os.path.join(files_folder,"lists_created")

output_loc = ""                                 # Output location variable

"""Making directory if it not exists already"""

if not os.path.exists(files_folder):
    os.makedirs(files_folder)

if not os.path.exists(file_dir_further_seg):
    os.makedirs(file_dir_further_seg)

if not os.path.exists(lists_created_names_dir):
    os.makedirs(lists_created_names_dir)


total_no_of_files=0 
separator = "<SEPARATOR>"   #A separater variable.IT will help us in sending and receiving multiple messages in one go

no_of_servers=NUMBER_OF_THREADS
total_file_size=0                   #A variable to store the total file size    
og_file_name = ""                   #A varible to store the file name which will be downloaded


st_interval = 0                     #Interval variable for the output dislpay


true=True
var_false=False


no_of_files_towork=0
no_of_files_received=0


incase_server_stopped_no_of_files=0

ip_adress=""
port_num=0

total_connections=[]            # A list which stores the all connections available with IPs $ PORT numbers
connections_withoutErrors=[]    # <A list which stores the all connections available with IPs $ PORT numbers but remove a particular
                                # connection when a server fails>







remaining_list_names=[]         # A list which stores the list names which were intended to download from the failed servers
total_list_data=[]              # It stores the total file data downloaded from all the servers
list_names=[]                   # It stores the list which are received from the servers
all_list_names=[]               # It contains all the list names which will be created at the server end
seg_list_sizes={}               # It stores the list names with their sizes
seg_lists_in_a_list=[]          # It stores the list data from each servers with list names in 3D manner

again_seg_lists=[]              # It contains the names of those lists which were created by dividing the remaining lists into new chunks after a server failure

list_of_seg_sizes=[]            # It stores the total sizes of lists which servers will send to the client

recv_list_total_size=[]         # It stores the sizes of lists data which is being received from the server and shows the current sizes of lists as output
resume="false"
extra_size_var=[0]              
total_download_speed=[]         # It stores the individuals download speeds of file data in form of segmented lists data from each server and then Add them and display as output
dict_for_lists_data={}          # It stores the incoming data from servers and stores them in its individual list items

threading_list=[]               # It stores the threads created

#Function to connect to a server
def connects(serverIP,serverPort):
    ip_adress=serverIP          
    port_num=serverPort

    extra_list=[]               #local list to store ip and port
    extra_list.append(serverIP)     #Ip is added to the list
    extra_list.append(serverPort)   #Port number is added to the list
    
    global total_connections,connections_withoutErrors  #These lists are made global here
    
    
    connections_withoutErrors.append(extra_list)        #This list appends the ip and port of given server
    clientSocket = socket(AF_INET, SOCK_STREAM)         
    try:  #TRY BLOCK
        clientSocket.connect((serverIP,serverPort))     #Here client connects to a particular server
        
        
        receive_data_from_server(clientSocket,ip_adress,port_num)   # A function called which carries out the normal working of client if all the servers work correctly
        
        
        
        
        
    except :       #EXCEPT BLOCK
        print("Error Connection")
        extra_list = []  # local list to store ip and port
        extra_list.append(serverIP)     # Ip is added to the list
        extra_list.append(serverPort)   # Port number is added to the list
        connections_withoutErrors.remove(extra_list)    #<If a particular server fails then its ip and port is removed from this list
                                                        #which contains the inforamtion of only active servers>
   



#Function which contains the working of normal working of client if not a single server fails
def receive_data_from_server(socket,ip,port):

    #These lists & variables are made global here
    global output_loc, total_download_speed, recv_list_total_size, list_of_seg_sizes, total_file_size, og_file_name, seg_lists_in_a_list, dict_for_lists_data, seg_list_sizes, connections_withoutErrors, list_names, total_list_data, all_list_names, extra_size_var, NUMBER_OF_THREADS

    
    try:  # TRY BLOCK

        socket.send(resume.encode('utf-8'))     # here client sends servers the msg whether to send the previous video or not
        time.sleep(0.1)                         # Here client sleeps for some time

        for l in range(NUMBER_OF_THREADS):      # <This loop to create list items in dictionary depending upon the number of servers
            dict_for_lists_data["list{0}".format(l)] = []       # for storing lists data receiving from the server>
           

        for o in range(NUMBER_OF_THREADS):     # <This loop to create varibale items in dictionary depending upon the number of servers 
            seg_list_sizes["list{0}".format(o)] = 0             # to store each list size>

        
        
        all_list_names.sort() #The list is being sorted here
        
        string_to_send_to_divide="divide by "   #<Here client sends the server message to divide the file data in lists 
                                                # chunks depending upon the number of servers active>
        socket.send(f"{string_to_send_to_divide}{separator}{str(NUMBER_OF_THREADS)}".encode('utf-8'))

        time.sleep(0.1)

        socket.send("Total File Size and File Name".encode('utf-8')) # Client asks the server for file total size and its name
        
        data = socket.recv(204800).decode('utf-8')                  # Here client receives the file size and name from server 
        total_file_size, og_file_name = data.split(separator)       # Storing file size and name in variables

        
        

        
        # Loop which asks for a particular list size and receives it
        for j in range(NUMBER_OF_THREADS):
            if(int(current_thread().name) == (j)):
                
                string="Send size of "+all_list_names[j]           
               
                

                socket.send(string.encode('utf-8'))                   #Client asks for that particular list size
                time.sleep(0.1)
                data=socket.recv(204800).decode('utf-8')              #Client receives the size of particular list

                del list_of_seg_sizes[int(current_thread().name)]             # <List was initialized with range based on number of servers with 0 at each index
                list_of_seg_sizes.insert(int(current_thread().name), float(data))   # Here that value at index is removed and size of list is stored a that index>
                
                seg_list_sizes[all_list_names[j]] = float(data)       # Size is also being stored in the dictionary
        
        # Loop which sends the server message to send the particular list 
        for j in range(len(all_list_names)):
            if(int(current_thread().name) == (j)):
                string=all_list_names[int(current_thread().name)]+"_data"
                time.sleep(0.1)
                socket.send(string.encode('utf-8'))                    #Client sends the message to server
        

        

        # Local variables used in displaying the output in console
        server=""
        file_size=0
        r_file_size=0

        total_size=0
        

        data="sert"
        strings="done"
        stres=strings.encode('utf-8')

        

        
        

        
        file_name="list"+current_thread().getName()+".txt"          # A file name is set here based on the number of chunks/servers
        
        file_path= os.path.join(files_folder,file_name)             # The path for that file is set here
        

        ind_list_file = open(file_path,"ab")                        # File is opened here
        
        
        #While loop in which server downloads the data from the server
        while data:
            
            t1 = time.time()                      # Measuring the current time
            
            data=socket.recv(204800)              # Clieent is receiving the data from server
            t2 = time.time()                      # Measuring the current time
            
            
            if data==stres:                       # Message "done" is sent by server to the client indicating the server has sent all the data
                break                             # If this happens then we break out of loop
            
            else:  # ELSE BLOCK
                
                # <A loop where received file data is stored in the dictonary particular list item
                # based upon that which hread is being executed right now>
                for k in range(len(all_list_names)):
                    if((current_thread().name) == str(k)):
                        in_loop_list=dict_for_lists_data.get('list'+str(k))             # Get the particular list item from dictionary
                        in_loop_list.append(data)                                       # Appending data in that particular list item
                        
                        ind_list_file.write(data)                                       # Data is written to the file here
                        
                        server = "Server"+str(k)

                        
                        r_file_size = os.stat(file_path).st_size                        # Reading the size of file which is being downloaded

                        
                        r_file_size=r_file_size / (1024 * 1024)                          # Convert Bytes to MegaBytes (MB)
                        
                        del recv_list_total_size[int(current_thread().name)]            # <Here that value at a particular index is removed depending upon the current thread executing
                        recv_list_total_size.insert(int(current_thread().name),r_file_size)     #  and size of list is stored at that index>
                        
                        
                        
                        file_size=list_of_seg_sizes[int(current_thread().name)]         # Getting the list size which is in download progress
                        
                

                
                
                t = t2-t1               # Subtracting the current times t1 & t2
                if(t == 0):             # <If t becomes equal to zero we set it to 1
                    t = 1               # to avoid division by zero>
                ssp = file_size / t     # Calculating list download speed from a particular server
                del total_download_speed[int(current_thread().name)]                    # <Here that value at a particular index is removed 
                total_download_speed.insert(int(current_thread().name),ssp)             # and speed of downloading list from a server is stored a that index>
                sp = sum(total_download_speed)                                          # It sums all the entries in the list
                
                
                # Output is displayed in the console
                print(server, ": {:.2f} MB / {:.2f} MB ,Download Speed: {:.2f} kB/s".format(r_file_size, file_size , ssp) )
                
                print("Total: {:.2f} MB / {:.2f} MB , Download Speed: {:.2f} kB/s".format((sum(recv_list_total_size)) ,float(total_file_size) ,sp) )
                time.sleep(st_interval)             # Client sleeps for a particular time set by the user                                
        
        
        test_list = dict_for_lists_data.get('list'+current_thread().name)   #Get the list from dictionary in which data was stored
        ex_test_list=[]                                                     # Appending data with list name in "ex_test_list"
        ex_test_list.append('list'+current_thread().name)
        ex_test_list.append(test_list)
        seg_lists_in_a_list.append(ex_test_list)                            # Appending data with name in this list in 3D manner
                                                                            # [['list0',[data]],....]

        ind_list_file.close()                                               # File is closed here
        #This loop adds the list name which is received from the server totally
        for m in range(NUMBER_OF_THREADS):                                  
            if((current_thread().name) == str(m)):
                list_names.append(all_list_names[m])
        
        socket.close()                              #Client closes the connection
        
        all_list_names.sort()                       # Lists are sorted here
        list_names.sort()

        
        # If all the lists are received then if block executes where the data is written to the file
        if (all_list_names==list_names):
            seg_lists_in_a_list.sort()              # List is sorted here
            total_list_data.clear()
            seg_lists_in_a_list = list(itertools.chain(*seg_lists_in_a_list))       #Converts the 3D list to 2D list
           
           #Converts the 2D list to 1D list and storing the data in another list
            for j in range(len(seg_lists_in_a_list)):
               
                if (j % 2) == 0:
                    continue
                for k in range(len(seg_lists_in_a_list[j])):
                    total_list_data.append(seg_lists_in_a_list[j][k])               #Appending data from one list to another
                    

            output_path = os.path.join(output_loc,og_file_name)                     # Here data is written to the file in location set by the user
            with open (output_path,"wb") as file :
                for i in range(len(total_list_data)):
                    file.write(total_list_data[i])
            
            
            
        
    except:  # EXCEPT BLOCK
        time.sleep(1)
        extra_list = []                             # local list to store ip and port
        extra_list.append(ip)                       # Ip is added to the list
        extra_list.append(port)                     # Port number is added to the list
        connections_withoutErrors.remove(extra_list)  #<If a particular server fails then its ip and port is removed from this list
                                                      #which contains the inforamtion of only active servers>

#Function to check if any data of file is remaining or not 
#If it is then to get the data of remaining server
def receive_the_remaining_data():
    #These lists & variables are made global here
    global total_download_speed, recv_list_total_size, list_of_seg_sizes, threading_list, connections_withoutErrors, remaining_list_names, total_connections, all_list_names, list_names, total_list_data, og_file_name

    all_list_names.sort()           # Lists are sorted here
    list_names.sort()
    remaining_list_names= list( set(all_list_names)- set(list_names))   # Client checks for any remaining file

    remaining_list_names.sort()     # List is sorted here

    

    total_download_speed.clear()    # Lists data is erased
    recv_list_total_size.clear()
    list_of_seg_sizes.clear()

    # Lists are assigned 0 value
    for t in range(len(connections_withoutErrors)):     
        list_of_seg_sizes.append(0)
        recv_list_total_size.append(0)
        total_download_speed.append(0)

    files_to_get=len(remaining_list_names)  #Get the list length 
    
    if (files_to_get==0):                       #If no further data is reamining then:
        print("The File has been Downloaded")   # this line will be executed
        
        try:
            shutil.rmtree(files_folder)
        except:
            pass
    else:       #ELSE BLOCK
        threading_list.clear()      # List data is erased
        time.sleep(1)
        #This loop creates new threads and each new socket is created by each thread based on the number of servers active and running
        for i in range(len(connections_withoutErrors)):
            # Thread is created here
            t=threading.Thread(target=connect_again_and_receive_the_remaining_data ,args=[connections_withoutErrors[i][0],connections_withoutErrors[i][1],remaining_list_names])
            t.setName(i)                # Thread is assigned a name here
            threading_list.append(t)    # Thread is added to threading list
            t.start()                   # Thread is started here
    
        
#Function to connect to an active server the second time when one or more servers failed
def connect_again_and_receive_the_remaining_data(ip, port, list_name):
    
    global total_connections,connections_withoutErrors  #These lists are made global here
    
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:  # TRY BLOCK
        clientSocket.connect((ip, port))         #Here client connects to a particular server
        print("Connected",ip,port)
        again_receive(clientSocket,ip,port,list_name)       # A function called which carries out the working of client if one or more servers stop working

    except:  # EXCEPT BLOCK
        print("Error Connection")
        extra_list = []                       # local list to store ip and port
        extra_list.append(ip)                 # Ip is added to the list
        extra_list.append(port)               # Port number is added to the list
        connections_withoutErrors.remove(extra_list)   #<If a particular server fails then its ip and port is removed from this list
                                                       #which contains the inforamtion of only active servers> 


#Function to receive the remaining data fom the active servers if one or more servers failed
def again_receive(socket, ip, port, name_of_list):
    #These lists & variables are made global here
    global output_loc, total_download_speed, recv_list_total_size, list_of_seg_sizes, total_list_data, extra_size_var, seg_lists_in_a_list, again_seg_lists, dict_for_lists_data, connections_withoutErrors, seg_list_sizes, remaining_list_names, seg_list_sizes, connections_withoutErrors, list_names
    
    try:  # TRY BLOCK

        
        extra_list=[]
        time.sleep(1)                   # Here client sleeps for some time
        

        #<Here client sends the server message to divide the file data in lists 
        # chunks depending upon the number of servers active>
        string_to_send_to_divide="divide by "
        socket.send(f"{string_to_send_to_divide}{separator}{str(len(connections_withoutErrors))}".encode('utf-8'))
            

        time.sleep(0.009)
        
        socket.send(str(len(remaining_list_names)).encode('utf-8'))  # Client send the number of original list remaining to the servers


        
        time.sleep(0.1)
        string_to_send_to_list_names=separator.join(remaining_list_names)   # List is converted to a string here
        
            
        socket.send(string_to_send_to_list_names.encode('utf-8'))    # Client sends the remaining lists lists names to servers
        #start of main work
        for x in range(len(remaining_list_names)):
            
            extra_list=remaining_list_names[x]                  # Gets the list name
            
            seg_list_sizes.clear()                              # Lists data is erased
            dict_for_lists_data.clear()
            extra_size_var.clear()
            recv_list_total_size.clear()
            list_of_seg_sizes.clear()
            total_download_speed.clear()
            
            #In this loop 0 is appended in these lists till the index (NUMBER_OF_THREADS-1)
            for z in range(len(connections_withoutErrors)):
                list_of_seg_sizes.append(0)
                recv_list_total_size.append(0)
                total_download_speed.append(0)

            for l in range(len(connections_withoutErrors)):          # <This loop to create list items in dictionary depending upon the number of servers
                dict_for_lists_data["list{0}".format(l)] = []               # for storing remaining lists data receiving from the server>

            for o in range(len(connections_withoutErrors)):         # <This loop to create varibale items in dictionary depending upon the number of servers 
                seg_list_sizes["list{0}".format(o)] = 0             # to store each list size>
            
            time.sleep(0.001)
            
            socket.send(str(len(connections_withoutErrors)).encode('utf-8'))         #Here client sends the server message to divide the reamining file data in lists   


            
            time.sleep(0.009)
            


            
            time.sleep(0.09)

            
            string_recv_with_dvd_ln=socket.recv(204800).decode('utf-8')# 3 step        # <Client receives the original list(which was intended to be received from the server)
                                                                                       #  divided into further list with their names excluding data>

            list_temp_files=list(string_recv_with_dvd_ln.split(separator))             # Received list names in string are stored in a list
            
            

            time.sleep(0.03)
            # Loop which asks for a particular list size and receives it
            for j in range(len(connections_withoutErrors)):
                if(int(current_thread().name) == (j)):
                    
                    string = "Send size of "+list_temp_files[j]

                    socket.send(string.encode('utf-8'))                          #Client asks for that particular list size
                    time.sleep(0.1)
                    data = socket.recv(204800).decode('utf-8')#                  #Client receives the size of particular list
                    del list_of_seg_sizes[int(current_thread().name)]                   # <List was initialized with range based on number of servers with 0 at each index
                    list_of_seg_sizes.insert(int(current_thread().name), float(data))   # Here that value at index is removed and size of list is stored a that index>

                    seg_list_sizes[list_temp_files[j]] = float(data)                    # Size is also being stored in the dictionary
            
            
            # Loop which sends the server message to send the particular list
            for j in range(len(list_temp_files)):
                if(int(current_thread().name) == (j)):
                    string = list_temp_files[j]+"_data"
                    time.sleep(0.1)
                    socket.send(string.encode('utf-8'))                 #Client sends the message to server
                    print(string)
            
            
            # Local variables used in displaying the output in console
            server = ""
            file_size = 0
            r_file_size = 0
            
            file_name = remaining_list_names[x]+"_"+"list"+current_thread().getName()+".txt"
            file_path = os.path.join(file_dir_further_seg, file_name)
            ind_list_file = open(file_path, "ab")

            data = "sert"
            strings = "done"
            stres = strings.encode('utf-8')
            # Local variables used in displaying the output in console
            while data:
                t1 = time.time()            # Measuring the current time

                data = socket.recv(204800)  # Client is receiving the data from server
                t2 = time.time()            # Measuring the current time

                if data == stres:            # Message "done" is sent by server to the client indicating the server has sent all the data
                    break                    # If this happens then we break out of loop

                else:  # ELSE BLOCK
                    
                    # <A loop where received file data is stored in the dictonary particular list item
                    # based upon that which hread is being executed right now>

                    for k in range(len(list_temp_files)):
                        if((current_thread().name) == str(k)):
                            in_loop_list = dict_for_lists_data.get('list'+str(k))           # Get the particular list item from dictionary
                            in_loop_list.append(data)                                       # Appending data in that particular list item
                            
                            ind_list_file.write(data)                                       # Data is written to the file

                            
                            r_file_size = os.stat(file_path).st_size                        # Reading the size of file in which data is being stored

                            server = "Server"+str(k)
                                                  
                            r_file_size = r_file_size/ (1024 * 1024)                        # Convert Bytes to MegaBytes (MB)

                            
                            del recv_list_total_size[int(current_thread().name)]            # <Here that value at a particular index is removed depending upon the current thread executing
                            recv_list_total_size.insert(int(current_thread().name),r_file_size)          #  and size of list is stored at that index>

                            file_size = list_of_seg_sizes[int(current_thread().name)]       # Getting the list size which is in download progress

                    
                    t = t2-t1                    # Subtracting the current times t1 & t2
                    if(t == 0):                  # <If t becomes equal to zero we set it to 1
                        t = 1                    # to avoid division by zero>
                    ssp = file_size / t          # Calculating list download speed from a particular server
                    del total_download_speed[int(current_thread().name)]                        # <Here that value at a particular index is removed 
                    total_download_speed.insert(int(current_thread().name), ssp)                # and speed of downloading list from a server is stored a that index>
                    sp = sum(total_download_speed)                                              # It sums all the entries in the list
                    
                    


                    # Output is displayed in the console
                    print(server, ": {:.2f} MB / {:.2f} MB ,Download Speed: {:.2f} kB/s".format(r_file_size, file_size, ssp) )

                    print("Total: {:.2f} MB / {:.2f} MB , Download Speed: {:.2f} kB/s".format(sum(recv_list_total_size) ,sum(list_of_seg_sizes) ,sp) )

                    time.sleep(st_interval)     # Client sleeps for a particular time set by the user
                
                        
            list_name=remaining_list_names[x]
            test_list = dict_for_lists_data.get('list'+current_thread().getName())     #Get the list from dictionary in which data was stored
            ex_test_list = []                                        # Appending data with list name in "ex_test_list"
            ex_test_list.append('list'+current_thread().getName())
            ex_test_list.append(test_list)
            again_seg_lists.append(ex_test_list)                    # Appending data with name in this list in 3D manner
            print(len(again_seg_lists))                             # [['list0',[data]],....]

            ind_list_file.close()               # File is closed here
            
            # <If the last thread is being executed then this code executes which
            # will order the data for one reamining file from the servers and 
            # stores in the list "seg_lists_in_a_list">
            if ( int(current_thread().name) == (len(connections_withoutErrors) - 1)):
                time.sleep(0.15)
                again_seg_lists.sort()                  # List is sorted here
                ex_test_list=[]
                again_seg_lists = list(itertools.chain(*again_seg_lists))   #Converts the 2D list to 1D list
                for i in range(len(again_seg_lists)):
                    if i % 2 == 0:
                        for k in range(len(again_seg_lists[i])):
                            print(again_seg_lists[i][k])
                    else:
                        for j in range(len(again_seg_lists[i])):
                            ex_test_list.append(again_seg_lists[i][j])      #Appending data from one list to another
                
                
                test=[]
                test.append(remaining_list_names[x])
                test.append(ex_test_list)               # Appending data with list original name in "test"
                seg_lists_in_a_list.append(test)        # Appending data with name in this list in 3D manner

                
                list_names.append(remaining_list_names[x])          # Adds the list name to "list_names" which is received from the server totally
                

                again_seg_lists.clear()                 # Lists data is erased

                total_download_speed.clear()
                recv_list_total_size.clear()
                list_of_seg_sizes.clear()

                # Lists are append 0 value with length of lists equal to that of "connections_withoutErrors"
                for t in range(len(connections_withoutErrors)):
                    list_of_seg_sizes.append(0)
                    recv_list_total_size.append(0)
                    total_download_speed.append(0)

            else:  # ELSE BLOCK
                
                time.sleep(0.4)
        socket.close()              # Client closes the connection
        
        
        
        
        list_names.sort()           # List is sorted here

        # This block of code will executes when all the data has received aqnd the last thread is running
        if ((all_list_names==list_names) and int(current_thread().name) == (len(connections_withoutErrors) - 1) ):
            total_list_data.clear()             # List data is erased
            seg_lists_in_a_list.sort()          # List is sorted here
            seg_lists_in_a_list = list(itertools.chain(*seg_lists_in_a_list))       #Converts the 3D list to 2D list
            
            
            
            #Converts the 2D list to 1D list and storing the data in another list
            for j in range(len(seg_lists_in_a_list)):
                if (j % 2) == 0:
                    for i in range(len(seg_lists_in_a_list[j])):
                        #total_list_data.append(seg_lists_in_a_list[j][k])
                        print(seg_lists_in_a_list[j][i])
                else:
                    for k in range(len(seg_lists_in_a_list[j])):
                        total_list_data.append(seg_lists_in_a_list[j][k])           #Appending data from one list to another

            

            
            #Writing data to the file
            output_path = os.path.join(output_loc,og_file_name)
            with open (output_path,"wb") as file :
                for i in range(len(total_list_data)):
                    file.write(total_list_data[i])
            
           
            

        

    except Exception as e:      # EXCEPT BLOCK
        time.sleep(3)
        extra_list = []                     # local list to store ip and port
        extra_list.append(ip)               # Ip is added to the list
        extra_list.append(port)             # Port number is added to the list
        connections_withoutErrors.remove(extra_list)         #<If a particular server fails then its ip and port is removed from this list
                                                             #which contains the inforamtion of only active servers>
        print("Server Failed")
        print(e)
        print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))     # It prints the line number at which an error occurred

# Function creates threads
def create_workers():
    #These lists & variables are made global here
    global NUMBER_OF_THREADS, total_connections,threading_list
    
    #This loop creates new threads and each new socket is created by each thread based on the number of servers 
    for i in range(NUMBER_OF_THREADS):
        
        print("IP ",total_connections[i][0]," port ",total_connections[i][1])
        # Thread is created here
        t=threading.Thread(target=connects ,args=[total_connections[i][0],total_connections[i][1]])
        t.setName(i)                     # Thread is assigned a name here
        threading_list.append(t)         # Thread is added to threading list
        t.start()                        # Thread is started here
        
        
        

#Function to stop the threads
def finish_threads():
    try:
        global threading_list           # This list is made global
        for i in range(len(threading_list)):
            t=threading_list[i]         # Getting a particular thread
            t.join()                    # Thread terminates
        threading_list.clear()          # List data is erased
    except:
        pass
#Function to get the user input
def input_of_user():
    #These lists and variables are made global here
    global list_of_seg_sizes, st_interval, NUMBER_OF_THREADS,total_connections,resume,all_list_names,resume,output_loc
    no_of_servers=int(input("Enter the number of servers executing: "))         # Input is asked for the number of users
    NUMBER_OF_THREADS=no_of_servers                 # Number of threads are made equal to number of servers. One thread for one socket 
    
    list_of_seg_sizes.clear()                       # Lists data is erased
    recv_list_total_size.clear()
    total_download_speed.clear()
    
    file_path = os.path.join(lists_created_names_dir,"lists_names.txt")     # File path is set here
    file = open(file_path,"a")                      # File is opened here
    string="total_lists:"+str(no_of_servers)
    file.write(string+"\n")                         # Data is written to the file here
    file.close()                                    # File is opened here
    
    #Some inputs are taken here
    for i in range(no_of_servers):
        extra_list=[]
        ip=input("Enter IP address: ")              # User is asked for the sever ip address
        port=int(input("Enter Port number:"))       # User is asked for the sever PORT NUMBER
        extra_list.append(ip)
        extra_list.append(port)                     # IP and Port number are appended in the "extra_list"
        total_connections.append(extra_list)        # IP and Port are appended in the "total_connections" in 2D style
                                                    # [[ip,port],....]
        
        
        all_list_names.append("list"+str(i))        # list names are created based upon the number of servers in which the file will be divided
        
        

    
    st_interval=eval(input("Enter status interval time: "))     # User is asked for the metric reporting interval (output display on console) time
    
    
    resume_input=input("You want to resume downloading video then press Y/y otherwise N/n: ")       # User is asked whether to resume the download or not
    resume_input=resume_input.lower()
    if (resume_input and resume_input=="y"):
        resume="true"
    else:
        resume="false"
    
    output_loc = input("Enter location to store file: ")        # User is asked for the location to store the file
    
    
    #In this loop 0 is appended in these lists till the index (NUMBER_OF_THREADS-1)
    for t in range(NUMBER_OF_THREADS):
        list_of_seg_sizes.append(0)
        recv_list_total_size.append(0)
        total_download_speed.append(0)
    
    print("AFTER USER INPUT FUNCTION")
    

""" Resume working functions start from here"""


#Function to connect to a server in resume condition
def connects_in_resume(serverIP, serverPort):
    ip_adress = serverIP
    port_num = serverPort

    extra_list = []                             # local list to store ip and port
    extra_list.append(serverIP)                 # Ip is added to the list
    extra_list.append(serverPort)               # Port number is added to the list

    # These lists are made global here
    global total_connections, connections_withoutErrors
    

    connections_withoutErrors.append(extra_list)    # This list appends the ip and port of given server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:  # TRY BLOCK
        
        clientSocket.connect((serverIP, serverPort))    # Here client connects to a particular server

        # A function called which carries out the normal working of client in case of resume and none of the servers fails
        receive_data_from_server_in_resume(clientSocket, ip_adress, port_num)

    except:  # EXCEPT BLOCK
        print("Error Connection")
        extra_list = []                             # local list to store ip and port
        extra_list.append(serverIP)                 # Ip is added to the list
        extra_list.append(serverPort)               # Port number is added to the list
                                                        
        connections_withoutErrors.remove(extra_list)        # <If a particular server fails then its ip and port is removed from this list
                                                            # which contains the inforamtion of only active servers>


#Function which contains the working of normal working of client if not a single server fails in resume condition
def receive_data_from_server_in_resume(socket,ip,port):

    #These lists & variables are made global here
    global output_loc, total_download_speed, recv_list_total_size, list_of_seg_sizes, total_file_size, og_file_name, seg_lists_in_a_list, dict_for_lists_data, seg_list_sizes, connections_withoutErrors, list_names, total_list_data, all_list_names, extra_size_var, NUMBER_OF_THREADS

    
    try:  # TRY BLOCK
        

        file_path = os.path.join(lists_created_names_dir,"lists_names.txt")             # File path is set here
        file_name = open(file_path,'r')                         # File is opened here. <It opens the file which contains the info of
                                                                # how many servers were used or connected>

        string_of_original_list_names = file_name.readline()[12:]       # First line is read. Which tells the numbers of servers active in previous session
        file_name.close()                   # File is closed here
        
        
        socket.send(resume.encode('utf-8'))                     # Client sends the msg to servers whether to get data the previous file or download a new one
        time.sleep(0.1)
        
        # If number of currently active servers is equal to the number of active servers in previous session then this block executes
        if (int(string_of_original_list_names) == NUMBER_OF_THREADS):  # IF BLOCK
            

            for l in range(NUMBER_OF_THREADS):      # <This loop to create list items in dictionary depending upon the number of servers
                dict_for_lists_data["list{0}".format(l)] = []       # for storing lists data receiving from the server>
           

            for o in range(NUMBER_OF_THREADS):     # <This loop to create varibale items in dictionary depending upon the number of servers 
                seg_list_sizes["list{0}".format(o)] = 0             # to store each list size>

            
        
            all_list_names.sort()                   #The list is being sorted here
        
            string_to_send_to_divide="divide by "   #<Here client sends the server message to divide the file data in lists 
                                                    # chunks depending upon the number of servers active>
            socket.send(f"{string_to_send_to_divide}{separator}{str(NUMBER_OF_THREADS)}".encode('utf-8'))
            
            
            time.sleep(0.1)

            socket.send("Total File Size and File Name".encode('utf-8'))  # Client asks the server for file total size and its name
        
            data = socket.recv(204800).decode('utf-8')                  # Here client receives the file size and name from server 
            total_file_size, og_file_name = data.split(separator)       # Storing file size and name in variables

            
        

            
            # Loop which asks for a particular list size and receives it
            for j in range(NUMBER_OF_THREADS):
                if(int(current_thread().name) == (j)):
                         
               
                    string="Send size of "+all_list_names[j]          

                    socket.send(string.encode('utf-8'))                   #Client asks for that particular list size 
               
                    file_name = "list"+current_thread().getName()+".txt"    

                    file_path = os.path.join(files_folder, file_name)       # File path is set here

                    """ Here we are reading the file and getting the cursor/(row * column) position """
                    n = -1
                    string0 = ""
                    string0 = string0.encode('utf-8')
                    with open(file_path, 'rb') as file:     # File is opened here
                        for each_line in file:              # going through each line in file
                            n = n+1
                            string0 = string0+each_line     # storing each line in the string variablle
                    file.close()             # File is closed here           

                    cursor = len(string0)                   # Getting the cursor value by getting the length of "string0"

                    socket.send(str(cursor).encode('utf-8'))    # Client sends the cursor position to servers

                    
                    time.sleep(0.1)
                    data=socket.recv(204800).decode('utf-8')              #Client receives the size of particular list

                    del list_of_seg_sizes[int(current_thread().name)]             # <List was initialized with range based on number of servers with 0 at each index
                    list_of_seg_sizes.insert(int(current_thread().name), float(data))   # Here that value at index is removed and size of list is stored a that index>
                
                    seg_list_sizes[all_list_names[j]] = float(data)       # Size is also being stored in the dictionary
        
            # Loop which sends the server message to send the particular list 
            for j in range(len(all_list_names)):
                if(int(current_thread().name) == (j)):
                    string=all_list_names[int(current_thread().name)]+"_data"
                    time.sleep(0.1)
                    socket.send(string.encode('utf-8'))                    #Client sends the message to server
        

            

            # Local variables used in displaying the output in console
            server=""
            file_size=0
            r_file_size=0

            total_size=0
        

            data="sert"
            strings="done"
            stres=strings.encode('utf-8')

            

        
        

        
            file_name="list"+current_thread().getName()+".txt"              # A file name is set here based on the number of chunks/servers
        
            file_path= os.path.join(files_folder,file_name)                 # The path for that file is set here

            """ Here we are reading the file and getting the cursor/(row * column) position """
            n=-1
            string0=""
            string0 = string0.encode('utf-8')
            with open(file_path, 'rb') as file:             # File is opened here
                for each_line in file:                      # going through each line in file
                    n=n+1
                    string0=string0+each_line               # storing each line in the string variablle
            file.close()                                    # File is closed here

            cursor = len(string0)                           # Getting the cursor value by getting the length of "string0"

            socket.send(str(cursor).encode('utf-8'))        # Client sends the cursor position to servers



            ind_list_file = open(file_path,"ab")                # File is opened here
        
        
            #While loop in which server downloads the data from the server
            while data:
                
                t1 = time.time()                      # Measuring the current time
            
                data=socket.recv(204800)              # Clieent is receiving the data from server
                t2 = time.time()                      # Measuring the current time
                
            
                if data==stres:                       # Message "done" is sent by server to the client indicating the server has sent all the data
                    break                             # If this happens then we break out of loop
            
                else:  # ELSE BLOCK
                
                    # <A loop where received file data is stored in the dictonary particular list item
                    # based upon that which hread is being executed right now>
                    for k in range(len(all_list_names)):
                        if((current_thread().name) == str(k)):
                            in_loop_list=dict_for_lists_data.get('list'+str(k))             # Get the particular list item from dictionary
                            in_loop_list.append(data)                                       # Appending data in that particular list item
                        
                            ind_list_file.write(data)                                       # Data is written to the file here
                        
                            server = "Server"+str(k)

                            
                            r_file_size = os.stat(file_path).st_size                        # Reading the size of file which is being downloaded

                            
                            r_file_size=r_file_size / (1024 * 1024)                         # Convert Bytes to MegaBytes (MB)
                        
                            del recv_list_total_size[int(current_thread().name)]            # <Here that value at a particular index is removed depending upon the current thread executing
                            recv_list_total_size.insert(int(current_thread().name),r_file_size)     #  and size of list is stored at that index>
                            
                        
                            
                            file_size=list_of_seg_sizes[int(current_thread().name)]         # Getting the list size which is in download progress
                        
                

                    
                
                    t = t2-t1               # Subtracting the current times t1 & t2
                    if(t == 0):             # <If t becomes equal to zero we set it to 1
                        t = 1               # to avoid division by zero>
                    ssp = file_size / t     # Calculating list download speed from a particular server
                    del total_download_speed[int(current_thread().name)]                    # <Here that value at a particular index is removed 
                    total_download_speed.insert(int(current_thread().name),ssp)             # and speed of downloading list from a server is stored a that index>
                    sp = sum(total_download_speed)                                          # It sums all the entries in the list
                
                
                    

                    
                    print(server, ": {:.2f} MB / {:.2f} MB ,Download Speed: {:.2f} kB/s".format(r_file_size, file_size , ssp) )
                    
                    print("Total: {:.2f} MB / {:.2f} MB , Download Speed: {:.2f} kB/s".format((sum(recv_list_total_size)) ,float(total_file_size) ,sp) )
                    time.sleep(st_interval)             # Client sleeps for a particular time set by the user                                
            
        
            test_list = dict_for_lists_data.get('list'+current_thread().name)   #Get the list from dictionary in which data was stored
            ex_test_list=[]                                                     # Appending data with list name in "ex_test_list"
            ex_test_list.append('list'+current_thread().name)
            ex_test_list.append(test_list)
            seg_lists_in_a_list.append(ex_test_list)                            # Appending data with name in this list in 3D manner
                                                                            # [['list0',[data]],....]

            ind_list_file.close()                   # File is closed here
            #This loop adds the list name which is received from the server totally
            for m in range(NUMBER_OF_THREADS):                                  
                if((current_thread().name) == str(m)):
                    list_names.append(all_list_names[m])
        
            socket.close()                              #Client closes the connection
        
            all_list_names.sort()                       # Lists are sorted here
            list_names.sort()

        
            # If all the lists are received then if block executes where the data is written to the file
            if (all_list_names==list_names):
                total_list_data.clear()
                # Here received chunks from servers are written to the list "total_list_data" from the file
                for j in range(len(all_list_names)):
                    file_path = os.path.join(files_folder,all_list_names[j]+".txt")
                    file = open(file_path,'rb')
                    total_list_data.append(file.read())
                    file.close()


                #Writing data to the file
                output_path = os.path.join(output_loc, og_file_name)
                with open (output_path,"wb") as file :
                    for i in range(len(total_list_data)):
                        file.write(total_list_data[i])

        # If number of currently active servers is smaller than the number of active servers in previous session then this blocks executes
        elif (int(string_of_original_list_names) > NUMBER_OF_THREADS):  # ELIF BLOCK
            
            all_list_names.clear()                              # Lists data is erased
            for p in range(int(string_of_original_list_names)):
                all_list_names.append("list"+str(p))

            for l in range(NUMBER_OF_THREADS):      # <This loop to create list items in dictionary depending upon the number of servers
                dict_for_lists_data["list{0}".format(l)] = []       # for storing lists data receiving from the server>
           

            for o in range(NUMBER_OF_THREADS):     # <This loop to create varibale items in dictionary depending upon the number of servers 
                seg_list_sizes["list{0}".format(o)] = 0             # to store each list size>

        
        
            all_list_names.sort()                   #The list is being sorted here
        
            string_to_send_to_divide="divide by "   #<Here client sends the server message to divide the file data in lists 
                                                # chunks depending upon the number of original servers failed>
            socket.send(f"{string_to_send_to_divide}{separator}{string_of_original_list_names}".encode('utf-8'))

            time.sleep(0.1)

            socket.send("Total File Size and File Name".encode('utf-8')) # Client asks the server for file total size and its name
        
            data = socket.recv(204800).decode('utf-8')                  # Here client receives the file size and name from server 
            total_file_size, og_file_name = data.split(separator)       # Storing file size and name in variables

           
            # Loop which asks for a particular list size and receives it
            for j in range(NUMBER_OF_THREADS):
                if(int(current_thread().name) == (j)):
                
                    string="Send size of "+all_list_names[j]          

                    socket.send(string.encode('utf-8'))                   #Client asks for that particular list size 
               
                    file_name = "list"+current_thread().getName()+".txt"

                    file_path = os.path.join(files_folder, file_name)     # File path is set here

                    """ Here we are reading the file and getting the cursor/(row * column) position """
                    n = -1
                    string0 = ""
                    string0 = string0.encode('utf-8')
                    with open(file_path, 'rb') as file:             # File is opened here
                        for each_line in file:                      # going through each line in file
                            n = n+1
                            string0 = string0+each_line             # storing each line in the string variablle
                    file.close()                        # File is closed here

                    cursor = len(string0)                           # Getting the cursor value by getting the length of "string0"

                    socket.send(str(cursor).encode('utf-8'))        # Client sends the cursor position to servers

                    
                    time.sleep(0.1)
                    data=socket.recv(204800).decode('utf-8')              #Client receives the size of particular list

                    del list_of_seg_sizes[int(current_thread().name)]             # <List was initialized with range based on number of servers with 0 at each index
                    list_of_seg_sizes.insert(int(current_thread().name), float(data))   # Here that value at index is removed and size of list is stored a that index>
                
                    seg_list_sizes[all_list_names[j]] = float(data)       # Size is also being stored in the dictionary
        
            # Loop which sends the server message to send the particular list 
            for j in range(len(all_list_names)):
                if(int(current_thread().name) == (j)):
                    string=all_list_names[int(current_thread().name)]+"_data"
                    time.sleep(0.1)
                    socket.send(string.encode('utf-8'))                    #Client sends the message to server
        

            

            # Local variables used in displaying the output in console
            server=""
            file_size=0
            r_file_size=0

            total_size=0
        

            data="sert"
            strings="done"
            stres=strings.encode('utf-8')

            #extra file code

        
        

        
            file_name="list"+current_thread().getName()+".txt"          # A file name is set here based on the number of chunks/servers
        
            file_path= os.path.join(files_folder,file_name)             # The path for that file is set here

            """ Here we are reading the file and getting the cursor/(row * column) position """
            n=-1
            string0=""
            string0 = string0.encode('utf-8')
            with open(file_path, 'rb') as file:                 # File is opened here
                for each_line in file:                          # going through each line in file
                    n=n+1
                    string0=string0+each_line                   # storing each line in the string variablle
            file.close()                                        # File is closed here

            cursor = len(string0)                       # Getting the cursor value by getting the length of "string0"

            socket.send(str(cursor).encode('utf-8'))    # Client sends the cursor position to servers



            ind_list_file = open(file_path,"ab")        # File is opened here
        
        
            #While loop in which server downloads the data from the server
            while data:
                
                t1 = time.time()                      # Measuring the current time
            
                data=socket.recv(204800)              # Clieent is receiving the data from server
                t2 = time.time()                      # Measuring the current time
                
            
                if data==stres:                       # Message "done" is sent by server to the client indicating the server has sent all the data
                    break                             # If this happens then we break out of loop
            
                else:  # ELSE BLOCK
                
                    # <A loop where received file data is stored in the dictonary particular list item
                    # based upon that which hread is being executed right now>
                    for k in range(len(all_list_names)):
                        if((current_thread().name) == str(k)):
                            in_loop_list=dict_for_lists_data.get('list'+str(k))             # Get the particular list item from dictionary
                            in_loop_list.append(data)                                       # Appending data in that particular list item
                        
                            ind_list_file.write(data)                                       # Data is written to the file here
                        
                            server = "Server"+str(k)

                            
                            r_file_size = os.stat(file_path).st_size                         # Reading the size of file which is being downloaded

                            
                            r_file_size=r_file_size / (1024 * 1024)                          # Convert Bytes to MegaBytes (MB)
                        
                            del recv_list_total_size[int(current_thread().name)]            # <Here that value at a particular index is removed depending upon the current thread executing
                            recv_list_total_size.insert(int(current_thread().name),r_file_size)     #  and size of list is stored at that index>
                            
                            file_size=list_of_seg_sizes[int(current_thread().name)]         # Getting the list size which is in download progress
                        
                

                    
                
                    t = t2-t1               # Subtracting the current times t1 & t2
                    if(t == 0):             # <If t becomes equal to zero we set it to 1
                        t = 1               # to avoid division by zero>
                    ssp = file_size / t     # Calculating list download speed from a particular server
                    del total_download_speed[int(current_thread().name)]                    # <Here that value at a particular index is removed 
                    total_download_speed.insert(int(current_thread().name),ssp)             # and speed of downloading list from a server is stored a that index>
                    sp = sum(total_download_speed)                                          # It sums all the entries in the list
                
                
                    # Output is displayed in the console

                    
                    print(server, ": {:.2f} MB / {:.2f} MB ,Download Speed: {:.2f} kB/s".format(r_file_size, file_size , ssp) )
                    
                    print("Total: {:.2f} MB / {:.2f} MB , Download Speed: {:.2f} kB/s".format((sum(recv_list_total_size)) ,float(total_file_size) ,sp) )
                    time.sleep(st_interval)             # Client sleeps for a particular time set by the user                                
            
        
            test_list = dict_for_lists_data.get('list'+current_thread().name)   #Get the list from dictionary in which data was stored
            ex_test_list=[]                                                     # Appending data with list name in "ex_test_list"
            ex_test_list.append('list'+current_thread().name)
            ex_test_list.append(test_list)
            seg_lists_in_a_list.append(ex_test_list)                            # Appending data with name in this list in 3D manner
                                                                            # [['list0',[data]],....]

            ind_list_file.close()               # File is closed here
            #This loop adds the list name which is received from the server totally
            for m in range(NUMBER_OF_THREADS):                                  
                if((current_thread().name) == str(m)):
                    list_names.append(all_list_names[m])
        
            
        
            all_list_names.sort()                       # Lists are sorted here
            list_names.sort()

            # Calling another function to request to divide any remaining file data among live servers and getting it
            receive_data_from_server_in_resume_addon(socket,ip,port)

            # If all the lists are received then if block executes where the data is written to the file
            if (all_list_names==list_names):

                
                total_list_data.clear()
                # Here received chunks from servers are written to the list "total_list_data" from the file
                for j in range(len(all_list_names)):
                    file_path = os.path.join(files_folder,all_list_names[j]+".txt")
                    file = open(file_path,'rb')
                    total_list_data.append(file.read())
                    file.close()
                

                #Writing data to the file
                output_path = os.path.join(output_loc, og_file_name)
                with open (output_path,"wb") as file :
                    for i in range(len(total_list_data)):
                        file.write(total_list_data[i])
        
        # If number of currently active servers is greater than the number of active servers in previous session then this blocks executes
        else:
            
            all_list_names.clear()  # List data is erased

            for p in range(int(string_of_original_list_names)):
                all_list_names.append("list"+str(p))
            string_to_send_to_divide="divide by"
            
            # Client sends message to server to divide the data based upon the active servers in previous session
            socket.send(f"{string_to_send_to_divide}{separator}{str(string_of_original_list_names)}".encode('utf-8'))

            time.sleep(0.04)
            socket.send("Total File Size and File Name".encode('utf-8')) # Client asks the server for file total size and its name
        
            data = socket.recv(204800).decode('utf-8')                  # Here client receives the file size and name from server 
            total_file_size, og_file_name = data.split(separator)       # Storing file size and name in variables
            
            time.sleep(1)
            # Calling another function to request to divide any remaining file data among live servers and getting it
            receive_data_from_server_in_resume_addon(socket,ip,port)
            
            all_list_names.sort()               # Lists are sorted here
            list_names.sort()
            
            # If all the lists are received then if block executes where the data is written to the file
            if (all_list_names == list_names):
                total_list_data.clear()
                
                # Here received chunks from servers are written to the list "total_list_data" from the file
                for j in range(len(all_list_names)):
                    file_path = os.path.join(files_folder,all_list_names[j]+".txt")
                    file = open(file_path,'rb')
                    total_list_data.append(file.read())
                    file.close()


                #Writing data to the file
                output_path = os.path.join(output_loc, og_file_name)
                with open (output_path,"wb") as file :
                    for i in range(len(total_list_data)):
                        file.write(total_list_data[i])
        
    except:  # EXCEPT BLOCK
        time.sleep(1)
        extra_list = []                             # local list to store ip and port
        extra_list.append(ip)                       # Ip is added to the list
        extra_list.append(port)                     # Port number is added to the list
        connections_withoutErrors.remove(extra_list)  #<If a particular server fails then its ip and port is removed from this list
                                                      #which contains the inforamtion of only active servers>

#Function which works when number of current active servers is either greater or smaller than the number of active servers
#in previous session. This function is also used whenver a server fails in resume condition
def receive_data_from_server_in_resume_addon(socket,ip,port):

    #These lists & variables are made global here
    global total_download_speed, recv_list_total_size, list_of_seg_sizes,  connections_withoutErrors, remaining_list_names, total_connections, all_list_names, list_names, total_list_data, og_file_name, seg_lists_in_a_list,again_seg_lists,dict_for_lists_data,seg_list_sizes

    all_list_names.sort()           # Lists are sorted here
    list_names.sort()
    # Client checks for any remaining file
    remaining_list_names = list(set(all_list_names) - set(list_names))

    remaining_list_names.sort()     # List is sorted here

    

    
    
    files_to_get = len(remaining_list_names)  # Get the list length

    if (files_to_get == 0):  # IF BLOCK                  # If no further data is reamining then this if block executes
        print("The File has been Downloaded")   
        
        try:  # TRY BLOCK
            shutil.rmtree(files_folder)         # Removing the folder with data which contains segmented filess this folder is deleted only when the file is downloaded and written to the storage device
        except:  # EXCEPT BLOCK
            pass
    
    else:  # ELSE BLOCK
        try:  # TRY BLOCK

            
            extra_list=[]
            time.sleep(1)
            

            #<Here client sends the server message to divide the file data in lists 
            # chunks depending upon the number of servers active>
            string_to_send_to_divide="divide by"
            socket.send(f"{string_to_send_to_divide}{separator}{str(len(connections_withoutErrors))}".encode('utf-8'))
                

            time.sleep(0.009)
            
            socket.send(str(len(remaining_list_names)).encode('utf-8'))  # Client send the number of original list remaining to the servers


            
            time.sleep(0.1)
            string_to_send_to_list_names=separator.join(remaining_list_names)
            
            
            socket.send(string_to_send_to_list_names.encode('utf-8'))   # Client sends the remaining lists lists names to servers
            #start of main work
            for x in range(len(remaining_list_names)):

                
                
                file_name = remaining_list_names[x]+".txt"

                file_path = os.path.join(files_folder, file_name)       # File path is set here

                """ Here we are reading the file and getting the cursor/(row * column) position """
                n = -1
                string0 = ""
                string0 = string0.encode('utf-8')
                with open(file_path, 'rb') as file:                  # File is opened here
                    for each_line in file:                           # going through each line in file
                        n = n+1
                        string0 = string0+each_line                  # storing each line in the string variablle
                file.close()                                         # File is closed here

                cursor = len(string0)                                # Getting the cursor value by getting the length of "string0"

                socket.send(str(cursor).encode('utf-8'))             # Client sends the cursor position to servers




                extra_list=remaining_list_names[x]                  # Gets the list name
                
                seg_list_sizes.clear()                              # Lists data is erased
                dict_for_lists_data.clear()
                extra_size_var.clear()
                recv_list_total_size.clear()
                list_of_seg_sizes.clear()
                total_download_speed.clear()

                for z in range(len(connections_withoutErrors)):
                    list_of_seg_sizes.append(0)
                    recv_list_total_size.append(0)
                    total_download_speed.append(0)

                for l in range(len(connections_withoutErrors)):          # <This loop to create list items in dictionary depending upon the number of servers
                    dict_for_lists_data["list{0}".format(l)] = []               # for storing remaining lists data receiving from the server>

                for o in range(len(connections_withoutErrors)):         # <This loop to create varibale items in dictionary depending upon the number of servers 
                    seg_list_sizes["list{0}".format(o)] = 0             # to store each list size>
            
                time.sleep(0.1)
                
                socket.send(str(len(connections_withoutErrors)).encode('utf-8'))         #Here client sends the server message to divide the reamining file data in lists   


                
                time.sleep(0.009)
                


                print("sent list name", current_thread().getName(), remaining_list_names[x])
                time.sleep(0.09)

                
                string_recv_with_dvd_ln=socket.recv(204800).decode('utf-8')# 3 step        # <Client receives the original list(which was intended to be received from the server)
                                                                                       #  divided into further list with their names excluding data>

                list_temp_files=list(string_recv_with_dvd_ln.split(separator))             # Received list names in string are stored in a list
                

                time.sleep(0.03)
                # Loop which asks for a particular list size and receives it
                for j in range(len(connections_withoutErrors)):
                    if(int(current_thread().name) == (j)):
                    
                        string = "Send size of "+list_temp_files[j]

                        socket.send(string.encode('utf-8'))                        #Client asks for that particular list size
                        time.sleep(0.1)
                        
                        data = socket.recv(204800).decode('utf-8')               #Client receives the size of particular list
                        
                        del list_of_seg_sizes[int(current_thread().name)]                   # <List was initialized with range based on number of servers with 0 at each index
                        list_of_seg_sizes.insert(int(current_thread().name), float(data))   # Here that value at index is removed and size of list is stored a that index>
                        
                        seg_list_sizes[list_temp_files[j]] = float(data)                    # Size is also being stored in the dictionary
                
            
            # Loop which sends the server message to send the particular list
                for j in range(len(list_temp_files)):
                    if(int(current_thread().name) == (j)):
                        string = list_temp_files[j]+"_data"
                        time.sleep(0.1)
                        socket.send(string.encode('utf-8'))         #Client sends the message to server
                        print(string)
                
            
                # Local variables used in displaying the output in console
                server = ""
                file_size = 0
                r_file_size = 0

                

                file_name = remaining_list_names[x]+"_"+"list"+current_thread().getName()+".txt"
                file_path = os.path.join(file_dir_further_seg, file_name)
                ind_list_file = open(file_path, "ab")

                data = "sert"
                strings = "done"
                stres = strings.encode('utf-8')
                # Local variables used in displaying the output in console
                while data:
                    t1 = time.time()            # Measuring the current time

                    data = socket.recv(204800)  # Clieent is receiving the data from server
                    t2 = time.time()            # Measuring the current time

                    if data == stres:            # Message "done" is sent by server to the client indicating the server has sent all the data
                        print("ok in break")
                        break                    # If this happens then we break out of loop

                    else:  # ELSE BLOCK
                    
                        # <A loop where received file data is stored in the dictonary particular list item
                        # based upon that which hread is being executed right now>

                        for k in range(len(list_temp_files)):
                            if((current_thread().name) == str(k)):
                                in_loop_list = dict_for_lists_data.get('list'+str(k))           # Get the particular list item from dictionary
                                in_loop_list.append(data)                                       # Appending data in that particular list item
                            
                                ind_list_file.write(data)                                       # Data is written to the file                        

                                
                                r_file_size = os.stat(file_path).st_size                        # Reading the size of file in which data is being stored

                                server = "Server"+str(k)
                                
                                r_file_size = r_file_size/ (1024 * 1024)                        # Convert Bytes to MegaBytes (MB)

                                
                                del recv_list_total_size[int(current_thread().name)]            # <Here that value at a particular index is removed depending upon the current thread executing
                                recv_list_total_size.insert(int(current_thread().name),r_file_size)          #  and size of list is stored at that index>

                                file_size = list_of_seg_sizes[int(current_thread().name)]       # Getting the list size which is in download progress

                    
                        t = t2-t1                    # Subtracting the current times t1 & t2
                        if(t == 0):                  # <If t becomes equal to zero we set it to 1
                            t = 1                    # to avoid division by zero>
                        ssp = file_size / t          # Calculating list download speed from a particular server
                        del total_download_speed[int(current_thread().name)]                        # <Here that value at a particular index is removed 
                        total_download_speed.insert(int(current_thread().name), ssp)                # and speed of downloading list from a server is stored a that index>
                        sp = sum(total_download_speed)                                              # It sums all the entries in the list
                    
                    


                        # Output is displayed in the console
                        print(server, ": {:.2f} MB / {:.2f} MB ,Download Speed: {:.2f} kB/s".format(r_file_size, file_size, ssp) )

                        print("Total: {:.2f} MB / {:.2f} MB , Download Speed: {:.2f} kB/s".format(sum(recv_list_total_size) ,sum(list_of_seg_sizes) ,sp) )

                        time.sleep(st_interval)     # Client sleeps for a particular time set by the user
                
                           
                list_name=remaining_list_names[x]
                test_list = dict_for_lists_data.get('list'+current_thread().getName())     #Get the list from dictionary in which data was stored
                ex_test_list = []                                        # Appending data with list name in "ex_test_list"
                ex_test_list.append('list'+current_thread().getName())
                ex_test_list.append(test_list)
                again_seg_lists.append(ex_test_list)                    # Appending data with name in this list in 3D manner
                print(len(again_seg_lists))                             # [['list0',[data]],....]

                ind_list_file.close()
            
                # <If the last thread is being executed then this code executes which
                # will order the data for one reamining file from the servers and 
                # stores in the list "seg_lists_in_a_list">
                if ( int(current_thread().name) == (len(connections_withoutErrors) - 1)):
                    time.sleep(0.15)
                    again_seg_lists.sort()                  # List is sorted here
                    ex_test_list=[]
                    again_seg_lists = list(itertools.chain(*again_seg_lists))   #Converts the 2D list to 1D list
                    for i in range(len(again_seg_lists)):
                        if i % 2 == 0:
                            for k in range(len(again_seg_lists[i])):
                                print(again_seg_lists[i][k])
                        else:
                            for j in range(len(again_seg_lists[i])):
                                ex_test_list.append(again_seg_lists[i][j])      #Appending data from one list to another
                
                    
                    test=[]
                    test.append(remaining_list_names[x])
                    test.append(ex_test_list)               # Appending data with list original name in "test"
                    seg_lists_in_a_list.append(test)        # Appending data with name in this list in 3D manner

                
                    list_names.append(remaining_list_names[x])          # Adds the list name to "list_names" which is received from the server totally
                    print(remaining_list_names[x])

                    again_seg_lists.clear()                 # Lists data is erased

                    

                else:  # ELSE BLOCK
                    print("IN ELSE")
                    time.sleep(0.002)
            
            socket.close()              # Client closes the connection
        
        
            
            list_names.sort()           # List is sorted here

            # This block of code will executes when all the data has received aqnd the last thread is running
            if ((all_list_names == list_names) and int(current_thread().name) == (len(connections_withoutErrors) - 1)):
                total_list_data.clear()             # List data is erased
                list_temp_files.sort()
                ex_list=[]
                
                # In this loop the further segmented data is written together to the 
                # file which contains data from the previous session
                for k in range (len(remaining_list_names)):
                    for j in range(len(connections_withoutErrors)):
                        file_path = os.path.join(file_dir_further_seg,remaining_list_names[k]+"_"+list_temp_files[j]+".txt")
                        file = open(file_path,'rb')
                        ex_list.append(file.read())
                        file.close()
                    file_path = os.path.join(files_folder,remaining_list_names[k]+".txt")
                    file = open(file_path,'ab')
                    for z in range( len(ex_list)):
                        file.write(ex_list[z])
                    file.close()
                    ex_list.clear()
            
           
            

            

        except Exception as e:      # EXCEPT BLOCK
            time.sleep(3)
            extra_list = []                     # local list to store ip and port
            extra_list.append(ip)               # Ip is added to the list
            extra_list.append(port)             # Port number is added to the list
            connections_withoutErrors.remove(extra_list)         #<If a particular server fails then its ip and port is removed from this list
                                                             #which contains the inforamtion of only active servers>
            print("Server Failed")
            print(e)
            print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))     # It prints the line number at which an error occurred


# Function which executes when one of the servers fail in resume condition
def receive_the_remaining_data_in_resume():
    #These lists & variables are made global here
    global output_loc, total_download_speed, recv_list_total_size, list_of_seg_sizes, threading_list, connections_withoutErrors, remaining_list_names, total_connections, all_list_names, list_names, total_list_data, og_file_name

    all_list_names.sort()           # Lists are sorted here
    list_names.sort()
    remaining_list_names= list( set(all_list_names)- set(list_names))   # Client checks for any remaining file

    remaining_list_names.sort()     # List is sorted here

    

    total_download_speed.clear()    # Lists data is erased
    recv_list_total_size.clear()
    list_of_seg_sizes.clear()

    # Lists are appended 0 value
    for t in range(len(connections_withoutErrors)):
        list_of_seg_sizes.append(0)
        recv_list_total_size.append(0)
        total_download_speed.append(0)

    files_to_get = len(remaining_list_names)  # Get the list length

    if (files_to_get==0):   # IF BLOCK                    #If no further data is reamining then:
        print("The File has been Downloaded")   # this line will be executed
        
        try:        # TRY BLOCK
            # Removing the folder with data which contains segmented filess this folder is deleted only when the file is downloaded and written to the storage device
            shutil.rmtree(files_folder)         
        except:     # EXCEPT BLOCK
            pass
    
    else:       #ELSE BLOCK
        threading_list.clear()      # List data is erased
        time.sleep(1)

        try:        # TRY BLOCK
            # In this loop extra further segmented files are deleted which  are already written to the 
            # previous session decided segmented files
            for i in range(len(remaining_list_names)):
                for j in range(len(total_connections)):
                    file_name = remaining_list_names[i]+"_"+"list"+j+".txt"
                    file_path = os.path.join(file_dir_further_seg, file_name)
                    os.remove(file_path)
        except:     # EXCEPT BLOCK
            pass

        #This loop creates new threads and each new socket is created by each thread based on the number of servers active and running
        for i in range(len(connections_withoutErrors)):
            # Thread is created here
            t=threading.Thread(target=connect_again_and_receive_the_remaining_data_in_resume ,args=[connections_withoutErrors[i][0],connections_withoutErrors[i][1]])
            t.setName(i)                # Thread is assigned a name here
            threading_list.append(t)    # Thread is added to threading list
            t.start()                   # Thread is started here

        finish_threads()                # Threads are ended here by calling a function

        all_list_names.sort()           # Lists are sorted here
        list_names.sort()
        
        # If all the lists are received then if block executes where the data is written to the file
        if (all_list_names == list_names):
            total_list_data.clear()

            # Here received chunks from servers are written to the list "total_list_data" from the file
            for j in range(len(all_list_names)):
                file_path = os.path.join(files_folder, all_list_names[j]+".txt")
                file = open(file_path, 'rb')
                total_list_data.append(file.read())
                file.close()

            #Writing data to the file
            output_path = os.path.join(output_loc, og_file_name)
            with open (output_path, "wb") as file:
                for i in range(len(total_list_data)):
                    file.write(total_list_data[i])


#Function to connect to an active server the second time when one or more servers failed
def connect_again_and_receive_the_remaining_data_in_resume(ip, port):
    
    global total_connections,connections_withoutErrors  #These lists are made global here
    
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:  # TRY BLOCK
        clientSocket.connect((ip, port))         #Here client connects to a particular server
        print("Connected",ip,port)
        receive_data_from_server_in_resume_addon(clientSocket,ip,port)       # A function called which carries out the working of client if one or more servers stop working

    except:  # EXCEPT BLOCK
        print("Error Connection")
        extra_list = []                       # local list to store ip and port
        extra_list.append(ip)                 # Ip is added to the list
        extra_list.append(port)               # Port number is added to the list
        connections_withoutErrors.remove(extra_list)   #<If a particular server fails then its ip and port is removed from this list
                                                       #which contains the inforamtion of only active servers> 




# Function creates threads
def create_workers_in_resume():
    #These lists & variables are made global here
    global NUMBER_OF_THREADS, total_connections,threading_list
    
    #This loop creates new threads and each new socket is created by each thread based on the number of servers 
    for i in range(NUMBER_OF_THREADS):
        
        print("IP ",total_connections[i][0]," port ",total_connections[i][1])
        # Thread is created here
        t=threading.Thread(target=connects_in_resume ,args=[total_connections[i][0],total_connections[i][1]])
        t.setName(i)                     # Thread is assigned a name here
        threading_list.append(t)         # Thread is added to threading list
        t.start()                        # Thread is started here


#Functions are called here in a sequence
input_of_user()
if resume and resume=="false":
    create_workers()
    finish_threads()
    receive_the_remaining_data()
    finish_threads()
    receive_the_remaining_data()
    finish_threads()
else:
    create_workers_in_resume()
    finish_threads()
    receive_the_remaining_data_in_resume()
    receive_the_remaining_data_in_resume()
    


