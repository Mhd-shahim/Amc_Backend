from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import TblSite, TblContractor, TblEquipmentDetails, TblContractDetails
from .serializers import SiteSerializer, ContractorSerializer, EquipmentDetailsSerializer, ContractDetailsSerializer, UserCreateSerializer
from .services import create_site, edit_site
from .authentications import TblUsersJWTAuthentication
from .permissions import  IsAuthenticatedTblUser,IsAdminOrSuperAdmin
from django.db.models import Exists, OuterRef, Subquery
from datetime import date
from dateutil.relativedelta import relativedelta

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
        if request.user.role not in ['super_admin']:
            if contract_data:
                contract_data['contract_amt'] = 0
                contract_data['currency'] = 'AED'

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
@permission_classes([IsAdminOrSuperAdmin])
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
@permission_classes([IsAdminOrSuperAdmin])
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

#---------4.Dashboard APIs-----------------

#1. Get Dashboard Data
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_dashboard_data(request):
    today = date.today()

    all_contracts = TblContractDetails.objects.filter(id_site=OuterRef('pk'))
    valid_contracts = all_contracts.filter(contract_end_date__gte=today)

    sites = TblSite.objects.annotate(
        has_amc=Exists(all_contracts),
        has_valid_amc=Exists(valid_contracts),
    )

    sites_without_amc_count = sites.filter(has_amc=False).count()
    sites_with_amc_count = sites.filter(has_valid_amc=True).count()
    sites_with_amc_expired_count = sites.filter(has_amc=True, has_valid_amc=False).count()

    all_equipment = TblEquipmentDetails.objects.all()
    total_equipment_count = all_equipment.count()
    total_servers_count = all_equipment.filter(equipment_type='Server').count()
    total_usb_count = all_equipment.filter(equipment_type='USB').count()
    total_camera_count = all_equipment.filter(equipment_type='Camera').count()

    return Response({
        'sites_without_amc_count': sites_without_amc_count,
        'sites_with_amc_count': sites_with_amc_count,
        'sites_with_amc_expired_count': sites_with_amc_expired_count,
        'total_equipment_count': total_equipment_count,
        'total_servers_count': total_servers_count,
        'total_usb_count': total_usb_count,
        'total_camera_count': total_camera_count,
    })


#2. Get Sites from Last Year
@api_view(['GET'])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_sites_from_last_year(request):

    today = date.today()

    # Example:
    # Aug 2026 -> start from Aug 2025
    start_month = date(today.year - 1, today.month, 1)

    monthly_project_data = []

    # Get latest contract end date for each site
    latest_contract = TblContractDetails.objects.filter(
        id_site=OuterRef('pk')
    ).order_by('-contract_end_date')

    for i in range(12):

        month_start = start_month + relativedelta(months=i)
        month_end = month_start + relativedelta(months=1)

        # All sites that existed before the end of this month
        sites = TblSite.objects.filter(
            created_at__lt=month_end
        ).annotate(
            latest_contract_end_date=Subquery(
                latest_contract.values('contract_end_date')[:1]
            )
        )

        # Active:
        # Contract expires on/after the next month starts
        # OR contract_end_date is NULL
        active_count = sites.filter(
            latest_contract_end_date__gte=month_end
        ).count()

        # Expired:
        # Contract ended before this month finished
        expired_count = sites.filter(
            latest_contract_end_date__lt=month_end
        ).count()

        monthly_project_data.append({
            "month": month_start.strftime("%b"),
            "active": active_count,
            "expired": expired_count
        })

    return Response({
        "monthlyProjectData": monthly_project_data
    })


#3. Get Expired Equipment
@api_view(["GET"])
@authentication_classes([TblUsersJWTAuthentication])
@permission_classes([IsAuthenticatedTblUser])
def get_expired_equipment(request):
    expired_equipment = TblEquipmentDetails.objects.filter(licen_expiry__lt=date.today())
    
    serializer = EquipmentDetailsSerializer(
        expired_equipment,
        many=True,
        context={"request": request},
    )

    all_sites = TblSite.objects.all()

    for i in range(len(serializer.data)):
        site_id = serializer.data[i]["id_site"]
        site = all_sites.filter(id_site=site_id).first()
        if site:
            serializer.data[i]["site_name"] = site.site_name
        else:
            serializer.data[i]["site_name"] = None

    return Response(serializer.data)
   
    