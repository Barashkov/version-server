from flask import Blueprint, request, jsonify
from app.auth import auth
from app.services.data_manager import DataManager
from app.models.schemas import MessageResponse, ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

areas_bp = Blueprint('areas', __name__)


@areas_bp.route('/api/v1.0/areas', methods=['GET'])
@auth.login_required
def get_areas():
    """
    Получить список всех площадок.
    ---
    responses:
      200:
        description: Список площадок успешно получен.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    areas = data_manager.get_areas()
    logger.info(f"Retrieved {len(areas)} areas")
    return jsonify({'areas': areas})


@areas_bp.route('/api/v1.0/area/<string:area>', methods=['POST'])
@auth.login_required
def create_area(area):
    """
    Создать новую площадку.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
    responses:
      200:
        description: Площадка успешно создана.
      400:
        description: Площадка уже существует.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if data_manager.area_exists(area):
        logger.warning(f"Area already exists: {area}")
        return jsonify({'message': 'Area already exists'}), 400
    
    data_manager.create_area(area)
    logger.info(f"Created area: {area}")
    return jsonify({'message': 'Area added successfully'}), 201


@areas_bp.route('/api/v1.0/area/<string:area>', methods=['DELETE'])
@auth.login_required
def delete_area(area):
    """
    Удалить площадку со всем содержимым.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
    responses:
      200:
        description: Площадка успешно удалена.
      404:
        description: Площадка не найдена.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'message': 'Area not found'}), 404
    
    data_manager.delete_area(area)
    logger.info(f"Deleted area: {area}")
    return jsonify({'message': 'Area deleted successfully'}), 200


@areas_bp.route('/api/v1.0/area/<string:area>', methods=['PUT'])
@auth.login_required
def update_area(area):
    """
    Перезаписать все сервисы для заданной площадки.
    ---
    parameters:
      - name: area
        in: path
        type: string
        required: true
        description: Имя площадки.
    responses:
      200:
        description: Сервисы для площадки успешно обновлены.
      404:
        description: Площадка не найдена.
    """
    from flask import current_app
    data_manager = current_app.extensions['data_manager']
    if not data_manager.area_exists(area):
        logger.warning(f"Area not found: {area}")
        return jsonify({'error': 'Area not found'}), 404
    
    if not request.json or area not in request.json:
        logger.warning(f"Invalid request data for area update: {area}")
        return jsonify({'error': 'Invalid request data'}), 400
    
    services = request.json[area]
    data_manager.update_area(area, services)
    logger.info(f"Updated area: {area} with {len(services)} services")
    return jsonify({'message': 'Area updated successfully'}), 200
