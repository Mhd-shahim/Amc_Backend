from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import TblSite, TblContractor, TblEquipmentDetails, TblContractDetails
from .serializers import SiteSerializer, ContractorSerializer, EquipmentDetailsSerializer, ContractDetailsSerializer, UserCreateSerializer
from .services import create_site, edit_site
from .authentications import TblUsersJWTAuthentication
from .permissions import  IsAuthenticatedTblUser
from django.db.models import Exists, OuterRef
from datetime import date

#---------1.Site APIs----------------

#1. Get all sites
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_sites(request):
    sites = TblSite.objects.all()
    serializer = SiteSerializer(sites, many=True)
    return Response(serializer.data)

#2.Create Site with contract and equipment details
@api_view(['POST'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def create_site_with_details(request):

    site_data = request.data.get('site')
    equipment_data = request.data.get('equipment')
    contract_data = request.data.get('contract')


    if not site_data :
        return Response({'error': 'Site data is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = create_site(contract_data, site_data, equipment_data)
        return Response({
            'site': SiteSerializer(result['site']).data,
            "equipment": EquipmentDetailsSerializer(result["equipment"], many=True).data,
            'contract': ContractDetailsSerializer(result['contract']).data,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#3. Edit Site with contract and equipment details
@api_view(['PATCH'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def edit_site_with_details(request, site_id):
    site_data = request.data.get('site') or {}
    equipment_data = request.data.get('equipment')
    contract_data = request.data.get('contract')

    if not site_data and equipment_data is None and contract_data is None:
        return Response(
            {'error': 'At least one of site, equipment, or contract data is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = edit_site(site_id, site_data, equipment_data, contract_data)

        return Response({
            'site': SiteSerializer(result['site']).data,
            # 'equipment': EquipmentDetailsSerializer(result['equipment'], many=True).data,
            'contract': ContractDetailsSerializer(result['contract']).data if result.get('contract') else None,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#4. Delete Site with contract and equipment details
@api_view(['DELETE'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def delete_site_with_details(request, site_id):
    try:
        site = TblSite.objects.get(pk=site_id)
        site.delete()
        return Response({'message': 'Site and related details deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except TblSite.DoesNotExist:
        return Response({'error': 'Site not found.'}, status=status.HTTP_404_NOT_FOUND)

#5. Get Site Detail with contract and equipment details
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_site_details(request, site_id):
    site = get_object_or_404(TblSite, pk=site_id)

    contract = TblContractDetails.objects.filter(id_site=site).order_by('-id_contract').first()
    equipment = TblEquipmentDetails.objects.filter(id_site=site).order_by('id_equipment_det')

    contract_data = ContractDetailsSerializer(contract).data if contract else None

    if contract_data and getattr(request.user, "role", None) != "super_admin":
       contract_data["contract_amt"] = "****"

    return Response({
        'site': SiteSerializer(site).data,
        'contract': contract_data,
        'equipment': EquipmentDetailsSerializer(equipment, many=True).data,
    })

#6. Get Site details with amc
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_sites_by_amc_status(request):
    today = date.today()

    all_contracts = TblContractDetails.objects.filter(id_site=OuterRef('pk'))
    valid_contracts = all_contracts.filter(contract_end_date__gte=today)

    sites = TblSite.objects.annotate(
        has_amc=Exists(all_contracts),
        has_valid_amc=Exists(valid_contracts),
    )

    sites_without_amc = sites.filter(has_amc=False)
    sites_with_amc = sites.filter(has_valid_amc=True)
    sites_with_amc_expired = sites.filter(has_amc=True, has_valid_amc=False)

    return Response({
        'sites_without_amc': SiteSerializer(sites_without_amc, many=True).data,
        'sites_with_amc': SiteSerializer(sites_with_amc, many=True).data,
        'sites_with_amc_expired': SiteSerializer(sites_with_amc_expired, many=True).data,
    })

#---------2.Equipment APIs----------------

#1.Create Equipment
@api_view(['POST'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def create_equipment(request):
    many = isinstance(request.data, list)

    serializer = EquipmentDetailsSerializer(data=request.data, many=many)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#2.Delete Equipment
@api_view(['DELETE'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def delete_equipment(request, equipment_id):
    try:
        equipment = TblEquipmentDetails.objects.get(pk=equipment_id)
        equipment.delete()
        return Response({'message': 'Equipment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except TblEquipmentDetails.DoesNotExist:
        return Response({'error': 'Equipment not found.'}, status=status.HTTP_404_NOT_FOUND)

#---------3.Contractor APIs----------------

#1. Get all contractors
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_contractors(request):
    
    contractors = TblContractor.objects.all()
    serializer = ContractorSerializer(contractors, many=True)
    return Response(serializer.data)

#2. Create Contractor
@api_view(['POST'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def create_contractor(request):
    serializer = ContractorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#3. Delete Contractor
@api_view(['DELETE'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def delete_contractor(request, contractor_id):
    try:
        contractor = TblContractor.objects.get(pk=contractor_id)
        contractor.delete()
        return Response({'message': 'Contractor deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except TblContractor.DoesNotExist:
        return Response({'error': 'Contractor not found.'}, status=status.HTTP_404_NOT_FOUND)
    
#4. Edit Contractor
@api_view(['PATCH'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def edit_contractor(request, contractor_id):
    try:
        contractor = TblContractor.objects.get(pk=contractor_id)
        serializer = ContractorSerializer(contractor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except TblContractor.DoesNotExist:
        return Response({'error': 'Contractor not found.'}, status=status.HTTP_404_NOT_FOUND)

#####