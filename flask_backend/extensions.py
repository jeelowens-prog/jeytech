"""
Extensions Flask partagées pour éviter les imports circulaires
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialiser le limiter sans l'application (sera lié plus tard avec init_app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)
