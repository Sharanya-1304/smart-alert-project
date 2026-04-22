from app import db, UserSession

# Get all columns from the model
columns = UserSession.__table__.columns
print('✓ UserSession columns in the model definition:')
for col in columns:
    print(f'  {col.name}: {col.type} (nullable: {col.nullable})')

print(f'\n✓ Total columns in model: {len(list(columns))}')
