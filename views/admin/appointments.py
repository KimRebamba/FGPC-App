"""Admin appointments view."""

from views.admin.dashboard import _build_appointments


def build_appointments_view(parent, database_path=None):
    _build_appointments(parent, database_path)