# Tax document generator for small businesses in Poland
This is a set of scripts for automated single-entry accounting (*Podatkowa Księga Przychodów i Rozchodów*) and **JPK_VAT**, **JPK_PKPIR** and **VAT-7** generation for small businesses in **Poland**.

## Usage
1. Check out the repo.
2. Create a file named `data.yaml`, with content similar to this:
```
subject:
  vat_id: 5252462530
  name: LEW21 Linus Lewandowski
  first_name: Linus
  last_name: Lewandowski
  birthdate: 1992-11-06
  email: linus@lew21.net
  phone: +48123456789
  auth_amount: 1234
  tax_office_code: 1435 # Pierwszy Urząd Skarbowy - Warszawa Śródmieście
  uses_cash_method: false # or true
  pays_health_insurance_since: 2019-01



contractors:
  netguru: &netguru
    vat_id: 7781454968
    name: NETGURU SPÓŁKA AKCYJNA
    address: ul. Wojskowa 6, 60-792 Poznań

  ovh: &ovh
    vat_id: 8992520556
    name: OVH SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ
    address: ul. Swobodna 1, 50-088 Wrocław

  google: &google
    vat_id: IE6388047V
    name: Google Ireland Limited
    address: Gordon House, Barrow Street, Dublin 4

  heroku: &heroku
    name: Heroku, Inc.
    address: 1 Market St. Suite 300, 94105 San Francisco, CA



invoices:

- date: 2019-03-30
  paid_on: 2019-04-01 # You need paid_on only if you're using cash method.
  issuer: *ovh
  id: PL2436776/F
  description: aiakos.co, aiakos.me, aiakos.net
  taxable_amount: 203.92
  vat_amount: 46.90

- date: 2019-03-31
  paid_on: 2019-04-02
  billed_to: *netguru
  id: A1/3/2019
  description: Usługi programistyczne
  taxable_amount: 2000
  vat_amount: 460

- date: 2019-03-31
  paid_on: 2019-04-02
  issuer: *google
  id: 3571748692
  description: Serwer
  taxable_amount: 0.12

- date: 2019-03-31
  paid_on: 2019-04-09
  issuer: *heroku
  id: 24963482
  description: Serwer
  taxable_amount: 187.99
```
3. Run `python jpk_vat.py 2019-03` to generate a JPK_VAT file
4. Run `python vat7.py 2019-03` to generate a VAT-7 file
5. Run `python pit.py 2019-03` to calculate the PIT tax to pay

If you need it, you can also
- Run `python jpk_pkpir.py 2019-03` to generate a JPK_PKPIR file

## Future plans
* Support for declaration submission
* Using Google Sheets as the data source
