import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataManager:
    """Thread-safe data manager for services.json file operations."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from file with error handling."""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"Data loaded from {self.file_path}")
            else:
                self._data = {}
                self._save_data()
                logger.info(f"Created new data file at {self.file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.file_path}: {e}")
            self._data = {}
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._data = {}
    
    def _save_data(self) -> None:
        """Save data to file with error handling."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Data saved to {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def get_all_services(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all services from all areas."""
        with self._lock:
            return self._data.copy()
    
    def get_areas(self) -> List[str]:
        """Get list of all area names."""
        with self._lock:
            return list(self._data.keys())
    
    def area_exists(self, area: str) -> bool:
        """Check if area exists."""
        with self._lock:
            return area in self._data
    
    def get_area_services(self, area: str) -> Optional[List[Dict[str, Any]]]:
        """Get services for a specific area."""
        with self._lock:
            return self._data.get(area, []).copy()
    
    def create_area(self, area: str) -> bool:
        """Create a new area."""
        with self._lock:
            if area in self._data:
                return False
            self._data[area] = []
            self._save_data()
            logger.info(f"Created area: {area}")
            return True
    
    def delete_area(self, area: str) -> bool:
        """Delete an area and all its services."""
        with self._lock:
            if area not in self._data:
                return False
            del self._data[area]
            self._save_data()
            logger.info(f"Deleted area: {area}")
            return True
    
    def update_area(self, area: str, services: List[Dict[str, Any]]) -> bool:
        """Update all services for an area."""
        with self._lock:
            self._data[area] = services
            self._save_data()
            logger.info(f"Updated area: {area} with {len(services)} services")
            return True
    
    def get_service(self, area: str, service_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific service by ID."""
        with self._lock:
            services = self._data.get(area, [])
            for service in services:
                if service.get('id') == service_id:
                    return service.copy()
            return None
    
    def service_exists(self, area: str, name: str, service_type: str, url: str) -> bool:
        """Check if service with given parameters exists."""
        with self._lock:
            services = self._data.get(area, [])
            return any(
                s.get('name') == name and 
                s.get('type') == service_type and 
                s.get('url') == url 
                for s in services
            )
    
    def create_service(self, area: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service in an area."""
        with self._lock:
            if area not in self._data:
                raise ValueError(f"Area {area} does not exist")
            
            services = self._data[area]
            new_id = 1 if not services else services[-1]['id'] + 1
            
            service = {
                'id': new_id,
                'type': service_data['type'],
                'name': service_data['name'],
                'url': service_data['url'],
                'version': service_data.get('version', ''),
                'status': service_data.get('status', '')
            }
            
            services.append(service)
            self._save_data()
            logger.info(f"Created service {new_id} in area {area}")
            return service.copy()
    
    def update_service(self, area: str, service_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a specific service."""
        with self._lock:
            if area not in self._data:
                return None
            
            services = self._data[area]
            for service in services:
                if service.get('id') == service_id:
                    for key, value in update_data.items():
                        if value is not None:
                            service[key] = value
                    self._save_data()
                    logger.info(f"Updated service {service_id} in area {area}")
                    return service.copy()
            return None
    
    def delete_service(self, area: str, service_id: int) -> bool:
        """Delete a specific service."""
        with self._lock:
            if area not in self._data:
                return False
            
            services = self._data[area]
            for i, service in enumerate(services):
                if service.get('id') == service_id:
                    services.pop(i)
                    self._save_data()
                    logger.info(f"Deleted service {service_id} from area {area}")
                    return True
            return False
