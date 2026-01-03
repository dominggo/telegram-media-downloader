#!/usr/bin/env python3
"""
Database Connection Module
Handles MySQL database connections for Telegram Utilities
"""

import json
import os
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


class DatabaseConfig:
    """Load and manage database configuration from my.json"""

    def __init__(self, config_file='my.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from my.json file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                f"Please create it from my.json.example"
            )

        with open(self.config_file, 'r') as f:
            config = json.load(f)

        if 'database' not in config:
            raise ValueError("Database configuration not found in my.json")

        return config['database']

    def get_telegram_config(self):
        """Get Telegram API configuration"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        return config.get('telegram', {})


class DatabaseConnection:
    """Manage database connections and operations"""

    def __init__(self, config_file='my.json'):
        self.db_config = DatabaseConfig(config_file)
        self.connection = None

    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config.config['host'],
                port=self.db_config.config.get('port', 3306),
                user=self.db_config.config['user'],
                password=self.db_config.config['password'],
                database=self.db_config.config['database'],
                charset=self.db_config.config.get('charset', 'utf8mb4')
            )

            if self.connection.is_connected():
                print(f"Connected to MySQL database: {self.db_config.config['database']}")
                return self.connection

        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL database connection closed")

    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager for database cursor"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor(dictionary=dictionary)
            yield cursor
            self.connection.commit()

        except Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"Database error: {e}")
            raise

        finally:
            if cursor:
                cursor.close()

    def execute_schema(self, schema_file='database_schema.sql'):
        """Execute SQL schema file to create/update database structure"""
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

            with self.get_cursor() as cursor:
                for statement in statements:
                    if statement:
                        cursor.execute(statement)

            print(f"Database schema executed successfully from {schema_file}")

        except Error as e:
            print(f"Error executing schema: {e}")
            raise

    def test_connection(self):
        """Test database connection"""
        try:
            self.connect()
            with self.get_cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL version: {version}")
                return True

        except Error as e:
            print(f"Connection test failed: {e}")
            return False

        finally:
            self.disconnect()


# Convenience functions
def get_db_connection(config_file='my.json'):
    """Get a database connection instance"""
    return DatabaseConnection(config_file)


@contextmanager
def get_db_cursor(config_file='my.json', dictionary=True):
    """Context manager for quick database operations"""
    db = DatabaseConnection(config_file)
    try:
        db.connect()
        with db.get_cursor(dictionary=dictionary) as cursor:
            yield cursor
    finally:
        db.disconnect()


if __name__ == '__main__':
    # Test the database connection
    print("Testing database connection...")
    db = DatabaseConnection()
    if db.test_connection():
        print("\n✓ Database connection successful!")
        print("\nInitializing database schema...")
        db.connect()
        db.execute_schema()
        db.disconnect()
        print("\n✓ Database schema initialized!")
    else:
        print("\n✗ Database connection failed!")
        print("Please check your my.json configuration")
