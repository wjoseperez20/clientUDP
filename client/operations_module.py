# -*- coding: utf-8 -*-
"""
Copyright (C) 2020 Wilmer Perez <wjperez.12@est.ucab.edu.ve>

This file is part of clientTCP.

clientTCP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

clientTCP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import telnetlib
import logging
from hashlib import md5
import base64
from .config import Config


class Client:

    def __init__(self):
        self.__conf = None

    @property
    def config(self):
        if self.__conf is None:
            self.__conf = Config()
        return self.__conf

    def telnet(self):
        # region Variables
        tn_username = self.config.client_name
        tn_port = self.config.bind_port
        tn_ip = self.config.bind_addr
        # endregion

        # region Instrumentation
        logging.info('Iniciando cliente - Conexion con %s:%s' % tn_ip)
        # endregion

        try:
            tn_conn = telnetlib.Telnet(tn_ip, tn_port, 15)

            tn_conn.set_debuglevel(100)
            tn_conn.read_until("No se que onda XD")
            tn_conn.write(tn_username + "\n")

        except:
            logging.error("Unable to connect to Telnet server: " + tn_ip)

            # region Instrumentation
            logging.info('Cerrando cliente - Conexion con %s:%s' % tn_ip)
            # endregion

    def start(self):
        """
        Inicio de la ejecución del client
        """

        # region Config_Instrumentation
        logging.basicConfig(
            filename=self.config.log['filename'],
            level=getattr(logging, self.config.log['level']),
            format=self.config.log['format']
        )
        # endregion

        self.telnet()

        """
        Fin de la ejecución del client
        """
        return 0
