
TEMPLATE_BASE = "auth/templates/base.html"

# enabled auth systems
import auth_systems
ENABLED_AUTH_SYSTEMS = auth_systems.AUTH_SYSTEMS.keys()
DEFAULT_AUTH_SYSTEM = None