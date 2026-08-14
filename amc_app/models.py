# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TblActivityLog(models.Model):
    id_log = models.BigAutoField(primary_key=True)
    id_user = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    action = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100, blank=True, null=True)
    record_id = models.IntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    logged_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_activity_log'
    

class TblAuditLog(models.Model):
    id_audit = models.AutoField(primary_key=True)
    id_site = models.ForeignKey('TblSite', models.DO_NOTHING, db_column='id_site')
    id_ppm = models.ForeignKey('TblPpmSchedule', models.DO_NOTHING, db_column='id_ppm', blank=True, null=True)
    audit_date = models.DateField()
    audited_by = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='audited_by', blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    corrective_actions = models.TextField(blank=True, null=True)
    audit_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    follow_up_required = models.BooleanField()
    follow_up_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    report_path = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_audit_log'


class TblContractDetails(models.Model):
    id_contract = models.AutoField(primary_key=True)
    contract_ref_no = models.CharField(unique=True, max_length=100, blank=True, null=True)
    id_site = models.ForeignKey('TblSite', models.DO_NOTHING, db_column='id_site')
    id_contractor = models.ForeignKey('TblContractor', models.DO_NOTHING, db_column='id_contractor', blank=True, null=True)
    id_contract_status = models.ForeignKey('TblContractStatus', models.DO_NOTHING, db_column='id_contract_status', blank=True, null=True)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    contract_amt = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10)
    no_of_ppms = models.IntegerField()
    ppm_frequency = models.CharField(max_length=50, blank=True, null=True)
    next_ppm_schedule = models.DateField(blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)
    contract_document = models.TextField(blank=True, null=True)
    renewal_reminder_days = models.IntegerField()
    is_active = models.BooleanField()
    created_by = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='created_by', blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_contract_details'


class TblContractStatus(models.Model):
    id_contract_status = models.AutoField(primary_key=True)
    status_label = models.CharField(unique=True, max_length=50)

    class Meta:
        # managed = False
        db_table = 'tbl_contract_status'


class TblContractor(models.Model):
    id_contractor = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    trade_license_no = models.CharField(max_length=100, blank=True, null=True)
    trade_license_expiry = models.DateField(blank=True, null=True)
    vat_trn = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_contractor'


class TblDocuments(models.Model):
    id_doc = models.AutoField(primary_key=True)
    doc_type = models.CharField(max_length=50)
    ref_table = models.CharField(max_length=100, blank=True, null=True)
    ref_id = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    file_size_kb = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='uploaded_by', blank=True, null=True)
    uploaded_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_documents'


class TblEquipmentDetails(models.Model):
    id_equipment_det = models.AutoField(primary_key=True)
    id_site = models.ForeignKey('TblSite', models.DO_NOTHING, db_column='id_site')
    equipment_type = models.CharField(max_length=100, blank=True, null=True)
    equipment_name = models.CharField(max_length=100, blank=True, null=True)
    camera_make = models.CharField(max_length=100, blank=True, null=True)
    camera_model = models.CharField(max_length=100, blank=True, null=True)
    equipment_sl_no = models.CharField(unique=True, max_length=150, blank=True, null=True)
    cam_firmware = models.CharField(max_length=100, blank=True, null=True)
    engine = models.CharField(max_length=100, blank=True, null=True)
    licen_expiry = models.DateField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.TextField(blank=True, null=True)  # This field type is a guess.
    location_in_site = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    last_audited_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_equipment_details'


class TblNotifications(models.Model):
    id_notif = models.AutoField(primary_key=True)
    id_user = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    notif_type = models.CharField(max_length=50)
    ref_table = models.CharField(max_length=100, blank=True, null=True)
    ref_id = models.IntegerField(blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField()
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_notifications'


class TblPpmSchedule(models.Model):
    id_ppm = models.AutoField(primary_key=True)
    id_contract = models.ForeignKey(TblContractDetails, models.DO_NOTHING, db_column='id_contract')
    id_site = models.ForeignKey('TblSite', models.DO_NOTHING, db_column='id_site')
    scheduled_date = models.DateField()
    visit_date = models.DateField(blank=True, null=True)
    id_ppm_status = models.ForeignKey('TblPpmStatus', models.DO_NOTHING, db_column='id_ppm_status', blank=True, null=True)
    engineer_name = models.CharField(max_length=255, blank=True, null=True)
    id_assigned_user = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='id_assigned_user', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    report_document = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_ppm_schedule'


class TblPpmStatus(models.Model):
    id_ppm_status = models.AutoField(primary_key=True)
    status_label = models.CharField(unique=True, max_length=50)

    class Meta:
        # managed = False
        db_table = 'tbl_ppm_status'


class TblRegion(models.Model):
    id_region = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        # managed = False
        db_table = 'tbl_region'


class TblSite(models.Model):
    id_site = models.AutoField(primary_key=True)
    site_name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_code = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    id_region = models.ForeignKey(TblRegion, models.DO_NOTHING, db_column='id_region', blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    server_count = models.IntegerField()
    camera_count = models.IntegerField()
    current_software = models.CharField(max_length=100, blank=True, null=True)
    software_version = models.CharField(max_length=50, blank=True, null=True)
    site_contact_name = models.CharField(max_length=255, blank=True, null=True)
    site_contact_number = models.CharField(max_length=30, blank=True, null=True)
    site_contact_email = models.CharField(max_length=255, blank=True, null=True)
    allocated_site_engineer = models.ForeignKey('TblUsers', models.DO_NOTHING, db_column='allocated_site_engineer', blank=True, null=True)
    is_sira_connected = models.BooleanField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'tbl_site'


class TblUsers(models.Model):
    id_user = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    phone = models.CharField(max_length=30, blank=True, null=True)
    role = models.CharField(max_length=50)
    password_hash = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'tbl_users'
