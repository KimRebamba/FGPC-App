"""Create a repeatable development dataset for FGP Motorcycle Gear.

Run from the project root with:
    python database/seed.py

The default administrator is:
    Email: admin@example.com
    Password: admin12345
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from controllers.auth_controller import register_user
from database.db import initialize_database
from models.category import Category
from models.service import Service
from models.user import User

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin12345"


def seed(database_path: str | None = None) -> None:
    """Initialize the database and insert gear development records."""
    initialize_database(database_path)

    admin = User.find_by_email(ADMIN_EMAIL, database_path)
    if admin is None:
        admin = register_user(
            "System",
            "Administrator",
            ADMIN_EMAIL,
            ADMIN_PASSWORD,
            role="admin",
            database_path=database_path,
        )
        print(f"Created admin account: {ADMIN_EMAIL}")
    elif admin.role != "admin":
        raise RuntimeError(
            f"{ADMIN_EMAIL} already belongs to a non-admin account; refusing to change it."
        )
    else:
        print(f"Admin account already exists: {ADMIN_EMAIL}")

    
    if not admin.profile_image:
        admin.update_profile(
            first_name=admin.first_name,
            last_name=admin.last_name,
            address=admin.address,
            contact_number=admin.contact_number,
            profile_image="uploads/avatar_default.jpg",
            database_path=database_path,
        )
        print("Set admin avatar image.")

    category_data = (
        (
            "Helmets",
            "Full-face, modular, and track helmet deep sanitization, visor fitting, and ceramic coating.",
            "uploads/helmet.jpg",
        ),
        (
            "Jackets",
            "Leather and textile riding jacket reconditioning, waterproofing, and impact armor fitting.",
            "uploads/jacket.jpg",
        ),
        (
            "Gloves",
            "Full-grain leather glove restoration, carbon knuckle polishing, and seam re-stitching.",
            "uploads/gloves.jpg",
        ),
        (
            "Boots",
            "Riding boot waterproof hydrophobic treatment, sole re-attachment, and deep conditioning.",
            "uploads/boots.jpg",
        ),
    )
    categories: dict[str, Category] = {}
    for name, description, img in category_data:
        category = next(
            (item for item in Category.list_all(database_path=database_path)
             if item.category_name == name),
            None,
        )
        if category is None:
            category = Category.create(name, description, image_path=img, database_path=database_path)
            print(f"Created category: {name}")
        else:
            Category.update(category.category_id, name, description, image_path=img, database_path=database_path)
        categories[name] = category

    services = (
        (
            "Helmets",
            "Helmet Deep Sanitization & Ceramic Shield",
            "Ultrasonic padding sanitization, EPS liner inspection, and hydrophobic ceramic shell coat.",
            1850.0,
            30,
            "uploads/helmet.jpg",
        ),
        (
            "Helmets",
            "Visor Fitting & Pinlock Anti-Fog Service",
            "Precision visor adjustment, mechanism lubrication, and dual-pane anti-fog insert install.",
            650.0,
            15,
            "uploads/helmet.jpg",
        ),
        (
            "Jackets",
            "Leather Jacket Reconditioning & Waterproofing",
            "Deep pH-balanced cleaning, natural oil rehydration, and storm-proof hydrophobic sealing.",
            2400.0,
            45,
            "uploads/jacket.jpg",
        ),
        (
            "Jackets",
            "Armor Impact Pad Inspection & Custom Fitting",
            "CE Level 2 armor alignment, pocket seam reinforcement, and ergonomic body contouring.",
            950.0,
            25,
            "uploads/jacket.jpg",
        ),
        (
            "Gloves",
            "Apex Carbon Glove Seam Repair & Leather Balm",
            "Heavy-duty Kevlar thread re-stitching, knuckle buffing, and moisture-barrier balm.",
            850.0,
            20,
            "uploads/gloves.jpg",
        ),
        (
            "Boots",
            "Riding Boot Deep Clean & Hydrophobic Treatment",
            "Mud/grime extraction, leather nourishment, sole bonding check, and weather seal.",
            1200.0,
            35,
            "uploads/boots.jpg",
        ),
    )
    existing_services = Service.list_all(database_path=database_path)
    for category_name, name, description, price, duration, img in services:
        matched = next((item for item in existing_services if item.service_name == name), None)
        if matched is None:
            Service.create(
                categories[category_name].category_id,
                name,
                price,
                duration,
                description,
                image_path=img,
                database_path=database_path,
            )
            print(f"Created gear service: {name}")
        elif not matched.image_path:
            Service.update(
                matched.service_id,
                matched.category_id,
                name,
                price,
                duration,
                description,
                image_path=img,
                database_path=database_path,
            )


if __name__ == "__main__":
    seed()
    print("Seed completed successfully.")