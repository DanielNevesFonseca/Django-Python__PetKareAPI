from django.db import models


# on_delete não funciona no N:N
class Trait(models.Model):
    name = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # N:N apenas em um campo
    pets = models.ManyToManyField(
        "pets.Pet",
        related_name="traits"
    )
