# Crokinole Reference - Script to Generate webpages

## Generate player index, individual pages, bios and player dictionary
    ## 1) create player dictionary
    ## 2) main function to generate 3 types of pages
    ## 3) player index function
    ## 4) player pages function
    
# other crokinole reference scripts
import outputlog
import htmlwrite
import events
# python modules
import pandas
import unidecode
import numpy
    
# 1) player dictionary - Key: full name, value: html page link
def gen_player_dict(rawresults):
    # get unique list of all players
    list1 = rawresults['Player 1'].tolist()
    list2 = rawresults['Player 2'].tolist()
    list_full = list1 + list2 #append the lists
    unique_list = list(set(list_full))
    
    #build dictionary
    player_dict = {}
    for player_name in unique_list:
        if type(player_name) == str: # in case there's a non-string item (like nan)
            page_link = player_link(player_name, player_dict)
            player_dict[player_name] = page_link
        
    if '' in player_dict: #removing the empty string from the dictionary
        del player_dict['']
    
    return player_dict

### 1-helper) create html link when given player name
def player_link(player_name, player_dict):
    # style of html link is: "players/" + lower case name + ".html"
    # spaces replaced with "-", special characters on letters are removed

    # html links to check for multiples and add numbers when needed
    links_so_far = list(player_dict.values())

    name = player_name.lower() #convert to lowercase
    link = unidecode.unidecode(name) #remove special characters
    link = link.replace(" ", "-") #replace spaces with dash
    links_so_far.append(link)
    ## check if already exists, and how many
    count = links_so_far.count(link)
    if count != 1:
        link = link + str(count) #append number if multiple
            
    link = 'players/' + link + ".html" #add players/ and append html
    return link


# 2) main function
def generate(rawresults, rawmatches, rawrankings, player_dict, events_dict_div_format, ranking_cat_dict, league_year_cat_dict, webpage_output_location, layout_dict):
    # player index
    html_dict_player_index = generate_player_index(rawresults, player_dict)
    htmlwrite.generate('players.html', webpage_output_location, html_dict_player_index, layout_dict)
    outputlog.generate("player index page created")
    # player pages
    for player in player_dict.keys():
        html_dict = generate_player_page(player, rawresults, rawmatches, rawrankings, player_dict, events_dict_div_format, ranking_cat_dict, league_year_cat_dict)
        htmlwrite.generate(player_dict[player], webpage_output_location, html_dict, layout_dict)
    outputlog.generate("player pages created")
    #generate_player_bios(player_dict, rawplayerbio) #skipped for now

# 3) player index function
def generate_player_index(rawresults, player_dict):
    # make draft table: player name, # events
    player_index_table = pandas.DataFrame(columns = ('Player Name', "# Events", "Link"))
    player_index_table['Player Name'] = player_dict.keys()
    ### sort the table
    player_index_table = player_index_table.sort_values(by=["Player Name"], ascending = True, key=lambda x: x.str.lower())
    ### add num events and links
    for i in player_index_table.index:
        cur_player = player_index_table.loc[i, 'Player Name']
        final_rank_list = rawresults[((rawresults['Player 1']==cur_player)
                                      | (rawresults['Player 2']==cur_player))
                                     & ((rawresults['Classification']=='Final Rank')
                                      | (rawresults['Classification']=='Final Rank-Incomplete'))
                                     ]
        player_index_table.loc[i, '# Events'] = len(final_rank_list)
        player_index_table.loc[i, 'Link'] = player_dict[cur_player]
    
    # make final table
    player_index_final = player_index_table[['Player Name', '# Events']]
    # make href table
    dict_href_columns = {'# Events': 'Link'}
    player_href = make_href_table(player_index_final, player_index_table, dict_href_columns, 0)
    # make lists
    list_of_tables_values = [player_index_final]
    list_of_tables_href = [player_href]
    list_of_tables_titles = ['Player Index']
    list_of_tables_subtitles = ['']
    list_of_tables_titles_href = ['']
    list_of_tables_titles_id = ['']
    list_of_tables_subtitles_href = ['']
    
    html_dict_player_index = {
        'meta-title': "Crokinole Reference - Player Index",
        'table-sort': 1,
        'header-sub': 0,
        'page-heading': "Player Index",
        'sub-header': ['Included below are the available records of ' 
                       + str(len(player_index_table)) + ' players.'],
        'description': ['Any clubs who were entered into an event included in this database are also included below.'],
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
    
    return html_dict_player_index
    
    
# 4) player pages function
def generate_player_page(player, rawresults, rawmatches, rawrankings, player_dict, events_dict_div_format, ranking_cat_dict, league_year_cat_dict):
    # 0) Setup inputs: filter for player
    rawresults_plyr = rawresults[((rawresults['Player 1']==player)
                                  | (rawresults['Player 2']==player))
                                 & ((rawresults['Classification']!='League Standings')
                                    & (rawresults['Classification']!='League Standings-Incomplete'))
                                 ]
    rawleagues_plyr = rawresults[((rawresults['Player 1']==player)
                                  | (rawresults['Player 2']==player))
                                 & ((rawresults['Classification']=='League Standings')
                                    | (rawresults['Classification']=='League Standings-Incomplete'))
                                 & (rawresults['Stage']=='Final')
                                 ]
    rawmatches_plyr = rawmatches[((rawmatches['Player 1']==player)
                                  | (rawmatches['Player 2']==player))]
    rawrankings_plyr = rawrankings[((rawrankings['Player 1']==player)
                                  | (rawrankings['Player 2']==player))]
    ## 0) Setup inputs: add columns for Partner, partner link, event link
    rawresults_plyr = add_partner_event_link_fields(rawresults_plyr, player, player_dict, events_dict_div_format)
    rawmatches_plyr = add_partner_event_link_fields(rawmatches_plyr, player, player_dict, events_dict_div_format)
    rawrankings_plyr = add_partner_rank_link_fields(rawrankings_plyr, player, player_dict, ranking_cat_dict)
    ### add columns to rawresults for league link, and league name
    rawresults_plyr = add_league_link_fields(rawresults_plyr, league_year_cat_dict)
    html_tables = {}
    
    # A) create values and href tables
    ## 1)
    title = 'Career: All Tournament Placements'
    subtitle = ''
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All Tournament Placements'
    all_finishes = build_all_finishes(rawresults_plyr)
    all_finishes_final = all_finishes[['#','Date','Tournament','League','Division','Category','Partner','Rank','# Entries']].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'League': 'league link'
                         ,'Partner': 'Partner Link'}
    all_finishes_href = make_href_table(all_finishes_final, all_finishes, dict_href_columns, 1)
    html_tables = track_tables(html_tables, all_finishes_final, all_finishes_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 2)
    title = 'Career: Best Finishes'
    subtitle = 'Top 5 finishes by category and discipline'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'Best Finishes'
    ### inputs: table, display num finishes, display min games ('' for no min), sort list, order to sort (true for ascending)
    #### top 5 finishes by rank
    best_finishes = sorted_values_table_split_by_cat(all_finishes, 5, '', ["Rank", "#"], [True, True])
    best_finishes_final = best_finishes[["#", "Date", "Tournament", "League", "Division", "Category", "Partner", "Rank", "# Entries"]].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'League': 'league link'
                         ,'Partner': 'Partner Link'}
    best_finishes_href = make_href_table(best_finishes_final, best_finishes, dict_href_columns, 1)
    html_tables = track_tables(html_tables, best_finishes_final, best_finishes_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 3)
    title = 'Detailed Results: All Round Robin Scores'
    subtitle = ''
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All Round Robin Scores'
    all_RR_scores = build_all_RR(rawresults_plyr)
    all_RR_scores_final = all_RR_scores[["#", "Date", "Tournament", "Division", "Category","Stage","Pool", "Partner", "Rank", "# Entries", "Games", "Pts", "20s"]].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'Partner': 'Partner Link'}
    all_RR_scores_href = make_href_table(all_RR_scores_final, all_RR_scores, dict_href_columns, 1)
    html_tables = track_tables(html_tables, all_RR_scores_final, all_RR_scores_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 4)
    title = 'Best Performances: Most Points'
    subtitle = 'Top 10 performances, ranked by 10-Game-Adj Points (min 4 games)'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'Most Points'
    ### filtering RR scores to only include "public" records (so the excluded pieces don't count in records)
    all_RR_scores_public = all_RR_scores[(all_RR_scores['Inclusion']=='Public') 
                                         | (all_RR_scores['Inclusion']=='Ranking Exclude')]
    ### filtering RR scores further to only include scores where Pts exist
    all_RR_scores_public_pts = all_RR_scores_public[pandas.to_numeric(all_RR_scores_public['Pts'], errors='coerce').notnull()]
    #### top 10 finishes by 10-game-adj pts, min 4 games
    best_pts = sorted_values_table_split_by_cat(all_RR_scores_public_pts, 10, 4, ["10-Game-Adj Pts", "#"], [False, True])
    best_pts_final = best_pts[["#", "Date", "Tournament", "Division", "Category","Stage","Pool", "Partner", "Rank", "# Entries", "Games", "Pts", "20s", "10-Game-Adj Pts"]].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'Partner': 'Partner Link'}
    best_pts_href = make_href_table(best_pts_final, best_pts, dict_href_columns, 1)
    html_tables = track_tables(html_tables, best_pts_final, best_pts_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 5)
    title = 'Best Performances: Most 20s'
    subtitle = 'Top 10 performances, ranked by 10-Game-Adj 20s (min 4 games)'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'Most 20s'
    ### filtering RR scores further to only include scores where 20s exist
    all_RR_scores_public_20s = all_RR_scores_public[pandas.to_numeric(all_RR_scores_public['20s'], errors='coerce').notnull()]
    #### top 10 finishes by 10-game-adj 20s, min 4 games
    best_20s = sorted_values_table_split_by_cat(all_RR_scores_public_20s, 10, 4, ["10-Game-Adj 20s", "#"], [False, True])
    best_20s_final = best_20s[["#", "Date", "Tournament", "Division", "Category","Stage","Pool", "Partner", "20s Rank", "# Entries", "Games", "20s", "10-Game-Adj 20s"]].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'Partner': 'Partner Link'}
    best_20s_href = make_href_table(best_20s_final, best_20s, dict_href_columns, 1)
    html_tables = track_tables(html_tables, best_20s_final, best_20s_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 6)
    title = 'Best Performances: All Centuries'
    subtitle = 'Centuries are rounds where a player has scored both at least 100 20s, and has a 10-Game-Adj 20s score of at least 100.'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All Centuries'
    ### list all centuries
    #### filter and redo #
    centuries = all_RR_scores_public_20s[(all_RR_scores_public_20s['20s']>=100)
                                         & (all_RR_scores_public_20s['10-Game-Adj 20s']>=100)]
    del centuries["#"]
    centuries['#'] = range(1, len(centuries) + 1)
    centuries_final = centuries[["#", "Date", "Tournament", "Division", "Category","Stage","Pool", "Partner", "20s Rank", "# Entries", "Games", "20s", "10-Game-Adj 20s"]].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'Partner': 'Partner Link'}
    centuries_href = make_href_table(centuries_final, centuries, dict_href_columns, 1)
    html_tables = track_tables(html_tables, centuries_final, centuries_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 7)
    title = 'Detailed Results: All H2H Scores'
    subtitle = ''
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All H2H Scores'
    ### H2H scores
    all_H2H_scores = build_H2H_scores(rawmatches_plyr)
    ####### (split by opponent) 
    all_H2H_scores_sections = add_section_breaks(all_H2H_scores, ['Opponent','Structured Date'], [True,True], ['Opponent'])
    all_H2H_scores_final = all_H2H_scores_sections[['Date','Tournament','Division','Category','Stage','Pool','Partner','# Rounds','Total Pts','Hammer Total','First Total']].fillna('')
    dict_href_columns = {'Tournament': 'Event Link'
                         ,'Partner': 'Partner Link'}
    all_H2H_scores_href = make_href_table(all_H2H_scores_final, all_H2H_scores_sections, dict_href_columns, 1)
    all_H2H_scores_final = add_section_totals(all_H2H_scores_final, 4)
    ####### (split by event/date/division) 
    #all_H2H_scores_sections = add_section_breaks(all_H2H_scores, ['Structured Date'], [True], ['Date', 'Tournament', 'Division', 'Category'])
    #all_H2H_scores_final = all_H2H_scores_sections[['Tournament','Stage','Pool','Partner','Opponent','# Rounds','Total Pts','Hammer Total','First Total']].fillna(' ')
    #all_H2H_scores_href = make_href_table(all_H2H_scores_final, all_H2H_scores_sections, ['Event Link', '','','Partner Link','','','','',''], 1)
    html_tables = track_tables(html_tables, all_H2H_scores_final, all_H2H_scores_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 8)
    title = 'Rankings: All Ranks'
    subtitle = 'Calculated by CrokinoleCentre'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All Ranks'
    ### all rankings
    rawrankings_plyr = rankings_decimal_format(rawrankings_plyr)
    #### sort by date, then by rating for those unranked
    rawrankings_plyr = rawrankings_plyr.sort_values(by=['Structured Date'], ascending = [True])
    rankings_all = sorted_rankings_table_split_by_cat(rawrankings_plyr, len(rawrankings_plyr), ["Structured Date"], [True])
    rankings_all_final = rankings_all[['#','Date', 'Partner', 'Rank', 'Rating', 'Number Events', 'Number Games', 'Adj Number Games', 'Pts For','Pts Against','Pts %','Avg Opponent Rating','Avg Teammate Rating']].fillna(' ')
    rankings_all_final = rankings_all_final.rename(columns={'Number Events':'# Events', 'Number Games':'# Games'
                                               ,'Adj Number Games':'Adj # Games','Avg Opponent Rating':'Avg Opponent'
                                               ,'Avg Teammate Rating':'Avg Teammate'})
    ######### '#' column included to get section breaks
    dict_href_columns = {'Date': 'Rank Link'
                         ,'Partner': 'Partner Link'}
    rankings_all_href = make_href_table(rankings_all_final, rankings_all, dict_href_columns, 1)
    html_tables = track_tables(html_tables, rankings_all_final, rankings_all_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 9)
    title = 'Rankings: Best Ranks'
    subtitle = 'Calculated by CrokinoleCentre: Top 5 in each category'
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'Best Ranks'
    ### best rankings by category
    best_ranks = sorted_rankings_table_split_by_cat(rawrankings_plyr, 5, ["Rank", "Structured Date"], [True, True])
    best_ranks_final = best_ranks[['#', 'Date', 'Partner', 'Rank', 'Rating', 'Number Events', 'Number Games', 'Adj Number Games', 'Pts For','Pts Against','Pts %','Avg Opponent Rating','Avg Teammate Rating']].fillna(' ')
    best_ranks_final = best_ranks_final.rename(columns={'Number Events':'# Events','Number Games':'# Games',
                                               'Adj Number Games':'Adj # Games','Avg Opponent Rating':'Avg Opponent'
                                               ,'Avg Teammate Rating':'Avg Teammate'})
    dict_href_columns = {'Date': 'Rank Link'
                         ,'Partner': 'Partner Link'}
    best_ranks_href = make_href_table(best_ranks_final, best_ranks, dict_href_columns, 1)
    html_tables = track_tables(html_tables, best_ranks_final, best_ranks_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 10)
    title = 'Career: All League Finishes'
    subtitle = ''
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'All League Finishes'
    ### league finishes
    all_league_finishes_full = build_league_table(rawleagues_plyr, league_year_cat_dict) #build section breaks for league type and category, order by date, add columns for Season (year), league_year_cat link, change column name for pts (league pts), games (# Events)
    #### build section breaks for league type and category
    all_league_finishes_full = add_section_breaks(all_league_finishes_full, ['Structured Date'], [True], ['Tournament', 'Division'])
    all_league_finishes = all_league_finishes_full[['Season', 'Rank', '# Events', 'League Pts']].fillna('')
    dict_href_columns = {'Season': 'Season Link'}
    all_league_finishes_href = make_href_table(all_league_finishes, all_league_finishes_full, dict_href_columns, 1)
    html_tables = track_tables(html_tables, all_league_finishes, all_league_finishes_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    ## 11)
    title = 'Career: Team Results'
    subtitle = ''
    titles_href = ''
    titles_id = title
    subtitles_href = ''
    page_nav_dict_value = 'Team Results'
    ### team results
    team_results_full = build_team_results(all_finishes)
    team_results = team_results_full[['#','Date','Tournament','Team','Team Rank','# Teams']]
    dict_href_columns = {'Tournament': 'Event Link'}
    team_results_href = make_href_table(team_results, team_results_full, dict_href_columns, 1)
    html_tables = track_tables(html_tables, team_results, team_results_href, title, subtitle, titles_href, titles_id, subtitles_href, page_nav_dict_value)
    
    # B) unwind html_tables to create lists for the html dict (and specify order of html appearance)
    ## if table title in html_order doesn't exist in html_tables then it is skipped
    html_order = ['Career: Best Finishes', 'Career: All Tournament Placements', 'Best Performances: Most Points','Best Performances: Most 20s','Best Performances: All Centuries','Detailed Results: All Round Robin Scores','Detailed Results: All H2H Scores', 'Rankings: Best Ranks', 'Rankings: All Ranks', 'Career: All League Finishes', 'Career: Team Results']
    list_of_tables_values = unwind_tables(html_tables, html_order, 'values')
    list_of_tables_href = unwind_tables(html_tables, html_order, 'href')
    list_of_tables_titles = unwind_tables(html_tables, html_order, 'titles') #titles is key of html_tables
    list_of_tables_subtitles = unwind_tables(html_tables, html_order, 'subtitles')
    list_of_tables_titles_href = unwind_tables(html_tables, html_order, 'titles_href')
    list_of_tables_titles_id = unwind_tables(html_tables, html_order, 'titles_id')
    list_of_tables_subtitles_href = unwind_tables(html_tables, html_order, 'subtitles_href')
    list_of_tables_values = unwind_tables(html_tables, html_order, 'values')
    page_nav_dict = unwind_tables(html_tables, html_order, 'page_nav') #order parameter doesn't matter for page_nav
    
    # C) create the page-nav and subtitle/description info
    ## sub-header
    if len(all_finishes)==0:
        year_end = 'NULL'
        year_start = 'NULL'
        best_finish = 'NULL'
    else:
        year_end = max(all_finishes['Year'])
        year_start = min(all_finishes['Year'])
        ##### best finish work
        y=int(min(all_finishes["Rank"]))
        x=int(sum(all_finishes["Rank"][all_finishes["Rank"]==y])/y)
        best_finish = '#' + str(y) + ' (' + str(x) + ')'
    ### nca tours - start
    nca_tours = all_league_finishes_full[all_league_finishes_full['Tournament']=='NCA Tour']
    if len(nca_tours) == 0:
        nca_tour_str = ''
    else:
        nca_tours_played = len(set(nca_tours['Season'])) ## done this way to not double count recreational and competitive tours
        nca_best_finish = min(nca_tours['Rank'])
        nca_best_format_index = nca_tours.index[nca_tours['Rank']==nca_best_finish].tolist()[0]
        nca_best_format = nca_tours.loc[nca_best_format_index, 'Division']
        nca_tour_str = 'Number of NCA Tours played: <b>' +str(nca_tours_played)+'</b> (Best finish '+nca_best_format+' : <b>#'+str(nca_best_finish)+'</b>)'
    ### nca tours - end
    best_rank_for_subheader = best_rank_string_generator(rawrankings_plyr)
    lead = player + " has played in events from " + year_start + " to " + year_end + "."
    sub_header = [lead]
    ### include <b> tags
    tournaments_played = len(all_finishes)
    tournaments_played_str = 'Tournaments Played: <b>' + str(tournaments_played) + '</b>'
    best_finish_str = 'Best tournament placement: <b>' + best_finish + '</b>'
    best_rank_str = 'Best CrokinoleCentre ranking: <b>' + best_rank_for_subheader + '</b>'
    sub_header.extend([tournaments_played_str, best_finish_str, best_rank_str, nca_tour_str])
    
    ## description
    description = []
    
    ## page-nav items
    page_nav_table_layout = {'Career':['Career: Best Finishes','Career: All Tournament Placements','Career: All League Finishes','Career: Team Results']
                             ,'Best Performances':['Best Performances: Most Points','Best Performances: Most 20s','Best Performances: All Centuries','']
                             ,'Detailed Results':['Detailed Results: All Round Robin Scores','Detailed Results: All H2H Scores','','']
                             ,'Rankings': ['Rankings: Best Ranks', 'Rankings: All Ranks','','']
                             }
    page_nav_table_layout = pandas.DataFrame(page_nav_table_layout, columns = ['Career','Best Performances','Detailed Results','Rankings'])
    page_nav_header_display = [1,1,1,1]
    # coder check
    #page_nav_check_for_coder(page_nav_dict, page_nav_table_layout, page_nav_header_display)
    
    # D) html dict
    html_dict = {
        'meta-title': "Crokinole Reference - " + player,
        'header-sub': 1,
        'page-heading': player,
        'sub-header': sub_header,
        'description': description,
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
    
    return html_dict

# stores the 7 necessary tables in one dictionary of dictionaries, plus page_nav_dict, where main key is table title
def track_tables(table_dict, values, href, titles, subtitles, titles_href, titles_id, subtitles_href, page_nav_dict_entry):
    table_dict[titles] = {'values': values,
                          'href': href,
                          'subtitles': subtitles,
                          'titles_href': titles_href,
                          'titles_id': titles_id,
                          'subtitles_href': subtitles_href,
                          'page_nav': page_nav_dict_entry}

    return table_dict

# unwinds the track_tables of a particular attribute into desired order as specified
def unwind_tables(html_tables, html_order, attribute):
    ## note items in html_order may not be in the keys of html_tables (hence if statements below)
    if attribute == 'titles':
        ## out is the list of html_order with only existing keys of html_tables remaining
        out = []
        for title in html_order:
            if title in html_tables.keys():
                out += [title]
    elif attribute == 'page_nav':
        ## out is dictionary of page_nav elements of html_tables
        out = {}
        for title in html_order:
            if title in html_tables.keys():
                out[title] = html_tables[title]['page_nav']
    else:
        ## out is list of attribute elements of page_nav
        out = []
        for title in html_order:
            if title in html_tables.keys():
                out += [html_tables[title][attribute]]
    
    return out

# checks format of page_nav: ensures all included so it doesn't break on output
def page_nav_check_for_coder(page_nav_dict, page_nav_table_layout, page_nav_header_display):
    # everything in layout must appear in dict
    ## ensures when selected in page_nav the href link is available to jump to
    layout = page_nav_table_layout.values.flatten()
    for cell in layout:
        if (cell!='') & (cell not in page_nav_dict):
            print (cell+' not in page_nav_dict')
    for key in page_nav_dict.keys():
        if key not in layout:
            print (key+' not in page_nav_table_layout')

    # length of display must match column number of layout
    if len(page_nav_header_display) == len(page_nav_table_layout.columns):
        print('display length correct')
    else:
        print('display length wrong')
    

# 3/4-helper
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

# 4-table builds
def build_all_finishes(rawresults):
    ## filter for player + final ranks
    final_rank_list = rawresults[((rawresults['Classification']=='Final Rank')
                                  | (rawresults['Classification']=='Final Rank-Incomplete'))
                                 ]
    ## sort based on date
    final_rank_list = final_rank_list.sort_values(by=['Structured Date'], ascending = [True])
    ## add columns: # for order
    final_rank_list['#'] = range(1, len(final_rank_list) + 1)
    
    return final_rank_list

def build_best_finishes(all_finishes):
    ## Best finishes - by category and discipline and division
    ### Top 5 finishes for combinations of discipline and division
    display_num_finishes = 5
    display_min_games = '' #empty string to skip
    ### call function to generate values table
    sort_list = ["Rank", "#"]
    sort_list_order = [True, True] #true for ascending, false for descending
    top_finishes = sorted_values_table_split_by_cat(all_finishes, display_num_finishes, display_min_games, sort_list, sort_list_order)
        
    return top_finishes

def build_team_results(all_finishes):
    out = all_finishes.fillna('')
    out = out[out['Team']!='']
    # redoing the # column
    del out["#"]
    out['#'] = range(1, len(out) + 1)
    return out

### 4-helper) make values table split by division and discipline, sorted as desired
def sorted_values_table_split_by_cat(results_table, display_num, display_min_games, sort_list, sort_list_order):
    ## results_table: filtered table of scores/ranks, should have a "#" field indicating the index of chronological order
    ## display_num: number of the top results to display
    ## display_min_games: min threshold of games to have in row for record to potentially be displayed
    ## sort_list: columns to sort the data on to find the top results (can be multiple)
    ## sort_list_order: list of true (for ascending order), false for descending
    
    #setting empty value in case nothing populates
    top_finishes = pandas.DataFrame(columns=results_table.columns)
    
    if display_min_games != '': #it equals a number, filter results table
        results_table = results_table[results_table["Games"] >= display_min_games]
    
    #### q has unique combos of discipline/division, sorted by # appearances
    q = results_table.groupby(['Division', 'Category']).size().reset_index().rename(columns={0:'count'}).sort_values('count', ascending=False)

    for i in range(len(q)):
        this_division = q.loc[i, 'Division']
        this_sing_doub = q.loc[i, 'Category']
        this_category = results_table[(results_table['Division'] == this_division) & (results_table['Category'] == this_sing_doub)]
        # sort by sort_list
        this_category = this_category.sort_values(by=sort_list, ascending = sort_list_order)
        if len(this_category) > display_num: # check if table is large enough to be cut down to the best results
            # get value of worst rank to include in table
            ### loc references index (doesn't work for filtered, sorted table), iloc gets nth+1 row
            lowest_top_rank = this_category.iloc[display_num-1][sort_list[0]]
        else:
            lowest_top_rank = this_category.iloc[len(this_category)-1][sort_list[0]]
        
        # now only include results with ranking above/below lowest_top_rank
        if sort_list_order[0]: #want lower than or equal
            this_category_top = this_category[this_category[sort_list[0]] <= lowest_top_rank]
        else: # greater than or equal
            this_category_top = this_category[this_category[sort_list[0]] >= lowest_top_rank]
        
        # redoing the # column
        del this_category_top["#"]
        this_category_top['#'] = range(1, len(this_category_top) + 1)
        # adding in colspan section name
        section_name = 'Colspan!' + this_division + ' ' + this_sing_doub
        empty_string_list = ['']*(len(results_table.columns)-1)
        section_name_list =  empty_string_list + [section_name] #add colspan at the right, which is where the # field will be
        section_table = pandas.DataFrame([section_name_list], columns=this_category_top.columns)
        this_category_top = pandas.concat([section_table, this_category_top])
        if i == 0:
            top_finishes = this_category_top
        else:
            top_finishes = top_finishes.append(this_category_top).reset_index(drop=True)
            
    return top_finishes

### 4-helper) split rankings by class and discipline
def sorted_rankings_table_split_by_cat(results_table, display_num, sort_list, sort_list_order):
    ## results_table: filtered table of ranks
    ## display_num: number of the top results to display
    ## sort_list: columns to sort the data on to find the top results (can be multiple)
    ## sort_list_order: list of true (for ascending order), false for descending
    
    # remove nan rank rows
    results_table = results_table[results_table['Rank'].notnull()]
    
    # adding # column to results_table
    results_table['#'] = range(1, len(results_table) + 1)
    
    #setting empty value in case nothing populates
    top_finishes = pandas.DataFrame(columns=results_table.columns)
    
    #### q has unique combos of discipline/division, sorted by # appearances
    q = results_table.groupby(['Classification', 'Discipline']).size().reset_index().rename(columns={0:'count'}).sort_values('count', ascending=False)

    for i in range(len(q)):
        this_division = q.loc[i, 'Classification']
        this_sing_doub = q.loc[i, 'Discipline']
        this_category = results_table[(results_table['Classification'] == this_division) & (results_table['Discipline'] == this_sing_doub)]
        # sort by sort_list
        this_category = this_category.sort_values(by=sort_list, ascending = sort_list_order)
        if len(this_category) > display_num: # check if table is large enough to be cut down to the best results
            # get value of worst rank to include in table
            ### loc references index (doesn't work for filtered, sorted table), iloc gets nth+1 row
            lowest_top_rank = this_category.iloc[display_num-1][sort_list[0]]
        else:
            lowest_top_rank = this_category.iloc[len(this_category)-1][sort_list[0]]
        
        # now only include results with ranking above/below lowest_top_rank
        if sort_list_order[0]: #want lower than or equal
            this_category_top = this_category[this_category[sort_list[0]] <= lowest_top_rank]
        else: # greater than or equal
            this_category_top = this_category[this_category[sort_list[0]] >= lowest_top_rank]
        
        # adding the # column
        this_category_top['#'] = range(1, len(this_category_top) + 1)
        # adding in colspan section name
        section_name = 'Colspan!' + this_division + ' ' + this_sing_doub
        empty_string_list = ['']*(len(results_table.columns)-1)
        section_name_list =  empty_string_list + [section_name] #add colspan at the right, which is where the # field will be
        section_table = pandas.DataFrame([section_name_list], columns=this_category_top.columns)
        this_category_top = pandas.concat([section_table, this_category_top])
        if i == 0:
            top_finishes = this_category_top
        else:
            top_finishes = top_finishes.append(this_category_top).reset_index(drop=True)
            
    return top_finishes

## 4-helper) add columns to rawresults for league link, and league name
def add_league_link_fields(rawresults_plyr, league_year_cat_dict):
    results_table = rawresults_plyr.copy()
    results_table['league link'] = ''
    results_table['League Name'] = ''
    for i in results_table.index:
        league = results_table.loc[i, 'League']
        if league in league_year_cat_dict:
            results_table.loc[i,'league link'] = league_year_cat_dict[league]['link']
            results_table.loc[i,'League Name'] = league_year_cat_dict[league]['League Name']
    
    return results_table

def build_all_RR(rawresults_plyr):
    ## filter for player + final ranks
    RR_list = rawresults_plyr[((rawresults_plyr['Classification']=='Scores')
                               | (rawresults_plyr['Classification']=='Incomplete-Scores'))
                              ]
    ## sort based on date
    RR_list = RR_list.sort_values(by=['Structured Date'], ascending = [True])
    ## add columns: # for order
    RR_list['#'] = range(1, len(RR_list) + 1)
    
    return RR_list

def build_H2H_scores(rawmatches_plyr):
    H2H_scores = rawmatches_plyr[rawmatches_plyr['Pts/20s']=='Pts']
    H2H_scores = H2H_scores.rename(columns={'Total':'Total Pts'})
    #removed (already covered earlier on) #H2H_scores = add_partner_event_link_fields(H2H_scores, player, player_dict, events_dict_div_format)
    return H2H_scores

### 4-helper) add partner, partner link, event link fields to table
def add_partner_event_link_fields(data_table, this_player, player_dict, events_dict_div_format):
    output = data_table.copy()
    output['Partner'] = ''
    output['Partner Link'] = ''
    output['Event Link'] = ''
    for i in output.index:
        p1 = output['Player 1'][i]
        p2 = output['Player 2'][i]
        if p1 == this_player:
            output.loc[i, 'Partner'] = p2
        else:
            output.loc[i, 'Partner'] = p1
        partner = output.loc[i, 'Partner']
        event = output.loc[i, 'Tournament']
        ##date = output.loc[i, 'Structured Date']
        date = output.loc[i, 'Date']
        #year = date[-4:] #picking up right 4 characters
        division = output.loc[i, 'Division']
        discipline = output.loc[i, 'Category']
        if discipline == 'Team-dummy':
            discipline = 'Teams' #try to link to Teams category if team-dummy
        eventid = event + ' ' + date + ' ' + division + ' ' + discipline
        if eventid in events_dict_div_format: #guarding against run failure (although this should work)
            eventlink = events_dict_div_format[eventid]
            output.loc[i, 'Event Link'] = eventlink
        if partner in player_dict:
            output.loc[i, 'Partner Link'] = player_dict[partner]
        
    return output

def add_partner_rank_link_fields(data_table, this_player, player_dict, ranking_cat_dict):
    output = data_table.copy()
    output['Partner'] = ''
    output['Partner Link'] = ''
    output['Rank Link'] = ''
    for i in output.index:
        p1 = output['Player 1'][i]
        p2 = output['Player 2'][i]
        if p1 == this_player:
            output.loc[i, 'Partner'] = p2
        else:
            output.loc[i, 'Partner'] = p1
        partner = output.loc[i, 'Partner']
        this_class = output.loc[i, 'Classification']
        this_disc = output.loc[i, 'Discipline']
        this_date = output.loc[i,'Date']
        rank_id = this_date+' '+this_class+' '+this_disc
        if partner in player_dict:
            output.loc[i, 'Partner Link'] = player_dict[partner]
        if rank_id in ranking_cat_dict:
            output.loc[i, 'Rank Link'] = ranking_cat_dict[rank_id]
        
    return output

### 4-helper) make values table split into sections, no threshold cutoffs
def add_section_breaks(results_table, sort_list, sort_list_order, sections):
    ## results_table: filtered table of scores/ranks, should have a "Structured Date" field indicating the index of chronological order
    ## sort_list: columns to sort the data on to find the top results (can be multiple)
    ## sort_list_order: list of true (for ascending order), false for descending
    ## sections: list of fields to use to break into sections
    
    #setting empty value in case nothing populates
    finishes = pandas.DataFrame(columns=results_table.columns)
    
    #### q has unique combos of sections, sorted by # appearances
    q = results_table.groupby(sections).size().reset_index().rename(columns={0:'count'})

    for i in range(len(q)):
        this_category = results_table
        section_title = ''
        for j in range(len(sections)):
            section_col = sections[j]
            this_section = q.loc[i, section_col]
            section_title = section_title + ' - ' + this_section
            this_category = this_category[this_category[section_col] == this_section]
        
        # sort by sort_list
        this_category = this_category.sort_values(by=sort_list, ascending = sort_list_order)

        # adding in colspan section name
        section_title = section_title[2:]
        section_name = 'Colspan!' + section_title
        section_name_list = [section_name]*(len(results_table.columns)) #add colspan in every cell of row
        section_table = pandas.DataFrame([section_name_list], columns=this_category.columns)
        this_category = pandas.concat([section_table, this_category])
        if i == 0:
            finishes = this_category
        else:
            finishes = finishes.append(this_category).reset_index(drop=True)
            
    return finishes

# add section totals
## only works if no jumps in index
def add_section_totals(table, num_rightmost_cols_to_sum):
    results_table = table.reset_index(drop=True)
    last_row = len(results_table)
    for i in results_table.index:
        if i != (last_row-1):
            row_values = results_table.iloc[i]
            next_row_values = results_table.iloc[i+1]
            if (len(row_values[0])>8) & (row_values[0][0:8] == 'Colspan!'):
                ## reset totals, save row index to push totals to, and change Colspan! in the table
                cur_totals = [0]*num_rightmost_cols_to_sum
                row_total_id = i
                section_name = row_values[0][8:]
                rows_to_span = len(row_values) - num_rightmost_cols_to_sum
                ## asterisk used as flag to htmlwrite to note it's a modified Colspan with 2 digits to follow that indicate number of columns
                new_section_name = 'Colspan!' + "*"+ "{0:0=2d}".format(rows_to_span) + section_name
                results_table.iloc[i] = new_section_name
            else: ## add to totals
                for j in range(num_rightmost_cols_to_sum):
                    col_num = len(row_values) - num_rightmost_cols_to_sum + j
                    if (results_table.iloc[i,col_num] != ' ') & (results_table.iloc[i,col_num] != ''):
                        cur_totals[j] += results_table.iloc[i,col_num]
            if (len(next_row_values[0])>8) & (next_row_values[0][0:8] == 'Colspan!'):
                ## fill in totals of previous section
                for j in range(num_rightmost_cols_to_sum):
                    col_num = len(row_values) - num_rightmost_cols_to_sum + j
                    results_table.iloc[row_total_id,col_num] = cur_totals[j]
        else: ## last row of table so add fill in totals of last section
            ## add to totals first
            for j in range(num_rightmost_cols_to_sum):
                col_num = len(row_values) - num_rightmost_cols_to_sum + j
                if (results_table.iloc[i,col_num] != ' ') & (results_table.iloc[i,col_num] != ''):
                    cur_totals[j] += results_table.iloc[i,col_num]
            for j in range(num_rightmost_cols_to_sum):
                col_num = len(row_values) - num_rightmost_cols_to_sum + j
                results_table.iloc[row_total_id,col_num] = cur_totals[j]
            
    return results_table

### 4-helper) format rankings tables for decimal places
def rankings_decimal_format(rank_table):
    # formatting the table for rounding
    rank_table['Rating'] = round(rank_table['Rating'],0)
    rank_table['Adj Number Games'] = round(rank_table['Adj Number Games'],1)
    rank_table['Pts For'] = round(rank_table['Pts For'],1)
    rank_table['Pts Against'] = round(rank_table['Pts Against'],1)
    rank_table['Pts %'] = round(rank_table['Pts %'],3)
    rank_table['Avg Opponent Rating'] = round(rank_table['Avg Opponent Rating'],0)
    rank_table['Avg Teammate Rating'] = round(rank_table['Avg Teammate Rating'],0)
    
    return rank_table

### 4-helper) given a table containing the final league results, constructs the table which can later be subsetted into a summary table
def build_league_table(rawleagues_plyr, league_year_cat_dict):
    league_table = rawleagues_plyr.copy()
    # add columns for Season (year), league_year_cat link
    league_table['Season'] = ''
    league_table['Season Link'] = ''
    for i in league_table.index:
        league_id = league_table.loc[i, 'League']
        league_table.loc[i,'Season'] = league_year_cat_dict[league_id]['Season']
        league_table.loc[i,'Season Link'] = league_year_cat_dict[league_id]['link']
    # change column name for pts (league pts), games (# Events)
    league_table = league_table.rename(columns={'Games':'# Events','Pts':'League Pts'})

    return league_table

### 4c-helper)  takes best ranks table, and outputs string that specifies discipline and best rank
def best_rank_string_generator(rawrankings_plyr):
    if len(rawrankings_plyr)==0:
        return 'NULL'
    else:
        best_string = ''
        classification_list = ['Fingers', 'Cues']
        discipline_list = ['Overall', 'Singles', 'Doubles']
        for this_class in classification_list:
            for this_disc in discipline_list:
                this_rank = rawrankings_plyr[(rawrankings_plyr['Classification']==this_class)
                                             & (rawrankings_plyr['Discipline']==this_disc)]
                if (len(this_rank) != 0) & (len(this_rank['Rank'].dropna())!=0):
                    if min(this_rank['Rank'].dropna()) == min(this_rank['Rank'].dropna()): # not a nan value
                        string = this_class+'-'+this_disc+' #'+str(int(min(this_rank['Rank'].dropna())))+', '
                        best_string += string
        
    
        return best_string[:-2]
