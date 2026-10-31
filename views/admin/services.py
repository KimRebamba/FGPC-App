"""Admin services view."""

from views.admin.dashboard import _build_services


def build_services_view(parent, database_path=None):
    _build_services(parent, database_path)