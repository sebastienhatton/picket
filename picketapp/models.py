"""
Copyright 2008 Serge Matveenko

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

from django.contrib.auth.models import User, Group
from django.db                  import models
from django.utils.translation   import gettext_lazy as _

from picketapp.settings import *

class IntegrationError(Exception):
    pass

class ViewState(models.Model):
    name = models.CharField(_('view state name'),
        unique=True, max_length=255)
    groups = models.ManyToManyField(Group,
        verbose_name=_('view state groups'),
        help_text=_('groups allowed to view this view state'))
    def __unicode__(self):
        return u'%s' % self.name
    class Meta():
        verbose_name = _('view state')
        verbose_name_plural = _('view states')

class ProjectManager(models.Manager):
    def permited(self, user):
        return self.filter(view_state__groups__user = user.id)
        
class Project(models.Model):
    objects = ProjectManager()
    name = models.CharField(_('project name'),
        unique=True, max_length=255)
    status = models.PositiveIntegerField(_('project status'),
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_CHOICES_DEFAULT)
    enabled = models.BooleanField(_('project enabled'), default=True)
    view_state = models.ForeignKey(ViewState,
        verbose_name=_('project view state'))
    url = models.URLField(_('project url'))
    description = models.TextField(_('project description'),
        blank=True)
    parent = models.ForeignKey('Project',
        verbose_name=_('project parent'), blank=True, null=True)
    user_list = models.ManyToManyField(User,
        verbose_name=_('project user list'), related_name='project_list',
        through='ProjectUserList')
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return '%sp%s/' % (BASE_URL, self.id) \
            if not INTEGRATION_FOREIGN_ABSOLUTE_URL \
                else self.get_integrated().get_absolute_url()
    
    def get_integrated(self):
        """
        @return: integrated project if available
        @raise IntegrationError: if integration is improperly \
configured
        TODO: make _integration_cache working as cache
        """
        if not hasattr(self, '_integration_cache'):
            if not INTEGRATION_MODEL:
                raise IntegrationError
            try:
                app_label, model_name = INTEGRATION_MODEL.split('.')
                model = models.get_model(app_label, model_name)
                self._integration_cache = model._default_manager.get(
                    project__id__exact=self.id)
            except ImportError:
                raise IntegrationError
        return self._integration_cache
    
    class Meta():
        verbose_name = _('project')
        verbose_name_plural = _('projects')

class Category(models.Model):
    project = models.ForeignKey(Project,
        verbose_name=_('category project'))
    name = models.CharField(_('category name'), max_length=192)
    handler = models.ForeignKey(User,
        verbose_name=_('category handler'), blank=True, null=True)
    def __unicode__(self):
        return u'%s: %s' % (self.project, self.name)
    def get_absolute_url(self):
        return '%sp%s/c%s/' % (BASE_URL, self.project_id, self.id)
    class Meta():
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        unique_together = (('project', 'name'),)

class BugManager(models.Manager):
    def permited(self, user, project):
        bugs = self.filter(
            view_state__in=[viewstate.id for viewstates in [
                group.viewstate_set.all() for group in \
                user.groups.all()] for viewstate in viewstates],
            project__in=Project.objects.permited(user))
        return bugs.filter(project=project) \
            if project is not None else bugs

class Bug(models.Model):
    objects = BugManager()
    
    project = models.ForeignKey(Project, verbose_name=_('bug project'))
    reporter = models.ForeignKey(User, verbose_name=_('bug reporter'),
        related_name='reporter')
    handler = models.ForeignKey(User, verbose_name=_('bug handler'),
        related_name='handler')
    duplicate = models.ForeignKey('self', verbose_name=_('bug duplicate'),
        related_name='duplicateOf', blank=True, null=True,)
    priority = models.PositiveIntegerField(_('bug priority'),
        choices=PRIORITY_CHOICES, default=PRIORITY_CHOICES_DEFAULT)
    severity = models.PositiveIntegerField(_('bug severity'),
        choices=SEVERITY_CHOICES, default=SEVERITY_CHOICES_DEFAULT)
    reproducibility = models.PositiveIntegerField(_('bug reproducibility'),
        choices=REPRODUCIBILITY_CHOICES,
        default=REPRODUCIBILITY_CHOICES_DEFAULT)
    status = models.PositiveIntegerField(_('bug status'),
        choices=BUG_STATUS_CHOICES,
        default=BUG_STATUS_CHOICES_DEFAULT)
    resolution = models.PositiveIntegerField(_('bug resolution'),
        choices=RESOLUTION_CHOICES,
        default=RESOLUTION_CHOICES_DEFAULT)
    projection = models.PositiveIntegerField(_('bug projection'),
        choices=PROJECTION_CHOICES,
        default=PROJECTION_CHOICES_DEFAULT)
    category = models.ForeignKey(Category, verbose_name=_('bug category'))
    date_submitted = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    eta = models.PositiveIntegerField(_('bug ETA'), choices=ETA_CHOICES,
        default=ETA_CHOICES_DEFAULT)
    view_state = models.ForeignKey(ViewState, verbose_name=_('bug view state'))
    summary = models.CharField(_('bug summary'), max_length=255)
    description = models.TextField(_('bug description'))
    steps_to_reproduce = models.TextField(_('bug steps to reproduce'),
        blank=True)
    additional_information = models.TextField(_('bug additional information'),
        blank=True)
    sponsorship_total = models.IntegerField(_('bug sponsorship total'),
        default=0)
    sticky = models.BooleanField(_('bug sticky'), default=False)
    history = models.ManyToManyField(User, verbose_name=_('bug history'),
        related_name=_('history'), through='BugHistory')
    monitor = models.ManyToManyField(User, verbose_name=_('bug monitor'),
        related_name=_('monitor'), through='BugMonitor')
    relationship = models.ManyToManyField('self',
        verbose_name=_('bug relationship'), symmetrical=False,
        through='BugRelationship')
    
    def __unicode__(self):
        return u'%s: %s' % (self.id, self.summary)
    
    def get_absolute_url(self):
        return '%sp%s/b%s/' % (BASE_URL, self.project_id, self.id)
     
    class Meta():
        verbose_name = _('bug')
        verbose_name_plural = _('bugs')

class BugFile(models.Model):
    bug = models.ForeignKey(Bug, verbose_name=_('bug'))
    title = models.CharField(_('bug file title'), max_length=750)
    file = models.FileField(_('bug file'), upload_to='bugs/%Y/%m/%d-%H')
    date_added = models.DateTimeField(_('bug file date added'),
        auto_now_add=True, editable=False)
    def __unicode__(self):
        return u'%s' % self.title
    class Meta():
        verbose_name = _('bug file')
        verbose_name_plural = _('bug files')

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('project'))
    title = models.CharField(_('project file title'), max_length=750)
    file = models.FileField(_('project file'),
        upload_to='projects/%Y/%m/%d-%H')
    date_added = models.DateTimeField(_('project file date added'),
        auto_now_add=True, editable=False)
    description = models.TextField(_('project file description'), blank=True)
    def __unicode__(self):
        return u'%s' % self.title
    class Meta():
        verbose_name = _('project file')
        verbose_name_plural = _('project files')

class BugHistory(models.Model):
    """
    TODO: automate me
    """
    
    user = models.ForeignKey(User,
        verbose_name=_('bug history entry user'))
    bug = models.ForeignKey(Bug, verbose_name=_('bug'))
    date_modified = models.DateTimeField(_('bug history entry date'),
        auto_now=True)
    field_name = models.CharField(_('bug history entry field'),
        max_length=96, blank=True)
    old_value = models.CharField(
        _('bug history entry old field value'),
        max_length=255, blank=True)
    new_value = models.CharField(
        _('bug history entry new field value'),
        max_length=255, blank=True)
    type = models.PositiveIntegerField(_('bug history entry type'),
        choices=(
            (0,_('no field changed'),),
            (1,_('field changed'),),
            (2,_('relationship added'),),
            (3,_('relationship changed'),),
            (4,_('relationship removed'),),
        ))
    class Meta():
        verbose_name = _('bug history entry')
        verbose_name_plural = _('bug history entries')

class BugMonitor(models.Model):
    user = models.ForeignKey(User, verbose_name=_('bug monitor user'))
    bug = models.ForeignKey(Bug, verbose_name=_('bug'))
    mute = models.BooleanField(_('bug monitor mute'), default=False)
    class Meta():
        verbose_name = _('bug monitor entry')
        verbose_name_plural = _('bug monitor entries')

class BugRelationship(models.Model):
    source_bug = models.ForeignKey(Bug,
        verbose_name=_('bug relationship source'),
        related_name='source')
    destination_bug = models.ForeignKey(Bug,
        verbose_name=_('bug relationship destination'),
        related_name='destination')
    relationship_type = models.IntegerField(
        _('bug relationship type'), choices=(
            (1,_('related to'),),
            (2,_('parent of'),),
            (3,_('child of'),),
            (0,_('duplicate of'),),
            (4,_('has duplicate'),),
        ))
    class Meta():
        verbose_name = _('bug relationship entry')
        verbose_name_plural = _('bug relationship entries')

class Bugnote(models.Model):
    bug = models.ForeignKey(Bug, verbose_name=_('bugnote bug'))
    reporter = models.ForeignKey(User, verbose_name=_('bugnote user'))
    text = models.TextField(_('bugnote text'))
    view_state = models.ForeignKey(ViewState,
        verbose_name=_('bugnote view state'))
    date_submitted = models.DateTimeField(_('bugnote date submitted'),
        auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_('bugnote last modified'),
        auto_now=True, editable=False)
    note_type = models.IntegerField(_('bugnote type'),
        null=True, blank=True)
    note_attr = models.CharField(_('bugnote attr'),
        max_length=750, blank=True)
    def __unicode__(self):
        return u'%s: %s at %s' % (
            self.bug, self.reporter, self.date_submitted)
    class Meta():
        verbose_name = _('bugnote')
        verbose_name_plural = _('bugnotes')
        ordering = ['date_submitted',]

class ProjectUserList(models.Model):
    """
    TODO: automate me from view states
    """
    
    project = models.ForeignKey(Project, verbose_name=_('project'))
    user = models.ForeignKey(User, verbose_name=_('user'))
    access_level = models.PositiveIntegerField(
        _('project user access level'), choices=ACCESS_LEVELS_CHOICES)
    class Meta:
        unique_together = (('project', 'user'),)
    def __unicode__(self):
        return u'%s in %s is %s' % (
            self.user, self.project, self.get_access_level_display())
    class Meta():
        verbose_name = _('project user list entry')
        verbose_name_plural = _('project user list entries')
        pass

"""
class Config(models.Model):
    key = models.CharField(max_length=192)
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    access_reqd = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    value = models.TextField()
    class Meta:
        unique_together = (('project', 'user'),)

class CustomField(models.Model):
    name = models.CharField(max_length=192)
    type = models.IntegerField()
    possible_values = models.CharField(max_length=765)
    default_value = models.CharField(max_length=765)
    valid_regexp = models.CharField(max_length=765)
    access_level_r = models.IntegerField()
    access_level_rw = models.IntegerField()
    length_min = models.IntegerField()
    length_max = models.IntegerField()
    advanced = models.IntegerField()
    require_report = models.IntegerField()
    require_update = models.IntegerField()
    display_report = models.IntegerField()
    display_update = models.IntegerField()
    require_resolved = models.IntegerField()
    display_resolved = models.IntegerField()
    display_closed = models.IntegerField()
    require_closed = models.IntegerField()

class CustomFieldProject(models.Model):
    field = models.ForeignKey(CustomField)
    project = models.ForeignKey(Project)
    sequence = models.IntegerField()
    class Meta:
        unique_together = (('field', 'project'),)

class CustomFieldString(models.Model):
    field = models.ForeignKey(CustomField)
    bug = models.ForeignKey(Bug)
    value = models.CharField(max_length=765)
    class Meta:
        unique_together = (('field', 'bug'),)

class Filter(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    is_public = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=192)
    filter_string = models.TextField()

class ProjectVersion(models.Model):
    project = models.ForeignKey(Project)
    version = models.CharField(unique=True, max_length=192)
    date_order = models.DateTimeField()
    description = models.TextField()
    released = models.IntegerField()
    class Meta:
        unique_together = (('project', 'version'),)

class Sponsorship(models.Model):
    bug = models.ForeignKey(Bug)
    user = models.ForeignKey(User)
    amount = models.IntegerField()
    logo = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    paid = models.IntegerField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class UserPref(models.Model):
    #mantis anachronismus
    user = models.ForeignKey(User, unique=True)
    default_project = models.IntegerField()
    advanced_report = models.IntegerField()
    advanced_view = models.IntegerField()
    advanced_update = models.IntegerField()
    refresh_delay = models.IntegerField()
    redirect_delay = models.IntegerField()
    bugnote_order = models.CharField(max_length=12)
    email_on_new = models.IntegerField()
    email_on_assigned = models.IntegerField()
    email_on_feedback = models.IntegerField()
    email_on_resolved = models.IntegerField()
    email_on_closed = models.IntegerField()
    email_on_reopened = models.IntegerField()
    email_on_bugnote = models.IntegerField()
    email_on_status = models.IntegerField()
    email_on_priority = models.IntegerField()
    email_on_priority_min_severity = models.IntegerField()
    email_on_status_min_severity = models.IntegerField()
    email_on_bugnote_min_severity = models.IntegerField()
    email_on_reopened_min_severity = models.IntegerField()
    email_on_closed_min_severity = models.IntegerField()
    email_on_resolved_min_severity = models.IntegerField()
    email_on_feedback_min_severity = models.IntegerField()
    email_on_assigned_min_severity = models.IntegerField()
    email_on_new_min_severity = models.IntegerField()
    email_bugnote_limit = models.IntegerField()
    language = models.CharField(max_length=96)
"""