from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class TarifaIVA(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text="Código interno de la tarifa de IVA, por ejemplo: IVA_0, IVA_5, IVA_15, IVA_8_TUR."
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de la tarifa, por ejemplo 0.00, 5.00, 15.00.",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        help_text="Descripción del tratamiento tributario y su alcance legal."
    )
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio de vigencia de la tarifa."
    )
    fecha_fin = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de fin de vigencia. Si está vacío, la tarifa se considera vigente indefinidamente."
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si la tarifa está habilitada en el sistema."
    )
    es_temporal = models.BooleanField(
        default=False,
        help_text="Marca si la tarifa es una excepción temporal, como la reducción del 8% para actividades turísticas."
    )
    referencia_normativa = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Tarifa de IVA"
        verbose_name_plural = "Tarifas de IVA"
        ordering = ["porcentaje", "codigo"]

    def __str__(self):
        return f"{self.codigo} ({self.porcentaje}%)"

    def clean(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha final no puede ser anterior a la inicial."})
        if self.es_temporal and not self.fecha_fin:
            raise ValidationError({"fecha_fin": "Una tarifa temporal debe tener fecha final."})


class ClasificacionTributaria(models.Model):
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código interno de clasificación tributaria, por ejemplo: BIEN_NATURAL_0, MATERIAL_CONSTRUCCION_5."
    )
    nombre = models.CharField(
        max_length=255,
        help_text="Nombre de la clasificación tributaria."
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Explicación de qué productos jurídicamente pertenecen a esta clasificación."
    )
    tarifa = models.ForeignKey(
        TarifaIVA,
        on_delete=models.PROTECT,
        related_name="clasificaciones"
    )
    requiere_documentacion = models.BooleanField(
        default=False,
        help_text="Indica si la aplicación de esta clasificación requiere documentación o norma de respaldo."
    )
    fundamento_legal = models.CharField(max_length=255, blank=True)
    codigo_oficial = models.CharField(max_length=80, blank=True)
    es_material_construccion_listado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Clasificación Tributaria"
        verbose_name_plural = "Clasificaciones Tributarias"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.nombre} - {self.tarifa.porcentaje}%"

    def clean(self):
        if self.tarifa_id and self.tarifa.porcentaje == 5 and not self.es_material_construccion_listado:
            raise ValidationError(
                "La tarifa 5% exige una clasificación incluida expresamente en el listado oficial."
            )


class ReglaTemporalIVA(models.Model):
    """Excepción fechada; nunca sustituye a la clasificación ordinaria del producto."""

    codigo = models.CharField(max_length=50, unique=True)
    tarifa = models.ForeignKey(TarifaIVA, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    actividad = models.CharField(max_length=80, default="TURISMO")
    referencia_normativa = models.CharField(max_length=255)
    requiere_registro_turismo = models.BooleanField(default=True)
    requiere_licencia_anual = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    def clean(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha final no puede ser anterior a la inicial."})
        if not self.tarifa.es_temporal:
            raise ValidationError({"tarifa": "La regla debe utilizar una tarifa marcada como temporal."})

    def __str__(self):
        return f"{self.codigo}: {self.tarifa.porcentaje}% ({self.fecha_inicio}–{self.fecha_fin})"
