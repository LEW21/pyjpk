import sys
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from decimal import Decimal

from data import subject, invoices

@dataclass
class HealthInsurance:
    paid: Decimal
    deductible: Decimal

    def __add__(self, other):
        return HealthInsurance(self.paid + other.paid, self.deductible + other.deductible)

health_insurance = {
    2018: HealthInsurance(Decimal("319.94"), Decimal("275.51")),
    2019: HealthInsurance(Decimal("342.23"), Decimal("294.78")),
}

month_s = sys.argv[1]

year = int(month_s[:4])
month = int(month_s[5:7])

invoices = [i for i in invoices if i.tax_date.year == year and i.tax_date.month <= month]

issued = [i for i in invoices if i.billed_to]
received = [i for i in invoices if i.issuer]

revenue = sum(i.taxable_amount for i in issued)
costs = sum(i.taxable_amount for i in received)
income = revenue - costs

tax_base = income.quantize(Decimal('1')).quantize(Decimal('0.01'))
tax = (Decimal('0.19') * tax_base).quantize(Decimal('0.01'))

pays_health_insurance_since_year = int(subject.pays_health_insurance_since[:4])
pays_health_insurance_since_month = int(subject.pays_health_insurance_since[5:7])

health_insurance = ([health_insurance[year - 1]] if pays_health_insurance_since_year < year else []) + [health_insurance[year]] * (month - 1)
try:
    health_insurance = sum(health_insurance, health_insurance.pop())
except IndexError:
    health_insurance = HealthInsurance(Decimal('0.00'), Decimal('0.00'))

tax_advance = (tax - health_insurance.deductible).quantize(Decimal('1'))

print(f"{year}-01 - {year}-{month:02}")
print()
print(f"Revenue:  {revenue:10}")
print(f"Costs:    {costs:10}")
print(f"Income:   {income:10}")
print()
print(f"Tax base: {tax_base:10}")
print(f"19% PIT:  {tax:10}")
print()
print(f"Health insurance (NFZ) paid: {health_insurance.paid}")
print(f"Health insurance (NFZ) deductible: {health_insurance.deductible}")
print(f"(We assume you're paying regularly, the lowest amount possible.)")
print()
print(f"Cumulative PIT advance payment: {tax_advance} PLN")
print("Don't forget to subtract the PIT advances you've already paid this year!")
print()
