import pytest
from app.services.data_manager import DataManager


class TestDataManager:
    """Test cases for DataManager."""
    
    def test_create_area(self, data_manager):
        """Test creating a new area."""
        result = data_manager.create_area("test_area")
        assert result is True
        assert data_manager.area_exists("test_area")
    
    def test_create_duplicate_area(self, data_manager):
        """Test creating duplicate area returns False."""
        data_manager.create_area("test_area")
        result = data_manager.create_area("test_area")
        assert result is False
    
    def test_delete_area(self, data_manager):
        """Test deleting an area."""
        data_manager.create_area("test_area")
        result = data_manager.delete_area("test_area")
        assert result is True
        assert not data_manager.area_exists("test_area")
    
    def test_delete_nonexistent_area(self, data_manager):
        """Test deleting non-existent area returns False."""
        result = data_manager.delete_area("nonexistent")
        assert result is False
    
    def test_get_areas(self, data_manager):
        """Test getting list of areas."""
        data_manager.create_area("area1")
        data_manager.create_area("area2")
        areas = data_manager.get_areas()
        assert "area1" in areas
        assert "area2" in areas
        assert len(areas) == 2
    
    def test_create_service(self, data_manager):
        """Test creating a service."""
        data_manager.create_area("test_area")
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com",
            "version": "1.0",
            "status": "active"
        }
        service = data_manager.create_service("test_area", service_data)
        assert service["id"] == 1
        assert service["name"] == "test_service"
        assert service["type"] == "web"
    
    def test_create_service_auto_increment(self, data_manager):
        """Test service ID auto-increment."""
        data_manager.create_area("test_area")
        
        service_data = {
            "name": "service1",
            "type": "web",
            "url": "http://example1.com"
        }
        data_manager.create_service("test_area", service_data)
        
        service_data = {
            "name": "service2",
            "type": "api",
            "url": "http://example2.com"
        }
        service = data_manager.create_service("test_area", service_data)
        
        assert service["id"] == 2
    
    def test_create_service_nonexistent_area(self, data_manager):
        """Test creating service in non-existent area raises error."""
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com"
        }
        with pytest.raises(ValueError):
            data_manager.create_service("nonexistent", service_data)
    
    def test_service_exists(self, data_manager):
        """Test checking if service exists."""
        data_manager.create_area("test_area")
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com"
        }
        data_manager.create_service("test_area", service_data)
        
        assert data_manager.service_exists("test_area", "test_service", "web", "http://example.com")
        assert not data_manager.service_exists("test_area", "other", "web", "http://example.com")
    
    def test_get_service(self, data_manager):
        """Test getting a specific service."""
        data_manager.create_area("test_area")
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com"
        }
        created = data_manager.create_service("test_area", service_data)
        service = data_manager.get_service("test_area", created["id"])
        
        assert service is not None
        assert service["id"] == created["id"]
        assert service["name"] == "test_service"
    
    def test_get_nonexistent_service(self, data_manager):
        """Test getting non-existent service returns None."""
        data_manager.create_area("test_area")
        service = data_manager.get_service("test_area", 999)
        assert service is None
    
    def test_update_service(self, data_manager):
        """Test updating a service."""
        data_manager.create_area("test_area")
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com"
        }
        created = data_manager.create_service("test_area", service_data)
        
        update_data = {"version": "2.0", "status": "inactive"}
        updated = data_manager.update_service("test_area", created["id"], update_data)
        
        assert updated["version"] == "2.0"
        assert updated["status"] == "inactive"
        assert updated["name"] == "test_service"  # Unchanged
    
    def test_delete_service(self, data_manager):
        """Test deleting a service."""
        data_manager.create_area("test_area")
        service_data = {
            "name": "test_service",
            "type": "web",
            "url": "http://example.com"
        }
        created = data_manager.create_service("test_area", service_data)
        
        result = data_manager.delete_service("test_area", created["id"])
        assert result is True
        
        service = data_manager.get_service("test_area", created["id"])
        assert service is None
    
    def test_get_area_services(self, data_manager):
        """Test getting all services from an area."""
        data_manager.create_area("test_area")
        
        for i in range(3):
            service_data = {
                "name": f"service{i}",
                "type": "web",
                "url": f"http://example{i}.com"
            }
            data_manager.create_service("test_area", service_data)
        
        services = data_manager.get_area_services("test_area")
        assert len(services) == 3
    
    def test_update_area(self, data_manager):
        """Test updating all services in an area."""
        data_manager.create_area("test_area")
        
        new_services = [
            {"id": 1, "name": "service1", "type": "web", "url": "http://example.com", "version": "", "status": ""},
            {"id": 2, "name": "service2", "type": "api", "url": "http://api.example.com", "version": "", "status": ""}
        ]
        
        result = data_manager.update_area("test_area", new_services)
        assert result is True
        
        services = data_manager.get_area_services("test_area")
        assert len(services) == 2
