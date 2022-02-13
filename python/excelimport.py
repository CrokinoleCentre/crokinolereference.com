# Crokinole Reference - Script to Generate webpages

## Excel Import and Transformation
#### transformation involves adding columns to the tables

import pandas

def generate_results(file, sheet):
    rawresults = import_excel(file, sheet) #import
    
    #removing parts of results denoted private
    results = rawresults[rawresults["Inclusion"] != 'Private']
    # add Player 1/Player 2 fields
    results = split_team_names(results)
    # add 20s Rank if Classification=Scores
    results = add_20s_rank(results, '20s', "20s Rank")
    # add 10-Game-Adj-Pts and 10-Game-Adj-20s
    results = add_game_adjusted_field(results, "Pts", 10, "10-Game-Adj Pts")
    results = add_game_adjusted_field(results, "20s", 10, "10-Game-Adj 20s")
    # rename Date field to "Structured Date"
    results = results.rename(columns={'Date':'Structured Date'})
    # add the re-formatted date field as "Date"
    results['Date'] = results['Structured Date'].dt.strftime('%b %d, %Y')
    # add the field "Year"
    results['Year'] = results['Structured Date'].dt.strftime('%Y')
    #number of players in group/event
    results = add_num_players(results, '# Entries')
    # if there's a comment in a Category=Teams row containing 'Team members' then add dummy rows for those players if not already exist
    results = add_team_member_dummy_rows(results, 'Team members: ')
    #add team results: for final rank/Team dummy if team is not blank, add team rank, # team entries
    results = add_team_results(results, 'Team Rank', '# Teams')
    
    return results

def generate_matches(file, sheet):
    rawmatches = import_excel(file, sheet) #import
    
    #removing parts of results denoted private
    results = rawmatches[rawmatches["Inclusion"] != 'Private']
    # add Player 1/Player 2 fields to all rows
    results = split_team_names(results)
    # rename Date field to "Structured Date"
    results = results.rename(columns={'Date':'Structured Date'})
    # add the re-formatted date field as "Date"
    results['Date'] = results['Structured Date'].dt.strftime('%b %d, %Y')
    # add the field "Year"
    results['Year'] = results['Structured Date'].dt.strftime('%Y')
    # number of rounds
    results = add_num_rounds(results, '# Rounds')
    # number of hammer/1st shot pts/20s
    results = add_hammer_first_shot_totals(results, 'Hammer Total', 'First Total', '# Hammer Rounds', '# First Rounds')

    return results

def generate_rankings(file, sheet):
    rawrankings = import_excel(file, sheet) #import
    
    # add Player 1/Player 2 fields to all rows
    results = split_team_names(rawrankings)
    # rename Date field to "Structured Date"
    results = results.rename(columns={'Date':'Structured Date'})
    # add the re-formatted date field as "Date"
    results['Date'] = results['Structured Date'].dt.strftime('%b %d, %Y')

    return results

def save_to_excel(dataframe, location, filename, sheetname):
    path = location + filename + '.xlsx'
    # index false means dataframe index won't appear as separate column
    dataframe.to_excel(path, index=False, sheet_name = sheetname)

##### Helper Functions


def import_excel(file, sheet):
    wb = pandas.read_excel(file, sheet_name=sheet, converters={'Year': str})
    ## year conversion is for re-importing input files after they've been through the import script
    ### we want the year column the import script adds to be able to be referenced correctly
    return wb

### add columns to results, matches and ranking files to access individual players of doubles team
def split_team_names(raw_table):
##### input: any of the raw results/rankings tables
##### output: that same table with 2 appended columns "Player 1" and "Player 2"
###### if singles, then only Player 1 is filled, with same name as Player
###### all files put the player/doubles team in a field called "Player"
###### teams will be split by looking for "/" as separator
    p1_col = []
    p2_col = []
    for team_name in raw_table['Player']:
        if '/' in team_name: #look for /
            mid = team_name.find('/')
            p1 = team_name[:mid]
            p2 = team_name[mid+1:]
            p1_col += [p1]
            p2_col += [p2]
        else: # populate Player 1 with Player field
            p1_col += [team_name]
            p2_col += ['']
    
    out = raw_table.copy()
    out['Player 1'] = p1_col
    out['Player 2'] = p2_col
    return out

#res = add_20s_rank(rawresults, '20s','20s Rank')
def add_20s_rank(results_file, col_to_rank, new_rank_column_name):
    results = results_file.copy()
    results[new_rank_column_name] = ''
    scores_only = results[results['Classification']=='Scores']
    q = scores_only.groupby(['Date','Tournament','Division','Category','Stage','Pool']).size().reset_index().rename(columns={0:'count'})
    for date, tournament, division, category, stage, pool in zip(q['Date'],q['Tournament'],q['Division'],q['Category'],q['Stage'],q['Pool']):
        one_pool_results = results[(results["Date"]==date)
                                   & (results["Tournament"]==tournament)
                                   & (results["Division"]==division)
                                   & (results["Category"]==category)
                                   & (results["Stage"]==stage)
                                   & (results["Pool"]==pool)]
        only_20s = one_pool_results[col_to_rank]
        pool_20s_rank = only_20s.rank(method='min', ascending=False) #give min rank for ties
        z=pandas.Series(pool_20s_rank, name=new_rank_column_name)
        results.update(z)
    
    return results

### add game adjusted fields for Pts, 20s (can alter the game # to adjust for)
#### rounded to 1 decimal
def add_game_adjusted_field(results, raw_field, game_adj, target_column):
    results_file = results.copy()
    #initialize the target column
    results_file[target_column] = results_file[raw_field]
    #setting blanks to 0 to avoid errors later
    results_file[target_column][results_file[target_column]==""] = 0
    #pro-rate the field for the desired game adjustment
    results_file[target_column] = results_file[target_column] * game_adj / results_file["Games"]
    #round to 1 decimal
    results_file[target_column] = round(results_file[target_column],1)
    #replace nan values with blanks
    #results_file[target_column]=results_file[target_column].fillna('')

    return results_file

### add number of players in group 
#### for non-final rank -> num players in a particular stage/pool
#### for final rank -> num players in event
def add_num_players(results_file, column_name):
    results = results_file.fillna('')
    
    results[column_name] = ''
    q = results.groupby(['Classification','Date','Tournament','Division','Category','Stage','Pool','Comment']).size().reset_index().rename(columns={0:'count'})
    for classification, date, tournament, division, category, stage, pool, comment, num_entries in zip(q['Classification'],q['Date'],q['Tournament'],q['Division'],q['Category'],q['Stage'],q['Pool'],q['Comment'],q['count']):
        one_pool_results = results[(results["Date"]==date)
                                   & (results["Classification"]==classification)
                                   & (results["Tournament"]==tournament)
                                   & (results["Division"]==division)
                                   & (results["Category"]==category)
                                   & (results["Stage"]==stage)
                                   & (results["Pool"]==pool)]
        if 'Incomplete' in classification:
            list_comments = comment.split(';') #separate comments by semicolon
            if check_str_contained_in_list("Total number of players = ", list_comments):
                number = right_of_string("Total number of players = ", list_comments)
            else:
                number = 'Not recorded'
            one_pool_results[column_name] = number
        else:
            one_pool_results[column_name] = len(one_pool_results)

        z=pandas.Series(one_pool_results[column_name], name=column_name)
        results.update(z)
    
    results_file[column_name] = results[column_name]
    
    return results_file

def check_str_contained_in_list(check_string, list_of_comments):
    for i in range(len(list_of_comments)):
        if check_string in list_of_comments[i]:
            return True #function returns true if it's found
    return False # false returned if it gets to this step

def right_of_string(check_string, list_of_comments):
    for i in range(len(list_of_comments)):
        if check_string in list_of_comments[i]:
            len_full = len(list_of_comments[i])
            len_check = len(check_string)
            diff = len_full - len_check
            return list_of_comments[i][-diff:]

# add dummy rows to list team members of a team event, if that listing available in comments
## only if those players aren't already listed as part of the team in the results:
    ## ex. Schneider Haus singles results might be there listing the player on a team in the Category=Singles, so this dummy record wouldn't be needed
def add_team_member_dummy_rows(results, comment_string):
    #comment_string = 'Team members: '
    res = results.fillna('')
    team_rows_w_comment = res[(res['Category']=='Teams')
                              & (res['Comment']!='')]
    players_with_teams = res[res['Team']!='']
    dummy_rows = pandas.DataFrame(columns=res.columns)
    for i in team_rows_w_comment.index:
        comment = team_rows_w_comment.loc[i,'Comment']
        list_comments = comment.split(';')
        if check_str_contained_in_list(comment_string, list_comments):
                player_list_str = right_of_string(comment_string, list_comments)
                player_list = player_list_str.split(',') #team members separated by commas
                for player in player_list: #trim for spaces, add dummy rows
                    player = str.strip(player)
                    # make the row
                    new_row = team_rows_w_comment.loc[i]
                    new_row['Classification']='Team-dummy'
                    new_row['Category']='Team-dummy'
                    new_row['Player']=player
                    new_row['Player 1']=player
                    new_row['Rank']='Team-dummy'
                    new_row['Team']=team_rows_w_comment.loc[i,'Player']
                    # check if row already exists in dummy or players_with_teams
                    check_dummy = dummy_rows[(dummy_rows['Date']==new_row['Date'])
                                             & (dummy_rows['Tournament']==new_row['Tournament'])
                                             & (dummy_rows['Player']==player)]
                    check_players_w_teams = players_with_teams[(players_with_teams['Date']==new_row['Date'])
                                                               & (players_with_teams['Tournament']==new_row['Tournament'])
                                                               & (players_with_teams['Player']==player)]
                    # append row to dummy_rows
                    if (len(check_dummy)==0) & (len(check_players_w_teams)==0):
                        dummy_rows = dummy_rows.append(new_row).reset_index(drop=True)
    
    out_results = results.append(dummy_rows).reset_index(drop=True)

    return out_results

#add team results: for final rank/Team dummy if team is not blank, add team rank, # team entries
def add_team_results(results, rank_col, entries_col):
    res = results.fillna('')
    res[rank_col] = ''
    res[entries_col] = ''
    players_w_teams = res[(res['Team']!='')
                          & ((res['Classification']=='Team-dummy')
                             | (res['Classification']=='Final Rank')
                             | (res['Classification']=='Final Rank-Incomplete'))]
    team_results = res[(res['Category']=='Teams')
                       & ((res['Classification']=='Final Rank')
                          | (res['Classification']=='Final Rank-Incomplete'))]
    for i in players_w_teams.index:
        date = results.loc[i, 'Date']
        tournament = results.loc[i, 'Tournament']
        team = results.loc[i, 'Team']
        team_row = team_results[(team_results['Date']==date)
                                 & (team_results['Tournament']==tournament)
                                 & (team_results['Player']==team)]
        team_rank = team_row['Rank']
        team_rank = team_rank.iloc[0]
        team_entries = team_row['# Entries']
        team_entries = team_entries.iloc[0]
        results.loc[i, rank_col] = team_rank
        results.loc[i, entries_col] = team_entries
    
    return results

### add number of rounds to matches file
def add_num_rounds(results, column_name):
    results[column_name]=0
    
    for i in results.index:
        rounds_vector = results.loc[i, 'Round1':'Round20']
        # first look for number of rounds populated in the row
        num_rounds = 20 - rounds_vector.isnull().sum()
        if num_rounds == 0:
            # if no rows populated then find counterparty row and sum the points
            event = results.loc[i, 'Tournament']
            date = results.loc[i, 'Date']
            division = results.loc[i, 'Division']
            discipline = results.loc[i, 'Category']
            stage = results.loc[i, 'Stage']
            pool = results.loc[i, 'Pool']
            p1 = results.loc[i, 'Player']
            p2 = results.loc[i, 'Opponent']
            this_game = results[(results['Tournament']==event)
                                & (results['Date']==date)
                                & (results['Division']==division)
                                & (results['Category']==discipline)
                                & (results['Stage']==stage)
                                & (results['Pool']==pool)
                                & ((results['Player']==p1) | (results['Player']==p2))
                                & ((results['Opponent']==p1) | (results['Opponent']==p2))]
            pts_only_rows = this_game[this_game['Pts/20s']=='Pts']
            total_pts = sum(pts_only_rows['Total'])
            num_plyrs = len(pts_only_rows)
            num_rounds = round(total_pts/2)
            # incomplete data flag if not enough people found
            if (num_rounds != 4) & (num_plyrs != 2):
                num_rounds = str(num_rounds) + '?'
            
        results.loc[i, column_name] = num_rounds
        
    return results

def add_hammer_first_shot_totals(results, hammer_column, first_column, hammer_number, first_number):
    results[hammer_column]=''
    results[first_column]=''
    results[hammer_number]=''
    results[first_number]=''
    
    for i in results.index:
        if not isNaN(results.loc[i,'First/Hammer']):
            if results.loc[i,'First/Hammer']=='Hammer':
                hammer_id=['Round1','Round3','Round5','Round7','Round9','Round11','Round13','Round15','Round17','Round19']
                first_id=['Round2','Round4','Round6','Round8','Round10','Round12','Round14','Round16','Round18','Round20']
            if results.loc[i,'First/Hammer']=='First':
                first_id=['Round1','Round3','Round5','Round7','Round9','Round11','Round13','Round15','Round17','Round19']
                hammer_id=['Round2','Round4','Round6','Round8','Round10','Round12','Round14','Round16','Round18','Round20']
            hammer_rounds = results.loc[i,hammer_id]
            first_rounds = results.loc[i,first_id]
            # remove nan values
            hammer_rounds = hammer_rounds[~hammer_rounds.isnull()]
            first_rounds = first_rounds[~first_rounds.isnull()]
            # add data to table
            results.loc[i,hammer_column] = sum(hammer_rounds)
            results.loc[i,first_column] = sum(first_rounds)
            results.loc[i,hammer_number] = len(hammer_rounds)
            results.loc[i,first_number] = len(first_rounds)
    
    return results
    
def isNaN(string):
    return string != string

### 