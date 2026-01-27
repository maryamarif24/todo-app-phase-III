#!/usr/bin/env python3
"""
Script to fix the conversation table schema: change user_id to UUID and add foreign key.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def fix_conversation_table():
    """Fix the conversation table schema."""
    print("Fixing conversation table schema...")

    # Change to backend directory to load .env
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from backend.src.models.database import sync_engine
        from sqlalchemy import text

        with sync_engine.connect() as conn:
            trans = conn.begin()

            # Check if conversation table exists
            result = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'conversation')")).fetchone()
            if not result[0]:
                print("Conversation table does not exist, creating it...")
                # Create table using SQLModel
                from backend.src.models.conversation import Conversation
                from sqlmodel import SQLModel
                SQLModel.metadata.create_all(sync_engine, tables=[Conversation.__table__])
                trans.commit()
                print("Conversation table created successfully!")
                return True

            # Get existing conversation data to preserve
            print("Getting existing conversation data...")
            conv_result = conn.execute(text("SELECT * FROM conversation")).fetchall()
            existing_conversations = [dict(row._mapping) for row in conv_result]
            print(f"Found {len(existing_conversations)} existing conversations to preserve")

            # Drop the conversation table
            print("Dropping conversation table...")
            conn.execute(text("DROP TABLE conversation CASCADE"))

            # Create the conversation table with correct schema
            print("Creating conversation table with correct schema...")
            create_table_sql = """
            CREATE TABLE conversation (
                id VARCHAR(36) PRIMARY KEY,
                user_id UUID NOT NULL,
                metadata_json JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            conn.execute(text(create_table_sql))

            # Add foreign key constraint
            print("Adding foreign key constraint...")
            fk_sql = """
            ALTER TABLE conversation ADD CONSTRAINT fk_conversation_user_id
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            """
            conn.execute(text(fk_sql))

            # Create index
            conn.execute(text("CREATE INDEX idx_conversation_user_id ON conversation(user_id);"))

            # Restore conversation data
            if existing_conversations:
                print(f"Restoring {len(existing_conversations)} conversations...")
                for conv in existing_conversations:
                    # Convert user_id to UUID if it's string
                    user_id = conv['user_id']
                    if isinstance(user_id, str):
                        import uuid
                        try:
                            user_id = uuid.UUID(user_id)
                        except ValueError:
                            print(f"Invalid user_id {user_id}, skipping conversation {conv['id']}")
                            continue

                    # Check if user exists
                    user_exists = conn.execute(
                        text("SELECT 1 FROM users WHERE id = %s"),
                        (str(user_id),)
                    ).fetchone()

                    if user_exists:
                        insert_sql = """
                        INSERT INTO conversation (id, user_id, metadata_json, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        conn.execute(text(insert_sql), (
                            conv['id'],
                            str(user_id),
                            conv.get('metadata_json'),
                            conv['created_at'],
                            conv['updated_at']
                        ))
                        print(f"  Restored conversation: {conv['id']}")
                    else:
                        print(f"  Skipped (user not found): {conv['id']}")

            trans.commit()
            print("Conversation table fixed successfully!")

            # Verify
            verify_result = conn.execute(text("""
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='conversation';
            """)).fetchall()

            print("Foreign key constraints verification:")
            for row in verify_result:
                print(f"  - {row[2]} references {row[3]}.{row[4]}")

        return True

    except Exception as e:
        print(f"Error fixing conversation table: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

        try:
            trans.rollback()
        except:
            pass

        return False

def main():
    print("Starting conversation table fix...\n")
    success = fix_conversation_table()

    if success:
        print("\nSUCCESS: Conversation table has been fixed!")
    else:
        print("\nFAILED: Table fix was unsuccessful.")

if __name__ == "__main__":
    main()
