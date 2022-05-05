import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import re


# Team DAO
class Team():
    # Constructor
    def __init__(self, name, abbr, pts):
        self.name = name
        self.abbr = abbr
        self.pts = pts
        self.record = []
        self.ppg = []

    # Getters
    def GetName(self):
        return self.name
    
    def GetAbbr(self):
        return self.abbr

    def GetPts(self):
        return self.pts

# List of all team objects
teams = []
# List of DataFrames
# Indexed as follows
# 0 = Teams
# 1 = Results
# 2 = Records
# 3 = PPG
# 4 = Placement per match
df = []


# Populate teams list
def GetTeamsFromJSON():
    try:
        # Read from File
        file = open("teams.json")
        data = json.load(file)
        file.close()
        df.append(pd.DataFrame(data))
        # Debug to view data to test correctness of import
        ###print(df[0]) 

        # Assign Data to DAOs
        for team in data:
            name = team["name"]
            abbr = team["abbreviation"]
            pts = team["points"]
            teams.append(Team(name, abbr, pts))
    except:
        sys.exit("ERROR: JSON file was empty, Perhaps spider(s) were ran incorrectly? Check 'teams.json' to see if it is populated")

# Returns pd dataframe of results
def GetResultsFromJSON():
    try:
        # Read from File
        file = open("results.json")
        data = json.load(file)
        file.close()
        df.append(pd.DataFrame(data))
        # Debug to view data to test correctness of import
        # print(df[1]) 
        return df[1]

    except:
        sys.exit("ERROR: JSON file was empty, Perhaps spider(s) were ran incorrectly? Check 'results.json' to see if it is populated")
    
    # Debug to view data to test correctness of import
    # df = pd.DataFrame(data)
    # print(df)

# Returns team DAO by name
def FindTeam (team_name):
    for team in teams:
        if team.name == team_name:
            return team
    print("\n")
    print("ERROR: Team with name '" + team_name + "' was not found. Perhaps the name is spelt incorrectly?")
    print("\n")

# Populates 'record' and 'ppg' lists per team accordingly
def PopulateTeamResults():
    results = GetResultsFromJSON()
    for i in range(len(results)):
        # Corresponding Team DAO
        home_team = FindTeam(results.loc[i, "home"])
        away_team = FindTeam(results.loc[i, "away"])
    
        # Home Win
        if(results.loc[i,"home score"] > results.loc[i,"away score"]):
            home_team.record.insert(0,"W")
            away_team.record.insert(0,"L")
            home_team.ppg.insert(0,3)
            away_team.ppg.insert(0,0)
        # Away Win
        elif(results.loc[i,"home score"] < results.loc[i,"away score"]):
            home_team.record.insert(0,"L")
            away_team.record.insert(0,"W")
            home_team.ppg.insert(0,0)
            away_team.ppg.insert(0,3)
        # Draw
        elif(results.loc[i,"home score"] == results.loc[i,"away score"]):
            home_team.record.insert(0,"D")
            away_team.record.insert(0,"D")
            home_team.ppg.insert(0,1)
            away_team.ppg.insert(0,1)
    
    #Calculates Cumulative Sum of PPG for each team
    for team in teams:
        team_ppg_cumsum=[]
        for i in range(len(team.ppg)):
            if i == 0:
                team_ppg_cumsum.append(team.ppg[i])
            else:
                team_ppg_cumsum.append(team_ppg_cumsum[i-1] + team.ppg[i])
        team.ppg = team_ppg_cumsum

# Create recent record for last 5 games for table in option 1
def CreateRecentRecordDF():
    record_list = []
    for team in teams:
        record_list.append(team.record[-5:])
    df.append(pd.DataFrame(record_list))

# Evaluates placement of match index
def EvaluatePlacements(index):
    placement = sorted(teams, key=lambda team: team.ppg[index])
    for i in range(len(placement)):
        placement[i] = placement[i].name
    placement.reverse()
    return placement

# Prints league table
def PrintTable():
    CreateRecentRecordDF()
    table_df = pd.concat([df[0],df[2]], axis=1)
    print(table_df)  

# Prints a specified teams record
def PrintTeamRecord(team_name):
    team = FindTeam(team_name)
    print(team.record)     

# Prints a specified teams PPG (Cumulative)
def PrintTeamPPG(team_name):
    team = FindTeam(team_name)
    print(team.ppg)

def PrintTeamPlacements():
    placements = []
    team = teams[0]
    for i in range(len(team.ppg)):
        placements.append(EvaluatePlacements(i))
    placement_df = pd.DataFrame(placements).sort_index(axis="columns",ascending=True).swapaxes("rows","columns")
    placement_df.columns.name = "Match"
    placement_df.index.name = "Position"
    print(placement_df)

def PrintMainMenu():
    # Options Menu
    print("Type '1' to view the current Premier League Table.")
    print("\n")
    print("Type '2' to view a teams record.")
    print("\n")
    print("Type '3' to view a teams PPG over time.")
    print("\n")
    print("Type '4' to view a teams placement over the course of the season.")
    print("\n")
    #User input handling
    user_input = input("Select option: ")
    print("\n")
    #RegEx check on input
    num_format = re.compile(r'^[1-4]$')
    is_valid = re.match(num_format, user_input)
    if(not is_valid):
        print("That input was invalid, please try again, selecting from one of the following options...")
        PrintMainMenu()
    else:
        #Option handling
        if (user_input == "1"): 
            PrintTable()
        if (user_input ==  "2"):
            tname = input("Type the name of the team you would like to view the record of: ")
            PrintTeamRecord(tname)
        if (user_input ==  "3"):
            tname = input("Type the name of the team you would like to view the PPG of: ")
            PrintTeamPPG(tname)
        if (user_input ==  "4"):
            PrintTeamPlacements()

#####################################################################################################################

#Main Program
def main():
    #Retrieve teams from JSON generated by spider
    print("\n")
    print("Retrieving Team data from PLTeamSpider...")
    print("\n")
    GetTeamsFromJSON()
    #Populate results
    print("Retrieving Results data from PLResultsSpider...")
    print("\n")
    PopulateTeamResults()
    print("======================================================================================")
    print(" Welcome to my simple EPL data handler! Please choose one of the following options...")
    print("======================================================================================")
    print("\n")
    PrintMainMenu()


#Execute Main
main()