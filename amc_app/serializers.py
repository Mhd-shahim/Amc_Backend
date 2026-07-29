from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import TblSite, TblContractor, TblEquipmentDetails, TblContractDetails, TblUsers
from django.utils import timezone


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = TblSite

        fields = [
            'id_site',
            'site_name',
            'project_name',
            'project_code',
            'address',
            'id_region',
            'latitude',
            'longitude',
            'server_count',
            'camera_count',
            'current_software',
            'software_version',
            'site_contact_name',
            'site_contact_number',
            'site_contact_email',
            'allocated_site_engineer',
            'is_sira_connected',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

class SiteDetailsSerializer(serializers.ModelSerializer):
    equipment = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()

    class Meta:
        model = TblSite
        fields = [
            'id_site',
            'site_name',
            'project_name',
            'project_code',
            'address',
            'id_region',
            'latitude',
            'longitude',
            'server_count',
            'camera_count',
            'current_software',
            'software_version',
            'site_contact_name',
            'site_contact_number',
            'site_contact_email',
            'allocated_site_engineer',
            'is_sira_connected',
            'is_active',
            'created_at',
            'updated_at',
            'equipment',
            'contract',
        ]

    def get_equipment(self, obj):
        equipment = self.context.get('equipment')
        if equipment is None:
            equipment = TblEquipmentDetails.objects.filter(id_site=obj).order_by('id_equipment_det')
        return EquipmentDetailsSerializer(equipment, many=True).data

    def get_contract(self, obj):
        contract = self.context.get('contract')
        if contract is None:
            contract = TblContractDetails.objects.filter(id_site=obj).order_by('-id_contract').first()
        if contract is None:
            return None
        return ContractDetailsSerializer(contract).data


class EquipmentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TblEquipmentDetails
        fields = [
            'id_site',
            'id_equipment_det',
            'equipment_type',
            'equipment_name',
            'camera_make',
            'camera_model',
            'equipment_sl_no',
            'cam_firmware',
            'engine',
            'licen_expiry',
            'ip_address',
            'mac_address',
            'location_in_site',
            'is_active',
            'last_audited_at',
        ]

    def create(self, validated_data):
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

    def validate_equipment_sl_no(self, value):
        if value and TblEquipmentDetails.objects.filter(
            equipment_sl_no=value
        ).exclude(
            id_equipment_det=getattr(self.instance, "id_equipment_det", None)
        ).exists():
            raise serializers.ValidationError(
                "Equipment serial number already exists."
            )
        return value

class ContractDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblContractDetails
        fields = [
            'contract_ref_no',
            'id_site',
            'id_contractor',
            'id_contract_status',
            'contract_start_date',
            'contract_end_date',
            'contract_amt',
            'currency',
            'no_of_ppms',
            'ppm_frequency',
            'next_ppm_schedule',
            'scope_of_work',
            'contract_document',
            'renewal_reminder_days',
            'is_active',
            'created_by',
        ]


    def create(self, validated_data):
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)
    
class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblContractor
        fields = [
            'id_contractor',
            'company_name',
            'contact_person',
            'contact_phone',
            'contact_email',
            'address',
            'trade_license_no',
            'trade_license_expiry',
            'vat_trn',
            'is_active',
        ]

    def create(self, validated_data):
        validated_data['created_at'] = timezone.now()
        return super().create(validated_data)
        
#-------------------Users-------------------

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = TblUsers
        fields = [
            'id_user',
            'full_name',
            'email',
            'phone',
            'role',
            'password',
            'is_active',
            'created_at',
            'last_login',
        ]
        read_only_fields = ['id_user', 'created_at', 'last_login']

    def validate_role(self, value):
        allowed_roles = ['super_admin', 'admin', 'engineer']
        if value not in allowed_roles:
            raise serializers.ValidationError(
                'Role must be one of: super_admin, admin, engineer.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')

        validated_data['password_hash'] = make_password(password)
        validated_data['created_at'] = timezone.now()
        validated_data['last_login'] = None

        return TblUsers.objects.create(**validated_data)