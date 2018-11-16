#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Descripcion:      Realiza operaciones como descargar, checkear y bloquear
#                   dominos de los listado de coljuegos en MINTIC
# Fecha Creacion: 02 Oct 2018
#-----------------------------------------------------------------------------

#*****************************************************************************
# Library Load
#*****************************************************************************
import sys
import os
import argparse
import childporn
#******************************************************************************


#*****************************************************************************
# MAIN
#*****************************************************************************
def main():
    sys.path.append('/root/childporn_list')
    parser = argparse.ArgumentParser(description="Realiza checkeo, descarga"
                                                 " y bloqueo de listado Col"
                                                 "juegos en MinTIC")
    requiredNamed = parser.add_argument_group('Required arguments')
    requiredNamed.add_argument('-c', '--command', action='store',
                               type=str, required=True,
                               help="commands are check|verify")
    args = parser.parse_args()
    if args.command == 'check':
        childporn.check_list()
    elif args.command == 'verify':
        childporn.verify_list()
    else:
        print("Error al ingresar comando dar --help")


#******************************************************************************
# APP process
#******************************************************************************
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        try:
            print("Keyboard Interrupt")
            sys.exit(0)
        except SystemExit:
            os._exit(0)

#******************************************************************************
