"""
Copyright 2010 Serge Matveenko

This file is part of Picket.

Picket is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Picket is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Picket.  If not, see <http://www.gnu.org/licenses/>.
"""

from mongoengine import connect

from dist import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Firstname Lastname', 'admin@example.com'),
)

MANAGERS = ADMINS

DB = connect('picket')

SECRET_KEY = ''

#CACHE_BACKEND = 'locmem://'

SERVE_STATIC = False

#FORCE_SCRIPT_NAME = ''
