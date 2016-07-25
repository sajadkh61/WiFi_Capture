#Merge the final code with Gabe's code --  The same as WiFi_ Manual_final_2 -- tag position to the captured traffic and save it to csv and data base files

from kismetclient import Client as KismetClient
from socket import error as socket_error
from sys import platform as _platform
from paramiko import SSHClient
from pprint import pprint
from threading import Thread
import ConfigParser
import threading
import optparse
import paramiko
import datetime
import psycopg2
import thread
import time
import sys
import csv
import os



class HMB:
    
    def __init__(self,channel,ip,username,password):
        self.channel=channel
        self.ip=ip
        self.username=username
        self.password=password
        
        time_format= "%b-%d-%Y-at-%H-%M-%S"
        today = datetime.datetime.today()
        formated_today = today.strftime(time_format)
        path = os.path.dirname(__file__)
        self.fname =path+'/home/near/Documents/wifi capture code/kismetclient-master/startup logs/start-up_log_on_HMB_'+str(self.channel)+" - "+str(formated_today)+'.log'
        
    #ping a HMB and write the results into a log file
    def Check(self):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.ip,22,self.username,self.password)
        ping_command = 'ping -n -c 5 '+str(self.ip)
        stdin, stdout, stderr = client.exec_command(ping_command)
        try : 
            with open(self.fname,'ab') as text_file:
                #text_file.write("##################################### ping Logs #####################################\n")
                for line in stdout.read().splitlines():
                    print line
                    text_file.write(line+"\n")
            text_file.write("\n") 
            if text_file.open():
                text_file.close()
        except IOError:
            pass
        except ValueError:
            pass
        except:
            pass
                  
        client.close()
        
    #Run Kismet server on a HMB and the results back into a log file
    def KismetCheck(self,port=22):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.ip,port,self.username,self.password)
        stdin, stdout, stderr = client.exec_command('kismet_server -n')
        print "\nKismer server is running on HMB " + str(self.channel)+" "+"("+ self.ip +")!!!"
        try : 
            with open(self.fname,'ab') as text_file:
                #text_file.write("##################################### Kismet Server Running Logs #####################################\n")
                text_file.write("\n") 
                text_file.write("Kismer server is up on HMB " + str(self.channel)+" "+"("+ self.ip +")!!!"+"\n")
                text_file.write("\n") 
            if text_file.open():
                text_file.close()
        except IOError:
            pass
        except ValueError:
            pass
        except:
            pass
        
        client.close()
    
    #Send Sync Query to NTP server and write the results into a log file    
    def NTPCheck(self,port=22):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.ip,port, self.username,self.password)
        stdin1, stdout1, stderr1 = client.exec_command('date ' + '-R')
        print "current date and time on HMB " + self.channel+ " is: " + stdout1.readline()
        stdin2, stdout2, stderr2 = client.exec_command('dpkg-reconfigure ' + 'ntp')
        time.sleep(3)
        stdin3, stdout3, stderr3 = client.exec_command('ntpq ' + '-p')            
        print "HMB " + self.channel+ " is syncing with the folowing servers:\n"
        try : 
            with open(self.fname,'ab') as text_file:
                #text_file.write("##################################### NTP Logs #####################################\n")
                text_file.write(stdout1.readline())
                text_file.write("\n") 
                for line in stdout3.read().splitlines():
                    print line
                    text_file.write(line+"\n")
                text_file.write("\n")
            if text_file.open():
                text_file.close()
        except IOError:
            pass
        except ValueError:
            pass
        except:
            pass
        
        client.close()
        
        
    #Reset HMB    
    def Reset(self,port=22):
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.ip,port,self.username,self.password)
        print "HMB " + self.channel+ 'starts rebooting ...\n'
        stdin, stdout, stderr = client.exec_command('reboot')
        client.close()
        
        
    #Create Kismet client on HMB
    def KismetClient_start(self,port=2502):
        
        try:
            address = (self.ip, port)
            k = KismetClient(address)
            print "\nKismet client is running on HMB "+self.channel +" "+"("+ self.ip +")"+ "!!!"
            with open(self.fname,'ab') as text_file:
            #text_file.write("##################################### Kismet Client Running Logs #####################################\n")
                text_file.write("\n") 
                text_file.write("\n Kismet client is up on HMB " + self.channel +" "+"("+ self.ip +")"+ "!!!" + "\n")
            if text_file.open():
                text_file.close()
#            return k
        except socket_error :
#            self.KismetCheck()
            print 'sockrt_error'            
            sys.exit()
        except IOError:
            pass
        except ValueError:
            pass
        except:
            pass    
        return k
       
class WiFi_capture(threading.Thread):
     
    def __init__(self,*hmbs):
        
        threading.Thread.__init__(self)
        
        self.merge=[ ]
        self.ssids=[ ]
        self.bssids=[ ]
        self.hmbs_list=[ ]
        for hmb in hmbs:
            self.hmbs_list.append(hmb)
            
        #csv file name    
        self.fname=''
        #new config file name(different from kismet config file)
        self.Config_FileName=''
        
        #By default, all results will be sent to a CSV log file
        self.CSV_log_status=True
        #for csv file creation        
        self.csvfile=None
        
        #for SQL connection
        self.conn=None
        #By default, all results will be sent to a SQL database
        self.SQL_log_status=True
        #stop or start writing results on the screen - used for clearing the screen when user needs to enter input
        self.print_results_on_screen=True
        # list of x and y coordinations for three antenas as [x1,y1,x2,y2,x3,y3]
        self.positions= [0,0,0,0,0,0]    
        
        
    def run(self):
            
        #create thread based on length of hmb list
        
        k1.register_handler('BSSID', lambda  *args, **kwargs: self.handle_bssid(self.hmbs_list[0].channel,self.positions,**kwargs))
        k1.register_handler('SSID', lambda  *args,**kwargs: self.handle_ssid(**kwargs))
    
        k2.register_handler('BSSID', lambda  *args, **kwargs: self.handle_bssid(self.hmbs_list[1].channel,self.positions,**kwargs))
        k2.register_handler('SSID', lambda  *args,**kwargs: self.handle_ssid(**kwargs))
    
        k3.register_handler('BSSID', lambda  *args, **kwargs: self.handle_bssid(self.hmbs_list[2].channel,self.positions,**kwargs))
        k3.register_handler('SSID', lambda  *args,**kwargs: self.handle_ssid(**kwargs))
        
        #if there is no result on the screen, start showing them
        if self.print_results_on_screen==False:
            self.print_results_on_screen = True
            
        try:
            while True:
                
                k1.listen()
                thread.start_new_thread(self.handle_merge,())
                k2.listen()
                thread.start_new_thread(self.handle_merge,())
                k3.listen()
                thread.start_new_thread(self.handle_merge,())      
        
        except KeyboardInterrupt:
            pprint(k1.protocols)  
            pprint(k2.protocols) 
            pprint(k3.protocols)   
       
        
    #Take bssid data
    def handle_bssid(self,hmb_channel,position,**fields): 
        fields.update({'hmb_channel': hmb_channel})
        if hmb_channel=='A':
            fields.update({'position': str(position[0])+','+str(position[1])})
        elif  hmb_channel=='B':
            fields.update({'position': str(position[2])+','+str(position[3])})
        elif hmb_channel=='C':
            fields.update({'position': str(position[4])+','+str(position[5])})
        self.bssids=[ ]
        if not self.bssids:
            self.bssids.append(fields)
        elif fields not in self.bssids:  
            self.bssids.append(fields)
            self.bssids =[dict(t) for t in set([tuple(d.items()) for d in self.bssids])]    


    #Take ssid data 
    def handle_ssid(self,**fields):
#        self.ssids[:]=[]
        self.ssids=[ ]
        if not self.ssids:
            self.ssids.append(fields)
        elif fields not in self.ssids:  
            self.ssids.append(fields)
            self.ssids =[dict(t) for t in set([tuple(d.items()) for d in self.ssids])] 
    
    
    #get antena positin and update instance variable 'position'
    def handle_position(self,*positions):        
        for i in range(0,6):
            self.positions[i]=positions[i]
        print '\nCalculated positins are:'    
        print self.positions
       
        
        
        
    #Sniffed data will be merged here
    def handle_merge(self):
        
        if bool(self.ssids) and bool(self.bssids) :
            for ssid,bssid in zip(self.ssids,self.bssids):
            
                if ssid['mac'] == bssid['bssid'] : 
                    record = { 'firsttime':bssid['firsttime'],'lasttime':bssid['lasttime'],'hmb_channel': bssid['hmb_channel'],'bssid': bssid['bssid'], 'ssid': ssid['ssid'], 'Mac_Add': ssid['mac'],'type': ssid['type'],
                              'channel': bssid['channel'], 'signal': bssid['signal_dbm'], 'rssi': bssid['signal_rssi'], 'position':bssid['position']
                              }
                    
                    if record not in self.merge: 
                        if not any(( dup['hmb_channel'] == record['hmb_channel'] and dup['ssid'] == record['ssid'] and dup['bssid'] == record['bssid'] and dup['lasttime'] == record['lasttime'] and dup['channel'] == record['channel'] and dup['signal'] == record['signal'] and dup['rssi'] == record['rssi'] and dup['position']==record['position'] ) for dup in self.merge):
                            self.merge.append(record)
                            self.merge =[dict(t) for t in set([tuple(d.items()) for d in self.merge])]
                            if self.print_results_on_screen == True:
                                print 'Detected HMB_CHANNEL: %(hmb_channel)s  POSITION: %(position)s FISRTTIME: %(firsttime)s  LASTTIME: %(lasttime)s SSID: %(ssid)s  MODE:%(type)s  BSSID:%(bssid)s  MAC:%(Mac_Add)s  Channel : %(channel)s  SIGNAL : %(signal)s  RSSI %(rssi)s ' % record
                                print
                            
                            
                            #Start writing results to a csv file
                            if self.CSV_log_status==True:
                                try:                        
                                    with open(self.fname,'ab') as self.csvfile:
                                        spamwriter = csv.writer(self.csvfile, delimiter=' ')
                                        spamwriter.writerow(record.items()) 
                                        self.csvfile.close()  
                                except IOError:#, (errno, strerror):
                                        pass
                                except ValueError:
                                        pass
                                except:
                                        pass
                                        
                            #start storing results into a PostGre SQL database        
                            if self.SQL_log_status==True:
                                try:                                
                                    cursor = self.conn.cursor()                                   
                                    try:
                                        fields = ', '.join(record.keys())
                                        values = ', '.join(['%%(%s)s' % x for x in record])
                                        query = 'INSERT INTO wifi_captured (%s) VALUES (%s)' % (fields, values)
                                        cursor.execute(query,record)
                                    except psycopg2.IntegrityError:
                                        self.conn.rollback()
                                    else:
                                        self.conn.commit()
#                                    cursor.close()        
                                except:
                                    pass
            
                                
    # Allow for logging process to be turned on and off for_
    #WiFi data to a comma separated value (CSV) file and a PostGre SQL database.
    def Log(self,csv_log_flag, sql_log_flag):
        
        if csv_log_flag==True:
            
            self.CSV_log_status=True
            print "CSV log is on\n"
            print "Results will be stored at: " + self.fname + '\n'
        else:
            self.CSV_log_status=False
            print "CSV log is off\n"
            
        if sql_log_flag==True:
            self.SQL_log_status=True
            print "SQL log is on\n"
        else:
            self.SQL_log_status=False
            print "SQL log is off\n"   
    
    
    #Connect to the SQL database and return a handle for the class to use.
    #The handle would be a connection to the desired database
    def dbConnect(self,server_name,database_name,username,password,port=5432):
        try:        
            connStr = (r'host=' + server_name + ' dbname=' + database_name + ' user=' + username + ' password=' + password + '') 
            print "Connecting to database\n	->%s" % (connStr) + "\n"
            self.conn = psycopg2.connect(connStr)
            return self.conn
        except psycopg2.Error, err:
            print 'Database connection error!'
            print err
            
        if self.print_results_on_screen==False:
            self.print_results_on_screen = True
            
    #set the name of CSV log file in accordance with today's date and time 
    #return a handle for the class to use
    def CreateCSV(self):
        time_format= "%b-%d-%Y-at-%H-%M-%S"
        today = datetime.datetime.today()
        formated_today = today.strftime(time_format)
        path = os.path.dirname(__file__)
        self.fname =path+'/home/reconpoint/wifi capture code/kismetclient-master/csv logs/output-'+str(formated_today)+'.csv'
        
        if self.print_results_on_screen==False:
            self.print_results_on_screen = True
   
    #Stop WiFi data logging to the database and the CSV file
    def CaptureOff(self):
       #close data base connection, and flip the SQL_log_status flag
       try:
           print           
           self.SQL_log_status=False
           self.conn.close() 
           print 'database logging terminated. \n'
       except:
           print 'Cannot close datbase connection. \n'
           
       #close csv file  and flip the CSV_log_status flag
       try:
           self.CSV_log_status=False
           self.csvfile.close()
           print 'CSV logging terminated. \n'
       except:
#           print 'Cannot close CSV file. \n'
           pass
           
       try:
           self.print_results_on_screen = False
#           print 'No output will be shown on the screen \n'
       except:
           print '\nerror on clearing screen \n'
      
         

