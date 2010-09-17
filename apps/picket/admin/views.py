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

from ..decorators import render_to
from ..documents import Project


@render_to('picket/admin/index.html')
def index(request):
    return {}


@render_to('picket/admin/projects.html')
def projects(request):
    
    projects = Project.sorted()
    
    if not projects:
        projects = True
        
    return {}
