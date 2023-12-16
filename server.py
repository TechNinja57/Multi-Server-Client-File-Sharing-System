
import socket
import threading
import time
import os
import sys
import shutil


#An append function which takes data from one list and append it to other list
def list_append(to_append,from_list):
    for i in range(len(from_list)):
        to_append.append(from_list[i])

#Function to append data from a list to a file
def list_to_file_append(path_of_file,str_num,diction):
    separator = "<SEPARATOR>"
    separator = separator.encode('utf-8')
    from_list = diction.get('list'+str_num)
    
    stre = separator.join(from_list)
    test=''
    test = test.encode('utf-8')
    stres = stre.replace(separator,test)

    ind_file = open(path_of_file,"wb")
    ind_file.write(stres)
    
    ind_file.close()




PORT = int(input("Enter Port Number: "))                    #Here user writes the port number of server

st_interval= eval(input("Enter status interval time: "))    #Here user writes the server status interval time

file = input("Enter File Location: ")          #Here user writes the file location

file_name_tosend = os.path.basename(file)             #It gets the filename with extension name


#Here server is being created
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', PORT))
server.setblocking(1)   #It prevents timeout





files_folder = os.path.abspath(os.getcwd())         # Gets the server file path

files_folder = os.path.join(files_folder, "files")

file_dir_further_seg = os.path.join(files_folder,"further_seg_files")

if not os.path.exists(files_folder):                # Making directory if it not exists already
    os.makedirs(files_folder)

if not os.path.exists(file_dir_further_seg):        # Making directory if it not exists already
    os.makedirs(file_dir_further_seg)




list_og = []                        #This list is created for writing all the file data to it
sent_list_name=[]                   #It sores the number of segmented files created depends on the number of servers

#It reads the file and append it the list
with open(file, "rb") as f:
    test = "dtr"
    while test:
        test = f.read(204800)       #It creates the limit to read file to only 204800 bytes per list item
        list_og.append(test)

f.close()   # File is closed here

length = len(list_og)               #Length of the list which contains the file data is measured here

separator = "<SEPARATOR>"           #A separater variable.IT will help us in sending and receiving multiple messages in one go

''' We created a dictionary which can store varibales with their values'''
dict={} 

list_to_send_data_again=[]          #This list is used when server fails and it divides the remaining file size depending upon the number of servers
remaining_lists=[]                  #It stores the remaining list names from servers which failed

print("File has been read")

k=0


server.listen(50)                   #It specifies the number of unaccepted connections that the system will allow before refusing new connections

print("Listened")                   
conn, addr = server.accept()        #Server accepts the for the incoming connections

resume=""
print("The Server is accepting")
data = conn.recv(204800).decode('utf-8')

resume = data
server.settimeout(60)  # Server timeout limit is set to 100 secs

#This function contains the main working of the server in which server will send file data its name and size 
def working_server(conn):
    try:    
        global dict ,dict_to_store_add_data,list_that_has_been_sent #These variables are made global because if not then function will use them as its own local variables
        data="string"
        while data:
            data=conn.recv(204800)                                  #Queries and messages are received from the client here
        

            if (data and data.decode('utf-8') == "Total File Size and File Name"):  #If client asks for file size and file name then this block will executes

                send_data=os.stat(file).st_size                             #It reads the size of file in bytes
                send_data= send_data / (1024 * 1024)                        #Bytes are converted to MegaBytes
                conn.send(f"{send_data}{separator}{file_name_tosend}".encode('utf-8'))   #Server sends the file name and file size to client using separater variable in between them
        

            elif(data and data.decode('utf-8').find('Send size of list') != -1):    #If client asks for particlar chunk/list size then this block will executes
                stri = data.decode('utf-8')[13:]         #It extracts the particular chunk/list name
            
                for list_name in dict:                      #This loop looks for that particular chunk/list in dictionary which client asked for
                    if(list_name == stri):                  #A condition if the client asked list name matches the list name in dictionary
                    
                        
                        file_name=os.path.join(files_folder,list_name+".txt")
                        send_data_ind = os.stat(file_name).st_size          #It reads the size of file in bytes
                        send_data_ind = send_data_ind / (1024 * 1024)       #Bytes convert to MegaBytes

                        list_send = dict[list_name]         #Get the particular list from the dictionary
                        length=len(list_send)               #Reads the length of list
                        length=length * 204800              #Multiplying the list length with 204800 bytes. Because each item in list contains 204800 Bytes.
                        length = length / (1024 * 1024)     #Bytes convert to MegaBytes
                        conn.send(str(send_data_ind).encode('utf-8'))  #Server send the particular list size to client
        

            elif(data and data.decode('utf-8').find('_data') != -1):         #If client asks for the particlar list data then this block executes 
                stri=data.decode('utf-8')[:-5]              #It extracts the particular chunk/list name
            
                for list_name in dict:                      #This loop looks for that particular chunk/list in dictionary which client asked for
                    if(list_name==stri):                    #A condition if the client asked list name matches the list name in dictionary
                        list_send=dict[list_name]           #Get the particular list from the dictionary
                        list_that_has_been_sent=list_name   #It stores the name of list that will be send to client
                    
                        for i in range( len(list_send) ):   #This loop helps in sending particular list\chunk data to client
                            conn.send(list_send[i])         #Each item data in list is sent to cleint
                            #print(i)
                            time.sleep(st_interval)         #Servers sleeps for a particular time set by the user

                        conn.send("done".encode('utf-8'))   #After sending list data server sends the message to client that all the list data is delivered 

            elif(data and data.decode('utf-8').find('divide by') != -1):    #If a partcular server fails this block will exectes only if
                                                                        # client sends the query to send the remaining data 
            
                dvd=data.decode('utf-8')#1 step                             #It decodes the message send by the client
            
                text , num=dvd.split(separator)                             # <It stores the message and gets the number in which to divide the remaining data
                #num=int(num)                                               # depending upon the number of servers >
            
                dict_to_store_add_data = {}                                 # A local dictionary is created to store the remaining divided data
                time.sleep(0.01)          # Here server sleeps for some time

                itrs = conn.recv(204800).decode('utf-8')  # add step        #Server receives the message of number of reamining lists which were intended to be send by the failed servers
                time.sleep(0.05)          # Here server sleeps for some time

                #recevining lits names
                rem_lists_names = conn.recv(204800).decode('utf-8') # 2 step #It receives the names of list which were intended to send by the failed servers
                remaining_lists = list(rem_lists_names.split(separator))     #It stores the received names in the form of string into a list
                remaining_lists.sort()                                       #It sorts the list
            
                




                
                #Start of main work
                for y in range(int(itrs)):                                    #In this loop remaining data is divided, its size and data is send to client
                    dict_to_store_add_data.clear()                            #The local dictionary is cleared here
                    list_send = []                                            #A local list is created here
                    

                    les = dict[remaining_lists[y]]
                    print(remaining_lists[y])
                    list_to_send_data_again.append(les)



                    
                
                    num= conn.recv(204800).decode('utf-8')          #Client tells the server the to in how many parts to divide the remaining data
                    time.sleep(0.0002)               # Here server sleeps for some time
                
                    for t in range(len(list_to_send_data_again)):             #In this loop the particular list data from failed server is stored in the local list
                        if y==t:
                            for u in range(len(list_to_send_data_again[t])):
                                list_send.append(list_to_send_data_again[t][u])
                
                    
                    

                    for j in range(int(num)):                                  #<In this loop the dictionary creates the number of lists and stores them
                        dict_to_store_add_data["list{0}".format(j)] = []       # the number of lists depends upon the number of servers active that number
                                                                               # is told by the client to servers to create that number of lists>

                    

                    length=len(list_send)                       #The length of remaining list which was intended to be send by the failed server is measured here
                    leng=length//int(num)                       #That length is divided by the an integer depending upon the number of active servers
                
                    for i in range(int(num)):                   #This loop helps in dividing the data depending upon the number of active servers
                    
                        lis = []
                        list_infnc = dict_to_store_add_data.get('list'+str(i))  #Get the list item from the loacal dictionary
                        

                        '''If the num=3, range is from 0 to 3 (i=0,1,2) at i=2 if will be 
                            exectuted otherwise else segment will be executed  '''

                        if (i == (int(num)-1)):                                 
                            lis = list_send[(i*leng):length]                    #The list_og containing file data is being divided into chunks (It will only happen in the last at i=num-1)
                            
                            list_append(list_infnc, lis)                        #That data is then being stored in the list item of local dictionary using append function
                                    
                        else:
                            lis = list_send[(i*leng):((i+1)*leng)]              #The list_og containing file data is being divided into chunks
                            
                            list_append(list_infnc, lis)                        #That data is then being stored in the list item of dictionary using append function
                            

                    ex_list=[]                                  #This list will be used in sending new created list names to client

                    
                    for k in dict_to_store_add_data:            #This loop will store all the names of new created lists in local dictionary in "ex_list"
                        ex_list.append(k)
        
                    

                

                    string= separator.join(ex_list)             #"ex_list" content is stored in a string
                    
                    conn.send(string.encode('utf-8'))           #"ex_list" data is send to client which contains new creted list names in "dict_to_store_add_data"

                    time.sleep(0.05)  # Here server sleeps for some time

                    string1 = conn.recv(204800).decode('utf-8') #recv size query #Client asks the server for the newly created list size
                    
                    string2=string1[13:]                        # It extracts the list name
                    
                    seg_list=dict_to_store_add_data[string2]    # It gets the list from local dictionary 

                    file_name_seg_fur = remaining_lists[y]+"_"+string2+".txt"
                    file_path_seg_fur = os.path.join(file_dir_further_seg, file_name_seg_fur)
                    list_to_file_append(file_path_seg_fur, string2[4:], dict_to_store_add_data)     # Store List data to file function is called here

        
                    send_data_seg = os.stat(file_path_seg_fur).st_size
                    send_data_seg = send_data_seg / (1024 * 1024)   # Bytes convert to MegaBytes
                    conn.send(str(send_data_seg).encode('utf-8'))   # Server sends the size of asked list to the client
                
                    
                    string=conn.recv(204800).decode('utf-8')[:-5]   #recv order to send data #Client tells the server to sends the data of a particular list

                    seg_list_to_send=dict_to_store_add_data[string]   #It gets the particular list from the dictionary with its data
        
                    for i in range(len(seg_list_to_send)):      #This loop helps in sending particular list\chunk data to client
                        conn.send(seg_list_to_send[i])          #Each item data in list is sent to cleint
                        #print(i)
                        time.sleep(st_interval)                 #Servers sleeps for a particular time set by the user
                    
                    conn.send("done".encode('utf-8'))           #After sending list data server sends the message to client that all the list data is delivered 
                    time.sleep(0.5)                     #Here server sleeps for some time
        conn.close()        #Here the server closes the connection
    except:
        try:
            # Removing the folder with data which contains segmented filess this folder is deleted only when the file is sent and written to the storage device
            shutil.rmtree(files_folder)
        except:
            pass

#In Resume condition
#This function contains the main working of the server in which server will send file data its name and size
def resume_working_server(conn):
    try:
        # These variables are made global because if not then function will use them as its own local variables
        global dict, dict_to_store_add_data, list_that_has_been_sent
        data = "string"
        while data:
            
            
            data = conn.recv(204800)        # Queries and messages are received from the client here
            
            # If client asks for file size and file name then this block will executes
            if (data and data.decode('utf-8') == "Total File Size and File Name"):

                
                send_data = os.stat(file).st_size                   # It reads the size of file in bytes
                
                send_data = send_data / (1024 * 1024)               # Bytes are converted to MegaBytes
                
                conn.send(f"{send_data}{separator}{file_name_tosend}".encode('utf-8'))      # Server sends the file name and file size to client using separater variable in between them

            # If client asks for particlar chunk/list size then this block will executes
            elif(data and data.decode('utf-8').find('Send size of list') != -1):
                
                stri = data.decode('utf-8')[13:]        # It extracts the particular chunk/list name

                for list_name in dict:  # This loop looks for that particular chunk/list in dictionary which client asked for
                    # A condition if the client asked list name matches the list name in dictionary
                    if(list_name == stri):

                        
                        file_name = os.path.join(files_folder, list_name+".txt")

                        cursor = conn.recv(204800).decode('utf-8')      # Server receives the cursor number at which to read the file further

                        f = open(file_name, "rb")      # File is opened here         
                        f.seek(int(cursor))            # Cursor is set where to start reading the file
                        string0 = f.read()             # File is read here
                        f.close()       # File is closed here

                        send_data_ind = os.stat(file_name).st_size      # Reading the file size
                        send_data_ind = send_data_ind / (1024 * 1024)   # Bytes convert to MegaBytes

                        
                        # Server send the remaining data size to client
                        conn.send(str(send_data_ind).encode('utf-8'))

            # If client asks for the particlar list data then this block executes
            elif(data and data.decode('utf-8').find('_data') != -1):
                
                stri = data.decode('utf-8')[:-5]        # It extracts the particular chunk/list name

                cursor = conn.recv(204800).decode('utf-8')      # Server receives the cursor number at which to read the file further

                file_path = os.path.join(files_folder, stri+".txt")

                list_send = []

                """Here server starts reading the file at the specific cursor point and then append that 
                                                    data into a list"""
                string = ""
                string = string.encode('utf-8')
                with open(file_path, 'rb') as f:
                    f.seek(int(cursor))
                    test = "dd"
                    while test:
                        test = f.read(204800)
                        list_send.append(test)

                # This loop looks for that particular chunk/list in dictionary which client asked for
                for list_name in dict:  
                    
                    if(list_name == stri):      # A condition if the client asked list name matches the list name in dictionar
                        
                        # It stores the name of list that will be send to client
                        list_that_has_been_sent = list_name

                        # This loop helps in sending particular list\chunk data to client
                        for i in range(len(list_send)):
                           
                            conn.send(list_send[i])          # Each item data in list is sent to client
                            print(i)
                            
                            time.sleep(st_interval)         # Servers sleeps for a particular time set by the user

                        # After sending list data server sends the message to client that all the list data is delivered
                        conn.send("done".encode('utf-8'))
                        time.sleep(1)

            # If a partcular server fails this block will exectes only if
            elif(data and data.decode('utf-8').find('divide by') != -1):
                
                # client sends the query to send the remaining data
                # #It decodes the message send by the client
                dvd = data.decode('utf-8')
                
                                                                            # <It stores the message and gets the number in which to divide the remaining data
                text, num = dvd.split(separator)                            # depending upon the number of servers >
                #num=int(num)                                               

                
                dict_to_store_add_data = {}         # A local dictionary is created to store the remaining divided data
                time.sleep(0.01)                    # Here server sleeps for some time

                        
                itrs = conn.recv(204800).decode('utf-8')                    #Server receives the message of number of reamining lists which were intended to be send by the failed servers
                time.sleep(0.05)                                            # Here server sleeps for some time
                
                #recvining lits names
                
                rem_lists_names = conn.recv(204800).decode('utf-8')         #It receives the names of lists which were intended to send by the failed servers
                
                remaining_lists = list(rem_lists_names.split(separator))    # It converts the received names in the form of string into a list
                remaining_lists.sort()      # It sorts the list
                
                
                #Start of main work
                # In this loop remaining data is divided, its size and data is send to client
                for y in range(int(itrs)):

                    

                    cursor = conn.recv(204800).decode('utf-8')  # Receving the cursor from the client at which to start reading and sending the file 
                    

                    dict_to_store_add_data.clear()              # The local dictionary is cleared here
                    list_send = []                              # A local list is created here
                    

                    les = dict[remaining_lists[y]]              # Getting particular list item from the dictionary

                    
                    
                    list_to_send_data_again.append(les)

                    """Here server starts reading the file at the specific cursor point and then append that 
                                                    data into a list"""
                    file_path = os.path.join(files_folder, remaining_lists[y]+".txt")

                    string_size = ""
                    string_size = string_size.encode('utf-8')
                    with open(file_path, 'rb') as f:
                        f.seek(int(cursor))
                        test = "dd"
                        while test:
                            test = f.read(204800)
                            list_send.append(test)
                            string_size = string_size + test

                    

                         
                    num = conn.recv(204800).decode('utf-8')        #Client tells the server the to in how many parts to divide the remaining data
                    
                    
                    time.sleep(0.0002)                             # Here server sleeps for some time

                    
                    

                    # <In this loop the dictionary creates the number of lists and stores them
                    for j in range(int(num)):
                        
                        dict_to_store_add_data["list{0}".format(j)] = []        # the number of lists depends upon the number of servers active that number
                                                                                # is told by the client to servers to create that number of lists>

                    

                    # The length of remaining list which was intended to be send by the failed server is measured here
                    length = len(list_send)
                    # That length is divided by the an integer depending upon the number of active servers
                    leng = length//int(num)

                    # This loop helps in dividing the data depending upon the number of active servers
                    for i in range(int(num)):

                        lis = []
                        
                        list_infnc = dict_to_store_add_data.get('list'+str(i))          # Get the list item from the loacal dictionary
                        

                        '''If the num=3, range is from 0 to 3 (i=0,1,2) at i=2 if will be 
                            exectuted otherwise else segment will be executed  '''

                        if (i == (int(num)-1)):
                            
                            lis = list_send[(i*leng):length]            # The list_og containing file data is being divided into chunks (It will only happen in the last at i=num-1)
                            
                            
                            list_append(list_infnc, lis)                # That data is then being stored in the list item of local dictionary using append function
                            
                        else:
                            
                            lis = list_send[(i*leng):((i+1)*leng)]      # The list_og containing file data is being divided into chunks
                            
                            
                            list_append(list_infnc, lis)                # That data is then being stored in the list item of dictionary using append function
                            

                    ex_list = []  # This list will be used in sending new created list names to client

                    
                    for k in dict_to_store_add_data:  # This loop will store all the names of new created lists in local dictionary in "ex_list"
                        ex_list.append(k)

                    

                    
                    string = separator.join(ex_list)                # "ex_list" content is stored in a string
                    
                   
                    conn.send(string.encode('utf-8'))               #"ex_list" data is send to client which contains new creted list names in "dict_to_store_add_data"

                    time.sleep(0.05)  # Here server sleeps for some time

                    
                    string1 = conn.recv(204800).decode('utf-8')     #recv size query #Client asks the server for the newly created list size
                    
                    
                    string2 = string1[13:]                      # It extracts the list name
                    
                    
                    seg_list = dict_to_store_add_data[string2]  # It gets the list from local dictionary

                    file_name_seg_fur = remaining_lists[y]+"_"+string2+".txt"
                    file_path_seg_fur = os.path.join(file_dir_further_seg, file_name_seg_fur)
                    list_to_file_append(file_path_seg_fur,string2[4:], dict_to_store_add_data)          # Store List data to file function is called here

                    
                    send_data_seg = os.stat(file_path_seg_fur).st_size          # Reading the file size
                    send_data_seg = send_data_seg / (1024 * 1024)               # Bytes convert to MegaBytes
                    
                    conn.send(str(send_data_seg).encode('utf-8'))               #Server sends the size of asked list to the client

                   
                    
                    string = conn.recv(204800).decode('utf-8')[:-5]             #Client tells the server to sends the data of a particular list

                    
                    seg_list_to_send = dict_to_store_add_data[string]           # It gets the particular list from the dictionary with its data

                    # This loop helps in sending particular list\chunk data to client
                    for i in range(len(seg_list_to_send)):
                        
                        conn.send(seg_list_to_send[i])              # Each item data in list is sent to client
                        #print(i)
                        
                        time.sleep(st_interval)                     # Servers sleeps for a particular time set by the user

                    
                    conn.send("done".encode('utf-8'))               # After sending list data server sends the message to client that all the list data is delivered
                    time.sleep(0.05)            # Here server sleeps for some time
        
        conn.close()  # Here the server closes the connection
    except:  # EXCEPT BLOCK
        pass



# If user wants to resume the previous session then else block executes otherwise if block
if (data and data=="false"):

    stres="done"
    streee=stres.encode('utf-8')


    data=conn.recv(204800).decode('utf-8')          #Client will send message to server and server will receive it to in how many parts to divide the list_og
    
    divideby, num=data.split(separator)             # Rececived message style:"divide by <Separater>(any integer)
                                                # <The separater variable helps in sending and receving messages like this 
                                                # without needing for send/receive the message in  multiple parts>.
                                         

    for i in range(int(num)):                       # This loop to create list items in dictionary depending upon the number of servers
        dict["list{0}".format(i)]=[]


    list_infnc=[]                                   #It is an extra list used in divison of data and storing it dictionary

    leng=length//int(num)                           #It divides the list length by the num(This number is received from the client based on the number of servers)


    for i in range(int(num)):                       #A loop to divide the file in chunks and to store them in diictionary variables list
        lis=[]
        list_infnc=dict.get('list'+str(i))          #Get the list item from the dictionary

        '''If the num=3, range is from 0 to 3 (i=0,1,2) at i=2 if will be 
            exectuted otherwise else segment will be executed  '''
    
        if (i==(int(num)-1)):                   
            lis=list_og[(i*leng):length]           #The list_og containing file data is being divided into chunks (It will only happen in the last at i=num-1)
            list_append(list_infnc,lis)            #That data is then being stored in the list item of dictionary using append function
        
        else:

            lis = list_og[(i*leng):((i+1)*leng)]    #The list_og containing file data is being divided into chunks
            list_append(list_infnc,lis)             #That data is then being stored in the list item of dictionary using append function
        
    list_that_has_been_sent=""                      #It stores the name of list sent to client if server does not fail

    
    # This loop creates temporary files based upon the number of servers active by the request of client 
    # Store main file data into these temp files in divided chunks
    for i in range(int(num)):
        file_name="list"+str(i)+".txt"
        file_path=os.path.join(files_folder,file_name)
        list_to_file_append(file_path,str(i),dict)

    working_server(conn)  # Working function is called here
else:
    stres = "done"
    streee = stres.encode('utf-8')

    
    data = conn.recv(204800).decode('utf-8')            # Client will send message to server and server will receive it to in how many parts to divide the list_og
    
    
    divideby, num = data.split(separator)               # Rececived message style:"divide by <Separater>(any integer)
                                                        # <The separater variable helps in sending and receving messages like this
                                                        # without needing for send/receive the message in  multiple parts>.
    

    # This loop to create list items in dictionary depending upon the number of servers
    for i in range(int(num)):
        dict["list{0}".format(i)] = []

    list_infnc = []                         # It is an extra list used in divison of data and storing it dictionary

    
    leng = length//int(num)                 # It divides the list length by the num(This number is received from the client based on the number of servers)

    # A loop to divide the file in chunks and to store them in diictionary variables list
    for i in range(int(num)):
        lis = []
        
        list_infnc = dict.get('list'+str(i))        # Get the list item from the dictionary

        '''If the num=3, range is from 0 to 3 (i=0,1,2) at i=2 if will be 
            exectuted otherwise else segment will be executed  '''

        if (i == (int(num)-1)):
            
            lis = list_og[(i*leng):length]          # The list_og containing file data is being divided into chunks (It will only happen in the last at i=num-1)

            list_append(list_infnc, lis)            # That data is then being stored in the list item of dictionary using append function

        else:

            
            lis = list_og[(i*leng):((i+1)*leng)]         # The list_og containing file data is being divided into chunks
            
            list_append(list_infnc, lis)                 # That data is then being stored in the list item of dictionary using append function

    
    list_that_has_been_sent = ""                    # It stores the name of list sent to client if server does not fail

    

    # This loop creates temporary files based upon the number of servers active by the request of client
    # Store main file data into these temp files in divided chunks
    for i in range(int(num)):
        file_name = "list"+str(i)+".txt"
        file_path = os.path.join(files_folder, file_name)
        list_to_file_append(file_path, str(i), dict)
    
    resume_working_server(conn)             # Function called which caters about the resume thing


# If user wants to resume the previous session then else block executes otherwise if block
# Here server waits for another incoming connections
server.settimeout(100)  # Server timeout limit is set to 100 secs
if (resume and resume == "false"):  
    try:
        conn1 , addr1 = server.accept() #Here server waits for any incoming connection
        if (conn1):
            print("Connected",addr1)
            working_server(conn1)       #Here the function is called
    except:
        print("No connection was made") #If no connecction is made then this line gets printed

    server.settimeout(30)   #Server timeout limit is set to 30 secs
    try:
        conn1, addr1 = server.accept()  # Here server waits for any incoming connectiona
        if (conn1):
            print("Connected", addr1)
            working_server(conn1)       # Here the function is called
    except:
        print("No connection was made") #If no connecction is made then this line gets printed

    try:
        shutil.rmtree(files_folder)
    except:
        pass
else:
    try:
        conn1, addr1 = server.accept()  # Here server waits for any incoming connection
        if (conn1):
            print("Connected", addr1)
            resume_working_server(conn1)  # Here the function is called
    except:
        # If no connecction is made then this line gets printed
        print("No connection was made")

    server.settimeout(30)  # Server timeout limit is set to 30 secs
    try:
        conn1, addr1 = server.accept()  # Here server waits for any incoming connectiona
        if (conn1):
            print("Connected", addr1)
            resume_working_server(conn1)       # Here the function is called
    except:
        # If no connecction is made then this line gets printed
        print("No connection was made")

    try:
        shutil.rmtree(files_folder)
    except:
        pass

server.close()  #Here server is closed
