# -*- coding: utf-8 -*-
"""
Copyright (C) 2020 Wilmer Perez <wjperez.12@est.ucab.edu.ve>

This file is part of clientUDP.

clientUDP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

clientUDP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""
from .config import Config
from hashlib import md5
import logging
import socket
import base64
import sys


class Client:

    def __init__(self):
        self.__conf = None

    @property
    def config(self):
        if self.__conf is None:
            self.__conf = Config()
        return self.__conf

    def socket_director(self):
        # region Variables
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn_username = self.config.client_name
        udp_port = self.config.local_udp_port
        tn_port = self.config.server_port
        tn_ip = self.config.server_ip
        # endregion

        # region Instrumentation
        logging.info('Iniciando cliente - Conexion con %s' % tn_ip)
        # endregion

        try:
            s.connect((tn_ip, tn_port))
            s.sendall(b'Hello, world')
            data = s.recv(1024)
            print('Received', repr(data))

        except OSError:
            s.close()
            # region Instrumentation
            logging.error("Error al conectar via telnet con el servidor: %s" % tn_ip)
            # endregion

        # region Instrumentation
        logging.info('Cerrando cliente - Conexion con %s' % tn_ip)
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

        self.socket_director()

        """
        Fin de la ejecución del client
        """
        return 0
