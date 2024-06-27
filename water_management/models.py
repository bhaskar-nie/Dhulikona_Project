from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

class Person(models.Model):
    ROLE_CHOICES = [
        ('panchayathead', 'Panchayat Head'),
        ('consumer', 'Consumer'),
        ('contractor', 'Contractor'),
    ]

    person_name = models.CharField(max_length=100)
    aadhaar = models.CharField(max_length=16)
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="profile_image", blank=True)
    person_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="consumer")
    password = models.CharField(max_length=128)  # Password field, will be hashed
    is_enabled = models.BooleanField(default=True)
    gram_panchayat = models.ForeignKey('GramPanchayat', related_name='residents', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Ensure password is hashed before saving
        if not self.pk or not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.person_name
    
class Contractor(models.Model):
    contractor_detail = models.ForeignKey(Person, related_name="contractor_person", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.contractor_detail)

class GramPanchayat(models.Model):
    panchayat_name = models.CharField(max_length=100)
    panchayat_address = models.CharField(max_length=100)
    panchayat_head = models.ForeignKey(Person, related_name="panchayathead", on_delete=models.SET_NULL, null=True, blank=True)
    contractor = models.ForeignKey(Contractor, related_name="contractor_assigned_panchayats", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.panchayat_name
    
class WaterUserCommittee(models.Model):
    committee_name = models.CharField(max_length=100)
    committee_head = models.ForeignKey(Person, related_name="watercommitteehead", on_delete=models.SET_NULL, null=True, blank=True)
    committee_panchayat = models.ForeignKey(GramPanchayat, related_name="committeepanchayat", on_delete=models.CASCADE)

    def __str__(self):
        return self.committee_name

class Pipeline(models.Model):
    location = models.CharField(max_length=255)
    gram_panchayat = models.ForeignKey(GramPanchayat, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.location} - {self.gram_panchayat}"

class PumpOperator(models.Model):
    operator = models.ForeignKey(Person, related_name="pump_operator", on_delete=models.CASCADE)
    water_user_committee = models.ForeignKey(WaterUserCommittee, on_delete=models.CASCADE)

    def __str__(self):
        return self.operator.person_name

class WaterQuality(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    test_date = models.DateField()
    arsenic_level = models.FloatField()

    def __str__(self):
        return f"Test on {self.test_date} - Arsenic level: {self.arsenic_level}"

class SupplyFrequency(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    date = models.DateField()
    water_quantity = models.FloatField()

    def __str__(self):
        return f"Supply on {self.date} - Quantity: {self.water_quantity}"

class Maintenance(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    issue_reported = models.TextField()
    resolution_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Issue reported: {self.issue_reported[:30]}..."  # Preview first 30 chars

class FeeCollection(models.Model):
    fee_amount = models.FloatField(default=0)
    fee_date = models.DateField()
    concerned_person= models.ForeignKey(Person, related_name="person_fee", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Fee collected on {self.fee_date} - Amount: {self.fee_amount}"

class FeeRate(models.Model):
    fee_rate = models.IntegerField(default=3)
