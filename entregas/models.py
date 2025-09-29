from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

def default_hoje():
    return timezone.now().date()  # Retorna apenas a data

class Funcionario(models.Model):
    nome = models.CharField(max_length=200)
    matricula = models.CharField(max_length=50, unique=True)
    token = models.CharField(max_length=36, unique=True, editable=False, default='')

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Retirada(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='retiradas')
    criado_em = models.DateTimeField(default=timezone.now, editable=False)
    data = models.DateField(default=default_hoje)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['funcionario', 'data'], name='uma_retirada_por_dia')
        ]
        ordering = ['-criado_em']

    def clean(self):
        # Garante uma por dia (extra safety)
        if Retirada.objects.exclude(pk=self.pk).filter(funcionario=self.funcionario, data=self.data).exists():
            raise ValidationError('Funcionário já retirou a marmita neste dia.')

    def __str__(self):
        return f"{self.funcionario} - {self.data} {self.criado_em.strftime('%H:%M')}"
