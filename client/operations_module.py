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


class Client:

    def __init__(self):
        self.__conf = None

    @property
    def config(self):
        if self.__conf is None:
            self.__conf = Config()
        return self.__conf

    """
    @doc: Diccionario de Comandos para el server
    @param argument (int) - id del comando
    @param argument_2 (any)
    @return: comando en formato de bytes
    """
    def command_case(self, argument: int, argument_2=''):
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

    """
    @doc: Se encarga de enviar mensaje via TCP
    @param s_conn (Socket TCP) - objeto socket actual
    @param message (string)
    @return: Respuesta del servidor y un booleano si la respuesta es OK
    """
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

    """
    @doc: Desencripta un mensaje en base64 y calcula sus hash md5
    @param base64_message (bytes)
    @return: checksum del 
    """
    def udp_decryptor(self, base64_message):
        # region Variables
        msg_decode = ''
        check_sum = ''
        # endregion

        # region Instrumentation
        logging.info('Entrando en udp_decryptor')
        # endregion

        try:
            msg_decode = base64.b64decode(base64_message)
            check_sum = md5(msg_decode).digest().hex()

        except OSError:
            # region Instrumentation
            logging.error('Error en udp_decryptor - desencriptando el mensaje')
            # endregion

        # region Instrumentation
        logging.info('Saliendo de udp_decryptor msg: %s | check_sum: %s', msg_decode, check_sum)
        # endregion

        return msg_decode.decode('utf-8')[:-1], check_sum

    """
    @doc: Hilo que se encarga de comunicarse con el servidor via TCP
    @param quede_channel (Quede) Cola de comunicacion entre hilos
    @param s_conn (Socket)
    """
    def socket_producer(self, quede_channel: Queue, s_conn: socket):

        # region Instrumentation
        logging.info('Entrando en socket_producer')
        # endregion

        try:

            n = 0
            while n < 5:
                result_text, result = self.tcp_sender(s_conn, self.command_case(3))

                # DATA THREAD UDP
                data = quede_channel.get()
                msg_str, checksum = self.udp_decryptor(data)

                if checksum:
                    result_text, result = self.tcp_sender(s_conn, self.command_case(4, checksum))

                    if result:
                        result_text, result = self.tcp_sender(s_conn, self.command_case(5))
                        print('Su mensaje es: ' + msg_str)
                        s_conn.close()
                        break
                    else:
                        print('CheckSum Incorrecto')
                        n = n + 1
                else:
                    break

        except OSError:
            # region Instrumentation
            logging.error('Error en socket_producer - conexion al server')
            # endregion

        # region Instrumentation
        logging.info('Saliendo socket_producer')
        # endregion

    """
    @doc: Hilo que se queda en escucha en el puerto UDP y envia al hilo productor todo lo que recibe
    @param quede_channel (Quede) Cola de comunicacion entre hilos
    @param msg_length (int) Tamaño del mensaje a recibir por sockect
    """
    def socket_consumer(self, quede_channel: Queue, msg_length: int):

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
                (data, addr) = s.recvfrom(msg_length * 1024)
                quede_channel.put(data)

        except Exception as e:
            # region Instrumentation
            logging.error("Error en socket_consumer %s" % e)
            # endregion

        # region Instrumentation
        logging.info('Cerrando socket_consumer')
        # endregion

    """
    @doc: Crea los hilos y les asigna una cola de comunicacion
    @param s_conn (socket) Socket TCP creado previamente
    @param msg_length (int) Tamaño del mensaje a recibir por sockect UDP
    """
    def socket_director(self, s_conn: socket, msg_length: int):
        # region Variables
        queue = Queue()
        # endregion

        try:

            t1 = Thread(target=self.socket_consumer, args=(queue, int(msg_length)))
            t2 = Thread(target=self.socket_producer, args=(queue, s_conn))
            t1.start()
            t2.start()

        except Exception as e:
            # region Instrumentation
            logging.error("Error creando los hilos  %s" % e)
            # endregion

    """
    @doc: Inicia la comunicacion con el server via TCP y se encarga de mandar a generar los hilos si el server acepta al
    usuario registrado previamente, de lo contrario ciera la conexion y no se crean los hilos
    """
    def init_interaction(self):
        # region Variables
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn_port = self.config.server_port
        tn_ip = self.config.server_ip
        s.settimeout(10)
        # endregion

        # region Instrumentation
        logging.info('Entrando en init_interaction - conexion tcp %s:%s' % (tn_ip, tn_port))
        # endregion

        try:
            s.connect((tn_ip, tn_port))

            result_text, result = self.tcp_sender(s, self.command_case(1))

            if result:
                result_text, result = self.tcp_sender(s, self.command_case(2))

                if result:
                    self.socket_director(s, int(result_text[1]))
                else:
                    print('Ocurrio un error obteniendo el tamaño del mensaje')
                    s.close()
            else:
                s.close()

        except Exception as e:
            s.close()
            # region Instrumentation
            logging.error("Error en init_interaction - socket %s" % e)
            # endregion

        # region Instrumentation
        logging.info('Saliendo de init_interaction - conexion tcp %s:%s' % (tn_ip, tn_port))
        # endregion

    """
    @doc: Configura el loggin y inicia la comunicacion inicial en el hilo principal
    """
    def start(self):
        # region Config_Instrumentation
        logging.basicConfig(
            filename=self.config.log['filename'],
            level=getattr(logging, self.config.log['level']),
            format=self.config.log['format']
        )
        # endregion

        self.init_interaction()

        exit(1)
