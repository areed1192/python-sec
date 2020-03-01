# Scraping SEC XBRL Documents

## What is XBRL

XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage and is the open international standard for digital business reporting, XBRL is managed by a global not for profit consortium called XBRL International. In a nutshell, XBRL provides a language in which reporting terms can be authoritatively defined. Those terms can then be used to uniquely represent the contents of financial statements or other kinds of compliance, performance and business reports. XBRL lets reporting information move between organisations rapidly, accurately and digitally.

## XBRL in the context of US GAAP

Public companies are required to submit financial disclosures multiple times a year so that investors can understand their performance and are better able to understand/analyze the business. Accounting standards and rules define how the items, that are required to be disclosed, need to be classified and organized in financial statements and disclosure documents.

The US GAAP Financial Reporting Taxonomy is a list of computer-readable tags in XBRL that allows companies to label precisely the thousands of pieces of financial data that are included in typical long-form financial statements and related footnote disclosures. The tags allow computers to automatically search for and assemble data so those data can be readily accessed and analyzed by investors, analysts, journalists, and the SEC staff.

## XBRL in the context of the SEC

The SEC Rule **Interactive Data to Improve Financial Reporting** requires domestic and foreign companies using US GAAP and, eventually, foreign private issuers using International Financial Reporting Standards (IFRS) to provide their financial statements in the XBRL format as an exhibit to their periodic and current reports and registration statements, as well as to transition reports needed to be filed as a result of a change in fiscal year. Filers required to comply are to be phased-in over 3 years, in 2 stages, beginning with a periodic report on Form 10-Q, Form 20-F or Form 40-F (as applicable) containing financial statements for a fiscal period ending on or after June 15, 2009.

## SEC XBRL - A Technical Guide

When the SEC defines an XBRL document, it's define by what it consist of. For the SEC, an XBRL filing document will consist of the following:

1. One or more instance documents (instances) that contain actual data and facts.
2. One or more schema documents (schemas) that declare the elements that can be used in the instance, and identify other schemas and files where relationships among those elements are declared.
3. One or more linkbase documents (linkbases) containing additional information about, or relationships among, the elements in a schema document. There are five types of linkbases: Label, Definition, Reference, Presentation, and Calculation.
    - Note: Although the Reference Linkbase file is a valid attachment type, at the moment it is not used.

Schema and linkbase documents contain references to each other in the form of Uniform Resource Identifiers (URIs). Taxonomies are sets of schemas and linkbases that are designed to be loaded and used together; for example, a schema may contain a list of linkbases that have the URIs of other schemas to be loaded, and so on. 

Taxonomies generally fall into one of two categories:
    1. Standard base taxonomies 
    2. Company extension taxonomies.

Filers use company extension taxonomies to supplement base taxonomies and, within limits, customize those base taxonomies to their reporting goals. Instances also use URIs to reference schemas and linkbases.The Discoverable Taxonomy Set (DTS) of an instance document is the set of all schemas and linkbases that are found by following all URI links and references.

XBRL Document
Interactive Data Document Types
Root Element
Required Element
Instance
EX-101.INS, EX-99.SDR K.INS, EX-99.SDR L.INS
xbrli:xbrl
No info blank cell
Schema
EX-101.SCH, EX-99.SDR K.SCH, EX-99.SDR L.SCH
xsd:schema
No info blank cell
Calculation Linkbase
EX-101.CAL, EX-99.SDR K.CAL, EX-99.SDR L.CAL
link:linkbase
link:calculationLink

XBRL Document
Interactive Data Document Types
Root Element
Required Element
Definition Linkbase
EX-101.DEF, EX-99.SDR K.LAB, EX-99.SDR L.LAB
link:linkbase
link:definitionLink
Label Linkbase
EX-101.LAB, EX-99.SDR K.LAB, EX-99.SDR L.LAB
link:linkbase
link:labelLink
Presentation Linkbase
EX-101.PRE, EX-99.SDR K.PRE, EX-99.SDR L.PRE
link:linkbase
link:presentationLink
Reference Linkbase
EX-101.REF
link:linkbase
link:referenceLink


XBRL Document
Documentname Format
Instance
{base}-{date}.xml
Schema
{base}-{date}.xsd
Calculation Linkbase
{base}-{date}_cal.xml
Definition Linkbase
{base}-{date}_def.xml
Label Linkbase
{base}-{date}_lab.xml
Presentation Linkbase
{base}-{date}_pre.xml
Reference Linkbase
{base}-{date}_ref.xml

# GAAP Financial Reporting Taxonomy - A Technical Guide

When parsing XBRL documents that exist in a SEC filing directory it's important to understand the following:

1. How documents are organized. 
2. Location of Documents.
3. Naming Conventions.
4. Allowed tags and not allowed tags.


    When parsing an SEC Filing that contains XBLR files, it's curucial that you know how the files are structured
    and what each file contains. If you skip this portion it's very easy to get lost in the process and lose sight
    of how to get the data.

        CALCULATION FILE: TradingSymbol_EndDate_cal.xml
        This contains links to different calculations in the file this will be useful when trying to 
        reference how certain calculations were made.

        DEFINITION FILE: TradingSymbol_EndDate_def.xml
        This contains links to different definitions used in the 10K/Q and also external resources 
        that define those definitions, this would be entities like FASB.

        LABEL FILE: TradingSymbol_EndDate_lab.xml
        This contains a section for each label in the document along with their corresponding ID used 
        in the XML structuring. Additionally each one these labels also has a locator that will provide 
        a hyperlink to that label in the file.

        PRESENTATION FILE: TradingSymbol_EndDate_pre.xml
        This provides more links to different presentations that contain information regarding different 
        sections of the filing.

    The general strategy is as follows:

        1. Parse the labels file.
        2. Parse the definitions file, and match the information to the labels file.
        3. Parse the calculations file, and match the information to the labels file.
        4. Parse the maind HTML file.