"""Admin users view."""

from views.admin.dashboard import _build_users


def build_users_view(parent, database_path=None):
    _build_users(parent, database_path)