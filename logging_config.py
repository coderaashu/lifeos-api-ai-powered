
import logging
import json

#formatter turns each log event into JSON object
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })
    
        
def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )


    
    