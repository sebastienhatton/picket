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

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from mongoforms.forms import MongoForm

from documents import Issue


class AuthForm(AuthenticationForm):
    i_am_auth_form = forms.BooleanField(initial=True, widget=forms.HiddenInput)


class IssueForm(MongoForm):
    
    return_to_form = forms.BooleanField(required=False)
    
    def __init__(self, return_to_form=False, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['return_to_form'].initial = return_to_form
    
    class Meta:
        document = Issue
        fields = ('subject', 'text',)
