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
from multiprocessing import Process, Pipe
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

    def sender(self, s_conn, message):
        # region Variables
        response_bool = False
        response = []
        # endregion

        # region Instrumentation
        logging.info('Entrando en  sender - Mensaje a enviar %s' % message)
        # endregion

        try:
            s_conn.sendall(message)
            tn_response = s_conn.recv(1024)
            response = (tn_response.decode('utf-8')[:-1]).split()

            if response[0] == 'ok':
                response_bool = True

        except OSError:
            # region Instrumentation
            logging.error("Error timeout esperando respuesta server")
            # endregion

        # region Instrumentation
        logging.info('Saliendo de Sender - Mensaje recibido %s' % response)
        # endregion

        return response, response_bool

    def command_case(self, argument, argument_2=None):
        # region Variables
        if argument_2 is None:
            argument_2 = []
        tn_username = self.config.client_name
        udp_port = self.config.local_udp_port
        # endregion

        switcher = {
            1: ("helloiam " + tn_username),
            2: ("msglen " + argument_2),
            3: ("givememsg " + str(udp_port)),
            4: ("chkmsg " + argument_2),
            5: "bye"
        }

        return switcher.get(argument, "Invalid Command Id").encode('utf-8')

    def socket_director(self):
        # region Variables
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn_port = self.config.server_port
        tn_ip = self.config.server_ip
        result_text = []
        result = True
        # endregion

        # region Instrumentation
        logging.info('Iniciando cliente - Conexion con %s' % tn_ip)
        # endregion

        try:
            s.connect((tn_ip, tn_port))

            for i in range(1, 6):

                if i != 3 and i != 4 and result:
                    result_text, result = self.sender(s, self.command_case(i))
                elif i == 3 and result:
                    sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    result_text, result = self.sender(s, self.command_case(i, result_text[1]))
                elif i == 4 and result:
                    result_text, result = self.sender(s, self.command_case(i))
                else:
                    s.close()
                    break

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
