# -*- coding: latin-1 -*-
#! /usr/bin/env python2.7

import shlex
from subprocess import Popen,call,PIPE
import os
from threading import Thread
import vlc
import commands
import config
import jpype

from dvbobjects.PSI.NIT import network_information_section,transport_stream_loop_item
from dvbobjects.PSI.PAT import program_association_section,program_loop_item
from dvbobjects.PSI.SDT import service_description_section,service_loop_item
from dvbobjects.PSI.TDT import time_date_section
from dvbobjects.PSI.PMT import program_map_section,stream_loop_item
from dvbobjects.MHP.AIT import application_information_section,application_loop_item
from dvbobjects.DSMCC.STE import stream_event_section,stream_event_do_it_now_descriptor
from dvbobjects.DSMCC.STEO import str_event_use_tap,Taps,Event_names,Event_ids
from dvbobjects.MHP.Descriptors import DVB_J_application_type,transport_protocol_descriptor,MHP_OC_protocol_id,dvb_j_application_location_descriptor,application_descriptor,application_name_descriptor,dvb_j_application_descriptor
from dvbobjects.DVB.Descriptors import network_descriptor,service_list_descriptor,service_descriptor_loop_item,service_descriptor,application_signalling_descriptor,stream_identifier_descriptor,data_broadcast_id_descriptor
from dvbobjects.MPEG.Descriptors import association_tag_descriptor,carousel_identifier_descriptor

from datetime import datetime
from datetime import timedelta
from MBeanHelper import MBeanHelper
from _mysql_exceptions import OperationalError,MySQLError

import MySQLdb
import time
import threading

database='stcav1'
#ipdb='localhost'
ipdb='192.168.119.2'
logindb='root'
pwddb='st'

TERRESTRE=1
CABLE=2

modo_transmision=TERRESTRE
ruta_contenidos = '/home/gestv/parrilla/demo/content/Broadcast/'
ruta_iptv = '/home/gestv/parrilla/demo/content/'
ruta_tablas = '/home/gestv/parrilla/demo/'
modulador=115
numTarjeta=2
tsout_bitrate_t='13271000'
tsout_bitrate_c='38097647'
ts_video_bitrate='2990000'
ts_audio_bitrate='188000'
pid_video='2064'
pid_audio='2068'
dir_ip_destino='224.1.1.1'
puerto_destino='1234'
iptv=False
transport_stream_id = 1
original_transport_stream_id = 1
service_id = 1
pmt_pid = 1031
ait1_pid = 2001
ste1_pid = 2002
dsmccB_association_tag = 0xB
dsmccB_carousel_id = 1

mbeanName='Parrilla'
resName='ga1' 
mbeanHelper=None
mbeans=None

class TimerInfo(threading.Thread):
    def __init__(self, seconds, texto):
        self.runTime = seconds
        self.texto = texto
        threading.Thread.__init__(self)
    def run(self):
        time.sleep(self.runTime)
        self.crearTabla()
        print "Evento Informacion="+self.texto
        os.system('cp eventoinfo.ts ste.ts &')
        time.sleep(2)
        os.system('cp null.ts ste.ts &')
    def crearTabla(self):
        ste = stream_event_section(
        event_id = 1,
        stream_event_descriptor_loop = [
            stream_event_do_it_now_descriptor(
                event_id = 1,
                private_data = self.texto,
            ),
        ],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
        )
        out = open("./eventoinfo.sec", "wb")
        out.write(ste.pack())
        out.close
        out = open("./eventoinfo.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts ' + str(ste1_pid) + ' < ./eventoinfo.sec > ./eventoinfo.ts')

class TimerEncuesta(threading.Thread):
    def __init__(self, seconds, texto):
        self.runTime = seconds
        self.texto = texto
        threading.Thread.__init__(self)
    def run(self):
        time.sleep(self.runTime)
        self.crearTabla()
        print "Evento Encuesta="+self.texto
        os.system('cp eventoenc.ts ste.ts &')
        time.sleep(2)
        os.system('cp null.ts ste.ts &')
    def crearTabla(self):
        ste = stream_event_section(
        event_id = 2,
        stream_event_descriptor_loop = [
            stream_event_do_it_now_descriptor(
                event_id = 2,
                private_data = self.texto,
            ),
        ],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
        )
        out = open("./eventoenc.sec", "wb")
        out.write(ste.pack())
        out.close
        out = open("./eventoenc.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts ' + str(ste1_pid) + ' < ./eventoenc.sec > ./eventoenc.ts')

class tablas:
    def __init__(self):
        
        nit = network_information_section(
            network_id = 1,
                network_descriptor_loop = [
                network_descriptor(network_name = "STCAV",), 
                    ],
            transport_stream_loop = [
                transport_stream_loop_item(
                transport_stream_id = transport_stream_id,
                original_network_id = original_transport_stream_id,
                transport_descriptor_loop = [
                    service_list_descriptor(
                    dvb_service_descriptor_loop = [
                        service_descriptor_loop_item(
                        service_ID = service_id, 
                        service_type = 1,
                        ),
                    ],
                    ),
                ],        
                 ),
              ],
                version_number = 1,
                section_number = 0,
                last_section_number = 0,
                )
        
        pat = program_association_section(
            transport_stream_id = transport_stream_id,
                program_loop = [
                    program_loop_item(
                    program_number = service_id,
                    PID = pmt_pid,
                    ),  
                    program_loop_item(
                    program_number = 0,
                    PID = 16,
                    ), 
                ],
                version_number = 1,
                section_number = 0,
                last_section_number = 0,
                )
        
        sdt = service_description_section(
            transport_stream_id = transport_stream_id,
            original_network_id = original_transport_stream_id,
                service_loop = [
                service_loop_item(
                service_ID = service_id,
                EIT_schedule_flag = 0,
                EIT_present_following_flag = 0,
                running_status = 4,
                free_CA_mode = 0,
                service_descriptor_loop = [
                    service_descriptor(
                    service_type = 1,
                    service_provider_name = "STCAV",
                    service_name = "STCAV",
                    ),    
                ],
                ),    
                ],
                version_number = 1,
                section_number = 0,
                last_section_number = 0,
                )
        
        
        current_time = time.gmtime()
        tdt = time_date_section(
                year = current_time[0]-1900,
                month = current_time[1],
                day = current_time[2],
                hour = ((current_time[3] / 10) * 16) + (current_time[3] % 10),
                minute = ((current_time[4] / 10) * 16) + (current_time[4] % 10),
                second = ((current_time[5] / 10) * 16) + (current_time[5] % 10),
        )
        
        pmt = program_map_section(
            program_number = service_id,
            PCR_PID = 2064,
            program_info_descriptor_loop = [],
            stream_loop = [
                stream_loop_item(
                    stream_type = 2,
                    elementary_PID = 2064,
                    element_info_descriptor_loop = []
                ),
                stream_loop_item(
                    stream_type = 3,
                    elementary_PID = 2068,
                    element_info_descriptor_loop = []
                ),
                stream_loop_item(
                    stream_type = 5,
                    elementary_PID = ait1_pid,
                    element_info_descriptor_loop = [ 
                        application_signalling_descriptor(
                        application_type = 1,
                        AIT_version = 1,
                        ),
                    ]    
                ),
                stream_loop_item(
                    stream_type = 12,
                    elementary_PID = ste1_pid,
                    element_info_descriptor_loop = [ 
                        stream_identifier_descriptor(
                            component_tag = 0xD,
                        ),
                    ]    
                ),
                stream_loop_item(
                    stream_type = 11,
                    elementary_PID = 2003,
                    element_info_descriptor_loop = [
                        association_tag_descriptor(
                            association_tag = dsmccB_association_tag,
                            use = 0,
                            selector_lenght = 0,
                            transaction_id = 0x80000000,
                            timeout = 0xFFFFFFFF,
                            private_data = "",
                        ),
                        stream_identifier_descriptor(
                            component_tag = dsmccB_association_tag,
                        ),
                        carousel_identifier_descriptor(
                            carousel_ID = dsmccB_carousel_id,
                            format_ID = 0,
                            private_data = "",
                        ),
                        data_broadcast_id_descriptor(
                            data_broadcast_ID = 240,
                            ID_selector_bytes = "",
                        ),
                    ]
                )    
            ],
                version_number = 1,
                section_number = 0,
                last_section_number = 0,
                )    

        ait = application_information_section(
                application_type = DVB_J_application_type,
                common_descriptor_loop = [],
                application_loop = [
                application_loop_item(
                    organisation_id = 10,
                    application_id = 1001,
                    application_control_code = 2,
                    application_descriptors_loop = [
                    transport_protocol_descriptor(
                            protocol_id = MHP_OC_protocol_id,
                            transport_protocol_label = 1,
                            remote_connection = 0,
                            component_tag = 0xB,
                    ),
                    application_descriptor(
                            application_profile = 0x0001,
                            version_major = 1,
                            version_minor = 0,
                            version_micro = 2,
                            service_bound_flag = 1,
                            visibility = 3,
                            application_priority = 1,
                            transport_protocol_labels = [1],
                    ),
                    application_name_descriptor(application_name = "STCAV"),
                    dvb_j_application_descriptor(parameters = [""]),
                    dvb_j_application_location_descriptor(
                        base_directory = "/",
                        class_path_extension = "",
                        initial_class = "stcav.Stcav",
                    ),
                    ]
                    ),
               ],
                version_number = 1,
                section_number = 0,
                last_section_number = 0,
            )

        
        out = open("./nit.sec", "wb")
        out.write(nit.pack())
        out.close
        out = open("./nit.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts 16 < ./nit.sec > ./nit.ts')
        
        out = open("./pat.sec", "wb")
        out.write(pat.pack())
        out.close
        out = open("./pat.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts 0 < ./pat.sec > ./pat.ts')
        
        out = open("./sdt.sec", "wb")
        out.write(sdt.pack())
        out.close
        out = open("./sdt.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts 17 < ./sdt.sec > ./sdt.ts')
        
        out = open("./tdt.sec", "wb")
        out.write(tdt.pack())
        out.close
        out = open("./tdt.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts 20 < ./tdt.sec > ./tdt.ts')
        
        out = open("./pmt.sec", "wb")
        out.write(pmt.pack())
        out.close
        out = open("./pmt.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts ' + str(pmt_pid) + ' < ./pmt.sec > ./pmt.ts')
        
        out = open("./ait.sec", "wb")
        out.write(ait.pack())
        out.close
        out = open("./ait.sec", "wb")
        out.close
        os.system('/usr/local/bin/sec2ts ' + str(ait1_pid) + ' < ./ait.sec > ./ait.ts')
        
        os.system('cp null.ts ste.ts')
        os.system('mkdir ocdir1/test.event')
        
        tap = str_event_use_tap()
        tap.set(
                id = 0,
            assocTag = 0xD,
            )
        
        taps = Taps (
                taps_count = 1,
            tap_loop = [ tap,],
            )
        
        event_count = 3
        
        event_names = Event_names (
                eventnames_count = event_count,
                event_name_loop = [ "event 1", "event 2", "event 3"],
            )
        
        event_ids = Event_ids (
                eventids_count = event_count,
                event_id_loop = [ 1, 2, 3,],
            )
        
        out = open("ocdir1/test.event/.tap", "wb")
        out.write(taps.pack())
        out.close
        out = open("ocdir1/test.event/.tap", "wb")
        out.close
        
        out = open("ocdir1/test.event/.eid", "wb")
        out.write(event_ids.pack())
        out.close
        out = open("ocdir1/test.event/.eid", "wb")
        out.close
        
        out = open("ocdir1/test.event/.ename", "wb")
        out.write(event_names.pack())
        out.close
        out = open("ocdir1/test.event/.ename", "wb")
        out.close
        
#        os.system('echo '+config.dirip+':8888 > ocdir1/res/ip.txt')#Cambio ocdir1/res/ip.txt > ocdir1/res/ip_.txt
        os.system('echo '+config.dirip+':8888 > ocdir1/res/ip.txt')
        os.system('oc-update.sh ocdir1 0xB 6 2003 1 2 0 0 4066 0 2')

class Parrilla(Thread):
    def __init__(self):
        global mbeanHelper,mbeans
        Thread.__init__(self)
        hoy= datetime.today().strftime("%w")
        self.cursor = None
        self.resultado = None
        self.db = None
        try:
            self.db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if self.db is not None:
            self.cursor=self.db.cursor()
            sql='SELECT idEvento,Hora,Duracion,Ruta FROM (SELECT Programa.idPrograma, DATE_FORMAT(Programa.Hora,\'%T.%f\') as Hora, Evento.idEvento, DATE_FORMAT(Evento.Duracion,\'%T.%f\') as Duracion, REPLACE(Evento.Ruta,\'.mp4\',\'\') as Ruta FROM Programa LEFT JOIN Evento ON Evento.Programa_idPrograma=Programa.idPrograma AND Evento.Estado=\'completado\' WHERE Programa.Dia=\''+hoy+'\' ORDER BY Evento.idEvento DESC) AS s GROUP BY s.idPrograma ORDER BY s.Hora ASC;'
            self.cursor.execute(sql)
            self.resultado=self.cursor.fetchall()

    def arrancar(self):
        global mbeanHelper
        config.estado=config.estados[1]
        self.start()

    def run(self):
        global mbeanHelper,mbeans
        jpype.attachThreadToJVM()
        while config.estado in config.estados[0] :
            time.sleep(1)
        
        os.chdir(ruta_tablas)
        eventoActual=1
        numEventos=self.cursor.rowcount
        eventos = [w for w in self.resultado]
        dnsSg=05
        dnsMs=12
        rutaNoSenal='11_1322587936515'
        pesnum=1
        iniPes=False
        pespres = [0,0,0]
        pestimes = [0,0,0]

        args = shlex.split('rm -f fifo_out.ts fifo_tdt.ts fifo_audio.ts fifo_video.ts 1.video.pes 2.video.pes 1.audio.pes 2.audio.pes 1.audio.pes.length 2.audio.pes.length')
        try:
            call(args,shell=False)
        except:
            pass

        if os.path.exists(ruta_iptv+rutaNoSenal+'.mp4') is True :
            tablas()
    
            if modo_transmision is 1 :
                tsout_bitrate=tsout_bitrate_t
            else:
                tsout_bitrate=tsout_bitrate_c
                    
            if iptv :
                instance.vlm_add_broadcast('iptv', ruta_iptv+rutaNoSenal+'.mp4', '#gather:udp{mux=ts,dst='+dir_ip_destino+':'+puerto_destino+'}', 1, ("sout-keep",1), True, True)
            
            args = shlex.split('mkfifo fifo_out.ts fifo_tdt.ts fifo_audio.ts fifo_video.ts')
            self.p1 = Popen(args,shell=False)
            
            if modo_transmision is 1 :
                args = shlex.split('DtPlay fifo_tdt.ts -n '+str(numTarjeta)+' -t '+str(modulador)+' -mt DVBT -mC QAM16 -mG 1/4 -mc 2/3 -mf 578 -mS ON')
            else:
                args = shlex.split('DtPlay fifo_tdt.ts -n '+str(numTarjeta)+' -t '+str(modulador)+' -r '+tsout_bitrate_c+' -mt QAM64 -mf 578 -ma A -mS ON')
            self.p2 = Popen(args,shell=False)
            
            args = shlex.split('tstdt fifo_out.ts')
            fifo1 = open('fifo_tdt.ts', 'w')
            self.p3 = Popen(args,shell=False,stdout=fifo1)
            
            args = shlex.split('tscbrmuxer b:'+ts_video_bitrate+' fifo_video.ts b:'+ts_audio_bitrate+' fifo_audio.ts b:4000000 ocdir1.ts b:3008 pat.ts b:3008 pmt.ts b:2000 tdt.ts b:2000 ste.ts b:2000 ait.ts b:1500 sdt.ts b:1400 nit.ts o:'+tsout_bitrate+' null.ts')
            fifo2 = open('fifo_out.ts', 'w')
            self.p4 = Popen(args,shell=False,stdout=fifo2)
            
            print 'Lista de Eventos'
            for i in eventos:
                print 'Hora: '+str(i[1])+' Duracion: '+str(i[2])+' Ruta: '+str(i[3])
            
            for ie in self.resultado:
                if datetime.today().strftime("%H:%M:%S.%f") < str(ie[1]):
                    break;
                else:
                    del eventos[0]
                    numEventos-=1
            
            print "Numero de Eventos Siguientes="+str(numEventos)
            eventCount=1
            #delta=0
            numeventopres=0
            while config.estado in config.estados[1] :
                if eventCount % 2 == 1 :
                    pesnum=1
                else :
                    pesnum=2            
                #Configurando evento inicial y siguiente
                if not iniPes :
                    print '************************Configurando evento inicial y siguiente***********************************************************************'
                    horaact=datetime.today()
                    horaactst = horaact.strftime("%H:%M:%S.%f")
                    print 'horaActual='+horaactst
                    #Evento inicial
                    if numEventos > 0 :
                        evento=eventos[eventoActual-1]
                        if horaactst < str(evento[1]):
                            print 'Set noSenal 1'
                            pespres[1]=0
                            self.setContent(rutaNoSenal,1)
                            if iptv:
                                instance.vlm_set_input('iptv', ruta_iptv+rutaNoSenal+'.mp4')
                            horaact1=horaact+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                            horaactst1 = horaact1.strftime("%H:%M:%S.%f")
                            pestimes[1]=horaact1
                            print 'horasumada='+horaactst1
                            #Evento Siguiente
                            if horaactst1 < str(evento[1]):
                                print 'Set noSenal 2'
                                pespres[2]=0
                                self.setContent(rutaNoSenal,2)
                                horaact2=horaact1+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                                horaactst2 = horaact2.strftime("%H:%M:%S.%f")
                                pestimes[2]=horaact2
                                print 'horasumada='+horaactst2
                            else :
                                print 'Set evento 2'
                                pespres[2]=1
                                self.setContent(evento[3],2)
                                horaevt = datetime.strptime(str(evento[2]), "%H:%M:%S.%f")
                                print horaactst1
                                print str(horaevt.minute)
                                print str(horaevt.second)
                                print str(horaevt.microsecond)
                                
                                horaact2=horaact1+timedelta(minutes=horaevt.minute,seconds=horaevt.second,milliseconds=(horaevt.microsecond/1000))
                                horaactst2 = horaact2.strftime("%H:%M:%S.%f")
                                pestimes[2]=horaact2
                                print 'horasumada='+horaactst2
                                if numEventos+1 > eventoActual:
                                    eventoActual+=1
                        else :
                            print 'Set evento 1'
                            pespres[1]=1
                            self.setContent(evento[3],1)
                            if iptv:
                                instance.vlm_set_input('iptv', ruta_iptv+evento[3]+'.mp4')
                            horaevt = datetime.strptime(str(evento[2]), "%H:%M:%S.%f")
                            horaact1=horaact+timedelta(minutes=horaevt.minute,seconds=horaevt.second,milliseconds=(horaevt.microsecond/1000))
                            horaactst1 = horaact1.strftime("%H:%M:%S.%f")
                            pestimes[1]=horaact1
                            print 'horasumada='+horaactst1
                            if numEventos+1 > eventoActual:
                                eventoActual+=1
                                #Evento Siguiente
                                if horaactst1 < str(eventos[eventoActual-1][1]):
                                    print 'Set noSenal 2'
                                    pespres[2]=0
                                    self.setContent(rutaNoSenal,2)
                                    horaact2=horaact1+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                                    horaactst2 = horaact2.strftime("%H:%M:%S.%f")
                                    pestimes[2]=horaact2
                                    print 'horasumada='+horaactst2                        
                                else :
                                    print 'Set evento 2'
                                    pespres[2]=1
                                    evento=eventos[eventoActual-1]
                                    self.setContent(evento[3],2)
                                    horaevt = datetime.strptime(str(evento[2]), "%H:%M:%S.%f")
                                    horaact2=horaact1+timedelta(minutes=horaevt.minute,seconds=horaevt.second,milliseconds=(horaevt.microsecond/1000))
                                    horaactst2 = horaact2.strftime("%H:%M:%S.%f")
                                    pestimes[2]=horaact2
                                    print 'horasumada='+horaactst2
                                    if numEventos+1 > eventoActual:
                                        eventoActual+=1
                            else:
                                    print 'Set noSenal 2'
                                    pespres[2]=0
                                    self.setContent(rutaNoSenal,2)
                                    horaact2=horaact1+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                                    horaactst2 = horaact2.strftime("%H:%M:%S.%f")
                                    pestimes[2]=horaact2
                                    print 'horasumada='+horaactst2  
                    else:
                        self.setContent(rutaNoSenal,1)
                        if iptv:
                            instance.vlm_set_input('iptv', ruta_iptv+rutaNoSenal+'.mp4')
                        self.setContent(rutaNoSenal,2)
                    
                    if iptv :
                        instance.vlm_play_media('iptv')
                        
                    args = shlex.split('pesvideo2ts '+pid_video+' 25 112 '+ts_video_bitrate+' 1 1.video.pes 2.video.pes')
                    fifo3 = open('fifo_video.ts', 'w')
                    self.p5 = Popen(args,shell=False,stdout=fifo3,stderr=PIPE)
                    
                    args = shlex.split('pesaudio2ts '+pid_audio+' 1152 48000 384 1 1.audio.pes 2.audio.pes')
                    fifo4 = open('fifo_audio.ts', 'w')
                    self.p6 = Popen(args,shell=False,stdout=fifo4,stderr=PIPE)
                    print '-----'+self.p5.stderr.readline()
                    print '-----'+self.p5.stderr.readline()
                    
                    if numEventos > 0 :
                        t0 = TimerInfo(1,'{\"id\" : \"1\" , \"tipo\" : \"1\", \"texto\" : \"kalash, kalash\" , \"duracion\" : \"1\"}\n')
                        t0.start()
                        iniPes=True
                    else:
                        break
                print '*************************Presentando evento**********************************************************************'
    
                if pespres[pesnum] is 1 :
                    eventopres=eventos[numeventopres]
                    duraevt = datetime.strptime(eventopres[2], "%H:%M:%S.%f")
                    tiempo=float(float((duraevt.minute*60*1000000)+(duraevt.second*1000000)+duraevt.microsecond)/float(1000000))
                    self.iniInfoAsociada(eventopres[0])
                    self.iniVotacion(eventopres[0],tiempo)
                    numeventopres+=1
                
                while True:
                    line=self.p6.stderr.readline()
                    parts1=line.split(",")
                    parts2=parts1[0].split(" ")
                    if len(parts2) > 1:
                        sync1=parts2[10]
                    else:
                        sync1=None
                    line=self.p5.stderr.readline()
                    parts1=line.split(",")
                    parts2=parts1[0].split(" ")
                    if len(parts2) > 1:
                        sync2=parts2[9]
                    else:
                        sync2=None
                    if sync1 is not None and sync2 is not None:
                        if sync1 != sync2 :
                            print '--- Out of Synchronization --- '+sync1+' different of '+sync2
                            mbeanHelper.sendNotification(mbeans[0],'gestv.error.audioVideoOutOfSynchronization', 'empty');
                    break
                
                horaact=datetime.today()
                horaactst = horaact.strftime("%H:%M:%S.%f")
                print 'horafintimer='+horaactst
                
                #Configurando evento posterior
                print '************************Configurando evento posterior***********************************************************************'            
                if pesnum is 1 :
                    pesevt=2
                else :
                    pesevt=1
                horaactst1 = pestimes[pesevt].strftime("%H:%M:%S.%f")
                print 'hora siguiente='+horaactst1
                if numEventos+1 > eventoActual:
                    evento=eventos[eventoActual-1]
                    if horaactst1 < str(evento[1]):
                        print 'Set noSenal '+str(pesnum)
                        pespres[pesnum]=0
                        self.setContent(rutaNoSenal,pesnum)
                        horaact1=pestimes[pesevt]+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                        horaactst1 = horaact1.strftime("%H:%M:%S.%f")
                        pestimes[pesnum]=horaact1
                        print 'horasumada='+horaactst1
                    else:
                        print 'Set evento id='+str(evento[0])+' '+str(pesnum)
                        pespres[pesnum]=1
                        self.setContent(evento[3],pesnum)
                        horaevt = datetime.strptime(str(evento[2]), "%H:%M:%S.%f")
                        horaact1=pestimes[pesevt]+timedelta(minutes=horaevt.minute,seconds=horaevt.second,milliseconds=(horaevt.microsecond/1000))
                        horaactst1 = horaact1.strftime("%H:%M:%S.%f")
                        pestimes[pesnum]=horaact1
                        print 'horasumada='+horaactst1
                        if numEventos+1 > eventoActual :
                            eventoActual+=1 
                else:
                    if pespres[1] is 0 and pespres[2] is 0:
                        break;
                    else:
                        print 'Set noSenal '+str(pesnum)
                        pespres[pesnum]=0
                        self.setContent(rutaNoSenal,pesnum)
                        horaact1=pestimes[pesevt]+timedelta(seconds=dnsSg,milliseconds=dnsMs)
                        horaactst1 = horaact1.strftime("%H:%M:%S.%f")
                        pestimes[pesnum]=horaact1
                        print 'horasumada='+horaactst1
                eventCount+=1
    
            if iptv :
                instance.vlm_set_input('iptv', ruta_iptv+rutaNoSenal+'.mp4')
    
            while config.estado in config.estados[1] :
                print 'colocando ciclo no senal'
                #tiempo=float(float((duraNoSenal.minute*60*1000000)+(duraNoSenal.second*1000000)+duraNoSenal.microsecond)/float(1000000))
                #time.sleep(tiempo-1)
                #while True:
                line=self.p6.stderr.readline()
                print '-- '+line+' --'
                line=self.p5.stderr.readline()
                print '-- '+line+' --'
        else :
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.contentRepositoryNotFound', 'empty');
            print "Error: No pudo conectarse al repositorio de contenidos."
            jpype.detachThreadFromJVM()
            self.parar()
        jpype.detachThreadFromJVM()
        
    def setContent(self,content,pesnum):
        print 'set content = '+content
        ruta_a=ruta_contenidos+content+'.audio.pes'
        ruta_al=ruta_contenidos+content+'.audio.pes.length'
        ruta_v=ruta_contenidos+content+'.video.pes'
        if iptv :
            instance.vlm_add_input('iptv', ruta_iptv+content+'.mp4')
        args = shlex.split('ln -f -s '+ ruta_v +' '+str(pesnum)+'.video.pes')
        self.p0 = Popen(args,shell=False)
        args = shlex.split('ln -f -s '+ ruta_a +' '+str(pesnum)+'.audio.pes')
        self.p0 = Popen(args,shell=False)
        args = shlex.split('ln -f -s '+ ruta_al +' '+str(pesnum)+'.audio.pes.length')
        self.p0 = Popen(args,shell=False)        

    def iniInfoAsociada(self,ids):
        sql='SELECT idInfo_Asociada,Texto,Duracion,Tiempo_despliegue FROM Info_Asociada WHERE Evento_idEvento='+str(ids)+';'
        try:
            self.cursor.execute(sql)
            resultado1=self.cursor.fetchall()
            tiempoinfo=0
            for evinfo in resultado1:
                print "info="+str(evinfo[0])
                print "info="+str(evinfo[1])
                print "info="+str(evinfo[2])
                print "info="+str(evinfo[3])
                tiempoinfo=int(evinfo[3])
                t = TimerInfo(tiempoinfo,'{\"id\" : \"'+str(evinfo[0])+'\", \"tipo\" : \"1\" , \"texto\" : \"'+str(evinfo[1])+'\" , \"duracion\" : \"'+str(evinfo[2])+'\"}\n')
                t.start()
        except MySQLError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        
            
    def iniVotacion(self,ids,tiempo):
        sql='SELECT idValoracion,Texto FROM Valoracion WHERE Evento_idEvento='+str(ids)+';'
        try:
            self.cursor.execute(sql)
            resultado1=self.cursor.fetchall()
            for evinfo in resultado1:
                print "encu="+str(evinfo[0])
                print "encu="+str(evinfo[1])
                t = TimerEncuesta(tiempo-20,'{\"id\" : \"'+str(evinfo[0])+'\", \"tipo\" : \"2\" , \"texto\" : \"'+str(evinfo[1])+'\"}\n')
                t.start()
        except MySQLError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty')
            print "Error: No puedo conectarse a la base de datos."

        
    def parar(self):
        config.estado=config.estados[0]
        if iptv :
            instance.vlm_del_media('iptv')
            instance.vlm_release()
            instance.release()
        self.p2.kill()
        self.p2.terminate()
        self.p2.wait()
        self.p3.kill()
        self.p3.terminate()
        self.p3.wait()        
        self.p4.kill()
        self.p4.terminate()
        self.p4.wait()
        self.p5.kill()
        self.p5.terminate()
        self.p5.wait()
        self.p6.kill()
        self.p6.terminate()
        self.p6.wait()
        args = shlex.split('rm -f fifo_out.ts fifo_tdt.ts fifo_audio.ts fifo_video.ts')
        try:
            call(args,shell=False)
        except:
            pass

        args = shlex.split('rm -f 1.video.pes 2.video.pes 1.audio.pes 2.audio.pes 1.audio.pes.length 2.audio.pes.length')
        call(args,shell=False)
        args = shlex.split('rm -f 2.video.pes 1.audio.pes 2.audio.pes 1.audio.pes.length 2.audio.pes.length')
        call(args,shell=False)
        args = shlex.split('rm -f 1.audio.pes 2.audio.pes 1.audio.pes.length 2.audio.pes.length')
        call(args,shell=False)
        args = shlex.split('rm -f 2.audio.pes 1.audio.pes.length 2.audio.pes.length')
        call(args,shell=False)
        args = shlex.split('rm -f 1.audio.pes.length 2.audio.pes.length')
        call(args,shell=False)
        args = shlex.split('rm -f 2.audio.pes.length')
        call(args,shell=False)        
        
        print 'Parrilla Parada'
        
class Consola(Thread):
        def run(self):
            global parr,mbeanHelper,mbeans
            jpype.attachThreadToJVM()
            mbeans=mbeanHelper.register([resName],mbeanName)
            
            fechaactual=time.strftime("%H:%M:%S %Y-%m-%d")
            mbeanHelper.changeAttribute(mbeanName, resName, 'uptime', fechaactual)
            retorno=self.checkCard()
            if retorno is 1 :
                config.dirip=commands.getoutput("ifconfig").split("\n")[1].split()[1][5:]
                print config.dirip
                while True:
                    print '\n************************ 1. Arrancar ************************\n'
                    print '************************ 2. Parar ************************\n'
                    print '************************ 3. Salir ************************\n'
                    command_line = raw_input()
                    print command_line 
                    if "1" in command_line:
                        if config.estados[0] in config.estado :
                            parr=Parrilla()
                            mbeanHelper.changeAttribute(mbeanName, resName, 'playing', 'true')
                            parr.arrancar()
                        else :
                            print "La parrilla se encuentra en ejecución."
                    if "2" in command_line:
                        if config.estados[1] in config.estado :
                            config.estado=config.estados[2]
                            print 'Parando Parrilla'
                            parr.parar()
                            parr.join(1)
                            mbeanHelper.changeAttribute(mbeanName, resName, 'playing', 'false')
                        else :
                            print "La parrilla se encuentra en detención."
                    if "5" in command_line:
                        t1 = TimerEncuesta(5,'{\"id\" : \"1\" , \"tipo\" : \"2\", \"texto\" : \"Qué te ha parecido el programa?\"}\n')
                        t1.start()
                    if "4" in command_line:
                        t2 = TimerInfo(5,'{\"id\" : \"1\" , \"tipo\" : \"1\", \"texto\" : \"El cosmos es todo lo que es, todo lo que fue y todo lo que será. Carl Sagan.\" , \"duracion\" : \"15\"}\n')
                        t2.start()                        
                    if "3" in command_line:
                        if config.estados[1] in config.estado or config.estados[2] in config.estado:
                            parr.parar()
                            parr.join(1)
                            mbeanHelper.changeAttribute(mbeanName, resName, 'playing', 'false')
                        os._exit(1)
            else :
                print 'Presione una tecla para salir ...'
                raw_input()
                os._exit(1)
                    
        def checkCard(self):
            global mbeanHelper,mbeans
            retorno = 0
            if modo_transmision is 1 :
                args = shlex.split('DtPlay '+ruta_tablas+'/null.ts -n '+str(numTarjeta)+' -t '+str(modulador)+' -mt DVBT -mC QAM16 -mG 1/4 -mc 2/3 -mf 578 -mS ON')
            else:
                args = shlex.split('DtPlay '+ruta_tablas+'/null.ts -n '+str(numTarjeta)+' -t '+str(modulador)+' -r '+tsout_bitrate_c+' -mt QAM64 -mf 474 -ma A -mS ON')
            p0 = Popen(args,shell=False,stdout=PIPE)
            flag = True
            count = 0
            while flag is True :
                linea=p0.stdout.readline()
                parts = linea.split(" ")
                if parts[0] == 'Start' :        
                    retorno = 1
                    flag = False
                if parts[0] == 'No' and parts[2] == 'found\n':        
                    retorno = 0
                    mbeanHelper.sendNotification(mbeans[0],'gestv.error.modulatorCardNotWorking', 'empty')
                    print 'Tarjeta moduladora no encontrada.'
                    flag = False
                if parts[0] == 'Invalid' and parts[1] == 'argument' :
                    retorno = 0
                    mbeanHelper.sendNotification(mbeans[0],'gestv.error.modulatorMissconfigured', 'empty')
                    print 'Parámetros de modulación incorrectos.'
                    flag = False
                count = count + 1
            try:
                p0.kill()
            except:
                pass
            return retorno

if iptv :
    instance=vlc.Instance()
if MBeanHelper.instance is None :
    mbeanHelper = MBeanHelper('broadcaster',10000)
    MBeanHelper.instance = mbeanHelper
else:
    mbeanHelper = MBeanHelper.instance
parr=Parrilla()
Consola().start()
    