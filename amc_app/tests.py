from datetime import date, timedelta
from unittest.mock import patch
from django.test import SimpleTestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from .models import TblContractDetails, TblEquipmentDetails, TblSite
from .serializers import SiteDetailsSerializer
from .views import create_equipment


class SiteDetailsSerializerTests(SimpleTestCase):
    def test_serializes_site_with_related_equipment_and_contract(self):
        site = TblSite(
            site_name='Main Site',
            server_count=2,
            camera_count=4,
            is_sira_connected=True,
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        equipment = TblEquipmentDetails(
            equipment_name='Camera 01',
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        contract = TblContractDetails(
            contract_start_date=date.today(),
            contract_end_date=date.today() + timedelta(days=30),
            currency='AED',
            no_of_ppms=4,
            renewal_reminder_days=15,
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        data = SiteDetailsSerializer(
            instance=site,
            context={'equipment': [equipment], 'contract': contract},
        ).data

        self.assertEqual(data['site_name'], 'Main Site')
        self.assertEqual(len(data['equipment']), 1)
        self.assertEqual(data['equipment'][0]['equipment_name'], 'Camera 01')
        self.assertEqual(data['contract']['currency'], 'AED')


class CreateEquipmentViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_equipment_accepts_array_payload(self):
        request = self.factory.post(
            '/create-equipment/',
            [{
                'id_site': 1,
                'equipment_name': 'Camera 01',
                'equipment_sl_no': 'SL-001',
                'is_active': True,
            }],
            format='json',
        )

        with patch('amc_app.views.EquipmentDetailsSerializer') as mock_serializer:
            mock_serializer.return_value.is_valid.return_value = True
            mock_serializer.return_value.data = [{'equipment_name': 'Camera 01'}]
            mock_serializer.return_value.save.return_value = TblEquipmentDetails(equipment_name='Camera 01', is_active=True)

            response = create_equipment(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, [{'equipment_name': 'Camera 01'}])
