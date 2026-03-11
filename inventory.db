import sqlite3
from datetime import datetime

DB_NAME = "inventory.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def initialize_db():
    """Create tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            price       REAL    NOT NULL DEFAULT 0.0,
            quantity    INTEGER NOT NULL DEFAULT 0,
            min_stock   INTEGER NOT NULL DEFAULT 5,
            description TEXT,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Activity log table  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            action      TEXT NOT NULL,
            product_id  INTEGER,
            details     TEXT,
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


# ─────────────────────────────────────────────
#  PRODUCT FUNCTIONS
# ─────────────────────────────────────────────

def add_product(name, category, price, quantity, min_stock=5, description=""):
    """Add a new product. Returns the new product's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, price, quantity, min_stock, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, price, quantity, min_stock, description))
    product_id = cursor.lastrowid
    _log_action(cursor, "ADD", product_id, f"Added '{name}' (qty: {quantity})")
    conn.commit()
    conn.close()
    return product_id


def get_all_products():
    """Return all products as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_product_by_id(product_id):
    """Return a single product by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_products(query):
    """Search products by name or category."""
    conn = get_connection()
    cursor = conn.cursor()
    like = f"%{query}%"
    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR category LIKE ?
        ORDER BY name ASC
    """, (like, like))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_product(product_id, name, category, price, quantity, min_stock, description=""):
    """Update an existing product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name=?, category=?, price=?, quantity=?, min_stock=?, description=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (name, category, price, quantity, min_stock, description, product_id))
    _log_action(cursor, "EDIT", product_id, f"Updated '{name}'")
    conn.commit()
    conn.close()


def delete_product(product_id):
    """Delete a product by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    product = get_product_by_id(product_id)
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    if product:
        _log_action(cursor, "DELETE", product_id, f"Deleted '{product['name']}'")
    conn.commit()
    conn.close()


def get_low_stock_products():
    """Return products where quantity is at or below min_stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE quantity <= min_stock
        ORDER BY quantity ASC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────────
#  DASHBOARD STATS
# ─────────────────────────────────────────────

def get_dashboard_stats():
    """Return summary stats for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_items = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price * quantity) FROM products")
    total_value = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_stock")
    low_stock_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
    total_categories = cursor.fetchone()[0]

    conn.close()
    return {
        "total_products":   total_products,
        "total_items":      total_items,
        "total_value":      round(total_value, 2),
        "low_stock_count":  low_stock_count,
        "total_categories": total_categories,
    }


# ─────────────────────────────────────────────
#  ACTIVITY LOG
# ─────────────────────────────────────────────

def _log_action(cursor, action, product_id, details):
    """Internal: write to the activity log (uses existing cursor)."""
    cursor.execute("""
        INSERT INTO activity_log (action, product_id, details)
        VALUES (?, ?, ?)
    """, (action, product_id, details))


def get_recent_activity(limit=10):
    """Return the most recent activity log entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM activity_log
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────────
#  QUICK TEST — run this file directly to test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    initialize_db()

    # Add sample products
    add_product("Apple iPhone 15",    "Electronics",  55000, 10, 3, "Latest iPhone model")
    add_product("Samsung Galaxy S24", "Electronics",  48000, 2,  3, "Android flagship")
    add_product("Office Chair",       "Furniture",    8500,  15, 5, "Ergonomic chair")
    add_product("Ballpen Box",        "Stationery",   120,   3,  10, "Box of 12 ballpens")
    add_product("A4 Bond Paper",      "Stationery",   350,   50, 10, "500 sheets per ream")

    print("\n📦 All Products:")
    for p in get_all_products():
        print(f"  [{p['id']}] {p['name']} | Qty: {p['quantity']} | ₱{p['price']}")

    print("\n⚠️  Low Stock:")
    for p in get_low_stock_products():
        print(f"  {p['name']} — only {p['quantity']} left!")

    print("\n📊 Dashboard Stats:")
    stats = get_dashboard_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n📝 Recent Activity:")
    for log in get_recent_activity():
        print(f"  [{log['timestamp']}] {log['action']} — {log['details']}")