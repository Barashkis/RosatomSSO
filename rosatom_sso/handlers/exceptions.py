class ActivityIdError(Exception):
    pass


class ActivityPointsError(Exception):
    pass


class AdminActivityIdError(ActivityIdError):
    pass


class InputDateError(Exception):
    pass


class UserActivityIdError(ActivityIdError):
    pass
