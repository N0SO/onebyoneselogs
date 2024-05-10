#!/usr/bin/env python3
"""
Search the MOQP database for 1x1 Special Event Station (SES) logs
received. Display status for (log received/not recieved).

Update History is in file __init__.py
"""


from onebyonelogsreceived.__init__ import VERSION
from moqputils.moqpdbutils import *
from moqputils.configs.moqpdbconfig import *
from datetime import datetime
from htmlutils.htmldoc import *


class Station():
    def __init__(self, call = None, 
                       status = False, 
                       lid = None,
                       timestamp=None):
        self.call = call
        self.status = status
        self.logID = lid
        try:
            self.updateTime = \
                    timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except:
            self.updateTime = timestamp
        
    def InLog(self):
        return self.status
        
    def csvLine(self):
        if self.updateTime:
            try:
                timestamp = \
                    self.updateTime.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = self.updateTime
        else:
            timestamp = ''
        if self.InLog():
            inlog='RECEIVED'
        else:
            inlog=''
        return ('{}\t{}\t{}'.format(\
                  self.call, 
                  inlog,
                  timestamp))
                  
class logsReceived():
    def __init__(self, args, callList = None):
        self.stationList = dict()
        self.valid = False
        if (callList!=None):
            self.fetchCalls(callList)
            
    def fetchCalls(self, callList):
        mydb = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
        mydb.setCursorDict()
        for call in callList:
                status = False
                logid = None
                log = None
                updatetime=None
                log = mydb.read_query("""SELECT ID, CALLSIGN, TIMESTAMP
                     FROM LOGHEADER WHERE CALLSIGN='{}'""".format(call))
                #print (call, log, len(log))
                if len(log) >=1 :
                    #print(log[0]['ID'], log[0]['CALLSIGN'])
                    status = True
                    logid = log[0]['ID']
                    updatetime = log[0]['TIMESTAMP']
                station = Station(call=call, status=status, 
                                  lid=logid, 
                                  timestamp=updatetime)
                #print(station.call, station.logID, station.status)
                self.stationList[station.call] = station
        
        #print (self.stationList)
        self.valid = True
        return self.valid

class csvlogsRecvd(logsReceived):
    
    def getCSV(self):
        CALLLIST = list(self.stationList.keys())
        csvData = ['CALLSIGN\tINLOG\tUPDATE TIME']

        for cs in CALLLIST:
            csvData.append(self.stationList[cs].csvLine())
        csvData.append('\n\nData Valid = {}'.format(self.valid))
        return csvData

    def showRpt(self, csvd = None):
        if csvd == None:
            csvd = self.getCSV()
        for line in csvd:
            print(line)

class htmlLogsRecvd(csvlogsRecvd):
    def showRpt(self,csvd=None):
        csvd = self.getCSV()
        
        htmd = self.makeHTML(csvd)
        #print (htmd)
        self.getHTML(htmd)
        
    def makeHTML(self, csvd):
        htmd = []
        for crow in csvd:
            hrow = crow.split('\t')
            htmd.append(hrow)
        #print(htmd)
        return htmd
    
    def getHTML(self, htmld = None ):
       d = htmlDoc()
       d.openHead(\
           '{} Missouri QSO Party 1x1 SE Log Submission Status'\
               .format(YEAR),'./styles.css')
       d.closeHead()
       d.openBody()
       d.addTimeTag(prefix='Report Generated On ', 
                    tagType='comment') 
                         
       d.add_unformated_text(\
           """<h2 align='center'>{} Missouri QSO Party 1x1 SE Log Submission Status</h2>\n""".format(YEAR))

       d.addTable(htmld, header=True)
       d.closeBody()
       d.closeDoc()

       d.showDoc()
       #d.saveAndView('test.html')
       
class logSummary(logsReceived):

    def fetchCalls(self, args, callList = None):
        """Fetch log summary data for 1x1 calls."""
        db = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
        db.setCursorDict()
        tableData = db.read_query(\
            """SELECT * FROM SES_SUMMARY_VIEW 
                WHERE 1 
                ORDER BY CALLSIGN""")
        #print(tableData)
        for t in tableData:
            station=stationSum()
            station._parseDB_data(t)
            self.stationList[station.call] = station
            #print(vars(q))
            #print(q.csvLine())
        self.valid=True
        return self.valid
        
    def getCSV(self, CALLLIST= None):
        if CALLLIST==None:
            CALLLIST = list(self.stationList.keys())
        
        csvData = ['CALLSIGN\tLOC\tMOQPCAT\tSCORE\tQSO_SCORE\tCW Qs\tPH Qs\tRY Qs\tMULTS\tW0MA\tK0GQ\tCABRILLO\tVHF Qs\tDIGITAL\tVHF\tROOKIE\tLOG ID\tSUM ID\tUPDATE TIME\tSTATUS']

        for cs in CALLLIST:
            if cs in self.stationList.keys():
                csvData.append(self.stationList[cs].csvLine())
            else:
                csvData.append('{}\t-'.format(cs))
                
        #csvData.append('\n\nData Valid = {}'.format(self.valid))
        return csvData

    def showRpt(self, csvd = None, callList = None):
        if csvd == None:
            csvd = self.getCSV(CALLLIST=callList)
        for line in csvd:
            print(line)


class stationSum(Station):
    def __init__(self, call = None, 
                       status = False, 
                       lid = None,
                       timestamp=None,
                       sumid=None,
                       cwq=None,
                       phq=None,
                       ryq=None,
                       vhfq=None,
                       mults=None,
                       qscore=None,
                       bonus1=None,
                       bonus2=None,
                       bonus3=None,
                       score=None,
                       mcategory=None,
                       digital=None,
                       vhf=None,
                       rookie=None,
                       loc=None
                       ):

        self.call = call
        self.status = status
        self.logID = lid
        self.sumID=sumid
        self.cwQs=cwq
        self.phQs=phq
        self.ryQs=ryq
        self.vhfQs=vhfq
        self.Mults=mults
        self.qsoScore=qscore
        self.w0ma_B=bonus1
        self.k0gq_B=bonus2
        self.cab_B=bonus3
        self.Score=score
        self.moqpCat=mcategory
        self.DIG=digital
        self.VHF=vhf
        self.Rookie=rookie
        self.Location=loc

        try:
            self.updateTime = \
                    timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except:
            self.updateTime = timestamp
        
    def InLog(self):
        return self.status
        
    def _parseDB_data(self, d):
        """ Fill values with 1 line from DB QSO summary table. """
        self.call = d['CALLSIGN']
        self.sumID = d['ID']
        self.logID = d['LOGID']
        self.cwQs = d['CWQSO']
        self.phQs= d['PHQSO']
        self.ryQs = d['RYQSO']
        self.vhfQs = d['VHFQSO']
        self.Mults = d['MULTS']
        self.qsoScore=d['QSOSCORE']
        self.w0ma_B=d['W0MABONUS']
        self.k0gq_B=d['K0GQBONUS']
        self.cab_B=d['CABBONUS']
        self.Score=d['SCORE']
        self.moqpCat=d['MOQPCAT']
        self.DIG=d['DIGITAL']
        self.VHF=d['VHF']
        self.Rookie=d['ROOKIE']
        self.Location=d['LOCATION']
        self.updateTime=d['TIMESTAMP']
        self.status = True
        return self.status
        
        
    def csvLine(self):
        if self.updateTime:
            try:
                timestamp = \
                    self.updateTime.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = self.updateTime
        else:
            timestamp = ''
        if self.InLog():
            inlog='RECEIVED'
        else:
            inlog=''
        return ('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(\
                self.call,
                self.Location,
                self.moqpCat,
                self.Score,
                self.qsoScore,
                self.cwQs,
                self.phQs,
                self.ryQs,
                self.Mults,
                self.w0ma_B,
                self.k0gq_B,
                self.cab_B,
                self.vhfQs,
                self.DIG,
                self.VHF,
                self.Rookie,
                self.logID,
                self.sumID,
                timestamp,
                self.status
))
    

class htmlSummary(logSummary):
    def showRpt(self,csvd=None, callList = None):
        csvd = self.getCSV(CALLLIST=callList)
        
        htmd = self.makeHTML(csvd)
        #print (htmd)
        self.getHTML(htmd)
        
    def makeHTML(self, csvd):
        htmd = []
        for crow in csvd:
            hrow = crow.split('\t')
            htmd.append(hrow)
        #print(htmd)
        return htmd
    
    def getHTML(self, htmld = None):
       d = htmlDoc()
       d.openHead(\
           '{} Missouri QSO Party 1x1 SE Log Submission Status with Statistics'\
               .format(YEAR),'./styles.css')
       d.closeHead()
       d.openBody()
       d.addTimeTag(prefix='Report Generated On ', 
                    tagType='comment') 
                         
       d.add_unformated_text(\
           """<h2 align='center'>{} Missouri QSO Party 1x1 SE Log Submission Status with Statistics</h2>\n""".format(YEAR))

       d.addTable(htmld, header=True)
       d.closeBody()
       d.closeDoc()

       d.showDoc()
       #d.saveAndView('test.html')
    
