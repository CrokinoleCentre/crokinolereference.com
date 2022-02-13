# Crokinole Reference - Script to Generate webpages

## Generate index and guide pages
    
# other crokinole reference scripts
import outputlog
import htmlwrite
# python modules
from datetime import datetime
import pandas
import unidecode
import math
import random


# Main)
def generate(rawresults, rawrankings, rawleagues, player_dict, events_dict, league_dict, league_year_cat_dict, events_dict_div_format, ranking_cat_dict, webpage_output_location, layout_dict):
    html_dict_index = gen_index_dict(rawresults, rawrankings, rawleagues, player_dict, events_dict, events_dict_div_format, ranking_cat_dict)
    link = 'index.html'
    htmlwrite.generate(link, webpage_output_location, html_dict_index, layout_dict)
    html_dict_guide = gen_guide_dict(rawresults, rawrankings, rawleagues, league_dict, league_year_cat_dict, events_dict, player_dict, events_dict_div_format, ranking_cat_dict)
    link = 'guide.html'
    htmlwrite.generate(link, webpage_output_location, html_dict_guide, layout_dict)
    outputlog.generate("Index and guide pages created")
    
# generate html index dictionary
def gen_index_dict(rawresults, rawrankings, rawleagues, player_dict, events_dict, events_dict_div_format, ranking_cat_dict):
    # initialize html lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_subtitles = []
    list_of_tables_titles_href = []
    list_of_tables_subtitles_href = []
    
    # make the tables
    
    ## 1) - latest CC rankings - fingers overall
    ### get latest ranking from dict
    a1=list(ranking_cat_dict.keys())
    a2=[x for x in a1 if ('Fingers Overall' in x)]
    a3=[x[0:12] for x in a2]
    a4=[datetime.strptime(x, '%b %d, %Y') for x in a3]
    a5=a4.index(max(a4))
    a6=a2[a5]
    a_date = a3[a5]
    a_link = ranking_cat_dict[a6]
    ### filter raw rankings for top 10
    a_rankings = rawrankings[(rawrankings['Classification']=='Fingers')
                             & (rawrankings['Discipline']=='Overall')
                             & (rawrankings['Date']==a_date)
                             & (rawrankings['Rank']<=10)]
    a_rankings = add_player_event_link(a_rankings, 1, 0, player_dict, events_dict_div_format)
    top10 = a_rankings[['Rank','Player','Rating']]
    top10['Rating'] = round(top10['Rating'],0)
    dict_href_columns = {'Player': 'Player Link'}
    top10_href = make_href_table(top10, a_rankings, dict_href_columns, 0)
    
    list_of_tables_values += [top10]
    list_of_tables_href += [top10_href]
    list_of_tables_titles += ['CrokinoleCentre Rankings']
    list_of_tables_subtitles += ['As of '+a_date]
    list_of_tables_titles_href += ['rankings.html']
    list_of_tables_subtitles_href += [a_link]
    
    
    ## 2) - Latest tournament results
    tournament_results = rawresults[(rawresults['Classification']!='League Standings')
                                    & (rawresults['Classification']!='League Standings-Incomplete')]
    q = tournament_results.groupby(['Tournament', 'Structured Date','Year','Date']).size().reset_index().rename(columns={0:'count'}).sort_values('Structured Date', ascending=False)
    latest_results_full = q.reset_index()[0:10]
    latest_results_full['Link'] = ''
    for i in range(0,10):
        eventid = latest_results_full.loc[i,'Tournament']
        link = events_dict[eventid]
        latest_results_full.loc[i,'Link'] = link
    latest_results = latest_results_full[['Date','Tournament']]
    dict_href_columns = {'Tournament': 'Link'}
    latest_results_href = make_href_table(latest_results, latest_results_full, dict_href_columns, 0)
    
    list_of_tables_values += [latest_results]
    list_of_tables_href += [latest_results_href]
    list_of_tables_titles += ['Tournament Results']
    list_of_tables_subtitles += ['Last 10 Events']
    list_of_tables_titles_href += ['events.html']
    list_of_tables_subtitles_href += ['']
    
    
    ## 3) - View all records - most NCA singles wins
    rawresults = rawresults_for_records(rawresults, rawleagues)
    winner_results = rawresults[((rawresults['Classification']=='Final Rank')
                                 | (rawresults['Classification']=='Final Rank-Incomplete'))
                                & (rawresults['Rank']==1)
                                & (rawresults['League Name']=='NCA Tour')
                                & (rawresults['Category']=='Singles')
                                & (rawresults['Division']=='Competitive-Fingers')]
    q = winner_results.groupby(['Player']).size().reset_index().rename(columns={0:'# Wins'}).sort_values('# Wins', ascending=False)
    nca_wins_full = q.reset_index()[0:10]
    nca_wins_full = add_rank_field_sort_cut(nca_wins_full,['# Wins'],[False],10)
    nca_wins_full['Link'] = ''
    nca_wins = nca_wins_full[['#','Player','# Wins']]
    for i in range(0,10):
        plyr = nca_wins_full.loc[i,'Player']
        link = player_dict[plyr]
        nca_wins_full.loc[i,'Link'] = link
    dict_href_columns = {'Player': 'Link'}
    nca_wins_href = make_href_table(nca_wins, nca_wins_full, dict_href_columns,0)
    
    list_of_tables_values += [nca_wins]
    list_of_tables_href += [nca_wins_href]
    list_of_tables_titles += ['View All Records']
    list_of_tables_subtitles += ['Most NCA Singles Event Wins']
    list_of_tables_titles_href += ['records.html']
    list_of_tables_subtitles_href += ['records/nca-tour-competitive-fingers-singles.html#Best%20Event%20Finishes']
    
    
    ## 4) - View all records - Most 20s in a singles round
    min4_singles = rawresults[(rawresults['Category']=='Singles')
                              & (rawresults['Games']>=4)]
    most_20s_full = add_rank_field_sort_cut(min4_singles,['10-Game-Adj 20s'],[False],10)
    most_20s_full = most_20s_full.reset_index().rename(columns={'10-Game-Adj 20s':'Adj 20s'})
    most_20s_full['Link'] = ''
    most_20s = most_20s_full[['#','Player','Adj 20s']]
    for i in range(0,10):
        plyr = most_20s_full.loc[i,'Player']
        link = player_dict[plyr]
        most_20s_full.loc[i,'Link'] = link
    dict_href_columns = {'Player': 'Link'}
    most_20s_href = make_href_table(most_20s, most_20s_full, dict_href_columns,0)
    
    list_of_tables_values += [most_20s]
    list_of_tables_href += [most_20s_href]
    list_of_tables_titles += ['View All Records']
    list_of_tables_subtitles += ['Most 20s in a Singles Round - Min 4 Games']
    list_of_tables_titles_href += ['records.html']
    list_of_tables_subtitles_href += ['records/all-time-competitive-fingers-singles.html#Most%2020s%20Scored%20in%20Round']
    
    
    # remaining html lists, this isn't used at all as there's no page nav here
    list_of_tables_titles_id = list_of_tables_titles
    
    html_dict_index = {
        'meta-title': "Crokinole Reference",
        'header-sub': 0,
        'page-heading': 'Welcome to Crokinole Reference',
        'sub-header': ['A home for competitive crokinole records and statistics'],
        'description': ['This website was designed to include results from competitive crokinole events all over the world.'
                        ,'Peruse the above navigation or use the tables below as starting point.'
                        ,''
                        ,'To provide corrections or comments email crokinolecentre@gmail.com.'
                        ,'To contribute to the database of results, please see instructions <b><a href="contribute.html">on this page.</a></b>'],
        'page-nav-dict': {},
        'page-nav-table-layout': '',
        'page-nav-header-display': '',
        'detail-values': list_of_tables_values,
        'detail-href': list_of_tables_href,
        'detail-titles': list_of_tables_titles,
        'detail-subtitles': list_of_tables_subtitles,
        'detail-titles-href': list_of_tables_titles_href,
        'detail-titles-id': list_of_tables_titles_id,
        'detail-subtitles-href': list_of_tables_subtitles_href,
        'detail-column-number': 4,
        'to_top_remove': 1 #only add when needed, 1 to not list "to top" link on page
        }
    
    return html_dict_index

# generate html guide dictionary
def gen_guide_dict(rawresults, rawrankings, rawleagues, league_dict, league_year_cat_dict, events_dict, player_dict, events_dict_div_format, ranking_cat_dict):
    # initialize html lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_subtitles = []
    list_of_tables_titles_href = []
    list_of_tables_subtitles_href = []
    
    # make the tables
    ## Table 1 - View Player Index
    ### 5 players (random), name and # events
    player5_full = pandas.DataFrame(columns=['Player','# Events','Link'])
    plyr_list = list(player_dict.keys())
    for i in range(0,5):
        random_index = random.randrange(len(plyr_list))
        plyr = plyr_list[random_index]
        link = ''
        if plyr in player_dict:
            link = player_dict[plyr]
        plyr_results = rawresults[((rawresults['Classification']=='Final Rank')
                                   | (rawresults['Classification']=='Final Rank-Incomplete'))
                                  & (rawresults['Stage']!='Final League Standings')
                                  & ((rawresults['Player 1']==plyr)
                                     | (rawresults['Player 2']==plyr))]
        num_events = len(plyr_results)
        this_row = pandas.DataFrame({'Player': [plyr], '# Events': [num_events],
                                     'Link': [link]})
        player5_full = player5_full.append(this_row, ignore_index=True)
    
    player5 = player5_full[['Player','# Events']]
    dict_href_columns = {'Player': 'Link'}
    player5_href = make_href_table(player5, player5_full, dict_href_columns, 0)
    x = len(plyr_list)
    
    list_of_tables_values += [player5]
    list_of_tables_href += [player5_href]
    list_of_tables_titles += ['Player Index']
    list_of_tables_subtitles += [str(x)+' player records']
    list_of_tables_titles_href += ['players.html']
    list_of_tables_subtitles_href += ['']
    
    ## Table 2 - View Event Index
    ### 5 events (random), name and # events
    event5_full = pandas.DataFrame(columns=['Event','Link'])
    event_list = list(events_dict.keys())
    for i in range(0,5):
        random_index = random.randrange(len(event_list))
        event = event_list[random_index]
        link = ''
        if event in events_dict:
            link = events_dict[event]
        #event_editions = editions_table[editions_table['Tournament']==event]
        #num_events = len(event_editions)
        this_row = pandas.DataFrame({'Event': [event],
                                     'Link': [link]})
        event5_full = event5_full.append(this_row, ignore_index=True)
    
    event5 = event5_full[['Event']]
    dict_href_columns = {'Event': 'Link'}
    event5_href = make_href_table(event5, event5_full, dict_href_columns, 0)
    x = len(event_list)
    
    list_of_tables_values += [event5]
    list_of_tables_href += [event5_href]
    list_of_tables_titles += ['Event Index']
    list_of_tables_subtitles += [str(x)+' event records']
    list_of_tables_titles_href += ['events.html']
    list_of_tables_subtitles_href += ['']
    
    ## Table 3 - Historic Rankings
    ### 5 random rankings dates, and #1 rank then
    rank_list = list(ranking_cat_dict.keys())
    rank_list = [x for x in rank_list if 'Fingers Overall' in x]
    rank5_full = pandas.DataFrame(columns=['Date', '#1 Rank', 'Link','plyr link'])
    for i in range(0,5):
        random_index = random.randrange(len(rank_list))
        rank_id = rank_list[random_index]
        date = rank_id[0:12]
        link = ''
        if rank_id in ranking_cat_dict:
            link = ranking_cat_dict[rank_id]
        date_rank = rawrankings[(rawrankings['Date']==date)
                                & (rawrankings['Classification']=='Fingers')
                                & (rawrankings['Discipline']=='Overall')
                                & (rawrankings['Rank']==1)]
        date_rank = date_rank.reset_index()
        plyr = date_rank.loc[0,'Player']
        plyrlink = ''
        if plyr in player_dict:
            plyrlink = player_dict[plyr]
        this_row = pandas.DataFrame({'Date': [date], '#1 Rank': [plyr],
                                     'Link': [link], 'plyr link': [plyrlink]})
        rank5_full = rank5_full.append(this_row, ignore_index=True)
        
    rank5 = rank5_full[['Date','#1 Rank']]
    dict_href_columns = {'Date': 'Link','#1 Rank':'plyr link'}
    rank5_href = make_href_table(rank5, rank5_full, dict_href_columns, 0)
    
    list_of_tables_values += [rank5]
    list_of_tables_href += [rank5_href]
    list_of_tables_titles += ['Historic Rankings']
    list_of_tables_subtitles += ['Overall Fingers']
    list_of_tables_titles_href += ['rankings.html']
    list_of_tables_subtitles_href += ['']
    
    ## Table 4 - View All Records
    ### most NCA singles wins
    rawresults = rawresults_for_records(rawresults, rawleagues)
    winner_results = rawresults[((rawresults['Classification']=='Final Rank')
                                 | (rawresults['Classification']=='Final Rank-Incomplete'))
                                & (rawresults['Stage']!='Final League Standings')
                                & (rawresults['Rank']==1)
                                & (rawresults['League Name']=='NCA Tour')
                                & (rawresults['Category']=='Singles')
                                & (rawresults['Division']=='Competitive-Fingers')]
    q = winner_results.groupby(['Player']).size().reset_index().rename(columns={0:'# Wins'}).sort_values('# Wins', ascending=False)
    nca_wins_full = q.reset_index()[0:5]
    nca_wins_full = add_rank_field_sort_cut(nca_wins_full,['# Wins'],[False],5)
    nca_wins_full['Link'] = ''
    nca_wins = nca_wins_full[['#','Player','# Wins']]
    for i in range(0,5):
        plyr = nca_wins_full.loc[i,'Player']
        link = player_dict[plyr]
        nca_wins_full.loc[i,'Link'] = link
    dict_href_columns = {'Player': 'Link'}
    nca_wins_href = make_href_table(nca_wins, nca_wins_full, dict_href_columns,0)
    
    list_of_tables_values += [nca_wins]
    list_of_tables_href += [nca_wins_href]
    list_of_tables_titles += ['View All Records']
    list_of_tables_subtitles += ['Most NCA Singles Event Wins']
    list_of_tables_titles_href += ['records.html']
    list_of_tables_subtitles_href += ['records/nca-tour-competitive-fingers-singles.html#Best%20Event%20Finishes']
    
    ## Table 5 - Leagues
    ### 5 random rankings dates, and #1 rank then
    league5_full = pandas.DataFrame(columns=['League','# Seasons','Link'])
    league_editions = make_editions_table_league(rawresults, league_dict, league_year_cat_dict)
    q = league_editions.groupby(['League Name', 'Season']).size().reset_index().rename(columns={0:'count'})
    disp_num = min(5, len(set(league_editions['League Name'])))
    league_list = list(set(league_editions['League Name']))
    
    random_index_list = random.sample(range(0,len(league_list)),disp_num) #unique random list
    for i in range(0,disp_num):
        random_index = random_index_list[i]
        league = league_list[random_index]
        x_league = league_editions[league_editions['League Name']==league]
        num_seasons = len(set(x_league['Season']))
        link = ''
        if league in league_dict:
            link = league_dict[league]
        this_row = pandas.DataFrame({'League': [league], '# Seasons': [num_seasons],
                                     'Link': [link]})
        league5_full = league5_full.append(this_row, ignore_index=True)
        
    league5 = league5_full[['League','# Seasons']]
    dict_href_columns = {'League': 'Link'}
    league5_href = make_href_table(league5, league5_full, dict_href_columns, 0)
    
    list_of_tables_values += [league5]
    list_of_tables_href += [league5_href]
    list_of_tables_titles += ['View All Leagues']
    list_of_tables_subtitles += ['']
    list_of_tables_titles_href += ['leagues.html']
    list_of_tables_subtitles_href += ['']
    
    # remaining html lists, this isn't used at all as there's no page nav here
    list_of_tables_titles_id = list_of_tables_titles
    
    html_dict_index = {
        'meta-title': "Crokinole Reference - Guide",
        'header-sub': 0,
        'page-heading': 'Crokinole Reference Guide',
        'sub-header': [''],
        'description': ['Use the data below to scan the list of available resources.'
                        ,'To contribute to the database of results, please see instructions <b><a href="contribute.html">on this page.</a></b>'],
        'page-nav-dict': {},
        'page-nav-table-layout': '',
        'page-nav-header-display': '',
        'detail-values': list_of_tables_values,
        'detail-href': list_of_tables_href,
        'detail-titles': list_of_tables_titles,
        'detail-subtitles': list_of_tables_subtitles,
        'detail-titles-href': list_of_tables_titles_href,
        'detail-titles-id': list_of_tables_titles_id,
        'detail-subtitles-href': list_of_tables_subtitles_href,
        'detail-column-number': 4,
        'to_top_remove': 1 #only add when needed, 1 to not list "to top" link on page
        }
    
    return html_dict_index


# Helper Functions
# add player/event link to given table
def add_player_event_link(in_table, player_flag, event_flag, player_dict, events_dict_div_format):
    table=in_table.copy()
    # player/event flag is 0 or 1 to indicate whether to add link field to table
    if player_flag == 1:
        table['Player Link'] = ''
        for i in table.index:
            plyr = table.loc[i,'Player']
            if plyr in player_dict:
                link = player_dict[plyr]
                table.loc[i,'Player Link'] = link
    if event_flag == 1:
        table['Event Link'] = ''
        for i in table.index:
            tournament = table.loc[i,'Tournament']
            date = table.loc[i,'Date']
            division = table.loc[i,'Division']
            t_format = table.loc[i,'Category']
            event_id = tournament+' '+date+' '+division+' '+t_format
            if event_id in events_dict_div_format:
                link = events_dict_div_format[event_id]
                table.loc[i,'Event Link'] = link
    
    return table

def make_href_table(final_values_table, draft_values_table, dict_href_columns, sub_link):
    # final values table has final structure that needs to be matched
    # draft values table contains the href links that are desired
    # dict maps the columns in final values to the columns of the links in draft
    # sub_link indicates preceding '../' if needed
    
    # set structure
    href_table = pandas.DataFrame('', index=final_values_table.index
                                  , columns=final_values_table.columns)
    for col in dict_href_columns.keys():
        href_col = dict_href_columns[col]
        links = draft_values_table[href_col]
        blank_indicator = (links!='') #false if value in link column is blank (and no table exists to link to)
        blank_binary = blank_indicator.astype(int)
        precede_link = '../' * sub_link  #if not link, then nothing populate so <a> tag not applied by htmlwrite
        z = (precede_link + links) * blank_binary
        href_table[col] = z
            
    return href_table

# add tour id to rawresults, and a binary if it was a century
def rawresults_for_records(rawresults, rawleagues):
    modresults = rawresults[rawresults['Classification']!='Team-dummy'] #patchwork solution as team-dummy rows have strings that error out in the 20s > below
    modresults['League Name'] = ''
    modresults['Century'] = 0
    for i in modresults.index:
        x = modresults.loc[i,'League']
        y = rawleagues.index[rawleagues['League tag']==x].tolist()
        if y != []:
            league = rawleagues.loc[y[0],'League Name']
            modresults.loc[i,'League Name'] = league
        if ((modresults.loc[i,'20s'] >= 100) & (modresults.loc[i,'10-Game-Adj 20s'] >= 100)):
            modresults.loc[i,'Century'] = 1
        
    return modresults

def add_rank_field_sort_cut(table,sort_fields,sort_order,display_num):
    ## rank field is added as '#'
    ## sort fields is list of column names to be sorted on
    ## sort_order is list of true (ascending), false (descending) for order
    ## display num is to cut the table to only show top X placements
    table = table.sort_values(by=sort_fields, ascending=sort_order)
    main_sort_field = sort_fields[0]
    main_ascending = sort_order[0]
    table['#1'] = table[main_sort_field].rank(method='min', na_option='bottom', ascending=main_ascending)
    table['#2'] = table[main_sort_field].rank(method='max', na_option='bottom', ascending=main_ascending)
    cut_table = table[table['#1']<=display_num]
    cut_table['#'] = 0
    for i in cut_table.index:
        min_rank = cut_table.loc[i,'#1']
        max_rank = cut_table.loc[i,'#2']
        if min_rank == max_rank:
            rank_value = min_rank
        else:
            rank_value = 'T'+str(int(min_rank))+'-'+str(int(max_rank))
        cut_table.loc[i,'#'] = rank_value
    
    return cut_table

def make_editions_table_league(rawresults, league_dict, league_year_cat_dict):
    ## reference table for number of editions and last edition
    editions_table = pandas.DataFrame(columns = ('Dict Key', "League Name", "Season", "Category", "Link", "Structured Date"))
    league_list = league_dict.keys()
    for cur_league in league_list:
        results_league_only = rawresults[(rawresults['Tournament']==cur_league)]
        q = results_league_only.groupby(['Division', 'League', 'Structured Date']).size().reset_index().rename(columns={0:'count'}).sort_values('count', ascending=False)
        ## change name of division to category, and league to Dict Key
        q = q.rename(columns={'Division': 'Category', 'League':'Dict Key'})
        ## add year, link, and league name to q
        q['Season'] = ''
        q['League Name'] = ''
        q['Link'] = ''
        for i in q.index:
            key = q.loc[i,'Dict Key']
            q.loc[i,'Season'] = league_year_cat_dict[key]['Season']
            q.loc[i,'League Name'] = league_year_cat_dict[key]['League Name']
            q.loc[i,'Link'] = league_year_cat_dict[key]['link']
        # append q to editions_table
        editions_table = editions_table.append(q, ignore_index=True)

    return editions_table
