class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """Route read operations for specific models."""
        # Check if the model's app_label is in the list
        if model._meta.app_label in ['Local_Church']:
            return 'secondary'  # Use the secondary database for these models
        return 'default'  # Default database for other models

    def db_for_write(self, model, **hints):
        """Route write operations for specific models."""
        # Check if the model's app_label is in the list
        if model._meta.app_label in ['Local_Church']:
            return 'secondary'  # Use the secondary database for these models
        return 'default'  # Default database for other models

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that migrations happen in the correct database."""
        # Check if the app label is in the list for the secondary database
        if app_label in ['Local_Church']:
            return db == 'secondary'
        return db == 'default'
