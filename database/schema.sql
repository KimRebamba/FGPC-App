
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT,
    contact_number TEXT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'customer'
        CHECK (role IN ('customer', 'admin')),
    profile_image TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    is_deleted INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT,
    image_path TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    is_deleted INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL CHECK (price >= 0),
    duration_minutes INTEGER NOT NULL
        CHECK (duration_minutes > 0),
    image_path TEXT,
    is_available INTEGER NOT NULL DEFAULT 1
        CHECK (is_available IN (0, 1)),
    is_deleted INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES Categories(category_id)
        ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS ServiceImages (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0
        CHECK (is_primary IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (service_id)
        REFERENCES Services(service_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    motorcycle_model TEXT NOT NULL,
    motorcycle_plate TEXT,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    price_at_booking REAL NOT NULL
        CHECK (price_at_booking >= 0),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (
            status IN (
                'pending',
                'confirmed',
                'completed',
                'cancelled',
                'rejected'
            )
        ),
    customer_notes TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0
        CHECK (is_deleted IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,

    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (service_id)
        REFERENCES Services(service_id)
        ON DELETE RESTRICT,

    UNIQUE (appointment_date, appointment_time, service_id)
);

CREATE INDEX IF NOT EXISTS idx_appointments_user
    ON Appointments(user_id);

CREATE INDEX IF NOT EXISTS idx_service_images_service
    ON ServiceImages(service_id);

CREATE INDEX IF NOT EXISTS idx_appointments_date
    ON Appointments(appointment_date);

CREATE INDEX IF NOT EXISTS idx_appointments_status
    ON Appointments(status);
