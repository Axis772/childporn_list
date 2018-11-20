#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Descripcion:      Realiza operaciones como descargar, checkear y bloquear
#                   dominos de los listado de coljuegos en MINTIC
# Fecha Creacion: 13 NOV 2018
#-----------------------------------------------------------------------------

#*****************************************************************************
# Library Load
#*****************************************************************************
import os
import subprocess
import time
import tldextract
import correo
#******************************************************************************

#******************************************************************************
# Global Variable
#******************************************************************************
PATH =  "/root/childporn_list/"
BIND_FILE = "/etc/bind/named.conf.redirect-childporn.zones"
# Variales con informacion de Acceso MIN TIC
User = "ArturoCuellar"
Pass = "ArturoCuellar6542"
URL_BASE = "http://archivo.mintic.gov.co/ubpi/620/w3-propertyvalue-7594.html"
Count_unblocked = 0
#******************************************************************************

#******************************************************************************
# Funtions
#******************************************************************************


def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


def get_output_cmd(cmd):
    out = os.popen(cmd).read().rstrip()
    return(out)


def get_link(url, pos):
    cmd = "lynx -accept_all_cookies " \
          "-auth=ArturoCuellar:ArturoCuellar6542 " \
          "-listonly -dump " + url + " | grep " + pos
    out = get_output_cmd(cmd)
    out = out.split(" ")[3].replace("'", "")
    return(out)


def get_mintic_link(url):
    url_temp = get_link(url, "18")
    return(url_temp)


def url2domain(url):
    urlparser = tldextract.extract(url)
    wildcard = urlparser.domain + '.' + urlparser.suffix
    return wildcard + '\n'


def check_ignoreDomain(domain):
    with open(PATH + 'ignoreDomain.txt') as dataf:
        for line in dataf:
            if domain in line:
               return True
               break
        return False


def domain2bindfile(domain):
    part1 = 'zone "'
    part2 = '"{\n\ttype master;\n\t'\
            'file "/etc/bind/redirect_childporn/' \
            'db.redirect_childporn.zone";\n\t' \
            'allow-query { any; };\n};\n\n'
    return part1 + domain + part2


def check_url_cmd(url):
    global Count_unblocked
    cmp_str = "<h1>Access Denied - by DNS BTLATAM</h1>"
    cmd = "curl -s '" + url + "' --insecure | egrep -i " \
          "'" + cmp_str + "'"
    access = get_output_cmd(cmd)
    if(access == cmp_str):
        pass
    else:
        print("Revisar blockeo de URL -> {}".format(url))
        Count_unblocked = Count_unblocked + 1


def download_list():
    """ Obtiene el listado de url a analizar
    """
    # Obtiene el link de descarga de listado actualizado
    URL_MINTIC = get_mintic_link(URL_BASE)
    #Checkea que el file exista y se pueda acceder
    cmd = "wget -SO- -T 1 -t 1 --spider --user=" + User + " --password=" \
          + Pass + " " + URL_MINTIC + " 2>&1 >/dev/null | " \
          "egrep -i '404|Authentication Fail'"
    check_list = get_output_cmd(cmd)
    if(check_list == ""):
        #Descarga el listado en formato txt de MINTIC
        cmd = "wget -q --user=" + User + " --password=" + Pass + \
              " --output-document=" + PATH + "listadoChild.txt " + \
              URL_MINTIC
        get_output_cmd(cmd)
        #Convierte la codificacion del archivo a UTF-8
        subprocess.call("iconv -f ISO-8859-1 -t UTF-8//TRANSLIT " + PATH + \
                        "listadoChild.txt -o " + PATH + \
                        "listadoChild_utf8.txt",
                        shell=True)
        return(True)
    elif (check_list == "Username/Password Authentication Failed."):
        print("ERROR: Usuario o Password fallaron!!!")
        return(False)
    else:
        print("ERROR: Cambios en URL de Listas en MINTIC!!")
        return(False)


def clean_files():
    """ Elimina los archivos temporales descargados y utilizaodos para
        la aplicacion
    """
    list = ["temp",
            "listadoChild_utf8.txt",
            "childporn_dominios.txt",
            "listadoChild.txt"]
    for file in list:
        if os.path.isfile(PATH + file):
            os.remove(PATH + file)


def block_list():
    """Genera el file para bind para bloquear el listado de Child Porn
    """
    # Partir del file de dominios obtenidos
    bindfile_ptr = open(BIND_FILE, 'w')
    with open(PATH + 'childporn_dominios.txt', 'r') as fin:
        for line in nonblank_lines(fin):
            if check_ignoreDomain(line):
                pass
            else:
                bindfile_ptr.write(domain2bindfile(line))
    bindfile_ptr.close()
    # Revisa si el archivo generado no tiene errores de sintaxis.
    cmd = "named-checkconf /etc/bind/named.conf"
    if get_output_cmd(cmd) == "":
        # Reinicia y syncroniza los servidores DNS de BTLATAM:
        cmd = "sh ~/sync-zones.sh"
        get_output_cmd(cmd)
        return("SE ACTUALIZA EL BLOQUEO")
    else:
        return("NO SE ACTUALIZA EL BLOQUEO, problemas file DNS generado")


def verify_list():
    """ Verifica que las urls del listado este bloqueados
    accesa cada URL y valida si esta siendo bloqueada
    """
    # Descarga el listado
    if download_list():
        # Toma las estadisticas de listado a verificar
        DateList = time.ctime(os.path.getmtime(PATH + "listadoChild.txt"))
        cmd = "cat " + PATH + "listadoChild_utf8.txt | wc -l"
        linesList = get_output_cmd(cmd)
        print("\n\tVerificando Listado con Fecha: {}".format(DateList))
        print("\tSe verificaran {} "
              "urls de ChildPorn en Min TIC".format(linesList))
        # Recorre el listado en formato UTF-8 y accesando cada url
        with open(PATH + 'listadoChild_utf8.txt', 'r') as fin:
            for line in nonblank_lines(fin):
                check_url_cmd(line)
        # Imprime la cantidad de URL a revisar.
        print("Se deben revisar {}".format(Count_unblocked))
    # Elimina files temporales
    clean_files()


def check_list():
    """ Descarga el listado de MINTIC actual y compara con la fecha del
    archivo de bloqueo en los DNS servers.
    """
    # Descarga el listado
    if download_list():
        # Genera el file Temp con los dominios sin URI.
        temp_ptr = open(PATH + 'temp', 'w')
        with open(PATH + 'listadoChild_utf8.txt', 'r') as fin:
            for line in nonblank_lines(fin):
                temp_ptr.write(url2domain(line))
        temp_ptr.close()
        # Ordena alfabeticamente el listado de dominos
        txt = open(PATH + 'temp', 'r').read()
        txt = txt.lower()
        content_set = '\n'.join(sorted(set(txt.splitlines())))
        # Genera el file de salida con los dominos alfabeticamente
        cleandata_ptr = open(PATH + 'childporn_dominios.txt', 'w')
        for line in content_set:
            cleandata_ptr.write(line)
        cleandata_ptr.close()
        # Toma informacion de los archivos para enviar por correo:
        DateList_segs = os.path.getmtime(PATH + "listadoChild.txt")
        DateList = time.ctime(DateList_segs)
        if os.path.isfile(BIND_FILE):
            DateDNSblocked_segs = os.path.getmtime(BIND_FILE)
            DateDNSblocked = time.ctime(DateDNSblocked_segs)
        else:
            DateDNSblocked_segs = 0
            DateDNSblocked = "Se crea el file de Bloqueo"
        cmd = "cat " + PATH + "listadoChild.txt | wc -l"
        lines_list = get_output_cmd(cmd)
        cmd = "cat " + PATH + "childporn_dominios.txt | wc -l"
        lines_dominios = get_output_cmd(cmd)
        # Confirmar el mensaje a enviar
        mns = "Fecha del Listados ChildPorn:\t\t{}".format(DateList)
        mns = mns + "\n"
        mns = mns + "URLs ChildPorn:\t\t{}".format(lines_list)
        mns = mns + "\n"
        mns = mns + "Dominios ChildPorn:\t\t{}".format(lines_dominios)
        mns = mns + "\nFecha bloqueo DNS BT:\t\t{}".format(DateDNSblocked)
        if DateList_segs > DateDNSblocked_segs:
            mns = mns + "\n\n\t"
            mns = mns + block_list()
        #print(mns)
        # Envio de correo
        subject = "Listado ChildPorn"
        correo.enviar("juan.ramirezangel@bt.com", subject, mns)
    # Elimina files temporales
    clean_files()

#******************************************************************************
