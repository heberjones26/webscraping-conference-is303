# Main Program File.

## General Conference Web Scraper - Member 1: (Carl) Setup & Scraping
# Description: This file handles the program entry point,
# database setup, and collecting all talk URLs from the
# General Conference page.
#import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot

# ── Database setup ───────────────────────────────────────────
# sqlalchemy needs a "connection string" that tells it where
# your postgres database lives and how to log in.
# Format: postgresql://username:password@host/database_name
# For BYU's IS303 class the defaults are usually:
#   username: postgres
#   password: your postgres password
#   host: localhost
#   database: is303
# Change these values to match YOUR setup.
 
USERNAME = "postgres"
PASSWORD = "your_password_here"   # <-- change this
HOST     = "localhost"
DATABASE = "is303"
 
engine = sqlalchemy.create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"
)
 
 
# ── Drop table if it exists ───────────────────────────────────
# Before scraping fresh data we delete any old version of the
# table so we don't end up with duplicates.
def drop_table():
    with engine.connect() as connection:
        connection.execute(
            sqlalchemy.text("DROP TABLE IF EXISTS general_conference")
        )
        # commit() makes the change permanent in the database
        connection.commit()
    print("Dropped existing general_conference table (if any).")
 
 
# ── Get all talk URLs from the main conference page ───────────
# This function loads the General Conference index page and
# returns a list of URLs for individual talks only —
# skipping session videos and the Sustaining page.
def get_talk_urls():
    base_url = "https://www.churchofjesuschrist.org"
    index_url = base_url + "/study/general-conference/2025/10?lang=eng"
 
    # requests.get() downloads the page HTML
    response = requests.get(index_url)
 
    # BeautifulSoup parses that HTML so we can search through it
    soup = BeautifulSoup(response.text, "html.parser")
 
    # The individual talk links live inside a list on the page.
    # Each link is an <a> tag. We grab all of them from the
    # tile-list section so we don't accidentally grab nav links.
    # The class name below targets the talk tile list — inspect
    # the page in your browser (F12) if this ever needs updating.
    all_links = soup.find_all("a", class_="item")
 
    talk_urls = []   # we'll fill this list with valid talk URLs
 
    for link in all_links:
        href = link.get("href")   # get the href attribute value
 
        # Skip if there's no href at all
        if href is None:
            continue
 
        # Skip session pages — their URLs contain the word "session"
        # e.g. .../saturday-morning-session?lang=eng
        if "session" in href.lower():
            continue
 
        # Build the full URL (the hrefs on this site are relative,
        # meaning they start with /study/... not https://...)
        full_url = base_url + href
 
        # We'll catch the Sustaining page by its title later
        # (its URL doesn't have a reliable keyword to filter on),
        # so for now we add everything else to our list.
        talk_urls.append(full_url)
 
    print(f"Found {len(talk_urls)} potential talk pages.")
    return talk_urls
 
 
# ── Main program loop ─────────────────────────────────────────
def main():
    user_input = input(
        "If you want to scrape data, enter 1. "
        "If you want to see summaries of stored data, enter 2. "
        "Enter any other value to exit the program: "
    )
 
    if user_input == "1":
        # Step 1: wipe any old data
        drop_table()
 
        # Step 2: collect all talk URLs
        talk_urls = get_talk_urls()
 
        # ── Hand off to Member 2 ──────────────────────────────
        # Member 2's function will loop through talk_urls,
        # scrape each page, and save rows to postgres.
        # Once Member 2 writes their code, replace the line
        # below with a call to their function, e.g.:
        #   member2.scrape_and_save(talk_urls, engine)
        print("Talk URLs ready — passing to Member 2's scraper.")
        # TODO: call Member 2's scrape_and_save() here
 
        print("You've saved the scraped data to your postgres database.")
 
    elif user_input == "2":
        # ── Hand off to Member 3 ──────────────────────────────
        # Member 3 handles the summary sub-menu.
        # Replace the line below with a call to their function.
        print("Passing to Member 3's summary menu.")
        # TODO: call Member 3's show_summaries() here
 
    else:
        print("Closing the program.")
 
 
# This makes sure main() only runs when you execute THIS file
# directly, not when another teammate imports it.
if __name__ == "__main__":
    main()

