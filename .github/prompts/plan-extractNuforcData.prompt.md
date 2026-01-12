## Plan: Extract NUFORC Data with Pagination to CSV

Build a web scraper to extract tabular UFO sighting data from the NUFORC website across all pagination pages and save it to CSV format in an organized output directory. The workspace is currently empty, requiring implementation from scratch.

### Steps

1. **Create requirements.txt** with `requests`, `beautifulsoup4`, and `lxml` dependencies
2. **Create directory structure** by adding `output/` folder for CSV files and `logs/` folder for error logs
3. **Create Python script** with requests and BeautifulSoup4 libraries to fetch and parse HTML from [nuforc.org/subndx/?id=lCA](https://nuforc.org/subndx/?id=lCA)
4. **Configure logging** to write verbose error logs to timestamped file in `logs/` directory
5. **Implement retry logic** with 2 retry attempts for failed HTTP requests with detailed error logging
6. **Extract table data** from the initial page by identifying the table structure and column headers
7. **Implement pagination logic** to detect and iterate through all available pages in the navigation
8. **Aggregate extracted data** from all pages into a unified dataset structure
9. **Export to CSV** in the `output/` directory with timestamped filename format like `nuforc_lCA_2026-01-12_14-30-45.csv`

### Further Considerations

1. **Rate limiting**: Should the script add delays between requests to be respectful to the server?
