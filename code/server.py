#coding: gb2312
import logging,sys,signal
import logging.config
from threading import Lock
from services import *
import gevent
from gevent.queue import Queue
import signal
import time
import importlib

import servershare
from util.commonutil import *

from systemconfig import *
from syncevent import *
from connection import *

from db.connect import *

import redis

class ServiceItem:
    u"""
    ·�ɱ��д����������ݽṹ
    1��serviceId������Id
    2��serverName ���ڷ��������
    3) connection �����ڷ��������Ƶ������
    """
    def __init__(self, serviceId, serverName, connection = None):
        self.serviceId = serviceId
        self.serverName = serverName
        self.connection = connection

    def __repr__(self):
        return str(self.serviceId) + ":" + self.serverName + ":" + str(self.connection)

class Server:
    
    u"""
    ���������󣬸�������ͨ�����������󣬿ɽ���
    1������֮��ͨѶ
    2����ȡ����

    ������������Ҫ�Ĺ��ܰ���
    1) ��ʼ��
    2����ȡ����
    3��װ�ط���
    4��ʵ��ͨѶ����

    ������ά�����¹ؼ����ݽṹ
    1��·�ɱ����յ��¼�����Ҫ��ѯ·�ɱ�Ѱ���¼��Ľ��շ�����
    2��������ñ���������ݣ����������Ĺ�ϵ
    3��ͨѶƵ�����ñ��浱ǰ��ͨ��������Ϣ
    """
    def __init__(self, conf):
        self.conf = conf
        self.route = {}
        self.services = {}
        self.lock = Lock()
        self.name = self.conf.myself.name
        # create route table
        for s in self.conf.servers:
            for svcId,svc in s.services.items():
                self.route[svcId] = ServiceItem(svcId,s.name)
                #logging.info(" add service in route : %d : %s" , svcId,s.name)
        # ͬ���¼�����
        self.sync_handler = SyncEventHandler()
        self.factory = ConnectionFactory(self,self.name)
        
        self.redis = redis.Redis(*conf.get_redis_config("server_redis"))

        

    def setServiceConnection(self, target, connection):
        u"""
        �����������Э�齨��������������������ͶԶ�Server��ͨѶƵ��
        1�����������󴴽�connection����
        2������������Ϊÿ����������ͨѶconnection"""
              
        for k,v in self.route.items():
            if v.serverName == target:
                v.connection = connection
        
        return connection

    def getServiceConnection(self,serviceId):
        item = self.route.get(serviceId)
        if item != None:
            return item.connection
        return None

    def registeService(self,service):
        u"""����ע�ắ��������ע��ɹ���������շ���Ϣ"""
        self.services[service.serviceId] = service
    
    def unregisteService(self,service):
        u"""����ע������������ע��ɹ���������շ���Ϣ"""
        del self.services[service.serviceId]
    
    def handle_network_event(self,connection,event):
        u"""
        connection�յ���Ӧ���¼��󽫵��÷����������handle����
        �������������dstId��ת������Ӧ�ı��ط���
        """
        self._dispatchEvent(event)
    

    def sendEvent(self,eventData,srcId=-1,dstId=-1,eventType=-1,param1=-1,param2=-1,origEvent=None):
        u"""
        ��ͨ�����ñ������������¼���ָ������
        1���������������ȼ��Ŀ������λ��
        2������Զ�̷���ͨ��connection�������¼����Զ˷�����
        3�����ڱ��ط�����ֱ��ת��
        eventData : ���͵�����
        srcId : Դ����ı�ǣ���origEvent��Ϊ�գ���ΪorigEvent.dstId
        dstId : Ŀ�����ı�ǣ���origEvent��Ϊ�գ���ΪorigEvent.srcId
        eventType: �¼�  �ͣ��������д��Ϊ��1
        origEvent: ΪԴ�¼�
        """
        # check whether event should be sent over network or not
        if origEvent != None:
            srcId = origEvent.dstId
            dstId = origEvent.srcId
            param1 = origEvent.param1
            param2 = origEvent.param2
        item = self.route.get(dstId)

        if item == None:
            logging.warning("Event(%s) Missing due to no this service(%d)",eventData,dstId)
            return -1
        
        event = Event.createEvent(srcId,dstId,eventType,param1,param2,eventData)  
        #print "----->",srcId,dstId,eventType,param1,param2
        if item.serverName == self.name: # local event
            self._dispatchEvent(event)
        else:
            if item.connection == None:
                logging.warning("Event(event=%d,dstId=%d) Missing due to network problem",eventType,dstId)
                return 
            item.connection.send(event.toStream())
        return event.tranId

    def sendSyncEvent(self,eventData,srcId=-1,dstId=-1,eventType=-1,param1=-1,param2=-1,wait = True,timeout = 10):
        item = self.route.get(dstId)
        if item == None:
            logging.warning("Event(%s) Missing due to no this service(%d)",eventData,dstId)
            return None

        event = Event.createSyncRequestEvent(srcId,dstId,eventType,param1,param2,eventData)     
        helper = self.sync_handler.add_event(event)
        
        if item.serverName == self.name: # local event
            self._dispatchEvent(event)
        else:
            if item.connection == None:
                logging.warning("Event(%s) Missing due to network problem",eventData)
                return None 
            item.connection.send(event.toStream())
        if wait:
            return helper.get_response(timeout)
        else:
            return helper

    def responseSyncEvent(self,eventData,srcId=-1,dstId=-1,eventType=-1,param1=-1,param2=-1,origEvent=None):
        if origEvent != None:
            srcId = origEvent.dstId
            dstId = origEvent.srcId
            param1 = origEvent.param1
            param2 = origEvent.param2
        item = self.route.get(dstId)

        if item == None:
            logging.warning("Event(%s) Missing due to no this service(%d)",eventData,dstId)
            return -1

        event = Event.createSyncResponseEvent(srcId,dstId,eventType,param1,param2,eventData,origEvent)  
        if item.serverName == self.name: # local event
            self._dispatchEvent(event)
        else:
            if item.connection == None:
                logging.warning("Event(event=%d,dstId=%d) Missing due to network problem",eventType,dstId)
                return 
            item.connection.send(event.toStream())
        return event.tranId

    def _dispatchEvent(self,event):
        u"""�ַ��¼������ط���ĺ���"""
        #logging.info("receive a event %d,%d,%d:",event.eventType,event.tranId,event.srcId)
        if event.mode == EVENT_MODE_SYNC_RESP:
            self.sync_handler.set_response(event)
            #logging.info("event %d response is ready",event.tranId)
        else:
            svc = self.services.get(event.dstId)
            if svc != None:
                try:
                    svc.dispatch(event)
                except Full,e:
                    logging.warning("Event(%s) Missing due to queue is full",event) 
            else:
                logging.warning("Event(%s) Missing due to no this service",event)


    def _dispatchTimerEvent(self,event):
        u"""�ַ�ʱ���¼������ط���ĺ���"""
        svc = self.services.get(event.dstId)
        if svc != None:
            svc.dispatchTimerEvent(event)
        else:
            logging.warning("Event(%s) Missing due to no this service",event)

    def installServices(self):
        u"""ͨ�������ļ�����Ϣ����������ʼ����ע�����"""
        for server_config in self.conf.servers:
            for svcId,svc in server_config.services.items():
                code = svc.options["handler"]
                mod =  importlib.import_module(code[:code.rindex(".")])
                id = svc.id
                
                service = eval("mod." + code[code.rindex(".")+1:] + "(self,id)")
                if hasattr(service,"setup_route"):
                    service.setup_route()
                
                # setup service handler 
                if server_config.name == self.conf.myself.name:
                    service.init()
                    logging.info(color.strong("install service ==> %s(%d)") % (code,id))
                    self.registeService(service)    
        """
        for svcId,svc in self.conf.myself.services.items():
            code = svc.options["handler"]
            mod =  importlib.import_module(code[:code.rindex(".")])
            id = svc.id
            
            service = eval("mod." + code[code.rindex(".")+1:] + "(self,id)")
            logging.info("install service ==> %s(%d)" % (code,id))
            self.registeService(service)
        """    
     
    def localBroadcastEvent(self,eventType,param1,param2,eventData):
        u"""ʵ�ֱ��ط���㲥"""
        for id,svc in self.services.items():
            evt = Event.createEvent(-1,svc.serviceId,eventType,param1,param2,eventData)
            self._dispatchEvent(evt)

    
    def getServerConfig(self,serverName):
        u"""���ָ����������������Ϣ"""
        for server in self.conf.servers:
            if server.name == serverName:
                return server

        return None
    
    def getMyselfConfig(self):
        return self.conf.myself

    def getServiceConfig(self,serviceId):
        u"""���ָ�������������Ϣ"""
        return self.conf.myself.services[serviceId]
    
    def hasService(self,serviceName):
        for k,svc in self.conf.myself.services.items():
            if svc.service == serviceName:
                return True
        return False
    
    def getServiceIds(self,serviceName):
        u""" ���ָ���������Ƶķ����ʶ"""
        return [x.id for x in self.conf.services[serviceName]]

    def run(self):
        conf = self.conf
        logging.info("Setup network configuration....")
        for i in range(0,len(conf.servers)):
            if conf.servers[i].name == self.name:
                self.factory.start_server_connection(conf.servers[i].port)
                break
            else:
                self.factory.create_client_connection(self.name,conf.servers[i].ip,conf.servers[i].port)
                                
        logging.info(color.red("System Started"))
        """
        try :
            loop = gevent.core.loop()
            loop.run()
        except:
            pass
            #traceback.print_exc()
        """    
    

    def stop(self):
        u"""ֹͣ��������"""
        for service in self.services.values():
            service.stop()
            
        #time.sleep(5)
        for service in self.services.values():
            self.unregisteService(service)
        logging.info(color.red("==> stop server <=="))

    

if __name__ == "__main__":
    import gevent
    from gevent import monkey;monkey.patch_all()
    
    from message.base import *
    MessageMapping.init()
    
    import os
    os.chdir(sys.path[0])
    file = "system.ini"
    if len(sys.argv) > 1:
        myselfName = sys.argv[1]
    else:
        logging.error("��Ҫ����server����")
        sys.exit()
    
    console = False
        
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-console":
            console = True
        elif sys.argv[i] == "-conf":
            file = sys.argv[i+1]        
        
            
    if console:
        logging.basicConfig(level=logging.DEBUG, \
                        format='%(asctime)s %(levelname)s %(message)s', \
                        stream=sys.stdout, \
                        filemode='a')
    else:
        #logging.basicConfig(level=logging.DEBUG, format="%(threadName)s:%(asctime)s %(levelname)s %(message)s", 
        #                filename= "./" + myselfName + ".log",filemode='a')
        logging.config.fileConfig("log4p.conf")
                        
    logging.info("System Starting -> loading configuration %s" , file)
    conf = SystemConfig(file,myselfName)   
    logging.info("System Starting -> creating server instance and initializing")
    servershare.SERVER = server = Server(conf)
    
    logging.info("System Starting -> preparing starting " )
    logging.info("Installing Services Now")
    
    system_config = conf.system_config
    
    DATABASE.setup_user_session(*conf.get_database_config("userdb"))
    DATABASE.setup_session(*conf.get_database_config("gamedb"))    
    
    server.installServices()
    
    _queue = Queue()    
    
    def quit():
        _queue.put_nowait(None)
    
    gevent.signal(signal.SIGINT,quit)
    
    #print server.conf.services
    #print server.route
    try:
        server.run()
        _queue.get()
        server.stop()
    except:
        pass
        #traceback.print_exc()
    sys.exit()

        
    
