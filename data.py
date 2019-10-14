from __future__ import annotations

import yaml
from datetime import date
from dataclasses import dataclass
from itertools import chain
import decimal
from decimal import Decimal

# Rounding required by law
decimal.getcontext().rounding = decimal.ROUND_HALF_UP


@dataclass
class Hacks:
	reverse_charges_paid_on_invoice_date: bool = False


@dataclass
class Entity:
	name: str
	vat_id: str = None
	address: str = None


@dataclass
class Subject(Entity):
	first_name: str = None
	last_name: str = None
	birthdate: date = None
	email: str = None
	phone: str = None
	tax_office_code: str = None
	auth_amount: Decimal = None
	uses_cash_method: bool = False
	pays_health_insurance_since: str = None
	hacks: Hacks = None


@dataclass
class Invoice:
	description: str
	id: str
	date: date
	taxable_amount: Decimal
	paid_on: date = None
	vat_amount_applied: Decimal = 0
	vat_amount_required: Decimal = None
	billed_to: Entity = None
	issuer: Entity = None
	reverse_charge: bool = False
	include_in_vat_registry: bool = True

	@property
	def contractor(self) -> Entity:
		return self.issuer or self.billed_to

	@property
	def tax_date(self):
		return self.paid_on if subject.uses_cash_method else self.date


def load_invoice(data):
	taxable_amount = Decimal(data.pop('taxable_amount')).quantize(Decimal('0.01'))

	try:
		vat_amount = Decimal(data.pop('vat_amount')).quantize(Decimal('0.01'))
	except KeyError:
		vat_amount = None

	try:
		vat_amount_applied = Decimal(data.pop('vat_amount_applied')).quantize(Decimal('0.01'))
	except KeyError:
		vat_amount_applied = vat_amount or Decimal('0.00')

	try:
		vat_amount_required = Decimal(data.pop('vat_amount_required')).quantize(Decimal('0.01'))
	except KeyError:
		vat_amount_required = vat_amount

	calculated_vat_amount_required = (taxable_amount * Decimal('0.23')).quantize(Decimal('0.01'))
	if not vat_amount_required:
		vat_amount_required = calculated_vat_amount_required
	#if vat_amount_required != calculated_vat_amount_required:
	#    print(vat_amount_required, calculated_vat_amount_required, invoice.contractor.name)

	try:
		issuer = Entity(**data.pop('issuer'))
	except KeyError:
		issuer = None

	try:
		billed_to = Entity(**data.pop('billed_to'))
	except KeyError:
		billed_to = None

	try:
		invoice_date = date.fromisoformat(data.pop('date'))
	except KeyError:
		invoice_date = None

	try:
		paid_on = date.fromisoformat(data.pop('paid_on'))
	except KeyError:
		paid_on = None

	include_in_vat_registry = parse_bool(data.pop('include_in_vat_registry', 'true'))

	return Invoice(
		taxable_amount = taxable_amount,
		vat_amount_applied = vat_amount_applied,
		vat_amount_required = vat_amount_required,
		issuer = issuer,
		billed_to = billed_to,
		date = invoice_date,
		paid_on = paid_on,
		include_in_vat_registry = include_in_vat_registry,
		**data
	)


def gen_reverse_charge_invoices(subject, invoices):
	reverse_charge_series = {}

	def gen_reverse_charge_invoices(invoice):
		month = str(invoice.date)[:7]
		num = reverse_charge_series.get(month, 0)
		num += 1
		reverse_charge_series[month] = num
		number = f'B{num}/{invoice.date.month}/{invoice.date.year}'

		return (Invoice(
			description = f'Faktura wewnętrzna dot. faktury {invoice.id}',
			id = number,
			date = invoice.date,
			taxable_amount = invoice.taxable_amount,
			vat_amount_applied = invoice.vat_amount_required,
			vat_amount_required = invoice.vat_amount_required,
			paid_on = invoice.date if subject.hacks.reverse_charges_paid_on_invoice_date else invoice.paid_on,
			issuer = invoice.issuer,
			reverse_charge = True,
		), Invoice(
			description = f'Faktura wewnętrzna dot. faktury {invoice.id}',
			id = number,
			date = invoice.date,
			taxable_amount = invoice.taxable_amount,
			vat_amount_applied = invoice.vat_amount_required,
			vat_amount_required = invoice.vat_amount_required,
			paid_on = invoice.date if subject.hacks.reverse_charges_paid_on_invoice_date else invoice.paid_on,
			billed_to = invoice.issuer,
			reverse_charge = True,
		))

	return list(chain(*(gen_reverse_charge_invoices(invoice) for invoice in invoices if invoice.vat_amount_applied != invoice.vat_amount_required)))


with open('data.yaml') as f:
	data = yaml.load(f.read(), Loader=yaml.BaseLoader)

def parse_bool(s):
	if s.lower() == 'true':
		return True
	if s.lower() == 'false':
		return False
	raise ValueError(s)

raw_subject = data['subject']
raw_hacks = raw_subject.pop('hacks', {})

subject = Subject(
	uses_cash_method = parse_bool(raw_subject.pop('uses_cash_method', 'false')),
	hacks = Hacks(
		reverse_charges_paid_on_invoice_date = parse_bool(raw_hacks.pop('reverse_charges_paid_on_invoice_date', 'false')),
		**raw_hacks,
	),
	**raw_subject,
)

invoices = [load_invoice(invoice) for invoice in data['invoices']]

vat_invoices = sorted([i for i in invoices + gen_reverse_charge_invoices(subject, invoices) if i.include_in_vat_registry], key = lambda i: i.tax_date)
