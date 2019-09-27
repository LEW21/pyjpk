from __future__ import annotations

import yaml
from datetime import date
from dataclasses import dataclass
from itertools import chain


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
	auth_amount: float = None
	uses_cash_method: bool = False
	hacks: Hacks = None


@dataclass
class Invoice:
	description: str
	id: str
	date: date
	taxable_amount: str
	paid_on: date = None
	vat_amount_applied: float = 0
	vat_amount_required: float = None
	billed_to: Entity = None
	issuer: Entity = None
	reverse_charge: bool = False

	@property
	def contractor(self) -> Entity:
		return self.issuer or self.billed_to

	@property
	def tax_date(self):
		return self.paid_on if subject.uses_cash_method else self.date


def load_invoice(data):
	taxable_amount = data.pop('taxable_amount')

	try:
		vat_amount = data.pop('vat_amount')
	except KeyError:
		vat_amount = None

	try:
		vat_amount_applied = data.pop('vat_amount_applied')
	except KeyError:
		vat_amount_applied = vat_amount or 0

	try:
		vat_amount_required = data.pop('vat_amount_required')
	except KeyError:
		vat_amount_required = vat_amount

	calculated_vat_amount_required = round(taxable_amount * 0.23, 2)
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

	return Invoice(
		taxable_amount = taxable_amount,
		vat_amount_applied = vat_amount_applied,
		vat_amount_required = vat_amount_required,
		issuer = issuer,
		billed_to = billed_to,
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
	data = yaml.safe_load(f.read())

try:
	hacks = Hacks(**data['subject'].pop('hacks'))
except KeyError:
	hacks = Hacks()

subject = Subject(hacks = hacks, **data['subject'])

invoices = [load_invoice(invoice) for invoice in data['invoices']]
invoices += gen_reverse_charge_invoices(subject, invoices)

invoices = sorted(invoices, key = lambda i: i.tax_date)
