from .echo import router_echo
from .add_post import router_add_post
from .test import router_test
from .edit_post import router_edit
from .free import router_free
from .start import router_start
from .calendar import router_calendar


routers = [
    router_start,
    router_add_post,
    router_free,
    router_edit,
    router_calendar,
    router_test,
    router_echo,
]
