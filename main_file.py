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
    # Updated to pull from most recent conference - Heber
    index_url = base_url + "/study/general-conference/2026/04?lang=eng"
 
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
        scrape_and_save(talk_ursl)

 
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


# Scraping function - Heber (Member 2)

def scrape_and_save(talk_ursl) :

    # Scrape data from every URL in the list prodived
    for url in talk_ursl :
        # Create a dictionary to track references for each book of scripture:
        standard_works_dict = {'Speaker_Name' : '', 'Talk_Name' : '', 'Kicker' : '', 
                               'Matthew': 0, 'Mark': 0, 'Luke': 0, 'John': 0, 'Acts': 0, 
                               'Romans': 0, '1 Corinthians': 0, '2 Corinthians': 0, 
                               'Galatians': 0, 'Ephesians': 0, 'Philippians': 0, 
                               'Colossians': 0, '1 Thessalonians': 0, '2 Thessalonians': 0, 
                               '1 Timothy': 0, '2 Timothy': 0, 'Titus': 0, 'Philemon': 0, 
                               'Hebrews': 0, 'James': 0, '1 Peter': 0, '2 Peter': 0, 
                               '1 John': 0, '2 John': 0, '3 John': 0, 'Jude': 0, 
                               'Revelation': 0, 'Genesis': 0, 'Exodus': 0, 'Leviticus': 0, 
                               'Numbers': 0, 'Deuteronomy': 0, 'Joshua': 0, 'Judges': 0, 
                               'Ruth': 0, '1 Samuel': 0, '2 Samuel': 0, '1 Kings': 0, 
                               '2 Kings': 0, '1 Chronicles': 0, '2 Chronicles': 0, 'Ezra': 0, 
                               'Nehemiah': 0, 'Esther': 0, 'Job': 0, 'Psalm': 0, 'Proverbs': 0, 
                               'Ecclesiastes': 0, 'Song of Solomon': 0, 'Isaiah': 0, 
                               'Jeremiah': 0, 'Lamentations': 0, 'Ezekiel': 0, 'Daniel': 0, 
                               'Hosea': 0, 'Joel': 0, 'Amos': 0, 'Obadiah': 0, 'Jonah': 0, 
                               'Micah': 0, 'Nahum': 0, 'Habakkuk': 0, 'Zephaniah': 0, 
                               'Haggai': 0, 'Zechariah': 0, 'Malachi': 0, '1 Nephi': 0, 
                               '2 Nephi': 0, 'Jacob': 0, 'Enos': 0, 'Jarom': 0, 'Omni': 0, 
                               'Words of Mormon': 0, 'Mosiah': 0, 'Alma': 0, 'Helaman': 0, 
                               '3 Nephi': 0, '4 Nephi': 0, 'Mormon': 0, 'Ether': 0, 'Moroni': 0, 
                               'Doctrine and Covenants': 0, 'Moses': 0, 'Abraham': 0, 
                               'Joseph Smith—Matthew': 0, 'Joseph Smith—History': 0, 
                               'Articles of Faith': 0}

        # Convert the URL into scrapable data
        oResponse = requests.get(url)
        soup = BeautifulSoup(oResponse.text, "html.parser")

        # The data we want to scrape is: 
        # speaker name, title, and kicker
        # Footnotes, and update scripture reference count

        header_section = soup.find("header")
        speaker_name = header_section.find("p", class_="author-name")
        title = header_section.find("h1")
        kicker = header_section.find("p", class_="kicker")

        footnotes_section = soup.find('footer', attrs={'class' : 'notes'})
        for books in standard_works_dict :
            iBookReference = footnotes_section.count(books)
            standard_works_dict[books] = iBookReference

        print(speaker_name, title, kicker, standard_works_dict)