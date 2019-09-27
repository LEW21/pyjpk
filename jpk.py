import sys
from datetime import datetime, timezone, timedelta

from data import subject, invoices


def to_jpk(subject, invoices, month):
	now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

	since_dt = datetime.fromisoformat(month + '-01T00:00:00+00:00')
	month_num = since_dt.month
	tmp = since_dt
	while tmp.month == month_num:
		until_dt = tmp
		tmp += timedelta(days=1)

	since = since_dt.date().isoformat()
	until = until_dt.date().isoformat()

	invoices = [i for i in invoices if str(i.tax_date).startswith(month)]

	issued = [i for i in invoices if i.billed_to]
	received = [i for i in invoices if i.issuer]

	sprzedaz_xml = [f"""
	<SprzedazWiersz>
		<LpSprzedazy>{i}</LpSprzedazy>
		<NrKontrahenta>{invoice.contractor.vat_id or 'brak'}</NrKontrahenta>
		<NazwaKontrahenta>{invoice.contractor.name}</NazwaKontrahenta>
		<AdresKontrahenta>{invoice.contractor.address}</AdresKontrahenta>
		<DowodSprzedazy>{invoice.id}</DowodSprzedazy>
		<DataWystawienia>{invoice.date}</DataWystawienia>
		<DataSprzedazy>{invoice.date}</DataSprzedazy>
		<K_10>0</K_10>
		<K_11>0</K_11>
		<K_12>0</K_12>
		<K_13>0</K_13>
		<K_14>0</K_14>
		<K_15>0</K_15>
		<K_16>0</K_16>
		<K_17>0</K_17>
		<K_18>0</K_18>
		<K_19>{invoice.taxable_amount if not invoice.reverse_charge else 0:1.2f}</K_19>
		<K_20>{invoice.vat_amount_applied if not invoice.reverse_charge else 0:1.2f}</K_20>
		<K_21>0</K_21>
		<K_22>0</K_22>
		<K_23>0</K_23>
		<K_24>0</K_24>
		<K_25>0</K_25>
		<K_26>0</K_26>
		<K_27>{invoice.taxable_amount if invoice.reverse_charge else 0:1.2f}</K_27>
		<K_28>{invoice.vat_amount_applied if invoice.reverse_charge else 0:1.2f}</K_28>
		<K_29>0</K_29>
		<K_30>0</K_30>
		<K_31>0</K_31>
		<K_32>0</K_32>
		<K_33>0</K_33>
		<K_34>0</K_34>
		<K_35>0</K_35>
		<K_36>0</K_36>
		<K_37>0</K_37>
		<K_38>0</K_38>
		<K_39>0</K_39>
	</SprzedazWiersz>
	""" for i, invoice in enumerate(issued, 1)]
	zakup_xml = [f"""
	<ZakupWiersz>
		<LpZakupu>{i}</LpZakupu>
		<NrDostawcy>{invoice.contractor.vat_id or 'brak'}</NrDostawcy>
		<NazwaDostawcy>{invoice.contractor.name}</NazwaDostawcy>
		<AdresDostawcy>{invoice.contractor.address}</AdresDostawcy>
		<DowodZakupu>{invoice.id}</DowodZakupu>
		<DataZakupu>{invoice.date}</DataZakupu>
		<DataWplywu>{invoice.date}</DataWplywu>
		<K_43>0</K_43>
		<K_44>0</K_44>
		<K_45>{invoice.taxable_amount:1.2f}</K_45>
		<K_46>{invoice.vat_amount_applied:1.2f}</K_46>
		<K_47>0</K_47>
		<K_48>0</K_48>
		<K_49>0</K_49>
		<K_50>0</K_50>
	</ZakupWiersz>
	""" for i, invoice in enumerate(received, 1)]

	return f"""
<JPK xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://jpk.mf.gov.pl/wzor/2017/11/13/1113/">
	<Naglowek>
		<KodFormularza kodSystemowy="JPK_VAT (3)" wersjaSchemy="1-1">JPK_VAT</KodFormularza>
		<WariantFormularza>3</WariantFormularza>
		<CelZlozenia>0</CelZlozenia>
		<DataWytworzeniaJPK>{now}</DataWytworzeniaJPK>
		<DataOd>{since}</DataOd>
		<DataDo>{until}</DataDo>
		<NazwaSystemu>pyjpk</NazwaSystemu>
	</Naglowek>
	<Podmiot1>
		<NIP>{subject.vat_id}</NIP>
		<PelnaNazwa>{subject.name}</PelnaNazwa>
	</Podmiot1>
	{"".join(sprzedaz_xml)}
	<SprzedazCtrl>
		<LiczbaWierszySprzedazy>{len(issued)}</LiczbaWierszySprzedazy>
		<PodatekNalezny>{sum(i.vat_amount_applied for i in issued):1.2f}</PodatekNalezny>
	</SprzedazCtrl>
	{"".join(zakup_xml)}
	<ZakupCtrl>
		<LiczbaWierszyZakupow>{len(received)}</LiczbaWierszyZakupow>
		<PodatekNaliczony>{sum(i.vat_amount_applied for i in received):1.2f}</PodatekNaliczony>
	</ZakupCtrl>
</JPK>
	""".replace('>0.00<', '>0<')

print(to_jpk(subject, invoices, sys.argv[1]))
