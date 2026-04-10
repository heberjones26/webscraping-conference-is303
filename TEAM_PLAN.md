# Team Plan — Conference Web Scraper

## Project Overview

A single-file Python scraper that pulls General Conference talk data, stores it in PostgreSQL, and provides two visualization modes via a menu-driven interface.

---

## Work Breakdown

### Member 1 — Setup & Scraping Foundation
- Write the main program loop (`enter 1 or 2` prompt)
- Set up the SQLAlchemy engine
- Drop the table if it exists
- Load the main conference page
- Find all talk links
- Filter out sessions and "Sustaining"
- Pass a clean list of URLs to Member 2

---

### Member 2 — Parsing Each Talk
- Take the URL list and loop through every talk page
- Scrape speaker name, title, and kicker
- Find (or gracefully handle missing) footnotes
- Count every scripture reference using `standard_works_dict`
- Save each row to PostgreSQL

---

### Member 3 — Part 2 Summary View
- Handle the Part 2 sub-menu
- Read data back from PostgreSQL
- Build the all-talks bar chart showing books referenced **more than 2 times**
- Apply correct title and axis labels

---

### Member 4 — Per-Talk Chart & Finishing Touches
- Display the numbered list of all speakers/talks
- Let the user pick one by number
- Show the per-talk bar chart (books with **≥1 reference**)
- Handle exit logic
- Write the header comment block (names/description)
- Lead final integration before submission

---

## Integration Tip

Since this is one Python file, **Member 1 should create the skeleton on day one** — main `if/elif` blocks with placeholder functions — so everyone can work in parallel without conflicts.

Members 3 and 4 can test against data Member 2 has already scraped; they don't need to re-run the scraper every time.
