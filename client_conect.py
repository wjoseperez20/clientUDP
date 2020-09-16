#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2020 Wilmer Perez / Arturo <wjperez.12@est.ucab.edu.ve>

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
from client import Client

if __name__ == '__main__':
    exit(Client().start())
