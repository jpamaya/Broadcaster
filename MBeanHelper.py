import jpype
from jpype import java, javax
import os.path

mbeanServer=None
dominio=None
puerto=None
mbeans=[]
mbnames=[]
type=None


class MBeanHelper():

    instance = None

    def __init__(self,domain,port):
        global dominio,puerto
        if MBeanHelper.instance is None:
            dominio=domain
            puerto=port
            #java.lang.System.setProperty("javafx.macosx.embedded", "true");
            #java.awt.Toolkit.getDefaultToolkit();
            self.startJVM()

    def startJVM(self):
        global mbeanServer,dominio,puerto
        print os.path.abspath('.')
        classpath = os.path.join(os.path.abspath('.'))
        print jpype.getDefaultJVMPath()
        jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.awt.headless=true',"-ea", "-Dvisualvm.display.name="+dominio+":"+str(puerto), "-Dcom.sun.management.jmxremote", "-Dcom.sun.management.jmxremote.port="+str(puerto), "-Dcom.sun.management.jmxremote.authenticate=false", "-Dcom.sun.management.jmxremote.ssl=false", "-Djava.class.path=simple-xml-2.6.9.jar:%s" % classpath)
        mbeanServer = java.lang.management.ManagementFactory.getPlatformMBeanServer();

    def register(self,noms,tipo):
        global dominio,mbnames,type,mbeans
        mbnames=noms
        type=tipo
        i=0;
        if len(mbeans) == 0:
            for name in mbnames:
                objectName = javax.management.ObjectName(dominio+":type="+type+",name="+name);
                DynamicMBeanFactory = jpype.JClass('mbean.DynamicMBeanFactory')
                str1=os.getcwd();
                mbean1 = DynamicMBeanFactory.getDynamicBean(dominio, name, type, str1, type, i);
                mbeans.append(mbean1)
                i=i+1
        return mbeans

    def unregister(self,tipo):
        global dominio,mbeanServer,mbnames,type
        for name in mbnames:
            objectName = javax.management.ObjectName(dominio+":type="+type+",name="+name);
            mbeanServer.unregisterMBean(objectName);

    def shutdownJVM(self):
        print 'Desconectando JVM'
        jpype.shutdownJVM()
        print 'Desconectada JVM'

    def changeAttribute(self,tipo,name,attribute,value):
        global mbeanServer,dominio,type
        objectName = javax.management.ObjectName(dominio+":type="+type+",name="+name);
        attr = javax.management.Attribute(attribute, value);
        mbeanServer.setAttribute(objectName, attr);

    def changeAttributes(self,tipo,name,attribute1,value1,attribute2,value2):
        global mbeanServer,dominio,type
        objectName = javax.management.ObjectName(dominio+":type="+type+",name="+name);
        attrlist = javax.management.AttributeList();
        attr1 = javax.management.Attribute(attribute1, value1);
        attr2 = javax.management.Attribute(attribute2, value2);
        attrlist.add(attr1);
        attrlist.add(attr2);
        mbeans[0].setAttributes(objectName, attrlist);

    def getAttribute(self,tipo,name,attribute):
        global mbeanServer,dominio,type
        objectName = javax.management.ObjectName(dominio+":type="+type+",name="+name);
        return mbeanServer.getAttribute(objectName,attribute)
        #return 0

    def sendNotification(self,mbean,tipo,message):
        global mbeanServer
        mbean.sendNotification(tipo, message);

'''
while True:
    print '\n************************ 1. Iniciar ************************\n'
    print '************************ 2. cambiar valor ************************\n'
    print '************************ 3. Cerrar ************************\n'
    command_line = raw_input()
    print command_line
    if "1" in command_line:
        startJVM()
    if "2" in command_line:
        changeAttribute('chat', 2)
    if "3" in command_line:
        shutdownJVM()
        os._exit(1)
'''