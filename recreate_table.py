from app import app, db, UserSession

with app.app_context():
    print("Dropping user_session table...")
    UserSession.__table__.drop(db.engine, checkfirst=True)
    
    print("Creating fresh user_session table...")
    UserSession.__table__.create(db.engine, checkfirst=False)
    
    print("✓ Fresh user_session table created with all columns including logout_time")
    
    # Verify the new schema
    import sqlite3
    db_path = 'instance/smart_alert.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user_session);")
    columns = cursor.fetchall()
    
    print("\n✓ Verification - user_session columns:")
    for col in columns:
        nullable = 'NULL' if col[3] == 0 else 'NOT NULL'
        print(f"  {col[1]}: {col[2]} ({nullable})")
    conn.close()
