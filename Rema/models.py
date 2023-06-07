from django.db import models

class Area(models.Model):
    id_area = models.IntegerField(primary_key=True)
    codigo_area = models.CharField(max_length=255, blank=True, null=True)
    nombre_area = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Area'


class Centrotrabajo(models.Model):
    id_centrotrabajo = models.IntegerField(db_column='id_centroTrabajo', primary_key=True)  # Field name made lowercase.
    id_area = models.IntegerField(blank=True, null=True)
    codigo_centrotrabajo = models.CharField(db_column='codigo_centroTrabajo', max_length=255, blank=True, null=True)  # Field name made lowercase.   
    nombre_centrotrabajo = models.CharField(db_column='nombre_centroTrabajo', max_length=255, blank=True, null=True)  # Field name made lowercase.   

    def __str__(self):
        return self.codigo_centrotrabajo + ' ' + self.nombre_centrotrabajo
    class Meta:
        managed = False
        db_table = 'CentroTrabajo'


class Maderas(models.Model):
    id_madera = models.IntegerField(primary_key=True)
    id_centrotrabajo = models.IntegerField(db_column='id_centroTrabajo', blank=False, null=True)  # Field name made lowercase.
    codigo_madera = models.CharField(max_length=255, blank=False, null=False)
    espesor = models.FloatField(blank=False, null=True)
    ancho = models.FloatField(blank=False, null=True)
    largo = models.FloatField(blank=False, null=True)
    diametro = models.FloatField(blank=False, null=True)
    volumenxpieza = models.FloatField(db_column='volumenxPieza', blank=False, null=True)  # Field name made lowercase.
    cantidadxpaquete = models.FloatField(db_column='cantidadxPaquete', blank=False, null=True)  # Field name made lowercase.
    factor = models.FloatField(blank=False, null=True)
    piezas = models.FloatField(blank=False, null=True)
    volumentotal = models.FloatField(db_column='volumenTotal', blank=False, null=True)  # Field name made lowercase.
    paquetes = models.FloatField(blank=False, null=True)
    nombre_centrotrabajo = models.CharField(db_column='nombre_centroTrabajo', max_length=255, blank=False, null=True)  # Field name made lowercase.   


    class Meta:
        managed = False
        db_table = 'Maderas'


class Maquina(models.Model):
    id_maquina = models.IntegerField(primary_key=True)
    id_centrotrabajo = models.IntegerField(db_column='id_centroTrabajo', blank=True, null=True)  # Field name made lowercase.
    nombremaquina = models.CharField(db_column='nombreMaquina', max_length=255, blank=True, null=True)  # Field name made lowercase.
    centrotrabajomaquina = models.CharField(db_column='centroTrabajoMaquina', max_length=255, blank=True, null=True)  # Field name made lowercase.   

    class Meta:
        managed = False
        db_table = 'Maquina'


class Proceso(models.Model):
    id_proceso = models.AutoField(primary_key=True)
    id_madera = models.IntegerField(blank=True, null=False)
    id_area = models.IntegerField(blank=True, null=False)
    id_centrotrabajo = models.IntegerField(db_column='id_centroTrabajo', blank=True, null=False)  # Field name made lowercase.
    id_maquina = models.IntegerField(blank=True, null=False)
    codigo_madera = models.CharField(max_length=255, blank=True, null=False)
    fecha = models.DateField(blank=True, null=False)
    nombre_centrotrabajo = models.CharField(db_column='nombre_centroTrabajo', max_length=255, blank=True, null=False)  # Field name made lowercase.   
    nombre_maquina = models.CharField(max_length=255, blank=True, null=False)
    piezasentrada = models.IntegerField(db_column='piezasEntrada', blank=False, null=True)  # Field name made lowercase.
    piezassalida = models.IntegerField(db_column='piezasSalida', blank=False, null=True)  # Field name made lowercase.
    volumenentrada = models.FloatField(db_column='volumenEntrada', blank=False, null=True)  # Field name made lowercase.
    volumensalida = models.FloatField(db_column='volumenSalida', blank=False, null=True)  # Field name made lowercase.
    piezasrechazohum = models.IntegerField(db_column='piezasRechazoHum', blank=False, null=True)  # Field name made lowercase.
    piezasrechazodef = models.IntegerField(db_column='piezasRechazoDef', blank=False, null=True)  # Field name made lowercase.
    piezasrechazoproc = models.IntegerField(db_column='piezasRechazoProc', blank=False, null=True)  # Field name made lowercase.
    volumenrechazohum = models.FloatField(db_column='volumenRechazoHum', blank=False, null=True)  # Field name made lowercase.
    volumenrechazodef = models.FloatField(db_column='volumenRechazoDef', blank=False, null=True)  # Field name made lowercase.
    volumenrechazoproc = models.FloatField(db_column='volumenRechazoProc', blank=False, null=True)  # Field name made lowercase.
    piezasreproceso = models.IntegerField(db_column='piezasReproceso', blank=False, null=True)  # Field name made lowercase.
    volumenreproceso = models.FloatField(db_column='volumenReproceso', blank=False, null=True)  # Field name made lowercase.
    piezascalidad = models.IntegerField(db_column='piezasCalidad', blank=False, null=True)  # Field name made lowercase.
    volumencalidad = models.FloatField(db_column='volumenCalidad', blank=False, null=True)  # Field name made lowercase.
    volumentotal = models.FloatField(db_column='volumenTotal', blank=False, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Proceso'


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