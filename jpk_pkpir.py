import sys
from datetime import datetime, timezone, timedelta

from data import subject, invoices


def to_jpk_pkpir_v2(subject, invoices, month):
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

	wiersz_xml = [f"""
	<PKPIRWiersz typ="G">
		<K_1>{i}</K_1>
		<K_2>{invoice.tax_date}</K_2>
		<K_3>{invoice.id}</K_3>
		<K_4>{invoice.contractor.name}</K_4>
		<K_5>{invoice.contractor.address}</K_5>
		<K_6>{invoice.description}</K_6>
		<K_7>{invoice.taxable_amount if not invoice.issuer and invoice.include_in_vat_registry else 0}</K_7>
		<K_8>{invoice.taxable_amount if not invoice.issuer and not invoice.include_in_vat_registry else 0}</K_8>
		<K_9>{invoice.taxable_amount if not invoice.issuer else 0}</K_9>
		<K_10>0</K_10>
		<K_11>0</K_11>
		<K_12>0</K_12>
		<K_13>{invoice.taxable_amount if invoice.issuer else 0}</K_13>
		<K_14>{invoice.taxable_amount if invoice.issuer else 0}</K_14>
		<K_15>0</K_15>
		<K_16A>brak</K_16A>
		<K_16B>0</K_16B>
	</PKPIRWiersz>
	""" for i, invoice in enumerate(invoices, 1)]

	revenue = sum(invoice.taxable_amount for invoice in invoices if not invoice.issuer)
	costs = sum(invoice.taxable_amount for invoice in invoices if invoice.issuer)
	income = revenue - costs

	return f"""
<JPK xmlns="http://jpk.mf.gov.pl/wzor/2016/10/26/10262/">
	<Naglowek>
		<KodFormularza kodSystemowy="JPK_PKPIR (2)" wersjaSchemy="1-0">JPK_PKPIR</KodFormularza>
		<WariantFormularza>2</WariantFormularza>
		<CelZlozenia>1</CelZlozenia>
		<DataWytworzeniaJPK>{now}</DataWytworzeniaJPK>
		<DataOd>{since}</DataOd>
		<DataDo>{until}</DataDo>
		<NazwaSystemu>pyjpk</NazwaSystemu>
		<DomyslnyKodWaluty>PLN</DomyslnyKodWaluty>
		<KodUrzedu>{subject.tax_office_code}</KodUrzedu>
	</Naglowek>
	<Podmiot1>
		<IdentyfikatorPodmiotu>
			<NIP>{subject.vat_id}</NIP>
			<PelnaNazwa>{subject.name}</PelnaNazwa>
		</IdentyfikatorPodmiotu>
	</Podmiot1>
	<PKPIRInfo>
		<P_1>0</P_1>
		<P_2>0</P_2>
		<P_3>{costs}</P_3>
		<P_4>{income}</P_4>
	</PKPIRInfo>
	{"".join(wiersz_xml)}
	<PKPIRCtrl>
		<LiczbaWierszy>{len(invoices)}</LiczbaWierszy>
		<SumaPrzychodow>{revenue}</SumaPrzychodow>
	</PKPIRCtrl>
</JPK>""".replace('>0.00<', '>0<')

print(to_jpk_pkpir_v2(subject, invoices, sys.argv[1]))
