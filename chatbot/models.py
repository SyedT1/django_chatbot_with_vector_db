from django.db import models
import uuid

class FileMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "file_metadata" 

    def __str__(self):
        return self.filename


