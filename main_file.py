# Contributors: Carl Ripplinger, Tyler Vanderwood, Heber Jones, Jake Gardenier
# This program scrapes the April 2026 general conference and get's scripture reference data from all of the talks.


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
PASSWORD = ""   # <-- change this
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
    all_links = soup.find_all("a", class_="list-tile")
 
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
 
 # Scraping function - Heber (Member 2)
def scrape_and_save(talk_urls):


    # Scrape data from every URL in the list provided
    for url in talk_urls:
        # Create a dictionary to track references for each book of scripture:
        standard_works_dict = {'Speaker_Name': '', 'Talk_Name': '', 'Kicker': '',
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
        #print(soup.find("div", class_="body"))


        # The data we want to scrape is:
        # speaker name, title, and kicker
        # Footnotes, and update scripture reference count


        header_section = soup.find("div", class_="body")
        try :
            speaker_name = header_section.find("p", class_="author-name").get_text(strip=True) if header_section else None
            title = header_section.find("h1").get_text(strip=True) if header_section else None
            kicker = header_section.find("p", class_="kicker").get_text(strip=True) if header_section else None


            standard_works_dict['Speaker_Name'] = speaker_name
            standard_works_dict['Talk_Name'] = title
            standard_works_dict['Kicker'] = kicker
        except :
            print("not a talk")
            continue


        footnotes_section = soup.find('footer', attrs={'class': 'notes'})
        footnotes_text = footnotes_section.get_text(separator=" ") if footnotes_section else ""
        non_scripture_keys = {'Speaker_Name', 'Talk_Name', 'Kicker'}
        for books in standard_works_dict:
            if books in non_scripture_keys:
                continue
            iBookReference = footnotes_text.count(books)
            standard_works_dict[books] = iBookReference


        # Save the dictionary with reference count and other data to database.
        df = pd.DataFrame([standard_works_dict])
        df.to_sql("general_conference", engine, if_exists='append', index=False)


# ── Member 4 - Jake ─────────────────────────────────────────


def display_talk_list(df):
    print("The following are the names of speakers and their talks:")


    talk_map = {}


    for display_num, (index, row) in enumerate(df.iterrows(), start=1):
        speaker = row["Speaker_Name"]
        talk_name = row["Talk_Name"]
        print(f"{display_num}: {speaker} - {talk_name}")
        talk_map[display_num] = index


    return talk_map




def graph_selected_talk(df, selected_index):
    selected_row = df.loc[selected_index]


    # Remove non-scripture columns
    non_reference_columns = ["Speaker_Name", "Talk_Name", "Kicker"]
    reference_data = selected_row.drop(labels=non_reference_columns)


    # Make sure everything is numeric
    reference_data = pd.to_numeric(reference_data, errors="coerce").fillna(0)


    # Only keep books with at least 1 reference
    reference_data = reference_data[reference_data >= 1]


    if reference_data.empty:
        print("This talk has no scripture references to display.")
        return


    reference_data.plot(kind="bar")
    plot.title(f"Standard Works Referenced in: {selected_row['Talk_Name']}")
    plot.xlabel("Standard Works Books")
    plot.ylabel("# Times Referenced")
    plot.xticks(rotation=45)
    plot.tight_layout()
    plot.show()




def specific_talk_summary():
    df = pd.read_sql_query("SELECT * FROM general_conference", engine)


    if df.empty:
        print("No data found. Run option 1 first.")
        return


    talk_map = display_talk_list(df)


    user_choice = input("Please enter the number of the talk you want to see summarized: ")


    try:
        user_choice = int(user_choice)


        if user_choice not in talk_map:
            print("Invalid talk number.")
            return


        selected_index = talk_map[user_choice]
        graph_selected_talk(df, selected_index)


    except ValueError:
        print("Invalid input. Please enter a number.")


# ── Summary menu - Member 3 - Tyler ───────────────────────────────────
# Handles the Part 2 sub-menu. Reads data back from postgres
# and displays a bar chart of scripture references across
# all talks combined.
def show_summaries():
    user_input_2 = input("You selected to see summaries. Enter 1 to see a summary of all talks. Enter 2 to select a specific talk. Enter anything else to exit: ")
   
    if user_input_2 == "1":
        # Read all data from postgres into a DataFrame
        sql_query = 'select * from general_conference'
        df_postgres = pd.read_sql_query(sql_query, engine)


        # Drop text columns so we can sum the scripture counts
        # then filter to only books referenced more than 2 times
        df_sum = df_postgres.drop(['Speaker_Name', 'Talk_Name', 'Kicker'], axis=1).sum()
        df_sum_filtered = df_sum[df_sum > 2]


        # Build and display the bar chart
        df_sum_filtered.plot(kind='bar')
        plot.title('Standard Works Referenced in General Conference')
        plot.xlabel('Standard Works Books')
        plot.ylabel('# Times Referenced')
        plot.show()


    elif user_input_2 == '2':
        specific_talk_summary()


    else:
        print("Closing the program.")


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
 
        # Step 3: scrape each talk and save to postgres
        scrape_and_save(talk_urls)


        print("You've saved the scraped data to your postgres database.")


    elif user_input == '2':
        # Step 4: show summary sub-menu
        show_summaries()
   
    else:
        print("Closing the program.")


# This makes sure main() only runs when you execute THIS file
# directly, not when another teammate imports it.
if __name__ == "__main__":
    main()
      