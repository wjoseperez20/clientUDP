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
from threading import Thread
from queue import Queue
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

    def command_case(self, argument, argument_2=''):
        # region Variables
        tn_username = self.config.client_name
        udp_port = self.config.local_udp_port
        # endregion

        switcher = {
            1: ("helloiam " + tn_username),
            2: "msglen",
            3: ("givememsg " + str(udp_port)),
            4: ("chkmsg " + argument_2),
            5: "bye"
        }

        return switcher.get(argument, "Invalid Command Id").encode('utf-8')

    def tcp_sender(self, s_conn, message):
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

    def socket_producer(self, out_q):
        # region Variables
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn_port = self.config.server_port
        tn_ip = self.config.server_ip
        result_text = []
        result = True
        # endregion

        # region Instrumentation
        logging.info('Iniciando socket_producer - Conexion con %s' % tn_ip)
        # endregion

        try:

            s.connect((tn_ip, tn_port))

            for i in range(1, 6):

                if i != 3 and i != 4 and result:
                    result_text, result = self.tcp_sender(s, self.command_case(i))
                elif i == 3 and result:
                    result_text, result = self.tcp_sender(s, self.command_case(i, result_text[1]))
                    out_q.put(result_text)
                elif i == 4 and result:
                    result_text, result = self.tcp_sender(s, self.command_case(i))
                else:
                    s.close()
                    break

        except OSError:
            s.close()
            # region Instrumentation
            logging.error("Error al conectar via telnet con el servidor: %s" % tn_ip)
            # endregion

        # region Instrumentation
        logging.info('Cerrando socket_producer - Conexion con %s' % tn_ip)
        # endregion

    def socket_consumer(self, in_q):
        # region Variables
        local_port = self.config.local_udp_port
        local_host = self.config.local_host
        # endregion

        # region Instrumentation
        logging.info('Iniciando socket_consumer udp %s:%s' % (local_host, local_port))
        # endregion

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.bind((local_host, local_port))

            while True:
                (data, addr) = s.recvfrom(128 * 1024)
                print(data)

        except Exception as e:
            # region Instrumentation
            logging.error("Error en socket_consumer %s" % e)
            # endregion

        # region Instrumentation
        logging.info('Cerrando socket_consumer')
        # endregion

    def start(self):
        # region Variables
        q = Queue()
        # endregion

        # region Config_Instrumentation
        logging.basicConfig(
            filename=self.config.log['filename'],
            level=getattr(logging, self.config.log['level']),
            format=self.config.log['format']
        )
        # endregion

        t1 = Thread(target=self.socket_consumer, args=(q,))
        t2 = Thread(target=self.socket_producer, args=(q,))
        t1.start()
        t2.start()

        return 0
