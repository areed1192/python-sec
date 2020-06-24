# SEC Text Search Examples

**Search By Company Name and Form Type:**

`(form-type=8-k*) AND (company-name="1 800 FLOWERS COM INC")`

**Search By Form Type and Items Type:**

`(form-type=8-k*) AND (Items=2.01)`

**Search By Form Type, Items Type, and Acceptance Datetime:**

`(form-type=8-k*) AND (items=2.01) AND (acceptance-datetime=20170605155635)`

**Search By Form Type, Items Type, Acceptance Datetime, and Filing Date:**

`(form-type=8-k*) AND (items=2.01) AND (acceptance-datetime=20170605155635) AND (filing-date=20170605)`

**Search By Form Type, Items Type, Acceptance Datetime, Filing Date, and CIK:**

`(form-type=8-k*) AND (items=2.01) AND (acceptance-datetime=20170605155635) AND (filing-date=20170605) AND (cik=0001084869)`

<https://www.sec.gov/cgi-bin/own-disp?CIK=0001084869&action=getissuer>
<https://www.sec.gov/cgi-bin/own-disp?CIK=0001460292&action=getowner>
<https://www.sec.gov/cgi-bin/srch-edgar>
<https://www.sec.gov/edgar/searchedgar/edgarzones.htm>
<https://www.sec.gov/rss/data>
<https://www.sec.gov/rss/investor/alerts>
<https://www.sec.gov/rss/forms>
<https://www.sec.gov/info/edgar/edgartaxonomies.xml>
<https://www.sec.gov/info/edgar/edgartaxonomies.shtml>

<https://www.sec.gov/Archives/edgar/xbrlrss.all.xml>
https://www.sec.gov/Archives/edgar/xbrl-inline.rss.xml
https://www.sec.gov/Archives/edgar/xbrl-rr.rss.xml
https://www.sec.gov/Archives/edgar/usgaap.rss.xml
https://www.sec.gov/Archives/edgar/monthly/

https://www.sec.gov/dera/data/financial-statement-and-notes-data-set.html
https://www.sec.gov/Archives/edgar/monthly/xbrlrss-2020-04.xml
https://www.sec.gov/dera/data/mutual-fund-prospectus-risk-return-summary-data-sets

https://www.sec.gov/Archives/edgar/data/1122304/000119312515118890/0001193125-15-118890.hdr.sgml
https://www.sec.gov/Archives/edgar/vprr/index.html
https://www.sec.gov/Archives/edgar/cik-lookup-data.txt
https://www.sec.gov/Archives/edgar/Oldloads/

https://www.sec.gov/cgi-bin/cik_lookup PARAMS : {'company':'alex'}

(file-number=000-26841)
(act=34)
(irs-number=113117311)
(zip=11514)
(state=CA)
(fiscal-year-end=0628)
(assigned-sic=5990)
(business-address=CHILE) OR (business-address=F3)
(business-address=(BANDERA 140 PISO 19))
(state-of-incorporation=ME)
(accession-number=0001085146-15-000014)


```xml
<SEC-HEADER>
    <COMPANY-NAME>Company Name
    <COMPANY-CIK>CIK
    <PUBLIC-DOCUMENT-COUNT>Public Document Count
    <ACCESSION-NUMBER>Accession Number
    <TYPE>Form Type
    <PERIOD>Period
    <FILING-DATE>Filing Date
    <FILER>
        <COMPANY-DATA>
            <CONFORMED-NAME>Company Name
            <CIK>CIK
            <ASSIGNED-SIC>Assigned SIC
            <IRS-NUMBER>IRS Number
            <STATE-OF-INCORPORATION>State of Incorporation
            <FISCAL-YEAR-END>Fiscal Year End
        </COMPANY-DATA>
        <FILING-VALUES>
            <FORM-TYPE>Form Type
            <ACT>SEC Act
            <FILE-NUMBER>File Number
            <FILM-NUMBER>Film Number
        </FILING-VALUES>
        <BUSINESS-ADDRESS>
            <STREET1>Street Address, Line One
            <STREET2>Street Address, Line Two
            <CITY>City
            <STATE>State
            <ZIP>ZIP Code
            <PHONE>Phone Number
        </BUSINESS-ADDRESS>
        <MAIL-ADDRESS>
            <STREET1>Street Address, Line One
            <STREET2>Street Address, Line Two
            <CITY>City
            <STATE>State
            <ZIP>ZIP Code
        </MAIL-ADDRESS>
            <FORMER-COMPANY>
            <FORMER-CONFORMED-NAME>Former Company Name
            <DATE-CHANGED>Date of Company Name Change
        </FORMER-COMPANY>
    </FILER>
</SEC-HEADER>
```
