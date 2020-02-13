# Parsing XBRL Filings

## Overview of the Problem

At this point, we've determined that the SEC has a treasure trove of data available to us. However, the biggest obstacle to getting this data is the following:

 1. Figuring out where it is
 2. Figuring out how to extract it

Well, in our situation there is a particular instance where getting this data isn't as difficult as it may seem. The particular situation I'm talking about is when the data is in somthing called an XBRL document. XBRL stands for e**X**tensible **B**usiness **R**eporting **L**anguage and is the open international standard for digital business reporting. The advantage of the data being in an XBRL document is that it's well structured and granular, meaning we can get very percise values with a deep understanding of the context.

## Understand XBRL in the Context of Scraping

As much as I would love to get into the scraping of the content I can't because I'm sure I would lose 90% of you in the first 5 minutes. Scraping XBRL documents can be an intimidating process when you first start out because the content often looks cryptic and arbitrary. However, even when it appears to be random there is inherent structure behind it. However, to understand this structure you need to understand what problem the XBRL document is trying to sovle.

We live in a world of information, and everyone is constantly looking for more insightful information to make informed decisions. No where else is this more apparaent then in the World of business. Public companies across the world are required, in many countries, to disclose their financial performance and the overall health and outlook of the company. The belief is that transparency promotes economic activity and builds a level of trust between investors and corporations.

To help promote transparecny and consistency in the way financial information is disclosed and shared with investors, a group decided that a new way of storing this data was needed. This framework would be called XBRL. By providing a framework that allows companies to provide detailed information on any of their financial metrics, XBRL is the go to solution for financial disclosure. In fact, it's so valuable that the SEC is requiring Public companies to follow the standard by a certain deadline.

### **Organzing Content to Promote Transparency**

Okay, so the goal is transparency, but also being flexible. How do we go about doing this? Well, it would probably help to understand the problem from the persepctive of a regulator.

I have a company who wants to present financial information to it's investors. What is the information an investor would need to understand a company's health? Well more than likely it would want to understand its' financial performance! Okay, but financial health can be made up of so many different metrics, so I'll probably need a way to identify any metric the company discloses.

Also, most financial metrics follow some sort of accounting prinicpal so it would probably help to provide the definition of that accounting standard. We should also promote consistency, so it might be helpful to define standard labels that a company can use.

If the company uses those labels they just need to follow the standards define. Additionally, we need to make sure that investors can easily navigate to the information, so it would probably be beneficial to define all the locations of all the information and where we can go to find it.

Another very important requirement is that it can be read by machines! You think with all the computational power out there that people won't want to use it on financial information?! I doubt that.

Let's follow a framework for organizing content so it can be easily read and extracted by a machine. XML is an older framework but this technology has been around since 2003 and back then XML was the cool kid on the block.
