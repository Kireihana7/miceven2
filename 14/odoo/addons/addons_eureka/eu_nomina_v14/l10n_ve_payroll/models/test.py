import base64
import requests
from re import sub
from bs4 import BeautifulSoup
from datetime import datetime, timedelta,date
from odoo.modules.module import get_module_resource
TODAY=date.today()

def scrap_from_venezuela_workingdays(self):

    r = requests.get("https://venezuela.workingdays.org/mobile_home.php")

    data = r.text
    soup = BeautifulSoup(data, 'html.parser')

    div = soup.find("div", attrs={'id':'feries'})

    days = [sub("[^\w ]", "", day.text).split() for day in div.find_all('div', attrs={'style':'float:left;width:100%;'}) ]

    return(days)

def scrap_from_publicholidays_ve(self):
    
    year=TODAY.year
    r = requests.get("https://publicholidays.com.ve/es/"+str(year)+"-dates/")

    data = r.text
    soup = BeautifulSoup(data, 'html.parser')

    tbody = soup.find("tbody")

    days = [[td.text for td in day.find_all("td")] for day in tbody.find_all('tr')]
   

    return(days)

def scrap_from_BCV_Prestaciones(self):

    r = requests.get("http://www.bcv.org.ve/", verify=False)

    data = r.text
    soup = BeautifulSoup(data, 'html.parser')

    span = soup.find("span", attrs={'class':'views-field views-field-field-tasa-prestaciones-sociales'})

    text_tasa = span.find('span', attrs={'class':'field-content'}).text 

    return(text_tasa)


def code_talker():
    txtpath=get_module_resource('l10n_ve_payroll', 'static/config/', 'configurate.txt')
    with open(txtpath,'r') as txtfile:
        lines=txtfile.readlines()
    datacode={}
    for line in lines:
        separator=line.split(':')
        datacode[separator[0].strip()]=separator[1].strip()
    
    if eval(datacode.get('CODIFICATE',False)):
        if not eval(datacode.get('BASEENCODE',False)):
            return datacode.get('PWD',False).encode('ascii')
        else:

            base64_message = datacode.get('PWD','')
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            
            return message
    else:
        return False


def numero_to_letras(numero):

        indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero)*100))
        #print 'decimal : ',decimal 
        contador = 0
        numero_letras = ""
        while entero >0:
            a = entero % 1000
            if contador == 0:
                en_letras = convierte_cifra(a,1).strip()
            else :
                en_letras = convierte_cifra(a,0).strip()
            if a==0:
                numero_letras = en_letras+" "+numero_letras
            elif a==1:
                if contador in (1,3):
                    numero_letras = indicador[contador][0]+" "+numero_letras
                else:
                    numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        if decimal>0:
            extra=" con " + str(decimal) +"/100"
        else:
            extra=" exactos"
        numero_letras = numero_letras+extra
        # print 'numero: ',numero
        return numero_letras
 

def convierte_cifra(numero,sw):

    lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
    lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                    ("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                    ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                    ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                    ("NOVENTA" , "NOVENTA Y ")]

    lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
    centena = int (numero / 100)
    decena = int((numero -(centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
    #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

    texto_centena = ""
    texto_decena = ""
    texto_unidad = "" 

    #Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad)!=0:
            texto_centena = texto_centena[1]
        else :
            texto_centena = texto_centena[0] 

    #Valida las decenas

    texto_decena = lista_decena[decena]
    if decena == 1 :
         texto_decena = texto_decena[unidad]
    elif decena > 1 :
        if unidad != 0 :
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]

    #Validar las unidades
    #print "texto_unidad: ",texto_unidad

    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw] 

    return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)


