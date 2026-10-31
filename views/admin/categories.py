"""Admin categories view."""

from views.admin.dashboard import _build_categories


def build_categories_view(parent, database_path=None):
    _build_categories(parent, database_path)