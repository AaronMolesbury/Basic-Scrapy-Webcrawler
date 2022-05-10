import json
from operator import index
import matplotlib.pyplot as plt
import pandas as pd
import sys
import re
import numpy as np
from tabulate import tabulate

##### Classes/DAOs #####

# Team DAO
class Team():
    # Constructor
    def __init__(self, name, abbr, pts):
        self.name = name
        self.abbr = abbr
        self.pts = pts
        self.record = []
        self.ppg = []


##### Global Vars #####

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


##### JSON Loaders #####

# Populate teams list
def GetTeamsFromJSON():
    try:
        # Read from File
        file = open("teams.json")
        data = json.load(file)
        file.close()
        df.append(pd.DataFrame(data))
        # Debug to view data to test correctness of import
        ##print(df[0]) 

        # Assign Data to DAOs
        for team in data:
            name = team["Name"]
            abbr = team["Abbreviation"]
            pts = team["Points"]
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
        ##print(df[1]) 
    except:
        sys.exit("ERROR: JSON file was empty, Perhaps spider(s) were ran incorrectly? Check 'results.json' to see if it is populated")
    
    # Debug to view data to test correctness of import
    # df = pd.DataFrame(data)
    # print(df)


##### Helper Functions #####

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
    results = df[1]
    for i in range(len(results)):
        # Corresponding Team DAO
        home_team = FindTeam(results.loc[i, "Home"])
        away_team = FindTeam(results.loc[i, "Away"])
    
        # Home Win
        if(results.loc[i,"Home Score"] > results.loc[i,"Away Score"]):
            home_team.record.insert(0,"W")
            away_team.record.insert(0,"L")
            home_team.ppg.insert(0,3)
            away_team.ppg.insert(0,0)
        # Away Win
        elif(results.loc[i,"Home Score"] < results.loc[i,"Away Score"]):
            home_team.record.insert(0,"L")
            away_team.record.insert(0,"W")
            home_team.ppg.insert(0,0)
            away_team.ppg.insert(0,3)
        # Draw
        elif(results.loc[i,"Home Score"] == results.loc[i,"Away Score"]):
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

# Returns list of totals for W/L/D for a team 
def CalculateWinLossDrawValues(team):
    team_wins = 0
    team_losses = 0
    team_draws = 0
    for result in team.record:
        if result == "W":
            team_wins += 1
        if result == "L":
            team_losses += 1
        if result == "D":
            team_draws += 1
    return [team_wins, team_losses, team_draws]


##### Print Functions #####

# Prints league table
def PrintTable():
    CreateRecentRecordDF()
    form = df[2][0] + " " + df[2][1] + " " + df[2][2] + " " + df[2][3] + " " + df[2][4] 
    table_df = pd.concat([df[0],form], axis=1)
    # Shift index from 0 -> 1 (readability)
    table_df.index = np.arange(1, len(table_df)+1)
    table_df.columns = ["Team Name", "Abbreviation", "Points", "Current Form"]
    print("Premier League Table:")
    print(tabulate(table_df, showindex = True, headers = table_df.columns, tablefmt="pretty"))
    PrintExitNotification()  

# Prints a specified teams record
def PrintTeamRecord(team_name):
    team = FindTeam(team_name)
    record = ""
    for i in range(len(team.record)):
        record += team.record[i]
        record += " "
    wld = CalculateWinLossDrawValues(team)
    data = { 
        "Team Name": team.name,
        "Current Record": record,
        "Won": wld[0],
        "Lost": wld[1],
        "Drawn": wld[2],
        "Total Points": team.pts,
    }
    team_record_df = pd.DataFrame(data, index = [team.name])
    print("\n")
    print(team.name + "'s Current Record:")
    print(tabulate(team_record_df, showindex = False, headers = team_record_df.columns, tablefmt="pretty"))   
    PrintExitNotification()

# Prints a specified teams PPG over a season
def PrintTeamPPG(team_name):
    team = FindTeam(team_name)
    print("\n")
    print("Team Name: " + team.name)
    match = []
    result = []
    points_gained = []
    running_total = []
    for i in range(len(team.ppg)):
        match.append(i + 1)
        result.append(team.record[i])
        gained = 0
        if(team.record[i] == "W"):
            gained = 3
        elif(team.record[i] == "D"):
            gained = 1
        points_gained.append(gained)
        running_total.append(team.ppg[i])
    data = {
        "Match Number": match,
        "Match Result": result,
        "Points Gained": points_gained,
        "Running Total": running_total
    }
    ppg_df = pd.DataFrame(data)
    print("PPG Table:")
    print(tabulate(ppg_df, showindex = False, headers = ppg_df.columns, tablefmt="pretty"))
    PrintExitNotification()

# Prints a League Table after each match of the season
def PrintTeamPlacements():
    placements = []
    # Calculate the minimum matches played by any team
    mp_min = len(teams[0].ppg)
    for team in teams:
        if len(team.ppg) < mp_min:
            mp_min = len(team.ppg)
    for i in range(mp_min):
        placements.append(EvaluatePlacements(i))
    placement_df = pd.DataFrame(placements).sort_index(axis="columns",ascending=True).swapaxes("rows","columns")
    placement_df.columns.name = "Match"
    placement_df.index.name = "Position"
    placement_df.index = np.arange(1, len(placement_df)+1)
    print("Placements Table:")
    print(placement_df)
    PrintExitNotification()

# Prints the comparisons of two given teams
def PrintComparisonResults(first_team_name, second_team_name):
    first_team = FindTeam(first_team_name)
    second_team = FindTeam(second_team_name)
    first_team_wld = CalculateWinLossDrawValues(first_team)
    second_team_wld = CalculateWinLossDrawValues(second_team)
    first_team_ratio = round(first_team_wld[0]/first_team_wld[1],1)
    second_team_ratio = round(second_team_wld[0]/second_team_wld[1],1)
    first_team_wrate = round((first_team_wld[0]/len(first_team.record)) * 100,1)
    second_team_wrate = round((second_team_wld[0]/len(second_team.record)) * 100,1)
    
    # List of comparison indicators
    comparisons = []
    # Compares matches played
    if(len(second_team.record) > len(first_team.record)):
        comparisons.append(" (↑" + str(abs(len(first_team.record) - len(second_team.record))) + ")")
    elif(len(second_team.record) < len(first_team.record)):
        comparisons.append(" (↓" + str(abs(len(second_team.record) - len(first_team.record))) + ")")
    else:
        comparisons.append("(=)")
    # Compares matches won
    if(second_team_wld[0] > first_team_wld[0]):
        comparisons.append(" (↑" + str(abs(first_team_wld[0] - second_team_wld[0])) + ")")
    elif(second_team_wld[0] < first_team_wld[0]):
        comparisons.append(" (↓" + str(abs(second_team_wld[0] - first_team_wld[0])) + ")")
    else:
        comparisons.append(" (=)")
    # Compares matches lost
    if(second_team_wld[1] > first_team_wld[1]):
        comparisons.append(" (↑" + str(abs(first_team_wld[1] - second_team_wld[1])) + ")")
    elif(second_team_wld[1] < first_team_wld[1]):
        comparisons.append(" (↓" + str(abs(second_team_wld[1] - first_team_wld[1])) + ")")
    else:
        comparisons.append(" (=)")
    # Compares matches drawn
    if(second_team_wld[2] > first_team_wld[2]):
        comparisons.append(" (↑" + str(abs(first_team_wld[2] - second_team_wld[2])) + ")")
    elif(second_team_wld[2] < first_team_wld[2]):
        comparisons.append(" (↓" + str(abs(second_team_wld[2] - first_team_wld[2])) + ")")
    else:
        comparisons.append(" (=)")
    # Compares win rates
    if(second_team_wrate > first_team_wrate):
        comparisons.append(" (↑" + str(round(abs(first_team_wrate - second_team_wrate),1)) + "%)")
    elif(second_team_wrate < first_team_wrate):
        comparisons.append(" (↓" + str(round(abs(second_team_wrate - first_team_wrate),1)) + "%)")
    else:
        comparisons.append(" (=)")   
    # Compares W/L ratio  
    if(second_team_ratio > first_team_ratio):
        comparisons.append(" (↑" + str(abs(first_team_ratio - second_team_ratio)) + ")")
    elif(second_team_ratio < first_team_ratio):
        comparisons.append(" (↓" + str(abs(second_team_ratio - first_team_ratio)) + ")")
    else:
        comparisons.append(" (=)") 
    # Compares total points
    if(second_team.pts > first_team.pts):
        comparisons.append(" (↑" + str(abs(int(first_team.pts) - int(second_team.pts))) + ")")
    elif(second_team.pts < first_team.pts):
        comparisons.append(" (↓" + str(abs(int(second_team.pts) - int(first_team.pts))) + ")")
    else:
        comparisons.append(" (=)")

    data = {
        "Matches Played": [len(first_team.record), str(len(second_team.record)) + comparisons[0]],
        "Matches Won": [first_team_wld[0], str(second_team_wld[0]) + comparisons[1]],
        "Matches Lost": [first_team_wld[1], str(second_team_wld[1]) + comparisons[2]],
        "Matches Drawn": [first_team_wld[2], str(second_team_wld[2]) + comparisons[3]],
        "Win Rate": [str(first_team_wrate) + "%", str(second_team_wrate) + "%" + comparisons[4]],
        "W/L Ratio": [first_team_ratio, str(second_team_ratio) + comparisons[5]],
        "Total Points": [first_team.pts, str(second_team.pts) + comparisons[6]],
    }
    comparison_df = pd.DataFrame(data, index=[first_team.name, second_team.name]).swapaxes("rows","columns")
    print("\n")
    print("Comparison Table:")
    print(tabulate(comparison_df, showindex = True, headers = comparison_df.columns, tablefmt="pretty"))
    PrintExitNotification()

# Prints Option Menu + Handles user inputs
def PrintMainMenu():
    # Options Menu
    option_one = "View the current Premier League Table."
    option_two = "View a teams record."
    option_three = "View a teams PPG over the course of the season."
    option_four = "View the team placements over the course of the season."
    option_five = "Compare two team's statistics."
    data = {
        "Option": [1,2,3,4,5],
        "Action": [option_one, option_two, option_three, option_four, option_five]
    }
    menu_df = pd.DataFrame(data)
    print("Options Menu:")
    print(tabulate(menu_df, showindex = False, headers = menu_df.columns, tablefmt="pretty"))
    #User input handling
    print("\n")
    user_input = input("Select option: ")
    print("\n")
    #RegEx check on input
    num_format = re.compile(r'^[1-5]$')
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
        if (user_input ==  "5"):
            first_team_name = input("Type the name of the first team you would like to compare: ")
            print("\n")
            second_team_name = input("Type the name of the second team you would like to compare: ")
            PrintComparisonResults(first_team_name, second_team_name)

# Prints option to continue to use program or exit
def PrintExitNotification():
    print("\n")
    print("Would you like to select another option?")
    user_input = input("(Type [y/n]): ")
    print("\n")
    #RegEx check on input
    response_format = re.compile(r'^[yn]$')
    is_valid = re.match(response_format, user_input)
    if(is_valid):
        if(user_input == "y"):
            print("======================================================================================")
            print("\n")
            PrintMainMenu()
        else:
            print("See you soon! Exiting...")
            return
    elif(not is_valid):
        print("That input was invalid, please try again:")
        PrintExitNotification()


##### Main Program #####

# Main Program
def main():
    #Retrieve teams from JSON generated by spider
    print("\n")
    print("Retrieving Team data from PLTeamSpider...")
    print("\n")
    GetTeamsFromJSON()
    #Populate results
    print("Retrieving Results data from PLResultsSpider...")
    print("\n")
    GetResultsFromJSON()
    PopulateTeamResults()
    print("=================================================================================================")
    print(" Welcome to my simple Premier League data handler! Please choose one of the following options...")
    print("=================================================================================================")
    print("\n")
    PrintMainMenu()


#Execute Main
main()