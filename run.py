from app import create_app
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info(f"Starting Version Server on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Environment: {Config.FLASK_ENV}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
