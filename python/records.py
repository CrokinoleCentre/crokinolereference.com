 # Crokinole Reference - Script to Generate webpages

## Generate record pages
    
# other crokinole reference scripts
import outputlog
import htmlwrite
# python modules
import pandas
import unidecode
import math


# Main)
def generate(rawresults, rawmatches, rawleagues, events_dict, events_dict_div_format, league_dict, player_dict, webpage_output_location, layout_dict):
    # filter to remove data not supposed to be in record book
    rawresults = rawresults[(rawresults['Inclusion']=='Public') 
                            | (rawresults['Inclusion']=='Ranking Exclude')]
    rawmatches = rawmatches[(rawmatches['Inclusion']=='Public')
                            | (rawmatches['Inclusion']=='Ranking Exclude')]
    
    # record index
    html_dict_record_index = gen_record_index(events_dict, events_dict_div_format)
    htmlwrite.generate('records.html', webpage_output_location, html_dict_record_index, layout_dict)
    outputlog.generate("record index page created")

    ## add tour id to rawresults, and a binary if it was a century
    modresults = rawresults_for_records(rawresults, rawleagues)
    
    ## make a table for all the record pages to be made: 
    ### tournament, league, division, format, link
    values_list = html_dict_record_index['detail-values']
    href_list = html_dict_record_index['detail-href']
    records_to_build_list = build_records_list(values_list, href_list)
    # individual record pages
    for i in records_to_build_list.index:
        html_dict_indiv_record = gen_indiv_record(modresults, rawmatches, player_dict, events_dict_div_format, i, records_to_build_list)
        link = records_to_build_list.loc[i,'Link']
        htmlwrite.generate(link, webpage_output_location, html_dict_indiv_record, layout_dict)
    outputlog.generate("all record pages created")

# 2) create record index page
def gen_record_index(events_dict, events_dict_div_format):
    league_dict = {'Competitive-Fingers':['All-time','NCA Tour']
                   , 'Competitive-Fingers Singles':['All-time','NCA Tour']
                   , 'Competitive-Fingers Doubles':['All-time','NCA Tour']
                   , 'Competitive-Cues':['All-time','']
                   , 'Competitive-Cues Singles':['All-time','']
                   , 'Competitive-Cues Doubles':['All-time','']}
    league_final = pandas.DataFrame(league_dict)
    league_href = make_href_for_record(league_final, 0)
    
    #event_final  = build_record_event_index(events_dict_div_format)
    record_index_table_event = build_record_event_index_old(events_dict, events_dict_div_format)
    #event_href = make_href_for_record(event_final, 0)

    ## finalize tables
    dict_href_columns = {'Category': 'base link'}
    event_final = record_index_table_event[['Event', 'Category']]
    event_href = make_href_table(event_final, record_index_table_event, dict_href_columns, 0)
    # make lists
    list_of_tables_values = [league_final, event_final]
    list_of_tables_href = [league_href, event_href]
    list_of_tables_titles = ['Records by League', 'Records by Event']
    list_of_tables_subtitles = ['', '']
    list_of_tables_titles_href = ['', '']
    list_of_tables_titles_id = ['', '']
    list_of_tables_subtitles_href = ['', '']
    
    html_dict_league_index = {
        'meta-title': "Crokinole Reference - Record Index",
        'header-sub': 0,
        'page-heading': "Record Index",
        'sub-header': ['Included below are the available records of several different events and leagues.'],
        'description': [],
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
        'detail-column-number': 1,
        'to_top_remove': 1
        }
    
    return html_dict_league_index
 
# 3) create individual record pages
def gen_indiv_record(modresults, rawmatches, player_dict, events_dict_div_format, i, records_to_build_list):
    tournament = records_to_build_list.loc[i,'Tournament']
    league = records_to_build_list.loc[i,'League']
    division = records_to_build_list.loc[i,'Division']
    x_format = records_to_build_list.loc[i,'Category']
    
    # filter results, matches
    filt_results = modresults.copy()
    filt_matches = rawmatches.copy()
    if tournament != '':
        filt_results = filt_results[filt_results['Tournament']==tournament]
    if league != '':
        filt_results = filt_results[filt_results['League Name']==league]
    filt_results = filt_results[filt_results['Division']==division]
    if x_format != '':
        filt_results = filt_results[filt_results['Category']==x_format]
    
    #records for individual players
    dict_records_tables = {}
    dict_records_tables = build_records_tables(filt_results, player_dict, events_dict_div_format, dict_records_tables, 'individual', league)
    #records for doubles teams
    if x_format == 'Doubles':
        dict_records_tables_doub = build_records_tables(filt_results, player_dict, events_dict_div_format, dict_records_tables, 'doubles', league)
        #merge dictionary
        dict_records_tables['values'] = dict_records_tables['values']+dict_records_tables_doub['values']
        dict_records_tables['href'] = dict_records_tables['href']+dict_records_tables_doub['href']
        dict_records_tables['titles'] = dict_records_tables['titles']+dict_records_tables_doub['titles']
        dict_records_tables['subtitles'] = dict_records_tables['subtitles']+dict_records_tables_doub['subtitles']
    
    ## if a doubles category, then want to duplicate tables for doubles teams
    page_nav_columns = 1
    page_nav_header = ['Individial Players']
    if x_format == 'Doubles':
        page_nav_columns = 2
        page_nav_header += ['Doubles Teams']
    
    # main html lists
    list_of_tables_values = dict_records_tables['values']
    list_of_tables_href = dict_records_tables['href']
    list_of_tables_titles = dict_records_tables['titles']
    list_of_tables_subtitles = dict_records_tables['subtitles']
        
    # remaining html lists
    list_of_tables_titles_id = list_of_tables_titles
    n = len(list_of_tables_values)
    list_of_tables_titles_href = ['']*n
    list_of_tables_subtitles_href = ['']*n
    
    ## page-nav items
    page_nav_dict = dict(zip(list_of_tables_titles_id, list_of_tables_titles_id))
    x = int(len(list_of_tables_values)/page_nav_columns)
    page_nav_table_layout = make_table_m_n(page_nav_columns, x, list_of_tables_titles_id)
    page_nav_header_display = page_nav_header
    
    ## page heading
    x = ''
    if (tournament == '') & (league == ''):
        x = 'all-time'
    page_heading = 'Records for '+tournament+league+x+' '+division+' '+x_format
    
    ## sub-header
    format_blurb = ''
    if x_format != '':
        format_blurb = ' and the '+x_format+' category'
    sh1 = 'Records comprise all '+tournament+' events played in the '+division+' division'+format_blurb+'.'
    sh_standard = 'Events lacking in either data or credibility relative to current results are excluded from the record book. These excluded results can still be found in event and player summaries.'
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - Records",
        'header-sub': 1,
        'page-heading': page_heading,
        'sub-header': [sh1, sh_standard],
        'description': ['Records are based on available data. If you see an error, please contact crokinolecentre@gmail.com to contribute additional data.'],
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
 
#### Helper function
# building a table to loop through to make individual record pages
def build_record_event_index(events_dict_div_format):
    editions = make_editions_table(events_dict_div_format)
    editions = editions[(editions['Division']=='Competitive-Fingers')
                        | (editions['Division']=='Competitive-Cues')]
    editions['combo'] = editions['Division']+' '+editions['Category']
    col_list = list(set(editions['combo']))
    col_list.sort()
    event_list = list(set(editions['Tournament']))
    event_list.sort()
    out = pandas.DataFrame('',index=event_list, columns=col_list)
    for event in out.index:
        event_editions = editions[editions['Tournament']==event]
        cat_list = list(set(event_editions['combo']))
        for cat in cat_list:
            out.loc[event,cat] = event
    
    return out


# building a table to loop through to make individual record pages
def build_record_event_index_old(events_dict, events_dict_div_format):
    record_index_table_event = pandas.DataFrame(columns = ('Event', "Category", "base link"))
    event_list = []
    category_list = []
    link_list = []
    check_list = []
    for event_name in events_dict:
        possible_list = list(events_dict_div_format.keys())
        for year_cat in possible_list:
            if (event_name in year_cat) and ('Competitive' in year_cat):
                cat = year_cat.split(' ')[-2] +' '+year_cat.split(' ')[-1]
                check = event_name+' '+cat
                if check not in check_list:
                    event_list += [event_name]
                    category_list += [cat]
                    check_list += [check]
                    # page link
                    link = unidecode.unidecode(check) #remove special characters
                    link = link.replace(" ", "-") #replace spaces with dash
                    link = link.lower()
                    link = 'records/'+link+'.html'
                    link_list += [link]
    record_index_table_event['Event'] = event_list
    record_index_table_event['Category'] = category_list
    record_index_table_event['base link'] = link_list

    return record_index_table_event

# taking a list the unique parts of the record html links and adding the common stuff (records/ and .html)
def convert_base_link_league(record_index_table_league):
    for i in record_index_table_league.index:
        link = record_index_table_league.loc[i, 'base link']
        link = unidecode.unidecode(link) #remove special characters
        link = link.replace(" ", "-") #replace spaces with dash
        link = link.lower()
        link = 'records/'+link+'.html'
        record_index_table_league.loc[i, 'base link'] = link
    return record_index_table_league

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

# make a table to list all parameters for the record pages to be made
def build_records_list(values_list, href_list):
    leagues_values = values_list[0]
    events_values = values_list[1]
    leagues_href = href_list[0]
    events_href = href_list[1]
    # tournament, league, division, format, link
    record_list = pandas.DataFrame(columns = ('Tournament','League','Division','Category','Link'))
    for i in leagues_values.index:
        tournament = ''
        for cat in leagues_values.columns:
            if leagues_values.loc[i,cat] != '':
                if leagues_values.loc[i,cat] == 'All-time':
                    league = ''
                else:
                    league = leagues_values.loc[i,cat]
                x = cat.split(' ')
                division = x[0]
                if len(x)>1:
                    this_format = x[1]
                else:
                    this_format = ''
                link = leagues_href.loc[i,cat]
                this_row = pandas.DataFrame({'Tournament': [tournament], 'League': [league],
                                     'Division': [division], 'Category': [this_format],
                                     'Link': [link]})
                record_list = record_list.append(this_row, ignore_index=True)

    for i in events_values.index:
        league = ''
        tournament = events_values.loc[i,'Event']
        x = events_values.loc[i,'Category'].split(' ')
        division = x[0]
        this_format = x[1]
        link = events_href.loc[i,'Category']
        this_row = pandas.DataFrame({'Tournament': [tournament], 'League': [league],
                                     'Division': [division], 'Category': [this_format],
                                     'Link': [link]})
        record_list = record_list.append(this_row, ignore_index=True)
    
    return record_list

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

# create table of specified column number (or square) from list of values
def make_table_m_n(column_number, row_number, values):
    # column_number can be "square" or number stating desired columns
    # values of the table
    num_values = len(values)
    ## determine number of rows and columns
    if column_number == 'square':
        num_rows = math.ceil(math.sqrt(num_values))
        num_columns = math.ceil(num_values/num_rows)
    else:
        num_rows = row_number
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

# builds a dictionary of a list of tables (values, href, titles) that will show all records
## the values of the dictionary are the tables list, the keys are values, href, titles
## team_tag = 'individual' or 'doubles'
def build_records_tables(filt_results, player_dict, events_dict_div_format, dict_records_tables, team_tag, league):
    display_num = 50
    # titles suffix
    suffix = ''
    if team_tag == 'doubles':
        suffix = ' as Team'
        filt_results['Partner'] = '' #placeholder because it is referenced later
    else:
        # if not doubles, expand filt_results to show both players in doubles team
        filt_results = expand_for_indiv_players(filt_results)
    # initialize
    values_list = []
    href_list = []
    titles_list = []
    subtitles_list = []
    
    # Build record tables
    ## 1) best league finishes: list # wins, 2nds, 3rd, 4th, 5ths ordered sequentially
    if (league != '') & (team_tag != 'doubles'):
        these_final_ranks = filt_results[((filt_results['Classification']=='League Standings')
                                          | (filt_results['Classification']=='League Standings-Incomplete'))
                                         & (filt_results['Tournament']==league)]
        league_placements = make_placements_table(these_final_ranks, player_dict)
        league_placements = add_rank_field_sort_cut(league_placements,['# Wins','2nd','3rd','4th','5th','Events Played'],[False,False,False,False,False,True],display_num)
        league_placements = add_player_event_link(league_placements, 1, 0, player_dict, events_dict_div_format)
        values = league_placements[['#','Player','# Wins','2nd','3rd','4th','5th','Events Played']]
        dict_href_columns = {'Player': 'Player Link'}
        href = make_href_table(values, league_placements, dict_href_columns,1)
        values_list += [values]
        href_list += [href]
        titles_list += ['Best League Finishes'+suffix]
        subtitles_list += ['Ranking based on wins, ordered by countback.']
    
    
    ## 2) best placements table: list # wins, 2nds, 3rd, 4th, 5ths ordered sequentially
    ### ensure tour standings aren't included -> ['Stage']!='Final League Standings'
    these_final_ranks = filt_results[((filt_results['Classification']=='Final Rank')
                                          | (filt_results['Classification']=='Final Rank-Incomplete'))
                                         & (filt_results['Stage']!='Final League Standings')]
    event_placements = make_placements_table(these_final_ranks, player_dict)
    event_placements = add_rank_field_sort_cut(event_placements,['# Wins','2nd','3rd','4th','5th','Events Played'],[False,False,False,False,False,True],display_num)
    event_placements = add_player_event_link(event_placements, 1, 0, player_dict, events_dict_div_format)
    values = event_placements[['#','Player','# Wins','2nd','3rd','4th','5th','Events Played']]
    dict_href_columns = {'Player': 'Player Link'}
    href = make_href_table(values, event_placements, dict_href_columns,1)
    values_list += [values]
    href_list += [href]
    titles_list += ['Best Event Finishes'+suffix]
    subtitles_list += ['Ranking based on wins, ordered by countback.']
        
    
    ## 3) most points in round robin (min 4 games)
    these_scores = filt_results[((filt_results['Classification']!='Final Rank')
                                 & (filt_results['Classification']!='Final Rank-Incomplete')
                                 & (filt_results['Classification']!='League Standings')
                                 & (filt_results['Classification']!='League Standings-Incomplete'))]
    min_4_games = these_scores[these_scores['Games']>=4]
    most_pts_full = add_rank_field_sort_cut(min_4_games,['10-Game-Adj Pts','Games','Structured Date'],[False,False,True],display_num)
    most_pts_full = add_player_event_link(most_pts_full, 1, 1, player_dict, events_dict_div_format)
    most_pts = most_pts_full[['#','Player','Partner','Date','Tournament','Category','Stage','Pool','Rank','Games','Pts','20s','10-Game-Adj Pts']]
    dict_href_columns = {'Player': 'Player Link', 'Tournament': 'Event Link'}
    most_pts_href = make_href_table(most_pts,most_pts_full,dict_href_columns,1)
    values_list += [most_pts]
    href_list += [most_pts_href]
    titles_list += ['Most Points Scored in Round'+suffix]
    subtitles_list += ['Ordered by 10 Game Average (Minumum 4 Games)']
    
    
    ## 4) most 20s in round robin (min 4 games)
    most_20s_full = add_rank_field_sort_cut(min_4_games,['10-Game-Adj 20s','Games','Structured Date'],[False,False,True],display_num)
    most_20s_full = add_player_event_link(most_20s_full, 1, 1, player_dict, events_dict_div_format)  
    most_20s = most_20s_full[['#','Player','Partner','Date','Tournament','Category','Stage','Pool','20s Rank','Games','Pts','20s','10-Game-Adj 20s']]
    dict_href_columns = {'Player': 'Player Link', 'Tournament': 'Event Link'}
    most_20s_href = make_href_table(most_20s,most_20s_full,dict_href_columns,1)
    values_list += [most_20s]
    href_list += [most_20s_href]
    titles_list += ['Most 20s Scored in Round'+suffix]
    subtitles_list += ['Ordered by 10 Game Average (Minumum 4 Games)']
    
    
    ## 5) most centuries
    most_cent_full = these_scores.groupby(['Player'])['Century'].sum().reset_index().rename(columns={'Century':'# Centuries'})
    most_cent_full = most_cent_full[most_cent_full['# Centuries']>0]
    most_cent_full = add_rank_field_sort_cut(most_cent_full,['# Centuries'],[False],display_num)
    most_cent_full = add_player_event_link(most_cent_full, 1, 0, player_dict, events_dict_div_format)
    most_cent = most_cent_full[['#','Player','# Centuries']]
    dict_href_columns = {'Player': 'Player Link'}
    most_cent_href = make_href_table(most_cent,most_cent_full,dict_href_columns,1)
    values_list += [most_cent]
    href_list += [most_cent_href]
    titles_list += ['Most Centuries Scored'+suffix]
    subtitles_list += ['Centuries are rounds where a player has scored both at least 100 20s, and has a 10-Game-Adj 20s score of at least 100.']
    
    
    ## 6) most events played
    most_events_full = these_final_ranks.groupby(['Player']).size().reset_index().rename(columns={0:'# Events Played'})
    most_events_full = add_rank_field_sort_cut(most_events_full,['# Events Played'],[False],display_num)
    most_events_full = add_player_event_link(most_events_full, 1, 0, player_dict, events_dict_div_format)
    most_events = most_events_full[['#','Player','# Events Played']]
    dict_href_columns = {'Player': 'Player Link'}
    most_events_href = make_href_table(most_events,most_events_full,dict_href_columns,1)
    values_list += [most_events]
    href_list += [most_events_href]
    titles_list += ['Most Events Played'+suffix]
    subtitles_list += ['']

    
    # convert into dictionary
    records_dict = {}
    records_dict['values'] = values_list
    records_dict['href'] = href_list
    records_dict['titles'] = titles_list
    records_dict['subtitles'] = subtitles_list
    
    return records_dict

# list Rank (based on countback), player, # wins, 2nds, 3rd, 4th, 5ths ordered sequentially
def make_placements_table(these_final_ranks, player_dict):
    table = pandas.DataFrame(columns=['Player','# Wins','2nd','3rd','4th','5th','Events Played'])
    plyr_list = list(set(these_final_ranks['Player']))
    for plyr in plyr_list:
        player_placements = these_final_ranks[these_final_ranks['Player']==plyr]
        r1 = sum(player_placements['Rank']==1)
        r2 = sum(player_placements['Rank']==2)
        r3 = sum(player_placements['Rank']==3)
        r4 = sum(player_placements['Rank']==4)
        r5 = sum(player_placements['Rank']==5)
        rtotal = len(player_placements)
        row = {'Player':plyr, '# Wins':r1,
               '2nd':r2, '3rd':r3, '4th':r4, '5th':r5, 'Events Played':rtotal}
        if (r1+r2+r3+r4+r5) != 0:
            table = table.append(row, ignore_index=True)
    
    return table

# sort a table, add a rank field, and cut to only display top X
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

# if not doubles, expand filt_results to show both players in doubles team
## add Partner field
def expand_for_indiv_players(filt_results):
    table1 = filt_results.copy()
    table1['Partner'] = ''
    table2 = table1.copy()
    table1['Player'] = table1['Player 1']
    table1['Partner'] = table1['Player 2']
    table2['Player'] = table2['Player 2']
    table2['Partner'] = table2['Player 1']
    table2 = table2[table2['Player']!=''] #remove blanks

    table = table1.append(table2, ignore_index=True) 
    
    return table

# add player/event link to given table
   #add_player_event_link(most_pts_full, 1, 1, player_dict, events_dict_div_format)
    
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

#make a table of league record links
def make_href_for_record(table_final, sub_link):
    out = pandas.DataFrame(columns = table_final.columns)
    for cat in table_final.columns:
        for i in table_final.index:
            link = table_final.loc[i,cat] + ' ' + cat
            link = unidecode.unidecode(link) #remove special characters
            link = link.replace(" ", "-") #replace spaces with dash
            link = link.lower()
            precede_link = '../' * sub_link
            link = precede_link + 'records/'+link+'.html'
            if table_final.loc[i,cat] == '':
                link = ''
            out.loc[i, cat] = link
    
    return out

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
