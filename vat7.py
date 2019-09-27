import sys
from datetime import datetime, date, timezone, timedelta

from data import subject, invoices


def to_vat7(subject, invoices, month):
	year_num = int(month[:4])
	month_num = int(month[5:7])

	invoices = [i for i in invoices if str(i.tax_date).startswith(month)]

	true_issued = [i for i in invoices if i.billed_to and not i.reverse_charge]
	reverse_charge_eu_issued = [i for i in invoices if i.billed_to and i.reverse_charge and i.billed_to.vat_id]
	reverse_charge_usa_issued = [i for i in invoices if i.billed_to and i.reverse_charge and not i.billed_to.vat_id]
	received = [i for i in invoices if i.issuer]

	true_sum = round(sum(i.taxable_amount for i in true_issued))
	true_vat = round(sum(i.vat_amount_applied for i in true_issued))

	reverse_charge_eu_sum = round(sum(i.taxable_amount for i in reverse_charge_eu_issued))
	reverse_charge_eu_vat = round(sum(i.vat_amount_applied for i in reverse_charge_eu_issued))

	reverse_charge_usa_sum = round(sum(i.taxable_amount for i in reverse_charge_usa_issued))
	reverse_charge_usa_vat = round(sum(i.vat_amount_applied for i in reverse_charge_usa_issued))

	issd_sum = true_sum + reverse_charge_usa_sum + reverse_charge_eu_sum
	issd_vat = true_vat + reverse_charge_usa_vat + reverse_charge_eu_vat

	recv_sum = round(sum(i.taxable_amount for i in received))
	recv_vat = round(sum(i.vat_amount_applied for i in received))

	"""
	print("1. Identyfikator podatkowy NIP podatnika")
	print("5 2 5 2 4 6 2 5 3 0")

	print()
	print(month)

	print()
	print("6. Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 22% albo 23%:")
	print(f"{true_sum} {true_vat}")

	print()
	print("11. Import usług z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy")
	print(f"{reverse_charge_usa_sum} {reverse_charge_usa_vat}")

	print()
	print("12. Import usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy")
	print(f"{reverse_charge_eu_sum} {reverse_charge_eu_vat}")

	print()
	print("Nabycie towarów i usług pozostałych")
	print(f"{recv_sum} {recv_vat}")
	"""

	return f"""<?xml version="1.0" encoding="UTF-8"?>
<Deklaracja xmlns="http://crd.gov.pl/wzor/2019/02/11/7013/" xmlns:etd="http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/">
	<Naglowek>
		<KodFormularza kodSystemowy="VAT-7 (19)" kodPodatku="VAT" rodzajZobowiazania="Z" wersjaSchemy="1-0E">VAT-7</KodFormularza>
		<WariantFormularza>19</WariantFormularza>
		<CelZlozenia poz="P_7">1</CelZlozenia>
		<Rok>{year_num}</Rok>
		<Miesiac>{month_num}</Miesiac>
		<KodUrzedu>{subject.tax_office_code}</KodUrzedu>
	</Naglowek>
	<Podmiot1 rola="Podatnik">
		<OsobaFizyczna>
			<etd:NIP>{subject.vat_id}</etd:NIP>
			<etd:ImiePierwsze>{subject.first_name}</etd:ImiePierwsze>
			<etd:Nazwisko>{subject.last_name}</etd:Nazwisko>
			<etd:DataUrodzenia>{subject.birthdate}</etd:DataUrodzenia>
		</OsobaFizyczna>
	</Podmiot1>
	<PozycjeSzczegolowe>

		<P_19>{true_sum}</P_19>
		<P_20>{true_vat}</P_20>
		<P_27>{reverse_charge_usa_sum}</P_27>
		<P_28>{reverse_charge_usa_vat}</P_28>
		<P_29>{reverse_charge_eu_sum}</P_29>
		<P_30>{reverse_charge_eu_vat}</P_30>
		<P_40>{issd_sum}</P_40>
		<P_41>{issd_vat}</P_41>

		<P_45>{recv_sum}</P_45>
		<P_46>{recv_vat}</P_46>
		<P_51>{recv_vat}</P_51>

		<P_54>{issd_vat - recv_vat}</P_54>
		<P_56>0</P_56>
		<P_62>0</P_62>

		<P_72>{subject.email}</P_72>
		<P_73>{subject.phone}</P_73>
		<P_74>{date.today()}</P_74>

	</PozycjeSzczegolowe>
	<Pouczenia>1</Pouczenia>
	<podp:DaneAutoryzujace xmlns:podp="http://e-deklaracje.mf.gov.pl/Repozytorium/Definicje/Podpis/">
		<podp:NIP>{subject.vat_id}</podp:NIP>
		<podp:ImiePierwsze>{subject.first_name}</podp:ImiePierwsze>
		<podp:Nazwisko>{subject.last_name}</podp:Nazwisko>
		<podp:DataUrodzenia>{subject.birthdate}</podp:DataUrodzenia>
		<podp:Kwota>{subject.auth_amount}</podp:Kwota>
	</podp:DaneAutoryzujace>
</Deklaracja>
"""

print(to_vat7(subject, invoices, sys.argv[1]))
