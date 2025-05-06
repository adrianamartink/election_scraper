"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Adriana Martinkova
email: martinkova.adriana01@gmail.com
discord: adaadrisek123#8811
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import urllib3

# Turn off HTTPS warnings (we're using verify=False in requests)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This function checks if the page we downloaded looks like an election results page
def validate_soup_content(soup):
    text = soup.get_text(separator=" ", strip=True)

    required_phrases = [
        "Volby do Poslanecké sněmovny Parlamentu České republiky konané ve dnech",
        "Výsledky hlasování za územní celky – výběr obce"
    ]

    for phrase in required_phrases:
        if phrase not in text:
            return False

    return True

# This function gets all the locations and their result links from the main table
def get_locations(soup):
    data = []
    tables = soup.find_all("table", class_="table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 3:
                number_tag = cols[0].find("a")
                name_tag = cols[1]
                
                if number_tag and name_tag:
                    number = number_tag.text.strip()
                    name = name_tag.text.strip()
                    relative_link = number_tag["href"].strip()
                    full_link = "https://www.volby.cz/pls/ps2017nss/" + relative_link
                    
                    data.append({
                        "number": number,
                        "name": name,
                        "link": full_link
                    })

    df = pd.DataFrame(data)
    return df

# This function visits every location link and collects overall + party results
def get_results(locations_df):
    overall_results_list = []
    party_results_list = []

    for _, row in locations_df.iterrows():  # idx not used, so we ignore it
        url = row['link']
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        ### --- Get overall statistics like turnout, registered voters, etc. ---
        overall_table = soup.find("table", id="ps311_t1")
        overall_data = {}

        if overall_table:
            cells = overall_table.find_all("td")
            if len(cells) >= 9:
                try:
                    overall_data = {
                        "districts_total": cells[0].text.strip().replace('\xa0', ''),
                        "districts_reported": cells[1].text.strip().replace('\xa0', ''),
                        "districts_percentage": cells[2].text.strip().replace('\xa0', ''),
                        "voters_registered": cells[3].text.strip().replace('\xa0', ''),
                        "envelopes_issued": cells[4].text.strip().replace('\xa0', ''),
                        "voter_turnout_percentage": cells[5].text.strip().replace('\xa0', ''),
                        "envelopes_submitted": cells[6].text.strip().replace('\xa0', ''),
                        "valid_votes": cells[7].text.strip().replace('\xa0', ''),
                        "valid_votes_percentage": cells[8].text.strip().replace('\xa0', ''),
                    }
                except IndexError:
                    pass  # if something goes wrong, skip it

        ### --- Get detailed party results ---
        party_results = []

        party_tables = soup.find_all("table", class_="table")
        for party_table in party_tables[1:]:  # Skip the first table (already used)
            party_rows = party_table.find_all("tr")
            for party_row in party_rows:
                party_cols = party_row.find_all("td")
                if len(party_cols) >= 4:
                    try:
                        party_data = {
                            "party_number": party_cols[0].text.strip(),
                            "party_name": party_cols[1].text.strip(),
                            "votes": party_cols[2].text.strip().replace('\xa0', ''),
                            "votes_percentage": party_cols[3].text.strip().replace('\xa0', '')
                        }
                        party_results.append(party_data)
                    except IndexError:
                        pass  # ignore bad rows

        # Add the collected data to lists
        overall_results_list.append(overall_data)
        party_results_list.append(party_results)

    # Add the lists back into the DataFrame
    locations_df = locations_df.copy()
    locations_df["overall_results"] = overall_results_list
    locations_df["party_results"] = party_results_list

    return locations_df

# This function turns the 'overall_results' dictionary into separate columns
def explode_results(results_df):
    overall_df = pd.json_normalize(results_df['overall_results'])

    # Merge new columns with the original table
    results_with_overall = pd.concat([
        results_df.drop(columns=['overall_results']).reset_index(drop=True),
        overall_df
    ], axis=1)

    # Rename columns to something simpler
    columns_mapping = {
        'number': 'code',
        'name': 'location',
        'voters_registered': 'registred',
        'envelopes_issued': 'envelopes',
        'valid_votes': 'valid',
        'party_results': 'party_results'
    }
    
    selected_df = results_with_overall[list(columns_mapping.keys())].rename(columns=columns_mapping)
    
    return selected_df

# This function unpacks party votes into separate columns
def explode_parties(results_with_overall):
    expanded_rows = []

    for _, row in results_with_overall.iterrows():
        # Save the general info from the row
        base_data = row.drop('party_results').to_dict()

        # Add each party's vote count to the dictionary
        party_votes = {}
        for party in row['party_results']:
            party_name = party.get('party_name', '').strip()
            votes = party.get('votes', '0').replace('\xa0', '').replace(' ', '')
            party_votes[party_name] = int(votes) if votes.isdigit() else 0

        # Merge everything together into one row
        merged_data = {**base_data, **party_votes}
        expanded_rows.append(merged_data)

    # Make a DataFrame from all rows
    final_df = pd.DataFrame(expanded_rows)

    return final_df

# Main program
def main():
    # We want exactly 2 arguments: the link and output filename
    if len(sys.argv) != 3:
        print("Usage: python election_scraper.py <link> <output_filename>")
        sys.exit(1)

    link = sys.argv[1]
    output_name = sys.argv[2]

    print(f"\n Starting to fetch election data from: {link}")
    print(f"📄 The final results will be saved to: {output_name}.csv\n")

    # Try downloading the main election page
    try:
        response = requests.get(link, verify=False)
    except Exception as e:
        print(f"Something went wrong when trying to download the page: {e}")
        sys.exit(1)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        if validate_soup_content(soup):
            print("Page looks good, starting to process locations and results...")
            locations_df = get_locations(soup)
            results_df = get_results(locations_df)
            results_with_overall = explode_results(results_df)
            parties_df = explode_parties(results_with_overall)

            # Save to CSV
            parties_df.to_csv(f"{output_name}.csv", index=False, encoding="utf-8-sig")
            print(f"\nDone! Results saved to: {output_name}.csv")
        else:
            print("The page doesn't contain valid election results. Please check the link.")
    else:
        print(f"Failed to download the page. HTTP status code: {response.status_code}")

# Make sure this only runs if the file is executed directly
if __name__ == "__main__":
    main()
