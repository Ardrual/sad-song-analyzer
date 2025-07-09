from django.db import models
from django.contrib.auth.models import User


class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lyrics = models.TextField()
    sad_score = models.DecimalField(max_digits=3, decimal_places=1)
    tags = models.JSONField(default=list)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sad_score', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.sad_score} - {self.lyrics[:50]}..."
