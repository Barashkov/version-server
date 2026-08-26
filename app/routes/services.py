from flask import Blueprint, request, jsonify, abort
from app.auth import auth
from app.services.data_manager import DataManager
from app.models.schemas import ServiceCreate, ServiceUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)

services_bp = Blueprint('services', __name__)


@services_bp.route('/api/v1.0/services', methods=['GET'])
@auth.login_required
def get_all_services():
    """
    Получить все сервисы со всех площадок.
    ---
    responses:
      200:
        description: Сервисы успешно получены.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    services = data_manager.get_all_services()
    logger.info("Retrieved all services")
    return jsonify({'services': services})


@services_bp.route('/api/v1.0/services/<string:area>', methods=['GET'])
@auth.login_required
def get_services_from_area(area):
    """
    Получить все сервисы с заданной площадки.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
    responses:
      200:
        description: Сервисы с площадки успешно получены.
      404:
        description: Площадка не найдена.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    services = data_manager.get_area_services(area)
    logger.info(f"Retrieved {len(services)} services from area: {area}")
    return jsonify({area: services})


@services_bp.route('/api/v1.0/services/<string:area>/<int:service_id>', methods=['GET'])
@auth.login_required
def get_service_from_area(area, service_id):
    """
    Получить сервис для заданной площадки по его id.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
      - name: service_id
        in: path
        type: integer
        required: true
        description: Id сервиса.
    responses:
      200:
        description: Сервис успешно получен.
      404:
        description: Сервис не найден.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    service = data_manager.get_service(area, service_id)
    if not service:
        logger.warning(f"Service not found: area={area}, id={service_id}")
        return jsonify({'error': 'Service not found'}), 404
    
    logger.info(f"Retrieved service {service_id} from area: {area}")
    return jsonify({'service': service})


@services_bp.route('/api/v1.0/services/<string:area>', methods=['POST'])
@auth.login_required
def create_service(area):
    """
    Создать сервис для заданной площадки.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
    responses:
      200:
        description: Сервис успешно создан.
      400:
        description: Неверные данные запроса.
      404:
        description: Площадка не найдена.
      500:
        description: Сервис с такими параметрами уже существует.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not request.json:
        logger.warning("No JSON data provided")
        return jsonify({'error': 'No JSON data provided'}), 400
    
    try:
        service_data = ServiceCreate.model_validate(request.json)
    except Exception as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    if data_manager.service_exists(area, service_data.name, service_data.type, service_data.url):
        logger.warning(f"Service already exists: {service_data.name} in area {area}")
        return jsonify({'error': 'Service with this Name, Type and URL already exists'}), 500
    
    try:
        service = data_manager.create_service(area, service_data.model_dump())
        logger.info(f"Created service {service['id']} in area {area}")
        return jsonify({'service': service}), 201
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@services_bp.route('/api/v1.0/services/<string:area>/<int:service_id>', methods=['PUT'])
@auth.login_required
def update_service(area, service_id):
    """
    Обновить сервис для заданной площадки по его id.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
      - name: service_id
        in: path
        type: integer
        required: true
        description: Id сервиса.
    responses:
      200:
        description: Сервис успешно обновлен.
      400:
        description: Неверные данные запроса.
      404:
        description: Сервис не найден.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not request.json:
        logger.warning("No JSON data provided")
        return jsonify({'error': 'No JSON data provided'}), 400
    
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    try:
        update_model = ServiceUpdate.model_validate(request.json)
    except Exception as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    
    update_data = update_model.model_dump(exclude_none=True)
    
    if not update_data:
        logger.warning("No valid fields to update")
        return jsonify({'error': 'No valid fields to update'}), 400
    
    service = data_manager.update_service(area, service_id, update_data)
    if not service:
        logger.warning(f"Service not found: area={area}, id={service_id}")
        return jsonify({'error': 'Service not found'}), 404
    
    logger.info(f"Updated service {service_id} in area {area}")
    return jsonify({'service': service}), 200


@services_bp.route('/api/v1.0/services/<string:area>/<int:service_id>', methods=['DELETE'])
@auth.login_required
def delete_service(area, service_id):
    """
    Удалить сервис для заданной площадки по его id.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
      - name: service_id
        in: path
        type: integer
        required: true
        description: Id сервиса.
    responses:
      200:
        description: Сервис успешно удален.
      404:
        description: Сервис не найден.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    success = data_manager.delete_service(area, service_id)
    if not success:
        logger.warning(f"Service not found: area={area}, id={service_id}")
        return jsonify({'error': 'Service not found'}), 404
    
    logger.info(f"Deleted service {service_id} from area {area}")
    return jsonify({'result': True}), 200
