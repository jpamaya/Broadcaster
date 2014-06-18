# -*- coding: latin-1 -*-
'''
Created on 30/11/2010
@author: stcav
'''
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
import web
import MySQLdb
import time
import commands
import config
from datetime import datetime
from MBeanHelper import MBeanHelper
from _mysql_exceptions import OperationalError
import netifaces
#import Analizador
idU=0

#28 servicios
urls = ('/infoAsociada/(.*)', 'infoasociada','/votacion', 'voto')
urls += ('/comunidad/registro', 'regcomunidad','/comunidad/miembros/(.*)','miembroscomunidad','/comunidades/usuario/(.*)','comunidades','/comunidad/(.*)','comunidad','/comunidades/(.*)','busquedacomunidades')
urls += ('/validacion/(.*)','valida','/personas/(.*)','busquedapersonas','/persona/(.*)', 'perfil','/persona', 'actualizarperfil','/miembros/(.*)', 'miembros')
urls += ('/programacion/(.*)','programacion','/preferencias', 'preferencias')
urls += ('/epg/favoritos/(.*)','epgfavoritos','/epg/top/(.*)','epgtop','/epg/busqueda/(.*)', 'epgbusqueda')
urls += ('/tablonMensaje/(.*)', 'tablonMensaje','/tablon', 'tablonpost','/tablon/comentario', 'tabloncomentariopost','/comentarioMensaje/(.*)', 'comentarioMensaje','/tablon/comentario/(.*)', 'tabloncomentario','/tablon/comentarios/(.*)', 'tabloncomentarios','/tablon/(.*)', 'tablon')
urls += ('/chat', 'chatpost','/chat/(.*)', 'chat')
urls += ('/notificacion/leidos/(.*)', 'notificacionLeidos','/notificacion', 'setNotificacion','/notificacionMensaje', 'setNotificacionMensaje','/notificacion/(.*)', 'getNotificaciones')
urls += ('/p1/(.*)','prueba1','/consultar/(.*)','consultar')

database='stcav1'
ipdb='localhost'
#ipdb='192.168.119.2'
logindb='root'
pwddb='st'
resName='ga1'
configName='ga2'
mbeanName='Webservices'
mbeanHelper=None

def getIpdb():
    ipdb=mbeanHelper.getAttribute(mbeanName,configName,'ipdb')
    return ipdb

def getLogindb():
    logindb=mbeanHelper.getAttribute(mbeanName, configName,'logindb')
    return logindb

def getPwddb():
    pwddb=mbeanHelper.getAttribute(mbeanName, configName,'pwddb')
    return pwddb

def getDbname():
    dbname=mbeanHelper.getAttribute(mbeanName, configName,'dbname')
    return dbname

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        #config.dirip=commands.getoutput("ifconfig").split("\n")[1].split()[1][5:]
        #config.dirip='192.168.0.26'
        config.dirip = netifaces.ifaddresses('en0')[netifaces.AF_INET][0].get('addr')
        func = web.application(urls, globals()).wsgifunc()
        a=None
        try:
            print 'Escuchando en: '+config.dirip+':'+str(port)
            a = WSGIServer((config.dirip, port), func).serve_forever()
        except:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.addressInUse', 'empty');
            print "Error: La dirección no pudo ser asignada. presione una tecla para salir ..."
            raw_input()
        return a
        #return WSGIServer(('192.168.120.25', port), func).serve_forever()
        #return WSGIServer(('192.168.190.61', port), func).serve_forever()

class getNotificaciones:#YA
    #Consulta las notificaciones para un usuario en una comunidad
    def GET(self,args):
        #http://192.168.120.80:8888/notificacion/?idusuario=1&idcomunidad=1&desdeid=0
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'notificaciones')
        mbeanHelper.changeAttribute(mbeanName,resName,'notificaciones',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        idcomunidad = web.input('idcomunidad').idcomunidad
        desdeid = web.input('desdeid').desdeid
        nummax=10
        db=None
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."

        if db is not None:
            cursor=db.cursor()
            #sql='SELECT * FROM (SELECT Noticia.idNoticia, Noticia.idTipo, Noticia.idNotificacion FROM Noticia LEFT JOIN Notificado ON Notificado.idNoticia=Noticia.idNoticia AND Notificado.idUsuario='+idusuario+' WHERE Noticia.idNoticia>'+str(desdeid)+' AND Noticia.idComunidad='+idcomunidad+' AND Notificado.idUsuario is null ORDER BY Noticia.idNoticia DESC LIMIT '+nummax+') AS tbl ORDER BY tbl.idNoticia ASC;'
            sql='SELECT * FROM (SELECT Noticia.idNoticia, Noticia.Tipo_Noticia_idTipo_Noticia, Noticia.Id_notificacion, Notificado.Usuario_idUsuario FROM Noticia LEFT JOIN Notificado ON Notificado.Noticia_idNoticia=Noticia.idNoticia AND Notificado.Usuario_idUsuario='+str(idusuario)+' WHERE Noticia.idNoticia>'+str(desdeid)+' AND Noticia.Comunidad_idComunidad='+str(idcomunidad)+' ORDER BY Noticia.idNoticia DESC LIMIT '+str(nummax)+') AS tbl ORDER BY tbl.idNoticia ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"idServicio\" : \"'+str(i[2])+'\", '
                cadena+='\"tipo\" : \"'+str(i[1])+'\", '
                if i[1] == 2 or i[1] == 3 :
                    if i[1] == 2:
                        sql='SELECT Usuario.Nombres, Usuario.Foto FROM Usuario,Tablon WHERE Tablon.Usuario_idUsuario=Usuario.idUsuario and Tablon.idTablon='+str(i[2])+';'
                    if i[1] == 3:
                        sql='SELECT tabla1.Nombres1, tabla1.Foto1, tabla2.Nombres2, tabla2.Foto2 FROM (SELECT Usuario.Nombres as Nombres1, Usuario.Foto as Foto1 FROM Usuario,Comentario_Tablon WHERE Comentario_Tablon.Usuario_idUsuario=Usuario.idUsuario and Comentario_Tablon.idComentario_Tablon='+str(i[2])+') as tabla1,(SELECT Usuario.Nombres as Nombres2, Usuario.Foto as Foto2 FROM Usuario,Comentario_Tablon,Tablon WHERE Tablon.Usuario_idUsuario=Usuario.idUsuario and Comentario_Tablon.Tablon_idTablon=Tablon.idTablon and Comentario_Tablon.idComentario_Tablon='+str(i[2])+') as tabla2;'
                        #sql='SELECT usuario.Nombres, usuario.Foto FROM usuario,Comentario_Tablon WHERE Comentario_Tablon.idUsuario=usuario.idUsuario and Comentario_Tablon.idComentario_Tablon='+str(i[2])+';'
                    cursor.execute(sql)
                    resultado2=cursor.fetchall()
                    for j in resultado2:
                        if i[1] == 2:
                            cadena+='\"nombre\" : \"'+str(j[0])+'\", '
                            if str(j[1]).strip() is None or str(j[1]).strip() is '':
                                cadena+='\"foto\" : \"\", '
                            else:
                                cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(j[1]).strip()+'\", '
                        if i[1] == 3:
                            cadena+='\"nombre1\" : \"'+str(j[0])+'\", '
                            if str(j[1]).strip() is None or str(j[1]).strip() is '':
                                cadena+='\"foto1\" : \"\", '
                            else:
                                cadena+='\"foto1\" : \"'+'http://'+config.dirip+'/Images/'+str(j[1]).strip()+'\", '
                            cadena+='\"nombre2\" : \"'+str(j[2])+'\", '
                            if str(j[3]).strip() is None or str(j[3]).strip() is '':
                                cadena+='\"foto2\" : \"\", '
                            else:
                                cadena+='\"foto2\" : \"'+'http://'+config.dirip+'/Images/'+str(j[3]).strip()+'\", '
                    if i[3] is None:
                        cadena+='\"leida\" : \"no\"'
                    else:
                        cadena+='\"leida\" : \"si\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"notificaciones\" : ['+cadena+']}'

class notificacionLeidos:#YA
    #Consulta los mensajes leidos del servicio notificacion
    def GET(self, args):
        #http://192.168.120.80:8888/notificacion/leidos/?idcomunidad=1&idusuario=1&desdeid=0&hastaid=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'notificacionLeidos')
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionLeidos',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        idusuario = web.input('idusuario').idusuario
        desdeid = web.input('desdeid').desdeid
        hastaid = web.input('hastaid').hastaid
        db=None
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."

        if db is not None:
            cursor=db.cursor()
            sql='SELECT Noticia.idNoticia,Notificado.Noticia_idNoticia FROM Noticia LEFT JOIN Notificado ON Notificado.Noticia_idNoticia=Noticia.idNoticia AND Notificado.Usuario_idUsuario='+idusuario+' WHERE Noticia.Comunidad_idComunidad='+idcomunidad+' AND Noticia.idNoticia>='+desdeid+' && Noticia.idNoticia<='+hastaid+' ORDER BY Noticia.idNoticia DESC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                if i[1] is None:
                    cadena+='\"leido\" : \"NO\"'
                else:
                    cadena+='\"leido\" : \"SI\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"leidos\" : ['+cadena+']}'

class setNotificacionMensaje:
    #Actualiza la lectura de una notificacion de un mensaje o comentario
    def POST(self):
        #curl -d "idusuario=1&idnoticia=1" http://192.168.120.80:8888/notificacionMensaje
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'notificacionMensaje')
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionMensaje',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        idnoticia = web.input('idnoticia').idnoticia
        print "idnoticia="+idnoticia
        db=None
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."

        if db is not None:
            cursor=db.cursor()
            sql='SELECT Noticia.idNoticia FROM Noticia WHERE Noticia.Id_notificacion='+str(idnoticia)+' AND Noticia.Tipo_Noticia_idTipo_Noticia=2;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            for i in resultado:
                id=str(i[0])
                print "id="+id
                #select idTablon from Tablon where idTablon not in (select Id_notificacion from Noticia WHERE Tipo_Noticia_idTipo_Noticia=2);
            sql='INSERT INTO Notificado (Noticia_idNoticia,Usuario_idUsuario) VALUES (\''+str(id)+'\',\''+str(idusuario)+'\');'
            try:
                cursor.execute(sql)
                db.commit()
            except:
                None
            finally:
                sql='SELECT Noticia.idNoticia FROM Noticia,Comentario_Tablon WHERE Comentario_Tablon.Tablon_idTablon='+str(idnoticia)+' AND Noticia.Id_notificacion=Comentario_Tablon.idComentario_Tablon AND Noticia.Tipo_Noticia_idTipo_Noticia=3;'
                cursor.execute(sql)
                resultado=cursor.fetchall()
                for j in resultado:
                    print str(j[0])
                    sql='INSERT INTO Notificado (Noticia_idNoticia,Usuario_idUsuario) VALUES (\''+str(j[0])+'\',\''+str(idusuario)+'\');'
                    try:
                        cursor.execute(sql)
                        db.commit()
                    except:
                        None
                db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class setNotificacion:
    #Actualiza la lectura de una notificacion
    def POST(self):
        #curl -d "idusuario=1&idnoticia=1" http://192.168.120.80:8888/notificacion
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'notificacion')
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacion',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        idnoticia = web.input('idnoticia').idnoticia
        db=None
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."

        if db is not None:
            cursor=db.cursor()
            sql='INSERT INTO Notificado (Noticia_idNoticia,Usuario_idUsuario) VALUES (\''+str(idnoticia)+'\',\''+str(idusuario)+'\');'
            cursor.execute(sql)
            db.commit()
            db.close()
        '''
        Analizador.notificacionLeida(idnoticia, idusuario)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'notificacionesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class actualizarperfil:#YA
    #Actualiza el perfil del usuario
    def POST(self):
        #curl -d "idusuario=1&nombre=juan amaya&email=jpamayag@gmail.com&profesion=vago profesional" http://192.168.120.80:8888/persona
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'actualizarPerfil')
        mbeanHelper.changeAttribute(mbeanName,resName,'actualizarPerfil',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        nombre = web.input('nombre').nombre
        nombre = nombre.replace("\"","\\\\\"")
        email = web.input('email').email
        email = email.replace("\"","\\\\\"")
        profesion = web.input('profesion').profesion
        profesion = profesion.replace("\"","\\\\\"")
        db=None
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='UPDATE Usuario SET Nombres=\''+nombre+'\',Email=\''+email+'\' WHERE idUsuario='+str(idusuario)+';'
            cursor.execute(sql)
            db.commit()
            '''
            sql='SELECT Profesion.Nombre FROM Usuario,Profesion,Usuario_has_Profesion WHERE Usuario_idUsuario='+str(idusuario)+' AND Usuario.idUsuario=Usuario_has_Profesion.Usuario_idUsuario AND Usuario_has_Profesion.Profesion_idProfesion=Profesion.idProfesion;'
            cursor.execute(sql)
            hay=cursor.rowcount

            sql='UPDATE Profesion SET Nombres=\''+nombre+'\', Profesion=\''+profesion+'\',Email=\''+email+'\' WHERE idUsuario='+str(idusuario)+';'
            cursor.execute(sql)
            db.commit()
            '''
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'actualizarPerfilTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class perfil:#YA
    #Consulta los datos de un usuario
    def GET(self,args):
        #print web.ctx.environ
        #http://192.168.120.80:8888/persona/?idusuario=1
        db=None
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName,resName,'perfil')
        mbeanHelper.changeAttribute(mbeanName,resName,'perfil',conteo.intValue()+1)
        #mbeanHelper.sendNotification('gestv.error.testerror', 'prueba de notificacion de error')
        idusuario = web.input('idusuario').idusuario
        try:
            db=MySQLdb.connect(host=getIpdb(),user=getLogindb(),passwd=getPwddb(),db=getDbname())
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No pudo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            #sql='SELECT Usuario.Nombres, Usuario.Email, Usuario.Profesion, Usuario.Foto FROM Usuario WHERE idUsuario='+str(idusuario)+';'
            sql='SELECT Usuario.Nombres, Usuario.Email, Profesion.Nombre, Usuario.Foto FROM Usuario,Profesion,Usuario_has_Profesion WHERE idUsuario='+str(idusuario)+' AND Usuario.idUsuario=Usuario_has_Profesion.Usuario_idUsuario AND Usuario_has_Profesion.Profesion_idProfesion=Profesion.idProfesion;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"nombre\" : \"'+i[0]+'\", '
                cadena+='\"correo\" : \"'+str(i[1])+'\", '
                if i[2] is None:
                    cadena+='\"profesion\" : \"\", '
                else:
                    cadena+='\"profesion\" : \"'+i[2]+'\", '
                #print str(i[3]).strip()
                if str(i[3]).strip() is None or str(i[3]).strip() is '':
                    cadena+='\"foto\" : \"\"'
                else:
                    cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(i[3]).strip()+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'perfilTime',str((end-start).total_seconds()))
        mbeanHelper.changeAttributes(mbeanName,resName,'perfil',conteo.intValue()+1,'perfilTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"perfil\" : ['+cadena+']}'

class busquedapersonas:#YA
    #Consulta la lista de usuarios en base a una palabra clave y adiciona la informacion de membresia
    def GET(self, args):
        #http://192.168.120.80:8888/personas/?idcomunidad=1&key=este
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName,resName,'busquedaPersonas')
        mbeanHelper.changeAttribute(mbeanName,resName,'busquedaPersonas',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        key = web.input('key').key
        key = key.replace("%"," ")
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Usuario.idUsuario, Usuario.Nombres, Usuario_has_Comunidad.Comunidad_idComunidad FROM Usuario LEFT JOIN Usuario_has_Comunidad ON Usuario_has_Comunidad.Comunidad_idComunidad='+idcomunidad+' AND Usuario_has_Comunidad.Usuario_idUsuario=Usuario.idUsuario WHERE Usuario.Nombres LIKE \'%'+key+'%\' OR Usuario.Email LIKE \'%'+key+'%\' ORDER BY Usuario_has_Comunidad.Comunidad_idComunidad ASC, Usuario.Nombres ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            #numrows=cursor.rowcount
            #print str(numrows)
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"nombre\" : \"'+i[1]+'\", '
                if i[2] is None:
                    cadena+='\"miembro\" : \"no\"'
                else:
                    cadena+='\"miembro\" : \"si\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'busquedaPersonasTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"personas\" : ['+cadena+']}'

class miembros:#YA
    #Consulta la lista de usuarios de una comunidad
    def GET(self, args):
        #http://192.168.120.80:8888/miembros/?idcomunidad=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'miembros')
        mbeanHelper.changeAttribute(mbeanName,resName,'miembros',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Usuario.idUsuario, Usuario.Nombres FROM Usuario,Usuario_has_Comunidad WHERE Usuario_has_Comunidad.Comunidad_idComunidad='+idcomunidad+' AND Usuario_has_Comunidad.Usuario_idUsuario=Usuario.idUsuario ORDER BY Usuario_has_Comunidad.Comunidad_idComunidad ASC, Usuario.Nombres ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"nombre\" : \"'+i[1]+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'miembrosTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"miembros\" : ['+cadena+']}'

class chatpost:#YA
    #Publica un mensaje en la sala de chat de una comunidad
    def POST(self):
        #curl -d "idusuario=1&idcomunidad=1&mensaje=hola a todos como estan" http://192.168.120.80:8888/chat
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'chatPost')
        mbeanHelper.changeAttribute(mbeanName,resName,'chatPost',conteo.intValue()+1)

        mensaje = web.input('mensaje').mensaje
        mensaje = mensaje.replace("\"","\\\\\"")
        #print mensaje
        mensaje=mensaje.strip('&')
        idcomunidad = web.input('idcomunidad').idcomunidad
        idusu = web.input('idusuario').idusuario
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='INSERT INTO Chat (Comunidad_idComunidad,Mensaje,Usuario_idUsuario) VALUES (\''+str(idcomunidad)+'\',\''+mensaje+'\',\''+str(idusu)+'\');'
            cursor.execute(sql)
            db.commit()
            db.close()
        #web.header('Content-Type', 'application/json')
        '''
        Analizador.nuevoMensajeChat(idcomunidad, idusu)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'chatPostTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class chat:#YA
    #Consulta los nuevos mensajes de una sala de chat de una comunidad
    def GET(self, args):
        #http://192.168.120.80:8888/chat/?idcomunidad=1&desdeid=0
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'chat')
        mbeanHelper.changeAttribute(mbeanName,resName,'chat',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        desdeid = web.input('desdeid').desdeid
        nummax=20
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            fechaactual=time.strftime("%Y-%m-%d")
            sql='SELECT * FROM (SELECT Chat.idChat,Chat.Mensaje,Chat.Estampa,Usuario.Nombres,Usuario.Foto FROM Chat,Usuario WHERE Chat.Comunidad_idComunidad='+str(idcomunidad)+' AND Usuario.idUsuario=Chat.Usuario_idUsuario AND Chat.idChat>'+str(desdeid)+' AND Chat.Estampa>\''+fechaactual+'\' ORDER BY Chat.Estampa DESC LIMIT '+str(nummax)+') AS tbl ORDER BY tbl.Estampa ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"mensaje\" : \"'+i[1]+'\", '
                cadena+='\"estampa\" : \"'+str(i[2])+'\", '
                cadena+='\"usuario\" : \"'+i[3]+'\", '
                if str(i[4]).strip() is None or str(i[4]).strip() is '':
                    cadena+='\"foto\" : \"\"'
                else:
                    cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(i[4]).strip()+'\"'

                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'chatTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"chat\" : ['+cadena+']}'
            #return '{\"chat\" : \"eduardo\" }'

class tabloncomentariopost:#YA
    #Crea un comentario a un mensaje del tablon
    def POST(self):
        #curl -d "idusuario=1&idtablon=1&mensaje=aqui no hay comunidad" http://192.168.120.80:8888/tablon/comentario
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablonComentarioPost')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentarioPost',conteo.intValue()+1)

        mensaje = web.input('mensaje').mensaje
        mensaje = mensaje.replace("\"","\\\\\"")
        mensaje=mensaje.strip('&')
        idtablon = web.input('idtablon').idtablon
        idusu = web.input('idusuario').idusuario
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='INSERT INTO Comentario_Tablon (Tablon_idTablon,Mensaje,Usuario_idUsuario) VALUES (\''+str(idtablon)+'\',\''+mensaje+'\',\''+str(idusu)+'\');'
            cursor.execute(sql)
            db.commit()
            sql='SELECT LAST_INSERT_ID();'
            cursor.execute(sql)
            idcomentario=cursor.fetchall()[0][0]
            sql='SELECT Comunidad_idComunidad FROM Tablon WHERE idTablon='+idtablon+';'
            print sql
            cursor.execute(sql)
            idcomunidad=cursor.fetchall()[0][0]
            sql='INSERT INTO Noticia (Comunidad_idComunidad,Tipo_Noticia_idTipo_Noticia,Id_notificacion) VALUES ('+str(idcomunidad)+',3,'+str(idcomentario)+');'
            cursor.execute(sql)
            db.commit()
            db.close()
        #web.header('Content-Type', 'application/json')
        '''
        Analizador.nuevoComentarioTablon(idcomunidad, idusu)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentarioPostTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class tabloncomentario:#YA
    #Consulta los comentarios de un mensaje del tablon
    def GET(self, args):
        #http://192.168.120.80:8888/tablon/comentario/?idtablon=1&desdeid=0
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablonComentario')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentario',conteo.intValue()+1)

        idtablon = web.input('idtablon').idtablon
        desdeid = web.input('desdeid').desdeid
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT * FROM (SELECT Comentario_Tablon.idComentario_Tablon,Comentario_Tablon.mensaje,Comentario_Tablon.estampa,Usuario.Nombres FROM Comentario_Tablon,Usuario WHERE Comentario_Tablon.Tablon_idTablon='+str(idtablon)+' AND Usuario.idUsuario=Comentario_Tablon.Usuario_idUsuario AND Comentario_Tablon.idComentario_Tablon>'+str(desdeid)+' ORDER BY Comentario_Tablon.Estampa DESC ) AS tbl ORDER BY tbl.Estampa ASC;'
            print sql
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"mensaje\" : \"'+i[1]+'\", '
                cadena+='\"estampa\" : \"'+str(i[2])+'\", '
                cadena+='\"usuario\" : \"'+i[3]+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentarioTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"comentariosTablon\" : ['+cadena+']}'

class tabloncomentarios:#YA
    #Consulta el numero de comentarios del servicio tablon
    def GET(self, args):
        #http://192.168.120.80:8888/tablon/comentarios/?idcomunidad=1&desdeid=0&hastaid=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablonComentarios')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentarios',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        desdeid = web.input('desdeid').desdeid
        hastaid = web.input('hastaid').hastaid
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Tablon.idTablon,COUNT(Comentario_Tablon.Tablon_idTablon) FROM Tablon LEFT JOIN Comentario_Tablon ON Comentario_Tablon.Tablon_idTablon=Tablon.idTablon WHERE Tablon.idTablon>='+str(desdeid)+' AND Tablon.idTablon<='+str(hastaid)+' AND Tablon.Comunidad_idComunidad='+str(idcomunidad)+' GROUP BY Tablon.idTablon ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"comentarios\" : \"'+str(i[1])+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonComentariosTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"tablon\" : ['+cadena+']}'

class tablonpost:#YA
    #Crea un nuevo mensaje de un usuario a una comunidad en el tablon
    def POST(self):
        #curl -d "idusuario=1&idcomunidad=1&mensaje=aqui no hay comunidad" http://192.168.120.80:8888/tablon
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablonPost')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonPost',conteo.intValue()+1)

        #hora1 = datetime.today()
        mensaje = web.input('mensaje').mensaje
        mensaje = mensaje.replace("\"","\\\\\"")
        mensaje=mensaje.strip('&')
        idcom = web.input('idcomunidad').idcomunidad
        idusu = web.input('idusuario').idusuario
        #print mensaje
        #print idcom
        #print idusu
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='INSERT INTO Tablon (Comunidad_idComunidad,Mensaje,Usuario_idUsuario) VALUES (\''+idcom+'\',\''+mensaje+'\',\''+idusu+'\');'
            cursor.execute(sql)
            db.commit()
            sql='SELECT LAST_INSERT_ID();'
            cursor.execute(sql)
            idtablon=cursor.fetchall()[0][0]
            sql='INSERT INTO Noticia (Comunidad_idComunidad,Tipo_Noticia_idTipo_Noticia,Id_notificacion) VALUES ('+str(idcom)+',2,'+str(idtablon)+');'
            cursor.execute(sql)
            db.commit()
            db.close()
        #hora2 = datetime.today()
        #print hora2-hora1
        #web.header('Content-Type', 'application/json')
        '''
        Analizador.nuevoMensajeTablon(idcom, idusu)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonPostTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class comentarioMensaje:#YA
    #Consulta un mensaje del servicio tablon-comentarios
    def GET(self, args):
        #http://192.168.120.80:8888/comentarioMensaje/?idmensaje=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'comentarioMensaje')
        mbeanHelper.changeAttribute(mbeanName,resName,'comentarioMensaje',conteo.intValue()+1)

        idmensaje = web.input('idmensaje').idmensaje
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Tablon.idTablon,Tablon.Mensaje,Tablon.Estampa,Usuario.Nombres,Usuario.Foto FROM Comentario_Tablon,Tablon,Usuario WHERE Comentario_Tablon.idComentario_Tablon='+str(idmensaje)+' AND Usuario.idUsuario=Tablon.Usuario_idUsuario AND Comentario_Tablon.Tablon_idTablon=Tablon.idTablon;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"mensaje\" : \"'+str(i[1])+'\", '
                cadena+='\"estampa\" : \"'+str(i[2])+'\", '
                cadena+='\"usuario\" : \"'+i[3]+'\", '
                if str(i[4]).strip() is None or str(i[4]).strip() is '':
                    cadena+='\"foto\" : \"\"'
                else:
                    cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(i[4]).strip()+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        #print cadena
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'comentarioMensajeTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"mensaje\" : ['+cadena+']}'

class tablonMensaje:#YA
    #Consulta un mensaje del servicio tablon
    def GET(self, args):
        #http://192.168.120.80:8888/tablonMensaje/?idmensaje=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablonMensaje')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonMensaje',conteo.intValue()+1)

        idmensaje = web.input('idmensaje').idmensaje
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Tablon.Mensaje,Tablon.Estampa,Usuario.Nombres,Usuario.Foto FROM Tablon,Usuario WHERE Tablon.idTablon='+str(idmensaje)+' AND Usuario.idUsuario=Tablon.Usuario_idUsuario;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(idmensaje)+'\", '
                cadena+='\"mensaje\" : \"'+i[0]+'\", '
                cadena+='\"estampa\" : \"'+str(i[1])+'\", '
                cadena+='\"usuario\" : \"'+i[2]+'\", '
                if str(i[3]).strip() is None or str(i[3]).strip() is '':
                    cadena+='\"foto\" : \"\"'
                else:
                    cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(i[3]).strip()+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        #print cadena
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonMensajeTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"mensaje\" : ['+cadena+']}'

class tablon:#YA
    #Consulta los mensajes del servicio tablon
    def GET(self, args):
        #http://192.168.120.80:8888/tablon/?idcomunidad=1&desdeid=0
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'tablon')
        mbeanHelper.changeAttribute(mbeanName,resName,'tablon',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        desdeid = web.input('desdeid').desdeid
        nummax=12
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT * FROM (SELECT Tablon.idTablon,Tablon.Mensaje,Tablon.Estampa,Usuario.Nombres,Usuario.Foto FROM Tablon,Usuario WHERE Tablon.Comunidad_idComunidad='+str(idcomunidad)+' AND Usuario.idUsuario=Tablon.Usuario_idUsuario AND Tablon.idTablon>'+str(desdeid)+' ORDER BY Tablon.Estampa DESC LIMIT '+str(nummax)+') AS tbl ORDER BY tbl.Estampa ASC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"mensaje\" : \"'+i[1]+'\", '
                cadena+='\"estampa\" : \"'+str(i[2])+'\", '
                cadena+='\"usuario\" : \"'+i[3]+'\", '
                if str(i[4]).strip() is None or str(i[4]).strip() is '':
                    cadena+='\"foto\" : \"\"'
                else:
                    cadena+='\"foto\" : \"'+'http://'+config.dirip+'/Images/'+str(i[4]).strip()+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        #print cadena
        '''
        if desdeid==0:
            Analizador.ingresoUsuario(idcomunidad, idU)
            Analizador.llenarTablaComunidad(idcomunidad)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'tablonTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else:
                return '{\"tablon\" : ['+cadena+']}'

class epgtop:#YA
    #Consulta los programas mas votados
    def GET(self,id):
        #http://192.168.120.80:8888/epg/top/1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'epgTop')
        mbeanHelper.changeAttribute(mbeanName,resName,'epgTop',conteo.intValue()+1)

        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT SUM(Votacion.Respuesta)/COUNT(Votacion.Valoracion_idValoracion),Programa.idPrograma, Programa.Nombre, Programa.Descripcion,DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia, Preferencias_Programas.Favorito, Preferencias_Programas.Recordatorio FROM Evento,Valoracion,Votacion,Programa LEFT JOIN Preferencias_Programas ON Preferencias_Programas.Programa_idPrograma=Programa.idPrograma AND Preferencias_Programas.Usuario_idUsuario='+id+' WHERE Valoracion.Evento_idEvento=Evento.idEvento AND Evento.Programa_idPrograma=Programa.idPrograma AND Votacion.Valoracion_idValoracion=Valoracion.idValoracion GROUP BY Programa.idPrograma ORDER BY SUM(Votacion.Respuesta)/COUNT(Votacion.Valoracion_idValoracion) DESC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            #numrows=cursor.rowcount
            #print str(numrows)
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"votos\" : \"'+str(i[0])+'\", '
                cadena+='\"id\" : \"'+str(i[1])+'\", '
                cadena+='\"Nombre\" : \"'+i[2]+'\", '
                cadena+='\"Descripcion\" : \"'+i[3]+'\", '
                hora=str(i[4])
                cadena+='\"Hora\" : \"'+hora+'\", '
                cadena+='\"Dia\" : \"'+str(i[5])+'\", '
                if i[6] is None:
                    cadena+='\"Favorito\" : \"\", '
                else:
                    cadena+='\"Favorito\" : \"'+str(i[6])+'\", '
                if i[7] is None:
                    cadena+='\"Recordatorio\" : \"\"'
                else:
                    cadena+='\"Recordatorio\" : \"'+str(i[7])+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'epgTopTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"programas_top\" : ['+cadena+']}'

class epgfavoritos:#YA
    #Consulta los programas favoritos de un usuario
    def GET(self,id):
        #http://192.168.120.80:8888/epg/favoritos/1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'epgFavoritos')
        mbeanHelper.changeAttribute(mbeanName,resName,'epgFavoritos',conteo.intValue()+1)

        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia, Preferencias_Programas.Recordatorio FROM Programa,Preferencias_Programas WHERE Preferencias_Programas.Programa_idPrograma=Programa.idPrograma AND Preferencias_Programas.Usuario_idUsuario='+id+' AND Preferencias_Programas.Favorito=1 ORDER BY Programa.Dia, Programa.Hora;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"Nombre\" : \"'+i[1]+'\", '
                cadena+='\"Descripcion\" : \"'+i[2]+'\", '
                hora=str(i[3])
                cadena+='\"Hora\" : \"'+hora+'\", '
                cadena+='\"Dia\" : \"'+str(i[4])+'\", '
                if i[5] is None:
                    cadena+='\"Recordatorio\" : \"\"'
                else:
                    cadena+='\"Recordatorio\" : \"'+str(i[5])+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'epgFavoritosTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"programas_busqueda\" : ['+cadena+']}'

class epgbusqueda:#YA
    #Consulta la programacion en base a una palabra clave y adiciona las preferencias del usuario
    def GET(self, args):
        #http://192.168.120.80:8888/epg/busqueda/?id=1&key=este
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'epgBusqueda')
        mbeanHelper.changeAttribute(mbeanName,resName,'epgBusqueda',conteo.intValue()+1)

        id = web.input('id').id
        key = web.input('key').key
        key = key.replace("%"," ")
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia, Preferencias_Programas.Favorito, Preferencias_Programas.Recordatorio FROM Programa LEFT JOIN Preferencias_Programas ON Preferencias_Programas.Programa_idPrograma=Programa.idPrograma AND Preferencias_Programas.Usuario_idUsuario='+id+' WHERE Programa.Nombre LIKE \'%'+key+'%\' OR Programa.Descripcion LIKE \'%'+key+'%\' ORDER BY Programa.Dia, Programa.Hora;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"Nombre\" : \"'+i[1]+'\", '
                cadena+='\"Descripcion\" : \"'+i[2]+'\", '
                hora=str(i[3])
                cadena+='\"Hora\" : \"'+hora+'\", '
                cadena+='\"Dia\" : \"'+str(i[4])+'\", '
                if i[5] is None:
                    cadena+='\"Favorito\" : \"\", '
                else:
                    cadena+='\"Favorito\" : \"'+str(i[5])+'\", '
                if i[6] is None:
                    cadena+='\"Recordatorio\" : \"\"'
                else:
                    cadena+='\"Recordatorio\" : \"'+str(i[6])+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'epgBusquedaTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"busqueda\" : ['+cadena+']}'

class infoasociada:#YA
    #Consulta la informacion asociada a un programa
    def GET(self, id):
        #http://192.168.120.80:8888/infoAsociada/1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'infoAsociada')
        mbeanHelper.changeAttribute(mbeanName,resName,'infoAsociada',conteo.intValue()+1)

        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Texto,Duracion FROM Info_Asociada WHERE Info_Asociada.idInfo_Asociada='+id+';'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            hay=cursor.rowcount
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'infoAsociadaTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if hay > 0:
                info=resultado[0]
                web.header('Content-Type', 'application/json')
                '''
                Analizador.lecturaInfoAsociada(id)
                '''
                return '{\"id\" : \"'+id+'\" , \"texto\" : \"'+info[0]+'\" , \"duracion\" : \"'+str(info[1])+'\"}\n'
            else :
                return ''


class voto:#YA
    #Realiza la votacion de un usuario a un programa
    def POST(self):
        #curl -d "idencuesta=1&voto=1" http://192.168.120.80:8888/votacion
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'voto')
        mbeanHelper.changeAttribute(mbeanName,resName,'voto',conteo.intValue()+1)

        i = web.input('voto').voto
        idenc = web.input('idencuesta').idencuesta
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='INSERT INTO Votacion (Valoracion_idValoracion,Respuesta) VALUES ('+idenc+',\''+i+'\');'
            cursor.execute(sql)
            db.commit()
            db.close()
        #web.header('Content-Type', 'application/json')
        '''
        Analizador.nuevoVoto(idenc)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'votoTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class valida:#YA
    #Realiza la validacion de un usuario en el sistema
    def GET(self,args):
        #http://192.168.120.80:8888/validacion/?login=luke&password=jaja
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName, 'valida')
        mbeanHelper.changeAttribute(mbeanName,resName,'valida',conteo.intValue()+1)

        login = web.input('login').login
        passwd = web.input('password').password
        #login=raw_input("l: ")
        #passwd=raw_input("p: ")
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Usuario.idUsuario,Usuario.Nombres,Usuario.Email,Profesion.Nombre,Usuario.Foto FROM Usuario,Profesion,Usuario_has_Profesion WHERE Login=\''+login+'\' AND Pwd=\''+passwd+'\' AND Usuario.idUsuario=Usuario_has_Profesion.Usuario_idUsuario AND Usuario_has_Profesion.Profesion_idProfesion=Profesion.idProfesion;'
            cursor.execute(sql)
            numrows=cursor.rowcount
            if numrows > 0 :
                resultado=cursor.fetchall()[0]
                if resultado[2] is None:
                    email=''
                else:
                    email=resultado[2]
                if resultado[3] is None:
                    prof=''
                else:
                    prof=resultado[3]
                if str(resultado[4]).strip() is None or str(resultado[4]).strip() is '':
                    foto=''
                else:
                    foto='http://'+config.dirip+'/Images/'+str(resultado[4]).strip()
                retorno='{\"exito\" : \"Si\" , \"id\" : \"'+str(resultado[0])+'\" , \"Nombre\" : \"'+str(resultado[1])+'\" , \"Email\" : \"'+str(email)+'\" , \"Profesion\" : \"'+str(prof)+'\" , \"foto\" : \"'+str(foto)+'\"}'
            else :
                retorno='{\"exito\" : \"No\"}'
            db.close()
        '''
        Analizador.actualizarComunidades()
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'validaTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return retorno



class miembroscomunidad:#YA
    #Consulta la lista de miembros de una comunidad
    def GET(self,args):
        #http://192.168.120.80:8888/comunidad/miembros/?idcomunidad=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'miembrosComunidad')
        mbeanHelper.changeAttribute(mbeanName,resName,'miembrosComunidad',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Usuario.idUsuario,Usuario.Nombres FROM Comunidad,Usuario,Usuario_has_Comunidad WHERE Comunidad.idComunidad='+idcomunidad+' AND Usuario_has_Comunidad.Comunidad_idComunidad=Comunidad.idComunidad AND Usuario_has_Comunidad.Usuario_idUsuario=Usuario.idUsuario ORDER BY Usuario_has_Comunidad.Rol DESC;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\" , '
                cadena+='\"nombre\" : \"'+str(i[1])+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        #retorno='{\"exito\" : \"Si\" , \"id\" : \"'+str(resultado[0])+'\" , \"Nombre\" : \"'+resultado[1]+' '+resultado[2]+'\" , \"foto\" : \"'+resultado[3]+'\"}'
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'miembrosComunidadTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"comunidad\" : ['+cadena+']}'

class comunidad:#YA
    #Consulta los datos de una comunidad
    def GET(self,args):
        #http://192.168.120.80:8888/comunidad/?idcomunidad=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'comunidad')
        mbeanHelper.changeAttribute(mbeanName,resName,'comunidad',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Comunidad.Nombre,Comunidad.Descripcion,Comunidad.Tematica,Usuario.Nombres FROM Comunidad,Usuario,Usuario_has_Comunidad WHERE Comunidad.idComunidad='+str(idcomunidad)+' AND Usuario_has_Comunidad.Rol=\'Coordinador\' AND Usuario_has_Comunidad.Comunidad_idComunidad=Comunidad.idComunidad AND Usuario_has_Comunidad.Usuario_idUsuario=Usuario.idUsuario;'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"nombre\" : \"'+i[0]+'\", '
                cadena+='\"descripcion\" : \"'+i[1]+'\", '
                cadena+='\"tematica\" : \"'+i[2]+'\", '
                cadena+='\"creador\" : \"'+i[3]+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        #retorno='{\"exito\" : \"Si\" , \"id\" : \"'+str(resultado[0])+'\" , \"Nombre\" : \"'+resultado[1]+' '+resultado[2]+'\" , \"foto\" : \"'+resultado[3]+'\"}'
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'comunidadTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"comunidad\" : ['+cadena+']}'

class comunidades:#YA
    #Consulta las comunidades a las que pertenece un usuario
    def GET(self,args):
        #http://192.168.120.80:8888/comunidades/usuario/?idusuario=1
        global idU
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'comunidades')
        mbeanHelper.changeAttribute(mbeanName,resName,'comunidades',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:
            cursor=db.cursor()
            sql='SELECT Comunidad.idComunidad,Comunidad.Nombre from Comunidad,Usuario_has_Comunidad WHERE Comunidad.idComunidad=Usuario_has_Comunidad.Comunidad_idComunidad AND Usuario_has_Comunidad.Usuario_idUsuario='+idusuario+';'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"nombre\" : \"'+i[1]+'\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        idU=idusuario
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'comunidadesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"comunidades\" : ['+cadena+']}'

class busquedacomunidades:#YA
    #Consulta las comunidades existentes en base a una palabra clave y adiciona el dato de pertenencia del usuario a la comunidad
    def GET(self,args):
        #http://192.168.120.80:8888/comunidades/?idusuario=2&key=com
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'busquedaComunidades')
        mbeanHelper.changeAttribute(mbeanName,resName,'busquedaComunidades',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        key = web.input('key').key
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT Comunidad.idComunidad,Comunidad.Nombre,Usuario_has_Comunidad.Usuario_idUsuario FROM Comunidad LEFT JOIN Usuario_has_Comunidad ON Comunidad.idComunidad=Usuario_has_Comunidad.Comunidad_idComunidad AND Usuario_has_Comunidad.Usuario_idUsuario='+str(idusuario)+' WHERE Comunidad.Nombre LIKE \'%'+key+'%\';'
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''
            for i in resultado:
                cadena+='{'
                cadena+='\"id\" : \"'+str(i[0])+'\", '
                cadena+='\"nombre\" : \"'+i[1]+'\", '
                if i[2] is None:
                    cadena+='\"estado\" : \"alta\"'
                else:
                    cadena+='\"estado\" : \"baja\"'
                cadena+='},'
            cadena=cadena.rstrip(',')
            db.close()
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'busquedaComunidadesTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            if len(cadena) == 0 :
                return ''
            else :
                return '{\"busqueda\" : ['+cadena+']}'

class regcomunidad:#YA
    #Da de alta o baja un usuario de una comunidad
    def POST(self):
        #curl -d "idusuario=1&idcomunidad=1&estado=alta" http://192.168.120.80:8888/comunidad/registro
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'regComunidad')
        mbeanHelper.changeAttribute(mbeanName,resName,'regComunidad',conteo.intValue()+1)

        idcomunidad = web.input('idcomunidad').idcomunidad
        idusu = web.input('idusuario').idusuario
        estado = web.input('estado').estado
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql=''
            if estado in 'alta':
                sql='INSERT INTO Usuario_has_Comunidad (Usuario_idUsuario,Comunidad_idComunidad,Rol) VALUES ('+str(idusu)+','+str(idcomunidad)+',\'Miembro\');'
            else :
                sql='DELETE FROM Usuario_has_Comunidad WHERE Usuario_has_Comunidad.Comunidad_idComunidad='+str(idcomunidad)+' AND Usuario_has_Comunidad.Usuario_idUsuario='+str(idusu)+';'
            cursor.execute(sql)
            db.commit()
            db.close()
        #web.header('Content-Type', 'application/json')
        '''
        Analizador.usuariosRegistrados(idcomunidad, idusu, estado)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'regComunidadTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class programacion:#YA
    #Consulta la programacion de la semana para uno o todos los dias y aï¿½ade los datos de preferencias del usuario
    def GET(self,args):
        #http://192.168.120.80:8888/programacion/?idusuario=1&dia=1
        #http://192.168.120.80:8888/programacion/?idusuario=todos&dia=1
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'programacion')
        mbeanHelper.changeAttribute(mbeanName,resName,'programacion',conteo.intValue()+1)

        idusuario = web.input('idusuario').idusuario
        dia = web.input('dia').dia
        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            if 'todos' in idusuario:
                if 'todos' in dia:
                    sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia FROM Programa WHERE Programa.Dia<>\'0\' ORDER BY Programa.Hora;'
                else:
                    sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia FROM Programa WHERE Programa.Dia=\''+dia+'\' ORDER BY Programa.Hora;'
            else:
                if 'todos' in dia:
                    sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia, Preferencias_Programas.Favorito, Preferencias_Programas.Recordatorio FROM Programa LEFT JOIN Preferencias_Programas ON Preferencias_Programas.Programa_idPrograma=Programa.idPrograma AND Preferencias_Programas.Usuario_idUsuario='+idusuario+' WHERE Programa.Dia<>\'0\' ORDER BY Programa.Dia, Programa.Hora;'
                else:
                    sql='SELECT Programa.idPrograma, Programa.Nombre, Programa.Descripcion, DATE_FORMAT(Programa.Hora,\'%H:%i:%s\') as Hora, Programa.Dia, Preferencias_Programas.Favorito, Preferencias_Programas.Recordatorio FROM Programa LEFT JOIN Preferencias_Programas ON Preferencias_Programas.Programa_idPrograma=Programa.idPrograma AND Preferencias_Programas.Usuario_idUsuario='+idusuario+' WHERE Programa.Dia=\''+dia+'\' ORDER BY Programa.Hora;'
            #print sql
            cursor.execute(sql)
            resultado=cursor.fetchall()
            cadena=''

            if 'todos' in idusuario:
                for i in resultado:
                    cadena+='{'
                    cadena+='\"id\" : \"'+str(i[0])+'\", '
                    cadena+='\"Nombre\" : \"'+i[1]+'\", '
                    cadena+='\"Descripcion\" : \"'+i[2]+'\", '
                    hora=str(i[3])
                    cadena+='\"Hora\" : \"'+hora+'\", '
                    cadena+='\"Dia\" : \"'+str(i[4])+'\"'
                    cadena+='},'
            else:
                for i in resultado:
                    cadena+='{'
                    cadena+='\"id\" : \"'+str(i[0])+'\", '
                    cadena+='\"Nombre\" : \"'+i[1]+'\", '
                    cadena+='\"Descripcion\" : \"'+i[2]+'\", '
                    hora=str(i[3])
                    cadena+='\"Hora\" : \"'+hora+'\", '
                    cadena+='\"Dia\" : \"'+str(i[4])+'\", '
                    if i[5] is None:
                        cadena+='\"Favorito\" : \"\", '
                    else:
                        cadena+='\"Favorito\" : \"'+str(i[5])+'\", '
                    if i[6] is None:
                        cadena+='\"Recordatorio\" : \"\"'
                    else:
                        cadena+='\"Recordatorio\" : \"'+str(i[6])+'\"'
                    cadena+='},'
            cadena=cadena.rstrip(',')
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'programacionTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{\"programas\" : ['+cadena+']}'

class preferencias:#YA
    #Actualiza o crea preferencias (favorito,recordatorio) del usuario sobre un programa
    def POST(self):
        #curl -d "idusuario=1&idprograma=1&favorito=0" http://192.168.120.80:8888/preferencias
        #curl -d "idusuario=1&idprograma=1&recordado=1" http://192.168.120.80:8888/preferencias
        start = datetime.now()
        conteo=mbeanHelper.getAttribute(mbeanName, resName,'preferencias')
        mbeanHelper.changeAttribute(mbeanName,resName,'preferencias',conteo.intValue()+1)

        fav=''
        rec=''
        user_data = web.input()
        if 'favorito' in user_data:
            fav = web.input('favorito').favorito
        if 'recordado' in user_data:
            rec = web.input('recordado').recordado
        idusu = web.input('idusuario').idusuario
        idprog = web.input('idprograma').idprograma

        try:
            db=MySQLdb.connect(host=ipdb,user=logindb,passwd=pwddb,db=database)
        except OperationalError:
            mbeanHelper.sendNotification(mbeans[0],'gestv.error.databaseConnectionRefused', 'empty');
            print "Error: No puedo conectarse a la base de datos."
        if db is not None:

            cursor=db.cursor()
            sql='SELECT * FROM Preferencias_Programas WHERE Usuario_idUsuario='+idusu+' AND Programa_idPrograma='+idprog+';'
            cursor.execute(sql)
            hay=cursor.rowcount
            if hay > 0:
                if fav:
                    sql='UPDATE Preferencias_Programas SET Favorito='+fav+' WHERE Usuario_idUsuario='+idusu+' AND Programa_idPrograma='+idprog+';'
                if rec:
                    sql='UPDATE Preferencias_Programas SET Recordatorio='+rec+' WHERE Usuario_idUsuario='+idusu+' AND Programa_idPrograma='+idprog+';'
            else:
                if fav:
                    sql='INSERT INTO Preferencias_Programas (Usuario_idUsuario,Programa_idPrograma,Favorito,Recordatorio) VALUES ('+idusu+','+idprog+','+fav+',0);'
                if rec:
                    sql='INSERT INTO Preferencias_Programas (Usuario_idUsuario,Programa_idPrograma,Favorito,Recordatorio) VALUES ('+idusu+','+idprog+',0,'+rec+');'
            cursor.execute(sql)
            db.commit()
            db.close()
        '''
        Analizador.nuevoFavorito(idprog, idusu, fav)
        Analizador.nuevoRecordatorio(idprog, idusu, rec)
        '''
        end = datetime.now()
        mbeanHelper.changeAttribute(mbeanName,resName,'preferenciasTime',str((end-start).total_seconds()))
        if db is None:
            return 'Not Working'
        else:
            return '{"respuesta" : "OK"}'

class prueba1:
    def GET(self,args):
        time = web.input('time').time
        #return '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><html><head><script type="text/javascript"> function fSynchronousGet() { alert("dfa"); var xmlhttp = new XMLHttpRequest();  xmlhttp.open("GET", "http://192.168.1.114:8080/persona/?idusuario=1",true);   xmlhttp.onreadystatechange=function() { if (xmlhttp.readyState==4) { alert(xmlhttp.responseText) } } xmlhttp.send(null) } </script></head><body><h1>My First Web Page</h1><p id="demo">This is a paragraph.</p><button type="button" onclick="fSynchronousGet()">Consultar</button></body></html>'
        #return '<html><head><script type="text/javascript">function show_alert(){var xmlhttp=new XMLHttpRequest();xmlhttp.open("GET","http://192.168.1.114:8080/persona/?idusuario=1",true);xmlhttp.onreadystatechange=function(){ if(xmlhttp.readyState==4) { var respuesta = eval(\'(\' + xmlhttp.responseText + \')\');ja = \'<p>\'+respuesta.perfil[0].nombre +\'</p>\';ja+= \'<p>\'+respuesta.perfil[0].correo+\'</p>\';ja+= \'<p>\'+respuesta.perfil[0].profesion+\'</p>\';document.getElementById("demo").innerHTML=ja;}};xmlhttp.send(null);}</script></head><body><p id="demo">This is a paragraph.</p><input type="button" onclick="show_alert()" value="Show alert box" /></body></html>'
        #hello = web.template.frender('/home/stcav/workspace2/prueba1/p1.html')
        #return hello()

class consultar:
        def GET(self,args):
            #print 'llego'
            ruta=web.ctx.fullpath
            ruta2=ruta.replace('/consultar/', '')
            rutaclase=ruta2[:ruta2.index('/')]
            clase=eval(rutaclase)();
            ruta2=ruta2.replace(rutaclase+'/', '')
            #web.header('Content-Type', 'text/javascript')
            #print 'consultar('+clase.GET(ruta2)+');';
            return 'consultar('+clase.GET(ruta2)+');';

if MBeanHelper.instance is None :
    mbeanHelper = MBeanHelper('broadcaster',10001)
    MBeanHelper.instance = mbeanHelper
else:
    mbeanHelper = MBeanHelper.instance

mbeans=mbeanHelper.register([resName,configName],mbeanName)
app = MyApplication(urls, globals())
if __name__ == "__main__":
    fechaactual=time.strftime("%H:%M:%S %Y-%m-%d")
    mbeanHelper.changeAttribute(mbeanName,resName,'uptime', fechaactual)
    app.run(port=8888)
    mbeanHelper.shutdownJVM()