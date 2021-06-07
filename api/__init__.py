from . import utils
from . import classes

from .utils.wrappers import wrap_auth as auth
from .utils.wrappers import wrap_validate as validate

mem = {
    "status": {},
    "stats": {},
    "ready": {}
}