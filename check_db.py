import sqlite3

db = sqlite3.connect('instance/smart_alert.db')
cursor = db.cursor()

# Check user_session table
cursor.execute('PRAGMA table_info(user_session);')
columns = cursor.fetchall()

print('✓ user_session table schema:')
for col in columns:
    nullable = 'NULL' if col[3] == 0 else 'NOT NULL'
    print(f'  {col[1]}: {col[2]} ({nullable})')

# Check row count
cursor.execute('SELECT COUNT(*) FROM user_session;')
count = cursor.fetchone()[0]
print(f'\n✓ Total rows in user_session: {count}')

db.close()
print('\n✓ Database verification complete')
