from sqlalchemy import text
from src.db.session import get_db, engine

def add_column_if_not_exists(connection, table_name, column_name, column_type):
    dialect = connection.dialect.name
    if dialect == 'sqlite':
        # SQLite check
        check_sql = text(f"PRAGMA table_info({table_name})")
        columns = connection.execute(check_sql).fetchall()
        # columns is a list of tuples (cid, name, type, notnull, dflt_value, pk)
        col_names = [c[1] for c in columns]
        if column_name not in col_names:
            print(f"Adding column {column_name} to {table_name}...")
            alter_sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            connection.execute(alter_sql)
            print(f"Column {column_name} added.")
        else:
            print(f"Column {column_name} already exists in {table_name}.")
    else:
        # Postgres/others check
        check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='{column_name}'")
        result = connection.execute(check_sql).fetchone()
        if not result:
            print(f"Adding column {column_name} to {table_name}...")
            alter_sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            connection.execute(alter_sql)
            print(f"Column {column_name} added.")
        else:
            print(f"Column {column_name} already exists in {table_name}.")

def update_schema():
    with engine.connect() as connection:
        # SQLite doesn't support begin() for DDL in the same way sometimes, but let's try
        # For SQLite, DDL is usually auto-committed or requires specific handling
        if connection.dialect.name == 'sqlite':
             # Just execute directly
             pass
        else:
             connection.begin()
             
        try:
            add_column_if_not_exists(connection, "sanctions", "entity_type", "VARCHAR")
            add_column_if_not_exists(connection, "sanctions", "gender", "VARCHAR")
            add_column_if_not_exists(connection, "sanctions", "url", "VARCHAR")
            add_column_if_not_exists(connection, "sanctions", "un_id", "VARCHAR")
            add_column_if_not_exists(connection, "sanctions", "remark", "TEXT")
            add_column_if_not_exists(connection, "sanctions", "function", "VARCHAR")
            
            if connection.dialect.name != 'sqlite':
                connection.commit()
            print("Schema update completed successfully.")
        except Exception as e:
            if connection.dialect.name != 'sqlite':
                connection.rollback()
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
