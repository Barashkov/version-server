import pytest
import json
from app import create_app


@pytest.fixture
def client(temp_data_file):
    """Create a test client for the Flask application."""
    app = create_app(data_file=temp_data_file)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    import base64
    from app.config import Config
    credentials = base64.b64encode(
        f"{Config.AUTH_USERNAME}:{Config.AUTH_PASSWORD}".encode()
    ).decode()
    return {'Authorization': f'Basic {credentials}'}


class TestAreasAPI:
    """Test cases for Areas API endpoints."""
    
    def test_get_areas_empty(self, client, auth_headers):
        """Test getting areas when none exist."""
        response = client.get('/api/v1.0/areas', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'areas' in data
        assert data['areas'] == []
    
    def test_create_area(self, client, auth_headers):
        """Test creating a new area."""
        response = client.post('/api/v1.0/area/test_area', headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_create_duplicate_area(self, client, auth_headers):
        """Test creating duplicate area."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        response = client.post('/api/v1.0/area/test_area', headers=auth_headers)
        assert response.status_code == 400
    
    def test_delete_area(self, client, auth_headers):
        """Test deleting an area."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        response = client.delete('/api/v1.0/area/test_area', headers=auth_headers)
        assert response.status_code == 200
    
    def test_delete_nonexistent_area(self, client, auth_headers):
        """Test deleting non-existent area."""
        response = client.delete('/api/v1.0/area/nonexistent', headers=auth_headers)
        assert response.status_code == 404
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access."""
        response = client.get('/api/v1.0/areas')
        assert response.status_code == 401


class TestServicesAPI:
    """Test cases for Services API endpoints."""
    
    def test_get_all_services_empty(self, client, auth_headers):
        """Test getting all services when none exist."""
        response = client.get('/api/v1.0/services', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'services' in data
    
    def test_create_service(self, client, auth_headers):
        """Test creating a service."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com',
            'version': '1.0',
            'status': 'active'
        }
        response = client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'service' in data
        assert data['service']['name'] == 'test_service'
    
    def test_create_service_missing_fields(self, client, auth_headers):
        """Test creating service with missing required fields."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {'name': 'test_service'}
        response = client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_create_service_nonexistent_area(self, client, auth_headers):
        """Test creating service in non-existent area."""
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com'
        }
        response = client.post(
            '/api/v1.0/services/nonexistent',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_get_services_from_area(self, client, auth_headers):
        """Test getting services from a specific area."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com'
        }
        client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        
        response = client.get('/api/v1.0/services/test_area', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'test_area' in data
        assert len(data['test_area']) == 1
    
    def test_get_service_by_id(self, client, auth_headers):
        """Test getting a specific service by ID."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com'
        }
        create_response = client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        service_id = json.loads(create_response.data)['service']['id']
        
        response = client.get(f'/api/v1.0/services/test_area/{service_id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'service' in data
        assert data['service']['id'] == service_id
    
    def test_update_service(self, client, auth_headers):
        """Test updating a service."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com'
        }
        create_response = client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        service_id = json.loads(create_response.data)['service']['id']
        
        update_data = {'version': '2.0', 'status': 'inactive'}
        response = client.put(
            f'/api/v1.0/services/test_area/{service_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['service']['version'] == '2.0'
    
    def test_delete_service(self, client, auth_headers):
        """Test deleting a service."""
        client.post('/api/v1.0/area/test_area', headers=auth_headers)
        
        service_data = {
            'name': 'test_service',
            'type': 'web',
            'url': 'http://example.com'
        }
        create_response = client.post(
            '/api/v1.0/services/test_area',
            data=json.dumps(service_data),
            content_type='application/json',
            headers=auth_headers
        )
        service_id = json.loads(create_response.data)['service']['id']
        
        response = client.delete(f'/api/v1.0/services/test_area/{service_id}', headers=auth_headers)
        assert response.status_code == 200
