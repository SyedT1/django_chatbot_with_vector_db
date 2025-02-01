class DatabaseRouter:
    """Routes metadata to MySQL and embeddings to SQLite"""

    def db_for_read(self, model, **hints):
        """Use MySQL for metadata models and SQLite for embeddings"""
        if model.__name__ == "FileMetadata":  # ✅ Metadata should go to MySQL
            return "mysql"
        return "default"  # ✅ Default (SQLite) is for embeddings (ChromaDB)

    def db_for_write(self, model, **hints):
        """Route writes based on model type"""
        if model.__name__ == "FileMetadata":
            return "mysql"
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Allow migrations only for the correct database"""
        if model_name == "filemetadata":  # ✅ Ensure metadata only goes to MySQL
            return db == "mysql"
        return db == "default"  # ✅ Everything else (including embeddings) in SQLite
