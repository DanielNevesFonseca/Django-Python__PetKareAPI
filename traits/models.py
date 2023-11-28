from django.db import models

# on_delete não funciona no N:N
class Trait(models.Model):
    name = models.CharField(max_length=20, unique=True)
    pets = models.ManyToManyField(
        "pets.Pet",
        related_name="traits"
    )
