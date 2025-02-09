from django.db import models
import uuid

class FileMetadata(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    filename = models.CharField(max_length=255)

    class Meta:
        db_table = "file_metadata" 

    def __str__(self):
        return self.filename


