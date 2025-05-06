Engeto Python Project 3: Elections Scraper
==========================================

This project is the final assignment for the Engeto Online Python Akademie.
The goal is to scrape the 2017 Czech parliamentary election results for a selected district
and export the data to a .csv file.

--------------------------------------------------
PROJECT OVERVIEW
--------------------------------------------------

The script downloads election results for all municipalities in a selected region
(e.g., Benešov, Prostějov) from the official volby.cz website.

It collects:
- The total number of registered voters
- Voter turnout details
- Valid votes
- Number of votes for each political party

The final output is saved as a CSV file, with one row per municipality.

--------------------------------------------------
HOW TO SET UP AND RUN THE PROJECT
--------------------------------------------------

Step 1: Clone the project and navigate to the folder

    git clone https://github.com/yourusername/elections-scraper.git
    cd elections-scraper

Step 2: Create a virtual environment (optional but recommended)

    python -m venv .venv
    .venv\Scripts\activate             

Step 3: Install required libraries

    pip install -r requirements.txt

--------------------------------------------------
HOW TO RUN THE SCRIPT
--------------------------------------------------

You must provide 2 arguments when running the script:

    python projekt_3.py <URL> <output_filename>

Where:
- <URL> is a valid link to a district's election summary page
- <output_filename> is the desired name for the output file (without .csv)

Example:

    python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103" vysledky_benesov

This will:
- Fetch results for Benešov
- Save them as vysledky_benesov.csv

--------------------------------------------------
PROJECT FILES
--------------------------------------------------

projekt_3.py       - The main script
requirements.txt   - List of required libraries
README.txt         - This file
vysledky_*.csv     - Output files generated after scraping

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Each row in the CSV file contains results for one municipality, including:

- Municipality code
- Municipality name
- Number of registered voters
- Issued envelopes
- Valid votes
- One column per party with number of votes

Example (shortened):

    code,location,registred,envelopes,valid,ANO 2011,ODS,ČSSD,...
    529303,Benešov,3950,2521,2495,1275,523,130,...

--------------------------------------------------
NOTES
--------------------------------------------------

- The script validates the input URL before running.
- If arguments are missing or incorrect, the script exits with a message.
- HTTPS warnings are disabled in the script for simplicity.
