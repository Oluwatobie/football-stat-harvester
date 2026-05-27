import os
import requests
import urllib3
import pandas as pd
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy import create_engine

# Suppress SSL warnings (for local testing behind firewalls)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Premier League (39)
LEAGUE_ID = 39 
SEASON = 2023 

def fetch_standings():
    """Fetches the final league table/standings"""
    url = "https://v3.football.api-sports.io/standings"
    
    querystring = {"league": str(LEAGUE_ID), "season": str(SEASON)}
    
    headers = {
        "x-apisports-key": API_KEY
    }

    print(f"Fetching Premier League Standings for season {SEASON}...")
    response = requests.get(url, headers=headers, params=querystring, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def process_data(json_data):
    """Transforms the standings JSON into a clean Pandas DataFrame"""
    try:
        # Navigate through the JSON structure to get the actual table
        standings = json_data['response'][0]['league']['standings'][0]
    except (IndexError, KeyError):
        print("Could not find standings data in the response.")
        return pd.DataFrame()

    team_list = []
    
    for row in standings:
        team_info = {
            "Rank": row['rank'],
            "Team": row['team']['name'],
            "Points": row['points'],
            "Played": row['all']['played'],
            "Wins": row['all']['win'],
            "Draws": row['all']['draw'],
            "Losses": row['all']['lose']
        }
        team_list.append(team_info)
        
    df = pd.DataFrame(team_list)
    return df

def push_to_azure_sql(df):
    """Pushes the Pandas DataFrame to the Azure SQL Database"""
    # 1. Load credentials from .env
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")

    if not all([server, database, username, password]):
        print("Missing Database credentials in .env file.")
        return

    # 2. Build the connection string
    # We use ODBC Driver 17, which is standard on most Windows machines
    # driver = '{ODBC Driver 17 for SQL Server}'
    driver = '{SQL Server}'
    
    print(f"\nConnecting to Azure SQL Database: {database}...")
    try:
        params = urllib.parse.quote_plus(
            f"Driver={driver};Server=tcp:{server},1433;Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
        # 3. Push the data! 
        # if_exists='replace' means it will drop the old table and create a fresh one every time it runs
        df.to_sql("PremierLeagueStandings", engine, if_exists="replace", index=False)
        print("✅ SUCCESS: Data successfully written to Azure SQL!")
        
    except Exception as e:
        print(f"❌ ERROR: Could not connect or write to database.\n{e}")

def main():
    # 1. Fetch the data
    raw_data = fetch_standings()
    
    # 2. Process the data
    if raw_data:
        df = process_data(raw_data)
        
        if not df.empty:
            print("\n✅ Data Successfully Processed:")
            print("-" * 65)
            print(df.to_string(index=False))
            print("-" * 65)
            
            # --- NEW LINE ADDED HERE ---
            push_to_azure_sql(df)
            
        else:
            print("\n--- RAW API RESPONSE (For Debugging) ---")
            print(raw_data)

if __name__ == "__main__":
    main()