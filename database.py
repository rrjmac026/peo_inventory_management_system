import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "assetmate.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            full_name  TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            contact    TEXT,
            email      TEXT,
            phone      TEXT,
            address    TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            supplier_id INTEGER REFERENCES suppliers(id),
            quantity    INTEGER NOT NULL DEFAULT 0,
            min_stock   INTEGER NOT NULL DEFAULT 1,
            unit_value  REAL    NOT NULL DEFAULT 0.0,
            condition   TEXT    DEFAULT 'Good',
            location    TEXT,
            serial_no   TEXT,
            description TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user       TEXT,
            action     TEXT NOT NULL,
            target     TEXT,
            details    TEXT,
            timestamp  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Default admin account
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator")
        )

    # Default categories
    defaults = ["Computers & IT", "Furniture", "Office Equipment", "Tools & Machinery", "Vehicles", "Others"]
    for cat in defaults:
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

    conn.commit()
    conn.close()


# ── AUTH ───────────────────────────────────────────────────────────────────────
def login(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── USERS ──────────────────────────────────────────────────────────────────────
def get_all_users():
    conn = get_connection()
    rows = [dict(r) for r in conn.execute("SELECT * FROM users ORDER BY username")]
    conn.close()
    return rows

def add_user(username, password, full_name=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
            (username, hash_password(password), full_name)
        )
        conn.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = get_connection()
    conn.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


# ── CATEGORIES ─────────────────────────────────────────────────────────────────
def get_all_categories():
    conn = get_connection()
    rows = [dict(r) for r in conn.execute("""
        SELECT c.*, COUNT(a.id) as asset_count
        FROM categories c
        LEFT JOIN assets a ON a.category_id = c.id
        GROUP BY c.id ORDER BY c.name
    """)]
    conn.close()
    return rows

def get_category_names():
    conn = get_connection()
    rows = [r[0] for r in conn.execute("SELECT name FROM categories ORDER BY name")]
    conn.close()
    return rows

def add_category(name):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True, "Category added."
    except sqlite3.IntegrityError:
        return False, "Category already exists."
    finally:
        conn.close()

def rename_category(cat_id, new_name):
    conn = get_connection()
    try:
        conn.execute("UPDATE categories SET name=? WHERE id=?", (new_name, cat_id))
        conn.commit()
        return True, "Category renamed."
    except sqlite3.IntegrityError:
        return False, "Name already exists."
    finally:
        conn.close()

def delete_category(cat_id):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()


# ── SUPPLIERS ──────────────────────────────────────────────────────────────────
def get_all_suppliers():
    conn = get_connection()
    rows = [dict(r) for r in conn.execute("SELECT * FROM suppliers ORDER BY name")]
    conn.close()
    return rows

def get_supplier_names():
    conn = get_connection()
    rows = [r[0] for r in conn.execute("SELECT name FROM suppliers ORDER BY name")]
    conn.close()
    return rows

def add_supplier(name, contact="", email="", phone="", address=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO suppliers (name, contact, email, phone, address) VALUES (?,?,?,?,?)",
        (name, contact, email, phone, address)
    )
    conn.commit()
    conn.close()

def update_supplier(sup_id, name, contact, email, phone, address):
    conn = get_connection()
    conn.execute(
        "UPDATE suppliers SET name=?, contact=?, email=?, phone=?, address=? WHERE id=?",
        (name, contact, email, phone, address, sup_id)
    )
    conn.commit()
    conn.close()

def delete_supplier(sup_id):
    conn = get_connection()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sup_id,))
    conn.commit()
    conn.close()

def get_supplier_by_id(sup_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM suppliers WHERE id=?", (sup_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── ASSETS ─────────────────────────────────────────────────────────────────────
def get_all_assets():
    conn = get_connection()
    rows = [dict(r) for r in conn.execute("""
        SELECT a.*, c.name as category_name, s.name as supplier_name
        FROM assets a
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN suppliers s ON a.supplier_id = s.id
        ORDER BY a.name ASC
    """)]
    conn.close()
    return rows

def get_asset_by_id(asset_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT a.*, c.name as category_name, s.name as supplier_name
        FROM assets a
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN suppliers s ON a.supplier_id = s.id
        WHERE a.id=?
    """, (asset_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def search_assets(query="", category_id=None):
    conn = get_connection()
    sql = """
        SELECT a.*, c.name as category_name, s.name as supplier_name
        FROM assets a
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN suppliers s ON a.supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if query:
        sql += " AND (a.name LIKE ? OR a.serial_no LIKE ? OR a.location LIKE ?)"
        like = f"%{query}%"
        params += [like, like, like]
    if category_id:
        sql += " AND a.category_id = ?"
        params.append(category_id)
    sql += " ORDER BY a.name ASC"
    rows = [dict(r) for r in conn.execute(sql, params)]
    conn.close()
    return rows

def add_asset(name, category_id, supplier_id, quantity, min_stock,
              unit_value, condition, location, serial_no, description, user="system"):
    conn = get_connection()
    conn.execute("""
        INSERT INTO assets
        (name, category_id, supplier_id, quantity, min_stock, unit_value,
         condition, location, serial_no, description)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (name, category_id, supplier_id, quantity, min_stock,
          unit_value, condition, location, serial_no, description))
    _log(conn, user, "ADD", "asset", f"Added asset '{name}' (qty: {quantity})")
    conn.commit()
    conn.close()

def update_asset(asset_id, name, category_id, supplier_id, quantity, min_stock,
                 unit_value, condition, location, serial_no, description, user="system"):
    conn = get_connection()
    conn.execute("""
        UPDATE assets SET name=?, category_id=?, supplier_id=?, quantity=?,
        min_stock=?, unit_value=?, condition=?, location=?, serial_no=?,
        description=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (name, category_id, supplier_id, quantity, min_stock,
          unit_value, condition, location, serial_no, description, asset_id))
    _log(conn, user, "EDIT", "asset", f"Updated asset '{name}'")
    conn.commit()
    conn.close()

def delete_asset(asset_id, user="system"):
    conn = get_connection()
    a = get_asset_by_id(asset_id)
    conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    if a:
        _log(conn, user, "DELETE", "asset", f"Deleted asset '{a['name']}'")
    conn.commit()
    conn.close()

def get_low_stock_assets():
    conn = get_connection()
    rows = [dict(r) for r in conn.execute("""
        SELECT a.*, c.name as category_name
        FROM assets a
        LEFT JOIN categories c ON a.category_id = c.id
        WHERE a.quantity <= a.min_stock
        ORDER BY a.quantity ASC
    """)]
    conn.close()
    return rows


# ── DASHBOARD STATS ────────────────────────────────────────────────────────────
def get_dashboard_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM assets");                              total_assets     = c.fetchone()[0]
    c.execute("SELECT SUM(quantity) FROM assets");                         total_units      = c.fetchone()[0] or 0
    c.execute("SELECT SUM(unit_value * quantity) FROM assets");            total_value      = c.fetchone()[0] or 0.0
    c.execute("SELECT COUNT(*) FROM assets WHERE quantity <= min_stock");  low_stock_count  = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT category_id) FROM assets");           total_categories = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM suppliers");                           total_suppliers  = c.fetchone()[0]
    conn.close()
    return {
        "total_assets":     total_assets,
        "total_units":      total_units,
        "total_value":      round(total_value, 2),
        "low_stock_count":  low_stock_count,
        "total_categories": total_categories,
        "total_suppliers":  total_suppliers,
    }


# ── ACTIVITY LOG ───────────────────────────────────────────────────────────────
def _log(conn, user, action, target, details):
    conn.execute(
        "INSERT INTO activity_log (user, action, target, details) VALUES (?,?,?,?)",
        (user, action, target, details)
    )

def get_recent_activity(limit=20):
    conn = get_connection()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (limit,)
    )]
    conn.close()
    return rows

def log_action(user, action, target, details):
    conn = get_connection()
    _log(conn, user, action, target, details)
    conn.commit()
    conn.close()


# ── REPORTS ────────────────────────────────────────────────────────────────────
def get_assets_for_report(category_id=None):
    return search_assets(category_id=category_id)