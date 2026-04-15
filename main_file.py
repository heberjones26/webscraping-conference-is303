# ============================================================
# General Conference Web Scraper - Main Program File
# Team Members:
#   Member 1 (Carl)  - Setup, DB connection, URL collection
#   Member 2 (Heber) - Scraping each talk, saving to postgres
#   Member 3 (Tyler) - Summary menu, all-talks bar chart
#   Member 4 (Jake)  - Talk list, per-talk bar chart
# Description: Scrapes speaker names, talk titles, kickers,
#   and scripture reference counts from the April 2026
#   General Conference, saves to postgres, and displays
#   summary bar charts on request.
# ============================================================

# ── Imports ──────────────────────────────────────────────────
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plot


# ── Database setup (Member 1 - Carl) ─────────────────────────
# Each team member: fill in YOUR postgres password below.
# The port 5434 is specific to this class setup — don't change it.
# Format: postgresql://username:password@host:port/database_name

USERNAME = "postgres"
PASSWORD = ""           # <-- each teammate fills in their own password here
HOST     = "localhost"
PORT     = "5432"
DATABASE = "is303"

engine = sqlalchemy.create_engine(
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)


# ── Drop table if it exists (Member 1 - Carl) ────────────────
# Deletes any old version of the table before scraping fresh
# data so we don't end up with duplicate rows.
def drop_table():
    with engine.connect() as connection:
        connection.execute(sqlalchemy.text(
            "DROP TABLE IF EXISTS general_conference"
        ))
        # commit() makes the deletion permanent in the database
        connection.commit()
    print("Dropped existing general_conference table (if any).")


# ── Collect all talk URLs (Member 1 - Carl) ──────────────────
# Loads the General Conference index page and returns a list
# of URLs for individual talks only — skipping session video
# pages and the Sustaining page.
def get_talk_urls():
    base_url = "https://www.churchofjesuschrist.org"
    index_url = base_url + "/study/general-conference/2026/04?lang=eng"

    # requests.get() downloads the page HTML
    response = requests.get(index_url)
    # Force UTF-8 encoding so special characters in names render correctly
    response.encoding = "utf-8"

    # BeautifulSoup parses that HTML so we can search through it
    soup = BeautifulSoup(response.text, "html.parser")

    # Each talk tile on the index page is an <a class="list-tile"> tag.
    # We grab all of them so we can loop through and filter below.
    all_links = soup.find_all("a", class_="list-tile")

    talk_urls = []   # will be filled with valid individual talk URLs

    for link in all_links:
        href = link.get("href")   # pull the URL string from the link tag

        # Skip any link that has no href attribute
        if not href:
            continue

        href_lower = href.lower()

        # Skip session video pages — their URLs contain "session"
        # e.g. .../saturday-morning-session?lang=eng
        if "session" in href_lower:
            continue

        # Skip the Sustaining page — its URL contains "sustaining"
        if "sustaining" in href_lower:
            continue

        # The hrefs are relative (start with /study/...) so we
        # prepend the domain to make a full working URL
        talk_urls.append(base_url + href)

    print(f"Found {len(talk_urls)} potential talk pages.")
    return talk_urls


# ── Scrape each talk and save to postgres (Member 2 - Heber) ─
# Loops through every URL in talk_urls, scrapes the speaker
# name, title, kicker, and scripture reference counts, then
# appends each talk as a row in the general_conference table.
def scrape_and_save(talk_urls):

    for url in talk_urls:
        print(f"trying to scrape url: {url}")

        # Create a fresh copy of the dictionary for every talk so
        # reference counts don't carry over from the previous talk
        standard_works_dict = {
            'Speaker_Name': '', 'Talk_Name': '', 'Kicker': '',
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
            'Articles of Faith': 0
        }

        try:
            # Download and parse the individual talk page.
            # Force UTF-8 so special characters in names render correctly
            # instead of showing garbled characters like Â or â.
            response = requests.get(url, timeout=10)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")

            # The talk content lives inside <div class="body">
            body = soup.find("div", class_="body")
            if not body:
                print("  Not a talk page — skipping.")
                continue

            # Find the speaker name, title, and kicker elements
            speaker = body.find("p", class_="author-name")
            title   = body.find("h1")
            kicker  = body.find("p", class_="kicker")

            # If there's no speaker or title it's not a real talk — skip it
            if not speaker or not title:
                print("  Missing required fields — skipping.")
                continue

            # Extract the text and strip the "By " prefix from speaker names
            # e.g. "By Elder David A. Bednar" → "Elder David A. Bednar"
            speaker_name = speaker.get_text(strip=True).replace("By ", "")
            title_text   = title.get_text(strip=True)
            # Kicker is optional — some talks don't have one
            kicker_text  = kicker.get_text(strip=True) if kicker else ""

            # Strip any leftover whitespace from all three fields
            speaker_name = speaker_name.strip()
            title_text   = title_text.strip()
            kicker_text  = kicker_text.strip()

            # Double-check for the Sustaining page in case it slips through
            if "sustaining" in title_text.lower():
                print("  Skipping sustaining page.")
                continue

            # Store the text fields in the dictionary
            standard_works_dict["Speaker_Name"] = speaker_name
            standard_works_dict["Talk_Name"]    = title_text
            standard_works_dict["Kicker"]       = kicker_text

        except Exception as e:
            print(f"  Error scraping page: {e}")
            continue

        # Get the footnotes section where scripture references are listed.
        # Some talks have no footnotes at all, so we default to empty string.
        footnotes = soup.find("footer", class_="notes")
        footnotes_text = footnotes.get_text(" ", strip=True) if footnotes else ""

        # Count how many times each book of scripture appears in the footnotes.
        # We skip the non-scripture keys so we don't overwrite the speaker
        # name, talk name, and kicker with 0s (that was the original bug).
        for book in standard_works_dict:
            if book in ["Speaker_Name", "Talk_Name", "Kicker"]:
                continue   # already set above — don't touch them
            standard_works_dict[book] = footnotes_text.count(book)

        # Convert the dictionary to a one-row DataFrame and append
        # it to the general_conference table in postgres
        df = pd.DataFrame([standard_works_dict])
        df.to_sql("general_conference", engine, if_exists="append", index=False)


# ── Helper: load and clean data from postgres ─────────────────
# Reads all rows from the general_conference table, removes any
# rows with a blank speaker name (non-talk pages that slipped
# through scraping), and resets the index so numbering is
# clean and consecutive with no gaps.
def load_clean_df():
    df = pd.read_sql_query("SELECT * FROM general_conference", engine)
    # Drop the auto-generated 'index' column if postgres saved one —
    # it's not a scripture column and would break the sum in the chart
    if "index" in df.columns:
        df = df.drop(columns=["index"])
    # Drop rows where Speaker_Name is blank — these are non-talk pages
    # like statistical reports or solemn assemblies that got saved
    # but shouldn't appear in the talk list or charts
    df = df[df["Speaker_Name"].str.strip() != ""]
    # Reset index so numbers run 0, 1, 2... with no gaps after dropping
    df = df.reset_index(drop=True)
    return df


# ── Display numbered talk list (Member 4 - Jake) ─────────────
# Prints every talk as "number: Speaker - Talk Name" and
# returns a dictionary mapping display numbers to DataFrame
# row positions so we can look up the selected talk later.
def display_talk_list(df):
    print("The following are the names of speakers and their talks:")

    talk_map = {}   # maps display number (1-based) → DataFrame row index (0-based)

    for i, row in enumerate(df.itertuples(index=False), start=1):
        print(f"{i}: {row.Speaker_Name} - {row.Talk_Name}")
        talk_map[i] = i - 1   # display number 1 → row index 0, etc.

    return talk_map


# ── Bar chart for a single selected talk (Member 4 - Jake) ───
# Displays a bar chart of scripture references for one talk,
# showing only books that appear at least once.
def graph_selected_talk(df, selected_index):
    # Pull the row for the selected talk
    row = df.iloc[selected_index]

    # Drop the text columns so we're left with only scripture counts
    data = row.drop(labels=["Speaker_Name", "Talk_Name", "Kicker"])

    # Convert to numbers in case any values are stored as strings
    data = pd.to_numeric(data, errors="coerce").fillna(0)

    # Only show books that were referenced at least once
    data = data[data >= 1]

    if data.empty:
        print("This talk has no scripture references to display.")
        return

    data.plot(kind="bar")
    plot.title(f"Standard Works Referenced in: {row['Talk_Name']}")
    plot.xlabel("Standard Works Books")
    plot.ylabel("# Times Referenced")
    plot.xticks(rotation=45)
    plot.tight_layout()
    plot.show()


# ── Per-talk summary flow (Member 4 - Jake) ──────────────────
# Reads all talks from postgres, shows the numbered list,
# asks the user to pick one, and displays its bar chart.
def specific_talk_summary():
    # Load and clean the data — removes blank rows and resets index
    df = load_clean_df()

    if df.empty:
        print("No data found. Run option 1 first to scrape the data.")
        return

    talk_map = display_talk_list(df)

    choice = input("Please enter the number of the talk you want to see summarized: ")

    try:
        choice = int(choice)

        if choice not in talk_map:
            print("Invalid selection — please enter a number from the list.")
            return

        # Look up the row index and display the chart
        graph_selected_talk(df, talk_map[choice])

    except ValueError:
        # Catches the case where the user types something that isn't a number
        print("Invalid input. Please enter a number.")


# ── Summary menu (Member 3 - Tyler) ──────────────────────────
# Handles the Part 2 sub-menu. Shows either an all-talks bar
# chart (books referenced more than twice total) or lets the
# user pick a specific talk to chart.
def show_summaries():

    choice = input(
        "You selected to see summaries. Enter 1 to see a summary of all talks. "
        "Enter 2 to select a specific talk. Enter anything else to exit: "
    )

    if choice == "1":
        # Load and clean the data — removes blank rows and resets index
        df = load_clean_df()

        # Drop the text columns so we're left with only scripture counts,
        # sum across all talks, then keep only books cited more than twice
        data = df.drop(["Speaker_Name", "Talk_Name", "Kicker"], axis=1).sum()
        data = data[data > 2]

        # Build and display the all-talks bar chart
        data.plot(kind="bar")
        plot.title("Standard Works Referenced in General Conference")
        plot.xlabel("Standard Works Books")
        plot.ylabel("# Times Referenced")
        plot.xticks(rotation=45)
        plot.tight_layout()
        plot.show()

    elif choice == "2":
        # Hand off to the per-talk summary flow
        specific_talk_summary()

    else:
        print("Closing the program.")


# ── Main program loop ─────────────────────────────────────────
# Entry point — loops until the user exits so they can scrape
# and then immediately view summaries without restarting.
def main():

    while True:
        user_input = input(
            "If you want to scrape data, enter 1. "
            "If you want to see summaries of stored data, enter 2. "
            "Enter any other value to exit the program: "
        )

        if user_input == "1":
            # Drop old data, collect URLs, scrape and save to postgres
            drop_table()
            urls = get_talk_urls()
            scrape_and_save(urls)
            print("You've saved the scraped data to your postgres database.")

        elif user_input == "2":
            # Show the summary sub-menu
            show_summaries()

        else:
            # Any other input exits the loop and ends the program
            print("Closing the program.")
            break


# Only run main() when this file is executed directly —
# not when it's imported by another file.
if __name__ == "__main__":
    main()