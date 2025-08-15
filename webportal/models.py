# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Administrators(models.Model):
    centreid = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=32, blank=True, null=True)
    mobile = models.CharField(max_length=32, blank=True, null=True)
    accessed = models.DateTimeField(blank=True, null=True)
    restricted = models.BooleanField(blank=True, null=True)
    notifications = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administrators'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Calls(models.Model):
    areaid = models.IntegerField(blank=True, null=True)
    langid = models.IntegerField(blank=True, null=True)
    cli = models.CharField(max_length=24, blank=True, null=True)
    ddi = models.CharField(max_length=16, blank=True, null=True)
    name = models.CharField(max_length=16, blank=True, null=True)
    keyzone = models.CharField(max_length=50, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    finish = models.DateTimeField(blank=True, null=True)
    session = models.DateTimeField(blank=True, null=True)
    sessid = models.IntegerField(blank=True, null=True)
    packets = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calls'


class Centres(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    abbreviation = models.CharField(max_length=32, blank=True, null=True)
    contact = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=32, blank=True, null=True)
    mobile = models.CharField(max_length=32, blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    dedicated = models.BooleanField(blank=True, null=True)
    billname = models.CharField(max_length=64, blank=True, null=True)
    address1 = models.CharField(max_length=64, blank=True, null=True)
    address2 = models.CharField(max_length=64, blank=True, null=True)
    address3 = models.CharField(max_length=64, blank=True, null=True)
    address4 = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'centres'


class Countries(models.Model):
    prefix = models.CharField(max_length=4, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    iso = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'countries'


class Devices(models.Model):
    centreid = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=16, blank=True, null=True)
    contact = models.CharField(max_length=64, blank=True, null=True)
    registered = models.DateTimeField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'devices'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Invites(models.Model):
    delivered = models.DateTimeField(blank=True, null=True)
    oprid = models.IntegerField(blank=True, null=True)
    cli = models.CharField(max_length=32, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invites'


class Languages(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    abbreviation = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'languages'


class Messages(models.Model):
    centreid = models.IntegerField(blank=True, null=True)
    content = models.CharField(max_length=128, blank=True, null=True)
    level = models.TextField(blank=True, null=True)  # This field type is a guess.
    expires = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'messages'


class Missed(models.Model):
    callid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'missed'


class Operators(models.Model):
    creation = models.DateTimeField(blank=True, null=True)
    centreid = models.IntegerField(blank=True, null=True)
    langid = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    identifier = models.CharField(max_length=32, blank=True, null=True)
    fname = models.CharField(max_length=32, blank=True, null=True)
    sname = models.CharField(max_length=32, blank=True, null=True)
    mobile = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=32, blank=True, null=True)
    calltotal = models.IntegerField(blank=True, null=True)
    callduration = models.DurationField(blank=True, null=True)
    accessed = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'operators'


class Payplan(models.Model):
    centreid = models.IntegerField(blank=True, null=True)
    langid = models.IntegerField(blank=True, null=True)
    acd = models.IntegerField(blank=True, null=True)
    rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payplan'


class Sessions(models.Model):
    operid = models.IntegerField(blank=True, null=True)
    devid = models.IntegerField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    callduration = models.DurationField(blank=True, null=True)
    holdduration = models.DurationField(blank=True, null=True)
    calltotal = models.IntegerField(blank=True, null=True)
    missed = models.IntegerField(blank=True, null=True)
    waiting = models.IntegerField(blank=True, null=True)
    external = models.BooleanField(blank=True, null=True)
    packets = models.IntegerField(blank=True, null=True)
    media = models.CharField(max_length=32, blank=True, null=True)
    silence = models.IntegerField(blank=True, null=True)
    clearcode = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sessions'


class Signins(models.Model):
    adminid = models.IntegerField(blank=True, null=True)
    tstamp = models.DateTimeField(blank=True, null=True)
    ipadr = models.CharField(max_length=32, blank=True, null=True)
    language = models.CharField(max_length=32, blank=True, null=True)
    clienttime = models.CharField(max_length=128, blank=True, null=True)
    application = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'signins'


class Suspects(models.Model):
    callid = models.IntegerField(blank=True, null=True)
    silence = models.IntegerField(blank=True, null=True)
    qualified = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suspects'
