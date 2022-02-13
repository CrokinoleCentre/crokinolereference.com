# Crokinole Reference - Script to Generate webpages

## Check input files to scan for errors
## NOTE: this script is independent of others

import outputlog

outputlog.generate_input_check("Beginning Import for Input Checks")
## A) links
import os
path = os.getcwd()
parent_path = os.path.abspath(os.path.join(path, os.pardir))
input_location = parent_path + '/inputs/'
results_name = input_location + 'All Crokinole Results.xlsx'
matches_name = input_location + 'Crokinole Match Detail.xlsx'
rankings_name = input_location + 'Rankings BT Python.xlsx'

## B) import scripts
import excelimport 
import pandas

## C) import files
a_results = excelimport.import_excel(results_name, 'Results')
a_matches = excelimport.import_excel(matches_name, 'Matches')
a_leagues = excelimport.import_excel(results_name, 'Leagues')
a_mapping = excelimport.import_excel(results_name, 'Mapping')
#### exclude private data
a_results = a_results[a_results['Inclusion']!='Private']
a_matches = a_matches[a_matches['Inclusion']!='Private']

## D) series of input checks on current inputs
outputlog.generate_input_check("Beginning Input Checks")

# 1) Check data types of results, check for blanks
def check_blanks_and_data_types(results, input_name):
    all_string_no_blanks = ['Inclusion','Classification','Tournament','Division','Player']
    all_string_some_blanks = ['League','Category','Format','Stage','Pool','Team','Comment']
    all_floats_some_blanks = ['Games','Pts','20s']
    all_integer_no_blanks = ['Rank']
    all_date_no_blanks = ['Date']
    
    for col in all_string_no_blanks:
        if col in results.columns:
            if len(results[col]) != len(results[col].dropna()):
                text = col +' in '+input_name+' has blanks when there should be none.'
                outputlog.generate_input_check(text)
            if set(results[col].apply(type)) != {str}:
                text = col +' in '+input_name+' has non string types.'
                outputlog.generate_input_check(text)
    for col in all_string_some_blanks:
        if col in results.columns:
            if set(results[col].dropna().apply(type)) != {str}:
                text = col +' in '+input_name+' has non string types.'
                outputlog.generate_input_check(text)
    for col in all_floats_some_blanks:
        if col in results.columns:
            if set(results[col].dropna().apply(type)) != {float}:
                text = col +' in '+input_name+' has non float types.'
                outputlog.generate_input_check(text)
    for col in all_integer_no_blanks:
        if col in results.columns:
            if len(results[col]) != len(results[col].dropna()):
                text = col +' in '+input_name+' has blanks when there should be none.'
                outputlog.generate_input_check(text)
            if set(results[col].apply(type)) != {int}:
                text = col +' in '+input_name+' has non integer types.'
                outputlog.generate_input_check(text)
    for col in all_date_no_blanks:
        if col in results.columns:
            if len(results[col]) != len(results[col].dropna()):
                text = col +' in '+input_name+' has blanks when there should be none.'
                outputlog.generate_input_check(text)
            if set(results[col].apply(type)) != {pandas._libs.tslibs.timestamps.Timestamp}:
                text = col +' in '+input_name+' has non integer types.'
                outputlog.generate_input_check(text)
check_blanks_and_data_types(a_results, "Results")
outputlog.generate_input_check("Step 1 check complete")

# 2) Results has 'Final Rank' or 'Final Rank-Incomplete' for every event-division-category combination, and those Final Ranks all have a #1
results = a_results.copy()
results = results.fillna('blank') #placeholder for nan values
q = results.groupby(['Date','Tournament','Division','Category'], dropna=False).size().reset_index().rename(columns={0:'count'})
for i in q.index:
    date=q.loc[i, 'Date']
    tournament=q.loc[i, 'Tournament']
    division=q.loc[i, 'Division']
    category=q.loc[i, 'Category']
    results_group = results[(results['Date']==date)
                            & (results['Tournament']==tournament)
                            & (results['Division']==division)
                            & (results['Category']==category)
                            & ((results['Classification'] == 'Final Rank')
                               | (results['Classification'] == 'Final Rank-Incomplete')
                               | (results['Classification'] == 'League Standings')
                               | (results['Classification'] == 'League Standings-Incomplete'))]
    results_group_final_rank = results_group[results_group['Rank']==1]
    if len(results_group) == 0:
        text_output = 'No final rank exists for '+ str(date)+' '+tournament+' '+division+' '+category
        outputlog.generate_input_check(text_output)
    elif len(results_group_final_rank) == 0:
        text_output = 'No #1 rank exists for '+ str(date)+' '+tournament+' '+division+' '+category
        outputlog.generate_input_check(text_output) 
    elif len(results_group_final_rank) != 1:
        text_output = 'Mult #1 rank exists for '+ str(date)+' '+tournament+' '+division+' '+category
        outputlog.generate_input_check(text_output)  
outputlog.generate_input_check("Step 2 check complete")

# 3) Every row tagged with Incomplete has a 'Total number of players' comment
results = a_results.fillna('')
incomplete_results = results[(results['Classification'] == 'Scores-Incomplete')
                             | (results['Classification'] == 'Final Rank-Incomplete')
                             | (results['Classification'] == 'Rank-Incomplete')
                             | (results['Classification'] == 'League Standings-Incomplete')]
for index in incomplete_results.index:
    comment = str(incomplete_results.loc[index, 'Comment'])
    if "Total number of players = " not in comment:
        date=incomplete_results.loc[index, 'Date']
        tournament=incomplete_results.loc[index, 'Tournament']
        division=incomplete_results.loc[index, 'Division']
        category=incomplete_results.loc[index, 'Category']
        stage = incomplete_results.loc[index, 'Stage']
        pool=incomplete_results.loc[index, 'Pool']
        player=incomplete_results.loc[index, 'Player']
        text_output = 'No comment for number of players for '+ str(date)+' '+tournament+' '+division+' '+category+' '+stage+' '+pool+' '+player
        outputlog.generate_input_check(text_output)
outputlog.generate_input_check("Step 3 check complete")

# 4) Every League in Results:Leagues has a League Standings in Results and vice versa
def league_comparison(a_leagues, results):
    league_list = list(a_leagues['League tag'])
    counter = 0 #can't use simple for loop on list index because deleting from a list terminates the loop
    adj = 0
    limit = len(league_list)
    for counter in range(limit): #remove ',' because these are for cross-listed events
        tag = league_list[counter-adj]
        if ',' in tag:
            league_list.remove(tag)
            adj += 1
        counter += 1
    league_standing_results = results[(results['Classification'] == 'League Standings')
                                      | (results['Classification'] == 'League Standings-Incomplete')]
    league_list_result = list(set(league_standing_results['League']))
    if len(league_list) == len(league_list_result):
        if league_list.sort() == league_list_result.sort():
            text = 'All leagues accounted for'
    else:
        missing_from_leagues = league_list_result
        missing_from_results = league_list
        for league in league_list:
            if league in league_list_result:
                missing_from_results.remove(league)
                missing_from_leagues.remove(league)
        text = 'Missing from leagues: '+str(missing_from_leagues)+'. Missing from results: '+str(missing_from_results)
    return text                    
text = league_comparison(a_leagues, a_results)   
outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 4 check complete")

# 5) every row has a Division with exactly one hyphen and no spaces
all_divisions = set(results['Division'])
for this_div in all_divisions:
    count_hyphen = this_div.count('-')
    if count_hyphen != 1:
        text_output = 'Results file does not have exactly one hyphen for: '+this_div
        outputlog.generate_input_check(text_output) 
    count_spaces = this_div.count(' ')
    if count_spaces != 0:
        text_output = 'Results file does not have 0 spaces for: '+this_div
        outputlog.generate_input_check(text_output) 
outputlog.generate_input_check("Step 5 check complete")

# 5-1) If the team field is populated, then there must be an event with the same Date and Tournament, and Category = Teams, and a team with the same name exists.
results = a_results.fillna('')
result_team_members = results[results['Team']!='']
results_teams = results[results['Category']=='Teams']
for date, tournament, division, category, team in zip(result_team_members['Date'],result_team_members['Tournament'],result_team_members['Division'],result_team_members['Category'],result_team_members['Team']):
    this_teams_result = results_teams[(results_teams['Date']==date)
                                      & (results_teams['Tournament']==tournament)
                                      & (results_teams['Player']==team)]
    if len(this_teams_result)==0:
        text = 'Team result does not exist for team '+team+' in '+str(date)+' '+tournament+' '+division+' '+category
        outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 5-1 check complete")

# 6) for league standings Category must be blank (because it’s not referenced)
results = a_results.fillna('')
league_results = results[(results['Classification'] == 'League Standings')
                         | (results['Classification'] == 'League Standings-Incomplete')]
if set(league_results['Category']) != {''}:
    outputlog.generate_input_check("A Category in League Standings is not blank. While this won't cause a failure, this field is never referenced so it should not be used to distinguish between another league.")
outputlog.generate_input_check("Step 6 check complete")

# 7) For the Scores, Rank, Scores-Inc: ensure no blanks in Games, Stage, Pool
results = a_results.copy()
pool_results = results[(results['Classification'] == 'Scores-Incomplete')
                       | (results['Classification'] == 'Scores')
                       | (results['Classification'] == 'Rank')]
col_list = ['Games','Stage','Pool']
for col in col_list:
    if len(pool_results[col]) != len(pool_results[col].dropna()):
        text = col +' in Results has blanks when there should be none.'
        outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 7 check complete")

# 8) For Rank-Inc: ensure no blanks Stage, Pool
pool_results = results[(results['Classification'] == 'Rank-Incomplete')]
col_list = ['Stage','Pool']
for col in col_list:
    if len(pool_results[col]) != len(pool_results[col].dropna()):
        text = col +' in Results has blanks when there should be none.'
        outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 8 check complete")

# 9) For League Standings: there is only one entry date per league, and Stage is either Final or Prelim
def league_standings_check(results):
    text = ''
    league_results = results[(results['Classification'] == 'League Standings-Incomplete')
                             | (results['Classification'] == 'League Standings')]
    league_list = list(set(league_results['League']))
    for league in league_list:
        date_list = list(set(league_results[league_results['League']==league]['Date']))
        if len(date_list) > 1:
            text += 'More than one date of league standings in Results for '+league+'.'
        stage_list = list(set(league_results[league_results['League']==league]['Stage']))
        if len(stage_list) > 1:
            text += 'More than one Stage tag for league standings in Results for '+league+'.'
        else:
            if (stage_list[0] != 'Final') & (stage_list[0] != 'Prelim'):
                text += 'Stage tag is not Final or Prelim for league standings in Results for '+league+'.'
       
    if text == '':
        text = 'League Standings check is all good.'
        
    return text

text = league_standings_check(a_results)
outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 9 check complete")

# 9-1) Check listing of stages. If there’s new stages they should be added to the Events script in the orders_stages function.
stages_in_results = list(set(a_results['Stage']))
stages_in_matches = list(set(a_matches['Stage']))
stage_list_order = [ #regular events
'Prelim', 'Power Pool','R16','R8','Quarter','Final 8','Final 6','Final 4','Final 3',
#little more strange stuff for top 4 playoffs
'Page Playoff','Semi','Semi G1','Semi G2','Semi G3','Final','Final G1','Final G2','Final G3',
#Mixed discipline event: Excelling Eight
'4 Player Singles','Doubles','Singles']
for stage in stages_in_results:
    if (stage==stage) & (stage not in stage_list_order):
        outputlog.generate_input_check(stage + " is in results, but is not in stage_list_order")
for stage in stages_in_matches:
    if (stage==stage) & (stage not in stage_list_order):
        outputlog.generate_input_check(stage + " is in matches, but is not in stage_list_order")
outputlog.generate_input_check("Step 9-1 check complete. Add missing stages to orders_stage function in Events script before running rest of script.")

# 10) Every League tag must exist in Results[‘League’] and vice versa
def league_comparison2(a_leagues, results):
    league_list = list(a_leagues['League tag'])
    league_list_result = list(set(results['League'].dropna()))
    if len(league_list) == len(league_list_result):
        if league_list.sort() == league_list_result.sort():
            text = 'All leagues accounted for'
    else:
        missing_from_leagues = league_list_result
        missing_from_results = league_list
        for league in league_list:
            if league in league_list_result:
                missing_from_results.remove(league)
                missing_from_leagues.remove(league)
        text = 'Missing from leagues: '+str(missing_from_leagues)+'. Missing from results: '+str(missing_from_results)
    return text                    
text = league_comparison2(a_leagues, a_results)   
outputlog.generate_input_check(text)
outputlog.generate_input_check("Step 10 check complete")

# 11) every league tag must be unique
league_list = list(a_leagues['League tag'])
unique_list = list(set(league_list))
if len(league_list) != len(unique_list):
    outputlog.generate_input_check("Not all league tags in Leagues are unique")
outputlog.generate_input_check("Step 11 check complete")

# 12) For every stage/pool every player and opponent must exist in the stage/pool of results
def matches_name_check(matches, results):
    q = matches.groupby(['Date','Tournament','Division','Category', 'Stage','Pool']).size().reset_index().rename(columns={0:'count'})
    for i in q.index:
        date = q.loc[i,'Date']
        tournament = q.loc[i,'Tournament']
        division = q.loc[i,'Division']
        category = q.loc[i,'Category']
        stage = q.loc[i,'Stage']
        pool = q.loc[i,'Pool']
        this_matches = matches[(matches['Date']==date)
                           & (matches['Tournament']==tournament)
                           & (matches['Division']==division)
                           & (matches['Category']==category)
                           & (matches['Stage']==stage)
                           & (matches['Pool']==pool)]
        this_results = results[(results['Date']==date)
                            & (results['Tournament']==tournament)
                            & (results['Division']==division)
                            & (results['Category']==category)
                            & (results['Stage']==stage)
                            & (results['Pool']==pool)]
        matches_players = list(set(this_matches['Player']))
        matches_opponents = list(set(this_matches['Opponent']))
        results_players = list(set(this_results['Player']))
        for this_player in matches_players:
            if not this_player in results_players:
                text_output = 'Player inconsistency for ' + str(date)+' '+tournament+' '+division+' '+category+' '+stage+' '+pool+': '
                text_output = text_output + this_player + ' in matches, but not in results.'
                outputlog.generate_input_check(text_output)
        for this_player in matches_opponents:
            if not this_player in results_players:
                text_output = 'Player inconsistency for ' + str(date)+' '+tournament+' '+division+' '+category+' '+stage+' '+pool+': '
                text_output = text_output + this_player + ' in matches, but not in results.'
                outputlog.generate_input_check(text_output)
            
matches_name_check(a_matches, a_results)
outputlog.generate_input_check("Step 12 check complete")

# 13) For every stage/pool the player points and totals should match results, but likely there's discrepancies -> find some way to note this -> maybe the script generates a tag saying “match data is incomplete” or “match data has numerous discprepances to official results” or “match data aligns nearly perfectly with official results”
## prev A2

## E) comparison to prior input
### Results
##### Check Date-Tournament-Division-Category combos, what's new/missing
####### for each of those, comparison of # rows with Scores, Ranks, Final Rank, etc
####### row by row comparison, but stop at max X differences

### same for Matches



