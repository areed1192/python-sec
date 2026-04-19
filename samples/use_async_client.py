"""Example usage of the async SEC EDGAR client with httpx."""

import asyncio

from edgar.async_client import EdgarAsyncClient


async def main():
    """Main async function to demonstrate usage of EdgarAsyncClient."""

    # Initialize the async client.
    # SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
    # Use as an async context manager for automatic cleanup.
    async with EdgarAsyncClient(user_agent="Your Name your-email@example.com") as client:

        # -------------------------------------------------------------------
        # Resolve a ticker symbol to a CIK number
        # -------------------------------------------------------------------

        cik = await client.resolve_ticker("AAPL")
        print(f"AAPL CIK: {cik}")
        # Output: AAPL CIK: 0000320193

        # -------------------------------------------------------------------
        # Get company information
        # -------------------------------------------------------------------

        info = await client.get_company_info("AAPL")
        print(f"Company: {info}")
        # Output: <CompanyInfo cik='320193' name='Apple Inc.'>

        # -------------------------------------------------------------------
        # Search for filings
        # -------------------------------------------------------------------

        results = await client.search(
            q='"revenue recognition"',
            form_types=["10-K"],
            size=5,
        )
        print(f"Search results: {len(results)}")
        for result in results[:3]:
            print(f"  - {result}")

        # -------------------------------------------------------------------
        # Get XBRL company facts
        # -------------------------------------------------------------------

        facts = await client.get_facts("MSFT")
        print(f"Facts: {facts}")
        # Output: <Facts cik=789019 entity_name='MICROSOFT CORP'>

        # -------------------------------------------------------------------
        # Download a filing document
        # -------------------------------------------------------------------

        # content = await client.download("https://www.sec.gov/Archives/edgar/data/...")
        # print(f"Downloaded {len(content)} characters")

        # -------------------------------------------------------------------
        # Concurrent requests (major advantage of async)
        # -------------------------------------------------------------------

        tickers = ["AAPL", "MSFT", "GOOGL"]
        tasks = [client.get_company_info(t) for t in tickers]
        companies = await asyncio.gather(*tasks)
        for company in companies:
            print(f"  {company}")


if __name__ == "__main__":
    asyncio.run(main())
