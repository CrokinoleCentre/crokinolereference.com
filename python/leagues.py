# Crokinole Reference - Script to Generate webpages

## Generate league pages and dictionaries
    # 1) create league dictionaries
    # Main) code to run scripts below
    # 2) create league index page
    # 3) create individual league index pages
    # 4) create individual season pages
    
# other crokinole reference scripts
import outputlog
import htmlwrite
# python modules
import pandas
import unidecode
import math
import numpy


# 1) create league dictionaries
## key: league name, value: link
def gen_league_dict(rawleagues):
    league_dict = {}
    q = rawleagues.groupby(['League Name']).size().reset_index()
    for league_tag in q['League Name']:
        link = league_tag #remove leading, trailing spaces
        link = unidecode.unidecode(link) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = 'leagues/' + link + ".html" #add events/ and append html
        league_dict[league_tag] = link
                    
    return league_dict

## key: league+cat+year, value: link, season and league name
def gen_league_dict_cat_year(rawleagues):
    league_dict = {}

    for league_tag, league_name, season_year, division in zip(rawleagues['League tag'],rawleagues['League Name'],rawleagues['Season'],rawleagues['Division']):
        season_year = str(season_year)
        season_tag = league_name +' '+season_year+' '+division
        x = season_tag.split(',')
        if len(x)>1: 
            # a comma exists in the results tag (in the Season column), therefore the tag exists for 2 leagues
            # assign link to just one of them
            league_listing = league_name.split(',')
            season_listing = season_year.split(',')
            category_listing = division.split(',')
            season_tag = league_listing[0]+' '+str(season_listing[0])+' '+category_listing[0]
            league_name = league_listing[0]
            season_year = str(season_listing[0])
        link = season_tag.strip() #remove leading, trailing spaces
        link = unidecode.unidecode(link) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = 'leagues/' + link + ".html" #add events/ and append html
        
        league_dict[league_tag] = {'link': link, 'League Name': league_name, 'Season': season_year}
                    
    return league_dict



# Main)
def generate(rawresults, rawleagues, player_dict, events_dict_div_format, league_dict, league_year_cat_dict, webpage_output_location, layout_dict):
    # prep tables - all se
    editions_table = make_editions_table(rawresults, league_dict, league_year_cat_dict)
    
    # league index
    html_dict_league_index = gen_league_index(rawleagues, league_dict, editions_table)
    htmlwrite.generate('leagues.html', webpage_output_location, html_dict_league_index, layout_dict)
    outputlog.generate("league index page created")
    # individual event index
    for this_league in league_dict.keys():
        html_dict_indiv_league = gen_indiv_league(rawresults, player_dict, this_league, editions_table)
        htmlwrite.generate(league_dict[this_league], webpage_output_location, html_dict_indiv_league, layout_dict)
    
    # individual season pages
    list_of_seasons = list(editions_table['Dict Key'])
    for this_season_dict_key in list_of_seasons:
        html_dict_indiv_season = gen_indiv_season(rawresults, player_dict, this_season_dict_key, league_year_cat_dict, events_dict_div_format, editions_table)
        htmlwrite.generate(league_year_cat_dict[this_season_dict_key]['link'], webpage_output_location, html_dict_indiv_season, layout_dict)      

# 2) create league index page
def gen_league_index(rawleagues, league_dict, editions_table):
    league_index_table = pandas.DataFrame(columns = ('League', "# Seasons", "Link"))
    league_index_table['League'] = league_dict.keys()

    ### add num editions, last season, link, and last season link
    for i in league_index_table.index:
        cur_league = league_index_table.loc[i, 'League']
        editions_table_cur_league = editions_table[editions_table['League Name']==cur_league]
        league_index_table.loc[i, 'Link'] = league_dict[cur_league]
        ## to get number of seasons (ignore double count of comp and rec, ignore)
        x = list(set(editions_table_cur_league['Season']))
        league_index_table.loc[i, '# Seasons'] = len(x)

    ### sort the table - by number of seasons
    league_index_table = league_index_table.sort_values(by=["# Seasons"], ascending = False)
    # make final table
    league_index_final = league_index_table[['League', '# Seasons']]
    # make href table
    dict_href_columns = {'League': 'Link'}
    league_href = make_href_table(league_index_final, league_index_table, dict_href_columns, 0)
    # make lists
    list_of_tables_values = [league_index_final]
    list_of_tables_href = [league_href]
    list_of_tables_titles = ['League Index']
    list_of_tables_subtitles = ['']
    list_of_tables_titles_href = ['']
    list_of_tables_titles_id = ['']
    list_of_tables_subtitles_href = ['']
    
    html_dict_league_index = {
        'meta-title': "Crokinole Reference - League Index",
        'header-sub': 0,
        'page-heading': "League Index",
        'sub-header': ['Included below are the available records of ' 
                       + str(len(league_index_table)) + ' different leagues.'],
        'description': ['Individual annual editions of leagues can be viewed by following the links below.'],
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
    
    return html_dict_league_index
 
# 3) create individual league index pages
def gen_indiv_league(rawresults, player_dict, this_league, editions_table):
    ## for each category: one table that lists seasons, winner, runner-up
    
    ## filter editions table for this_event
    editions_table_cur_league = editions_table[editions_table['League Name']==this_league]
    ### sort the table - from most recent to least
    editions_table_cur_league = editions_table_cur_league.sort_values(by=["Structured Date"], ascending = False)
    
    ## initializing html lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_titles_id = []
    
    ## number of categories to sort through
    category_list = list(set(editions_table_cur_league['Category']))
    
    ## build html lists one year at a time
    for this_cat in category_list:
        cat_editions_table = editions_table_cur_league[editions_table_cur_league['Category']==this_cat]
        cat_editions_table = cat_editions_table.reset_index(drop=True)
        cat_table = pandas.DataFrame(columns = ("Season", "Winner", "Runner-up", 'Season Link', 'Winner Player Link', 'Runner-up Player Link'))
        cat_table['Season'] = cat_editions_table['Season']
        cat_table['Season Link'] = cat_editions_table['Link']
        cat_table = cat_table.reset_index(drop=True)
        for i in cat_table.index:
            ## filter rawresults for this annual season
            league_id = cat_editions_table.loc[i, 'Dict Key']
            league_name = cat_editions_table.loc[i, 'League Name']
            season_results = rawresults[(rawresults['League']==league_id)
                                        & (rawresults['Tournament']==league_name)]
            winner_row = season_results[season_results['Rank']==1].reset_index()
            if len(winner_row)>0:
                winner = winner_row.loc[0,'Player']
            else:
                winner = ''
            if len(winner_row)>1:
                winner = winner_row.loc[0,'Player'] + ' and ' + winner_row.loc[1,'Player']
            runner_up_row = season_results[season_results['Rank']==2].reset_index()
            if len(runner_up_row)>0:
                runner_up = runner_up_row.loc[0,'Player']
            else:
                runner_up = ''
            winner_link = ''
            runner_up_link = ''
            if winner in player_dict:
                winner_link = player_dict[winner]
            if runner_up in player_dict:
                runner_up_link = player_dict[runner_up]
            cat_table.loc[i,'Winner'] = winner
            cat_table.loc[i,'Runner-up'] = runner_up
            cat_table.loc[i,'Winner Player Link'] = winner_link
            cat_table.loc[i,'Runner-up Player Link'] = runner_up_link
            final_or_prelim = winner_row.loc[0,'Stage']
            if final_or_prelim == 'Prelim':
                cat_table.loc[i, 'Season'] = str(cat_table.loc[i, 'Season']) + ' (In Progress)'
        
        cat_table_final = cat_table[["Season", "Winner", "Runner-up"]]
        dict_href_columns = {'Season': 'Season Link'
                             ,'Winner': 'Winner Player Link'
                             ,'Runner-up': 'Runner-up Player Link'}
        cat_table_href = make_href_table(cat_table_final, cat_table, dict_href_columns, 1)
   
        # update lists
        list_of_tables_values += [cat_table_final]
        list_of_tables_href += [cat_table_href]
        list_of_tables_titles += [this_cat]
        list_of_tables_titles_id += [this_cat]
        
    # remaining html lists
    n = len(list_of_tables_values)
    list_of_tables_subtitles = ['']*n
    list_of_tables_titles_href = ['']*n
    list_of_tables_subtitles_href = ['']*n
    
    ## page-nav items
    page_nav_dict = dict(zip(list_of_tables_titles_id, list_of_tables_titles_id))
    page_nav_table_layout = make_table_m_n(1, list_of_tables_titles_id)
    page_nav_header_display = [0] * len(page_nav_table_layout.columns) ## needs to be 0s of length num columns of page_nav
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - " + this_league,
        'header-sub': 1,
        'page-heading': this_league + " Results",
        'sub-header': ['Included below are the available records of ' 
                       + str(len(list_of_tables_values)) + ' different categories.'],
        'description': ['Results from particular seasons can be viewed by following the links below.'],
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
def gen_indiv_season(rawresults, player_dict, this_season_dict_key, league_year_cat_dict, events_dict_div_format, editions_table):
    ## 2 tables to display: 
        #1) summary table of final rank along with points from each event (if available) 
        #2) list of events (if available)
        
    # prep inputs
    league_name = league_year_cat_dict[this_season_dict_key]['League Name']
    final_ranks = rawresults[(rawresults['Classification']=='Final Rank')
                             | (rawresults['Classification']=='Final Rank-Incomplete')]
    league_standings = rawresults[((rawresults['Classification']=='League Standings')
                                  | (rawresults['Classification']=='League Standings-Incomplete'))
                                  & (rawresults['League']==this_season_dict_key)]
    season_results = final_ranks[(final_ranks['League']==this_season_dict_key)
                                 & ~(final_ranks['Tournament']==league_name)]
    q = season_results.groupby(['Tournament', 'Structured Date', 'Category', 'Division', 'Year', 'Date']).size().reset_index().rename(columns={0:'count'}).sort_values('Structured Date', ascending=True)
    q = q.reset_index(drop=True)
    
    # 1) list of events
    list_of_events = []
    event_table = q
    event_table['Link'] = ''
    for i in event_table.index:
        tournament = event_table.loc[i,'Tournament']
        date = event_table.loc[i,'Date']
        division = event_table.loc[i,'Division']
        sing_doub = event_table.loc[i,'Category']
        key = tournament+' '+date+' '+division+' '+sing_doub
        if key in events_dict_div_format: #guarding against run failure (although this should work)
            event_table.loc[i, 'Link'] = events_dict_div_format[key]
        list_of_events += [tournament+' '+sing_doub]
    event_table_final = event_table[['Date', 'Tournament', 'Category']]
    dict_href_columns = {'Tournament': 'Link'}
    event_table_href = make_href_table(event_table_final, event_table, dict_href_columns, 1)
    
    # 2) summary table
    points_summary = league_standings[['Rank','Player','Games','Pts']]
    points_summary['Link'] = ''
    for i in points_summary.index:
        player = points_summary.loc[i,'Player']
        if player in player_dict:
            link = player_dict[player]
        else:
            link = ''
        points_summary.loc[i,'Link'] = link
    for event in list_of_events:
        points_summary[event] = add_event_to_season_summary(season_results, points_summary, event)

    points_summary_final = points_summary.copy()
    del points_summary_final['Link']
    #points_summary_final = points_summary[['Rank','Player','Games','Pts',list_of_events]]
    dict_href_columns = {'Player':'Link'}
    points_summary_href = make_href_table(points_summary_final, points_summary, dict_href_columns, 1)
    
    
    # update lists
    list_of_tables_values = [points_summary_final, event_table_final]
    list_of_tables_href = [points_summary_href, event_table_href]
    list_of_tables_titles = ['Points Summary', 'Event Listing']
    list_of_tables_titles_id = list_of_tables_titles
    n = len(list_of_tables_values)
    list_of_tables_subtitles = ['']*n
    list_of_tables_titles_href = ['']*n
    list_of_tables_subtitles_href = ['']*n
    
    ## page-nav items
    page_nav_dict = dict(zip(list_of_tables_titles_id, list_of_tables_titles_id))
    page_nav_table_layout = make_table_m_n(1, list_of_tables_titles_id)
    page_nav_header_display = [0] * len(page_nav_table_layout.columns) ## needs to be 0s of length num columns of page_nav

    # header and description
    x = editions_table[editions_table['Dict Key']==this_season_dict_key]
    x = x.reset_index()
    page_title = x.loc[0, 'Season']+ ' ' +x.loc[0, 'League Name']+ ' ' +x.loc[0, 'Category']
    description_note = ''
    if len(season_results)>0:
        start_date = min(season_results['Structured Date']).strftime('%b %d, %Y')
        end_date = max(season_results['Structured Date']).strftime('%b %d, %Y')
    else:
        start_date = 'NULL'
        end_date = 'NULL'

    # D) html dict
    html_dict_cat_page = {
        'meta-title': "Crokinole Reference - " + page_title,
        'header-sub': 1,
        'page-heading': page_title + " Results",
        'sub-header': ['The ' + page_title + ' was played from ' + start_date + ' to '+end_date+'.'],
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

#create a list of league points from a particular event in the order matching the player from points_summary
def add_event_to_season_summary(season_results, points_summary, event):
    player_list = list(points_summary['Player'])
    column_entries_as_list = ['']*len(player_list)
    event_id = event.split(' ')
    sing_doub = event_id[len(event_id)-1]
    tournament = ''
    for i in range(len(event_id)-1):
        tournament += event_id[i] +' '
    tournament = tournament[:-1] #remove trailing space
    event_results = season_results[(season_results['Tournament']==tournament)
                                 & (season_results['Category']==sing_doub)]
    for i in event_results.index:
        p1 = event_results.loc[i,'Player 1']
        p2 = event_results.loc[i,'Player 2']
        points = event_results.loc[i,'Pts']
        if p1 in player_list:
            jindex = player_list.index(p1)
            column_entries_as_list[jindex] = points
        if p2 in player_list:
            jindex = player_list.index(p2)
            column_entries_as_list[jindex] = points
    
    return column_entries_as_list

def make_editions_table(rawresults, league_dict, league_year_cat_dict):
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


