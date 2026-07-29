from django.db import transaction
from .models import TblSite, TblContractor, TblEquipmentDetails, TblContractDetails
from .serializers import SiteSerializer, ContractDetailsSerializer, EquipmentDetailsSerializer
from django.shortcuts import get_object_or_404

def create_site(contract_data, site_data,equipment_data):
    with transaction.atomic():

        # 1. Create site
        site_serializer = SiteSerializer(data=site_data)
        site_serializer.is_valid(raise_exception=True)
        site = site_serializer.save()

        # 2. Create equipment details
        created_equipment = []
        if(equipment_data is not None):
            for eq in equipment_data:
                eq['id_site'] = site.id_site

                serializer = EquipmentDetailsSerializer(data=eq)
                serializer.is_valid(raise_exception=True)
                equipment = serializer.save()

                created_equipment.append(equipment)

        # 3. Create contract details
        contract_details = None
        if(contract_data is not None):
            contract_data['id_site'] = site.id_site

            contract_details_serializer = ContractDetailsSerializer(data=contract_data)
            contract_details_serializer.is_valid(raise_exception=True)
            contract_details = contract_details_serializer.save()

        return {
            'contract': contract_details,
            'site': site,
            'equipment': created_equipment
        }

def edit_site(id_site, site_data=None, equipment_data=None, contract_data=None, partial=True):
    site_data = site_data or {}

    with transaction.atomic():
        site = get_object_or_404(TblSite, pk=id_site)

        if site_data:
            site_serializer = SiteSerializer(site, data=site_data, partial=partial)
            site_serializer.is_valid(raise_exception=True)
            site = site_serializer.save()

        # if equipment_data is not None:
        #     if isinstance(equipment_data, dict):
        #         equipment_data = [equipment_data]

        #     for item in equipment_data:
        #         equipment_id = item.get('id_equipment_det')

        #         if equipment_id:
        #             equipment = get_object_or_404(TblEquipmentDetails, pk=equipment_id)
        #             serializer = EquipmentDetailsSerializer(
        #                 equipment,
        #                 data=item,
        #                 partial=partial
        #             )
        #         else:
        #             item['id_site'] = site.pk
        #             serializer = EquipmentDetailsSerializer(data=item)

        #         serializer.is_valid(raise_exception=True)
        #         serializer.save()

        if contract_data:
            contract = TblContractDetails.objects.filter(id_site=site).first()

            if contract:
                contract_serializer = ContractDetailsSerializer(
                    contract,
                    data=contract_data,
                    partial=partial
                )
            else:
                contract_data['id_site'] = site.pk
                contract_serializer = ContractDetailsSerializer(data=contract_data)

            contract_serializer.is_valid(raise_exception=True)
            contract_serializer.save()

        return {
            'site': site,
            # 'equipment': TblEquipmentDetails.objects.filter(id_site=site),
            'contract': TblContractDetails.objects.filter(id_site=site).first(),
        }

