# Crokinole Reference - Script to Generate webpages

## Generate event pages and dictionaries
    # 1) create event dictionaries
    # Main) code to run scripts below
    # 2) create event index page
    # 3) create individual event index pages
    # 4) create individual category pages
    
# other crokinole reference scripts
import outputlog
import htmlwrite
# python modules
import pandas
import unidecode
import math
import numpy


# 1) create event dictionaries
## key: event, value: link
def gen_event_dict(rawresults):
    events_dict = {}
    results = rawresults[(rawresults['Classification']!='League Standings')
                         & (rawresults['Classification']!='League Standings-Incomplete')
                         & (rawresults['Classification']!='Team-dummy')]
    q = results.groupby(['Tournament']).size().reset_index()
    for event in q['Tournament']:
        link = unidecode.unidecode(event) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = 'events/' + link + ".html" #add events/ and append html
        events_dict[event] = link
    
    return events_dict

def gen_event_dict_div_format(rawresults):
    events_dict = {}
    results = rawresults[(rawresults['Classification']!='League Standings')
                         & (rawresults['Classification']!='League Standings-Incomplete')
                         & (rawresults['Classification']!='Team-dummy')]
    q = results.groupby(['Tournament','Date','Division','Category']).size().reset_index()
    for event, date, division, category in zip(q['Tournament'],q['Date'],q['Division'],q['Category']):
        eventid = event + ' ' + date + ' ' + division + ' ' + category
        link = unidecode.unidecode(eventid) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = link.replace(",", "") #remove commas
        link = 'events/' + link + ".html" #add events/ and append html
        events_dict[eventid] = link
    
    return events_dict

def gen_event_mapping_dict(rawmapping):
    tournaments = rawmapping[rawmapping['Column']=='Tournament']
    mapping_dict = {}
    for tag, expanded in zip(tournaments['Results Tag'],tournaments['Expanded Term']):
        mapping_dict[tag] = expanded
    
    return mapping_dict

# Main)
def generate(rawresults, rawmatches, player_dict, events_dict, events_dict_div_format, events_mapping_dict, webpage_output_location, layout_dict):
    # prep tables
    #editions_table = make_editions_table(events_dict_year)
    editions_table = make_editions_table(events_dict_div_format)

    # event index
    html_dict_event_index = gen_event_index(events_dict, editions_table)
    htmlwrite.generate('events.html', webpage_output_location, html_dict_event_index, layout_dict)
    outputlog.generate("event index page created")
    # individual event index 
    ### this organized the event indexes by year
    #for this_event in events_dict.keys():
     #   html_dict_indiv_event = gen_indiv_event(rawresults, player_dict, this_event, events_dict_div_format, editions_table)
      #  htmlwrite.generate(events_dict[this_event], webpage_output_location, html_dict_indiv_event, layout_dict)
    # attempt 2 - organizes event indexes by category
    for this_event in events_dict.keys():
        html_dict_indiv_event = gen_indiv_event(rawresults, player_dict, this_event, events_dict_div_format, editions_table, events_mapping_dict)
        htmlwrite.generate(events_dict[this_event], webpage_output_location, html_dict_indiv_event, layout_dict)
    outputlog.generate("event sub-index pages created")
    
    # individual category pages
    for this_cat in events_dict_div_format.keys():
        html_dict_indiv_cat = gen_indiv_cat(rawresults, rawmatches, player_dict, this_cat)
        htmlwrite.generate(events_dict_div_format[this_cat], webpage_output_location, html_dict_indiv_cat, layout_dict)      
    outputlog.generate("all event pages created")

# 2) create event index page
def gen_event_index(events_dict, editions_table):
    event_index_table = pandas.DataFrame(columns = ('Tournament', "# Editions", "First Edition", "Last Edition", "Link"))
    event_index_table['Tournament'] = events_dict.keys()

    ### add num editions, last event, event link, and last edition link
    for i in event_index_table.index:
        cur_event = event_index_table.loc[i, 'Tournament']
        editions_table_cur_event = editions_table[editions_table['Tournament']==cur_event]
        last_event_year = max(editions_table_cur_event['Year'])
        first_year = min(editions_table_cur_event['Year'])
        event_index_table.loc[i, '# Editions'] = len(set(editions_table_cur_event['Date']))
        event_index_table.loc[i, 'Last Edition'] = last_event_year
        event_index_table.loc[i, 'First Edition'] = first_year
        event_index_table.loc[i, 'Link'] = events_dict[cur_event]

    ### sort the table - by number of editions
    event_index_table = event_index_table.sort_values(by=["# Editions"], ascending = False)
    # make final table
    event_index_final = event_index_table[['Tournament', '# Editions', 'First Edition', 'Last Edition']]
    # make href table
    dict_href_columns = {'Tournament': 'Link'}
    event_href = make_href_table(event_index_final, event_index_table, dict_href_columns, 0)
    # make lists
    list_of_tables_values = [event_index_final]
    list_of_tables_href = [event_href]
    list_of_tables_titles = ['Event Index']
    list_of_tables_subtitles = ['']
    list_of_tables_titles_href = ['']
    list_of_tables_titles_id = ['']
    list_of_tables_subtitles_href = ['']
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - Event Index",
        'header-sub': 0,
        'page-heading': "Event Index",
        'sub-header': ['Included below are the available records of ' 
                       + str(len(event_index_table)) + ' different events.'],
        'description': ['Individual annual editions of events can be viewed by following the links below.'],
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
        'detail-column-number': 1
        }
    
    return html_dict_event_index
 
# 3) create individual event index pages
def gen_indiv_event(rawresults, player_dict, this_event, events_dict_div_format, editions_table, events_mapping_dict):
    ## for each annual edition: one table that lists categories, # entries, winner, runner-up, data availability
    
    ## filter editions table for this_event
    editions_table_cur_event = editions_table[editions_table['Tournament']==this_event]
    ### sort the table - from most recent to least
    editions_table_cur_event['Struc Date']=pandas.to_datetime(editions_table_cur_event['Date'], format='%b %d, %Y')
    editions_table_cur_event = editions_table_cur_event.sort_values(by=["Struc Date"], ascending = False)
    
    ## initializing html lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_titles_id = []
    
    ## get div/category combos
    q = editions_table_cur_event.groupby(['Division','Category']).size().reset_index()
    
    ## build html lists one division/category at a time
    for division, category in zip(q['Division'],q['Category']):
        cat_table = pandas.DataFrame(columns = ("Date", "Winner", "Runner-up","# Entries", 'Data Availability', 'Winner Player Link', 'Runner-up Player Link'))
        ## filter rawresults for this division/category
        cat_results = rawresults[(rawresults['Tournament']==this_event)
                                 & (rawresults['Division']==division)
                                 & (rawresults['Category']==category)]
        ## use groupby to get unique division, format combinations
        date_list = list(set(cat_results['Structured Date']))
        date_list.sort(reverse=True)
        ## loop through categories
        for str_date in date_list:
            date = str_date.strftime('%b %d, %Y')
            this_results = cat_results[(cat_results['Date']==date)]
            this_results_rank = cat_results[(cat_results['Date']==date)
                                            & ((cat_results['Classification']=='Final Rank')
                                               | (cat_results['Classification']=='Final Rank-Incomplete'))]
            winner_row = this_results_rank[this_results_rank['Rank']==1].reset_index()
            num_entries = winner_row.loc[0,'# Entries']
            winner = winner_row.loc[0,'Player']
            if len(this_results_rank)>1:
                runner_up_row = this_results_rank[this_results_rank['Rank']==2].reset_index()
                runner_up = runner_up_row.loc[0,'Player']
            else:
                runner_up = ''
            data_availability = category_data(this_results)
            category_id = this_event + ' '+date+' '+division+' '+category
            category_link = events_dict_div_format[category_id]
            winner_link = ''
            runner_up_link = ''
            if winner in player_dict:
                winner_link = player_dict[winner]
            if runner_up in player_dict:
                runner_up_link = player_dict[runner_up]
            ## make into a row for the table
            this_category_row = pandas.DataFrame({'Date': [date], 'Winner': [winner],
                                                  'Runner-up': [runner_up],'# Entries': [num_entries], 'Data Availability': [data_availability],
                                                  'Category Link': [category_link], 'Winner Player Link': [winner_link],
                                                  'Runner-up Player Link': [runner_up_link]})
 
            ## update year_table
            cat_table = cat_table.append(this_category_row, ignore_index=True)
        
        cat_table_final = cat_table[["Date", "Winner", "Runner-up","# Entries", 'Data Availability']]
        dict_href_columns = {'Winner': 'Winner Player Link'
                             , 'Runner-up': 'Runner-up Player Link'
                             , 'Data Availability': 'Category Link'}
        cat_table_href = make_href_table(cat_table_final, cat_table, dict_href_columns, 1)
   
        # update lists
        list_of_tables_values += [cat_table_final]
        list_of_tables_href += [cat_table_href]
        list_of_tables_titles += [division+' '+category]
        list_of_tables_titles_id += [division+' '+category]
        
        
    # remaining html lists
    n = len(list_of_tables_values)
    list_of_tables_subtitles = ['']*n
    list_of_tables_titles_href = ['']*n
    list_of_tables_subtitles_href = ['']*n
    
    ## page-nav items
    page_nav_dict = dict(zip(list_of_tables_titles_id, list_of_tables_titles_id))
    page_nav_table_layout = make_table_m_n('square', list_of_tables_titles_id)
    #page_nav_table_layout = pandas.DataFrame(list_of_tables_titles_id)
    page_nav_header_display = [0] * len(page_nav_table_layout.columns) ## needs to be 0s of length num columns of page_nav
    #page_nav_header_display = [0]
    
    #sub-header
    sub_header = ['Included below are the available records of ' 
                       + str(len(list_of_tables_values)) + ' different categories.']
    if this_event in events_mapping_dict:
        x = events_mapping_dict[this_event]
        sub_header = [x] + sub_header
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - " + this_event,
        'header-sub': 1,
        'page-heading': this_event + " Results",
        'sub-header': sub_header,
        'description': ['Results from particular years can be viewed by following the links below.'],
        'page-nav-dict': page_nav_dict,
        'page-nav-table-layout': page_nav_table_layout,
        'page-nav-header-display': page_nav_header_display,
        'detail-values': list_of_tables_values,
        'detail-href': list_of_tables_href,
        'detail-titles': list_of_tables_titles,
        'detail-subtitles': list_of_tables_subtitles,
        'detail-titles-href': list_of_tables_titles_href,
        'detail-titles-id': list_of_tables_titles_id,
        'detail-subtitles-href': list_of_tables_subtitles_href,
        'detail-column-number': 1
        }
    
    return html_dict_event_index
 

# 4) create individual category pages
def gen_indiv_cat(rawresults, rawmatches, player_dict, this_cat):
    # 0) setup inputs
    ## get category details
    cat_list = this_cat.split(' ')
    sing_doub = cat_list[-1] # the last list element
    division = cat_list[-2] # second last
    date = cat_list[-5]+' '+cat_list[-4]+' '+cat_list[-3] # 3 words
    tournament_list = cat_list[0:-5] # rest of string
    tournament = ''
    for i in range(len(tournament_list)):
        tournament += tournament_list[i] + ' '
    tournament = tournament.strip() # remove trailing spaces
    
    ## filter rawresults and raw matches
    results = rawresults[(rawresults['Tournament'] == tournament)
                         & (rawresults['Division'] == division)
                         & (rawresults['Date'] == date)
                         & (rawresults['Category'] == sing_doub)]
    matches = rawmatches[(rawmatches['Tournament'] == tournament)
                         & (rawmatches['Division'] == division)
                         & (rawmatches['Date'] == date)
                         & (rawmatches['Category'] == sing_doub)]
    
    ## add player link to table
    results = add_player_link(results, player_dict)
    
    # initialize page_nav_dict
    page_nav_dict = {}

    # A) create values and href tables
    ## final ranking
    final_ranking_full = results[(results['Classification']=='Final Rank')
                            | (results['Classification']=='Final Rank-Incomplete')]
    final_ranking_full = final_ranking_full.sort_values(by=["Rank"], ascending = True)
    final_ranking = final_ranking_full[['Rank', 'Player', 'Pts']].fillna('')
    dict_href_columns = {'Player': 'Player Link'}
    final_ranking_href = make_href_table(final_ranking, final_ranking_full, dict_href_columns, 1)
    page_nav_dict['Overall: Final Ranking']='Final Ranking'
    ## scores/rankings for each stage and pool
    scores_ranks = results[(results['Classification']!='Final Rank')
                            & (results['Classification']!='Final Rank-Incomplete')]
    q = scores_ranks.groupby(['Stage', 'Pool']).size().reset_index()
    q = order_stages(q)
    scores_values_list = []
    scores_values_href = []
    scores_titles_list = []
    scores_subtitles_list = []
    if len(q) != 0:
        for i in q.index:
            this_pool_full = scores_ranks[(scores_ranks['Stage']==q.loc[i,'Stage'])
                                     & (scores_ranks['Pool']==q.loc[i,'Pool'])]
            this_pool_full = this_pool_full.sort_values(by=["Rank"], ascending = True)
            this_pool = this_pool_full[['Rank', 'Player', 'Games', 'Pts', '20s', '20s Rank']].fillna('')
            dict_href_columns = {'Player': 'Player Link'}
            this_pool_href = make_href_table(this_pool, this_pool_full, dict_href_columns, 1)
            scores_values_list += [this_pool]
            scores_values_href += [this_pool_href]
            stage_pool_id = q.loc[i,'Stage'] + ' - ' + q.loc[i,'Pool']
            stage_pool_id_long = 'Round Scores: ' + stage_pool_id
            scores_titles_list += [stage_pool_id_long]
            scores_subtitles_list += ['']
            page_nav_dict[stage_pool_id_long]=stage_pool_id
    ## H2H matrix for each stage and pool
    matches_values_list = []
    matches_values_href = []
    matches_titles_list = []
    matches_subtitles_list = []
    q = matches.groupby(['Stage', 'Pool']).size().reset_index()
    q = order_stages(q)
    if len(q) != 0:
        for i in q.index:
            this_matches_pool_orig = matches[(matches['Stage']==q.loc[i,'Stage'])
                                             & (matches['Pool']==q.loc[i,'Pool'])]
            # only produce H2H summaries if more than 2 players
            if len(set(this_matches_pool_orig['Player'])) > 2:
                this_matches_pool_pts = make_H2H_table(this_matches_pool_orig, 'Pts')
                this_matches_pool_pts_href_1 = add_player_link(this_matches_pool_pts, player_dict)
                #href_columns = ['Player Link']+['']*(len(this_matches_pool_pts.columns)-1)
                dict_href_columns = {'Player': 'Player Link'}
                this_matches_pool_pts_href = make_href_table(this_matches_pool_pts, this_matches_pool_pts_href_1, dict_href_columns,1)
                matches_values_list += [this_matches_pool_pts]
                matches_values_href += [this_matches_pool_pts_href]
                match_pool_id = q.loc[i,'Stage'] + ' - ' + q.loc[i,'Pool']
                match_pool_id_long = 'H2H Pts: ' + match_pool_id
                matches_titles_list += [match_pool_id_long]
                matches_subtitles_list += ['']
                page_nav_dict[match_pool_id_long]=match_pool_id
    
    ## Team member lists
    teams_values_list = []
    teams_values_href = []
    teams_titles_list = []
    teams_subtitles_list = []
    if sing_doub == 'Teams': #look for team listing
        res = rawresults.fillna('')
        team_members = res[(res['Tournament'] == tournament)
                           & (res['Date'] == date)
                           & (res['Category'] != sing_doub)
                           & (res['Team']!='')]
        if len(team_members)!=0: #then make the table
            team_table = make_team_listing(team_members)
            team_table_href = make_team_listing_href(team_table, player_dict, 1)
            teams_values_list += [team_table]
            teams_values_href += [team_table_href]
            stage_pool_id = 'Team Members'
            stage_pool_id_long = 'Teams: ' + stage_pool_id
            teams_titles_list += [stage_pool_id_long]
            teams_subtitles_list += ['']
            page_nav_dict[stage_pool_id_long]=stage_pool_id
    
    # B) create lists for the html dict (order is order of html appearance)
    list_of_tables_values = [final_ranking]+scores_values_list+matches_values_list+teams_values_list
    list_of_tables_href = [final_ranking_href]+scores_values_href+matches_values_href+teams_values_href
    list_of_tables_titles = ['Overall: Final Ranking']+scores_titles_list+matches_titles_list+teams_titles_list
    list_of_tables_subtitles = ['Points shown are league points awarded, if applicable.']+scores_subtitles_list+matches_subtitles_list+teams_subtitles_list
    n = len(list_of_tables_values)
    list_of_tables_titles_href = ['']*n
    list_of_tables_titles_id = list_of_tables_titles
    list_of_tables_subtitles_href = ['']*n
    
    # C) create the page-nav and subtitle/description info
    ## sub-header
    display_date = results.loc[min(results.index),'Date']
    league_note = ''
    if isinstance(results.loc[min(results.index),'League'],str):
        league = results.loc[min(results.index),'League']
        league_note = 'This was included in the ' + league + '.'
    
    ## standard description notice
    description_note = 'All available results for this category are listed below. For numerous events there is limited data for the number of players, the scores throughout the tournament, or the matches that took place. If in possession, please consider contributing outstanding information to Crokinole Reference.'

    ## page-nav items
    max_row_dim_page_nav = max(1, len(scores_values_list), len(matches_values_list), len(teams_values_list))
    scores_titles_list_extend = scores_titles_list
    if len(scores_titles_list_extend) < max_row_dim_page_nav:
        scores_titles_list_extend = scores_titles_list_extend+['']*(max_row_dim_page_nav - len(scores_titles_list_extend))
    matches_titles_list_extend = matches_titles_list
    if len(matches_titles_list_extend) < max_row_dim_page_nav:
        matches_titles_list_extend = matches_titles_list_extend+['']*(max_row_dim_page_nav - len(matches_titles_list_extend))
    teams_titles_list_extend = teams_titles_list
    if len(teams_titles_list_extend) < max_row_dim_page_nav:
        teams_titles_list_extend = teams_titles_list_extend+['']*(max_row_dim_page_nav - len(teams_titles_list_extend))
    page_nav_table_layout = {'Overall':['Overall: Final Ranking']+['']*(max_row_dim_page_nav-1)
                             , 'Round Scores': scores_titles_list_extend
                             , 'H2H Matches': matches_titles_list_extend
                             , 'Teams': teams_titles_list_extend}
    page_nav_table_layout = pandas.DataFrame(page_nav_table_layout, columns = ['Overall','Round Scores','H2H Matches','Teams'])
    display_round_scores_nav = 0
    if len(scores_values_list) != 0:
        display_round_scores_nav = 1
    display_H2Hmathces_nav = 0
    if len(matches_values_list) != 0:
        display_H2Hmathces_nav = 1
    display_teams_nav = 0
    if len(teams_values_list) != 0:
        display_teams_nav = 1
    page_nav_header_display = [1,display_round_scores_nav,display_H2Hmathces_nav,display_teams_nav]

    # D) html dict
    html_dict_cat_page = {
        'meta-title': "Crokinole Reference - " + this_cat,
        'header-sub': 1,
        'page-heading': this_cat + " Results",
        'sub-header': ['The ' + this_cat + ' was played on ' + display_date + '.', league_note],
        'description': [description_note],
        'page-nav-dict': page_nav_dict,
        'page-nav-table-layout': page_nav_table_layout,
        'page-nav-header-display': page_nav_header_display,
        'detail-values': list_of_tables_values,
        'detail-href': list_of_tables_href,
        'detail-titles': list_of_tables_titles,
        'detail-subtitles': list_of_tables_subtitles,
        'detail-titles-href': list_of_tables_titles_href,
        'detail-titles-id': list_of_tables_titles_id,
        'detail-subtitles-href': list_of_tables_subtitles_href,
        'detail-column-number': 1
        }
    
    return html_dict_cat_page

#### Helper function

def make_editions_table(events_dict_div_format):
    ## reference table for number of editions and last edition
    editions_table = pandas.DataFrame(columns = ("All","Tournament", "Date", "Division", "Category", "Year"))
    editions_table['All'] = events_dict_div_format.keys()
    for i in editions_table.index:
        this_event_all = editions_table.loc[i, 'All']
        list_spaces = [i for i, x in enumerate(this_event_all) if ' ' in x]
        this_category = this_event_all[list_spaces[-1]+1:] #cat will always be one word
        this_div = this_event_all[list_spaces[-2]+1:list_spaces[-1]] #division will be one word
        this_date = this_event_all[list_spaces[-5]+1:list_spaces[-2]] #date will be 3 words
        this_event = this_event_all[:list_spaces[-5]] # leave out the space
        this_year = int(this_date[-4:])
        editions_table.loc[i, 'Tournament'] = this_event
        editions_table.loc[i, 'Date'] = this_date
        editions_table.loc[i, 'Division'] = this_div
        editions_table.loc[i, 'Category'] = this_category
        editions_table.loc[i, 'Year'] = this_year
        
    return editions_table

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

## return a summary characteristic of the available data of a particular category
def category_data(this_results):
    # potential tags: 
    ## incomplete ranking - the final rank is incomplete
    ## final rank only - only the final rank is available
    ## no scores - only ranks are available
    ## some scores - a combination of Scores, Ranks, final ranks
    ## all scores - results are only scores and final rank
    list_of_classifications = set(this_results['Classification'])
    availability_tag = 'View Results' #fail safe in case no cases work
    if {'Final Rank'} == list_of_classifications:
        availability_tag = 'Final Rank Only'
    if list_of_classifications == {'Scores', 'Final Rank'}:
        availability_tag = 'All Scores'
    if list_of_classifications == {'Scores', 'Final Rank', 'Rank'}:
        availability_tag = 'Some Scores'
    if list_of_classifications == {'Final Rank', 'Rank'}:
        availability_tag = 'No Scores'
    if 'Final Rank-Incomplete' in list_of_classifications:
        availability_tag = 'Incomplete Ranking'
    
    return availability_tag

## create table of specified column number (or square) from list of values
def make_table_m_n(column_number, values):
    # column_number can be "square" or number stating desired columns
    # values of the table
    num_values = len(values)
    ## determine number of rows and columns
    if column_number == 'square':
        num_rows = math.ceil(math.sqrt(num_values))
        num_columns = math.ceil(num_values/num_rows)
    else:
        num_rows = math.ceil(num_values/column_number)
        num_columns = column_number
    ## adding '' to end of values list to complete the grid
    table_num_cells = num_rows * num_columns
    num_blanks_to_append = table_num_cells - num_values
    expanded_values = values + num_blanks_to_append * ['']
    
    ## build up table, row by row
    dimensioned_table = pandas.DataFrame()
    for i in range(num_rows):
        index_start = i * num_columns
        index_end = (i+1) * num_columns
        this_row_values = expanded_values[index_start:index_end]
        dimensioned_table = dimensioned_table.append([this_row_values])
        #table_formatted_values += [[this_row_values]] # double brackets for rows
    
    return dimensioned_table

#add player link to table
def add_player_link(results, player_dict):
    results_table = results.copy()
    results_table['Player Link'] = ''
    plyr_col = results_table['Player']
    unique_plyr = set(plyr_col)
    for player_team in unique_plyr:
        if player_team in player_dict:
            index_list = list(results_table[results_table['Player']==player_team].index.values)
            results_table.loc[index_list, 'Player Link'] = player_dict[player_team]
    
    return results_table

# order a table with a list of stages into typical tournament structure of occurrence
def order_stages(q):
    # from miscellaneous script
    stage_list_order = [ #regular events
    'Prelim', 'Power Pool','R16','R8','Quarter','Final 8','Final 6','Final 4','Final 3',
    #little more strange stuff for top 4 playoffs
    'Page Playoff','Semi','Semi G1','Semi G2','Semi G3','Final','Final G1','Final G2','Final G3',
    #Mixed discipline event: Excelling Eight
    '4 Player Singles','Doubles','Singles'
    ]
    stages_to_group = [['Semi G1','Semi G2','Semi G3'],['Final G1','Final G2','Final G3']]
    # initialize table
    ordered_stages = q.copy()
    ordered_stages['stage order']=100
    for index in ordered_stages.index:
        cur_stage = ordered_stages.loc[index,'Stage']
        order_candidate = stage_list_order.index(cur_stage)
        #if any(cur_stage in k for k in stages_to_group): #necessary to see if in sublist
        # check if stage should be grouped
        grouped_stages_candidate = []
        for i in range(len(stages_to_group)):
            sublist = stages_to_group[i]
            if cur_stage in sublist:
                 for j in range(len(sublist)):
                     cur_stage = sublist[j]
                     order_id = stage_list_order.index(cur_stage)
                     grouped_stages_candidate.append(order_id)
        if len(grouped_stages_candidate)!=0:
            order_candidate = min(order_candidate, min(grouped_stages_candidate))

        ordered_stages.loc[index,'stage order'] = order_candidate
    
    ordered_stages = ordered_stages.sort_values(by=["stage order", 'Pool'], ascending = True)
    ordered_stages = ordered_stages.reset_index()
    
    return ordered_stages
    
# take a section of the matches input and create a H2H matrix
def make_H2H_table(this_matches_pool_orig, pts_20s_view):
    this_matches_view = this_matches_pool_orig[this_matches_pool_orig['Pts/20s']==pts_20s_view]
    # get player list and order by pts/20s
    q = this_matches_view.groupby(['Player']).sum().sort_values('Total', ascending=False)
    player_list = list(q.index)
    player_list_initials = make_initials(player_list)
    # make shell table
    H2H_table = pandas.DataFrame(columns=['Player', 'Total '+pts_20s_view]+player_list_initials)
    H2H_table['Player'] = player_list
    H2H_table = H2H_table.fillna('')
    # fill in table row by row
    for i in range(len(player_list)):
        cur_player = player_list[i]
        cur_matches = this_matches_view[this_matches_view['Player']==cur_player]
        # fill in amount for each match
        for j in cur_matches.index:
            cur_total = int(cur_matches.loc[j, 'Total'])
            cur_opponent = cur_matches.loc[j, 'Opponent']
            opponent_position = player_list.index(cur_opponent)
            opponent_initial=player_list_initials[opponent_position]
            cell_total = H2H_table.loc[i,opponent_initial]
            if cell_total == '': # add in case there's multiple matches in a round
                cell_total_new = cur_total
            else:
                cell_total_new = cell_total + cur_total
            H2H_table.loc[i,opponent_initial] = cell_total_new
        # populate total
        H2H_table.loc[i,'Total '+pts_20s_view] = int(q.loc[cur_player,'Total'])
    
    return H2H_table

# convert a player list into a list of initials: to reduce column space
def make_initials(player_list):
    initials_list = []
    for player in player_list:
        team_initial = ''
        for plyr in player.split('/'): #split by slash
            initials = ''.join(name[0].upper() for name in plyr.split()) #split by space
            team_initial += initials + '/'
        team_initial = team_initial[:-1]
        if team_initial in initials_list:
            count_initial = initials_list.count(team_initial)
            team_initial += str(count_initial+1)
        initials_list += [team_initial]
    return initials_list

# make a table of team members, with club names as columns, and rows containing team members
def make_team_listing(res):
    # get list of team names
    team_list = list(set(res['Team']))
    # dictionary of team name as key, followed by team members
    member_list = {}
    max_members = 0
    for team in team_list:
        player_list = list(set(res[res['Team']==team]['Player']))
        max_members = max(len(player_list),max_members)
        member_list[team] = player_list
    
    # go through each key of dict make member lists the same length
    for team in member_list:
        x = len(member_list[team])
        if x < max_members:
            orig_list = member_list[team]
            extend_list = orig_list+['']*(max_members - len(orig_list))
            member_list[team] = extend_list
    
    team_table = pandas.DataFrame(member_list, columns = team_list)
    
    return team_table

# href links for entire team_table
def make_team_listing_href(team_table, player_dict, sub_link):
    precede_link = '../' * sub_link
    out = pandas.DataFrame('', columns = team_table.columns, index = team_table.index)
    for team in team_table.columns:
        for i in team_table.index:
            player = team_table.loc[i,team]
            if player in player_dict:
                out.loc[i,team] = precede_link + player_dict[player]
    
    return out
    