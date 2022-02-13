# Crokinole Reference - Script to Generate webpages

## Generate ranking index and pages for each date
    # 1) create ranking dictionaries
    # Main) code to run scripts below
    # 2) create ranking index page
    # 3) create ranking date pages
    
# other crokinole reference scripts
import outputlog
import htmlwrite
import events
# python modules
import pandas
import unidecode


# 1) create ranking dictionaries
## key is date, value: link to that page
def gen_ranking_dict(rawrankings):
    rankings_dict = {}
    q = rawrankings.groupby(['Date']).size().reset_index()
    for date in q['Date']:
        link = unidecode.unidecode(date) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = link.replace(",", "") #replace commas with nothing
        link = 'rankings/' + link + ".html"
        rankings_dict[date] = link
                    
    return rankings_dict

## key is date+category, value: link to that page and #href to id
def gen_ranking_cat_dict(rawrankings):
    rankings_cat_dict = {}
    q = rawrankings.groupby(['Date','Classification','Discipline']).size().reset_index()
    for date, classif, disc in zip(q['Date'],q['Classification'],q['Discipline']):
        rank_id = date + ' ' + classif + ' ' + disc
        link = unidecode.unidecode(date) #remove special characters
        link = link.lower()
        link = link.replace(" ", "-") #replace spaces with dash
        link = link.replace(",", "") #replace commas with nothing
        classif = classif.lower()
        disc = disc.lower()
        link = 'rankings/' + link + ".html#" + classif + '-' + disc
        rankings_cat_dict[rank_id] = link
    
    return rankings_cat_dict

# Main Code
def generate(rawrankings, player_dict, ranking_dict, ranking_cat_dict, webpage_output_location, layout_dict):
    # add player link to rankings table
    rawrankings = events.add_player_link(rawrankings, player_dict)
    
    # ranking index page
    html_dict_ranking_index = gen_ranking_index(rawrankings, player_dict, ranking_dict, ranking_cat_dict)
    htmlwrite.generate('rankings.html', webpage_output_location, html_dict_ranking_index, layout_dict)
    outputlog.generate("ranking index page created")
    # individual ranking date pages
    rank_helper_table = make_editions_table(ranking_cat_dict)
    for this_date in ranking_dict.keys():
        html_dict_indiv_date = gen_indiv_date_rank(rawrankings, player_dict, this_date, rank_helper_table, ranking_cat_dict)
        htmlwrite.generate(ranking_dict[this_date], webpage_output_location, html_dict_indiv_date, layout_dict)
    outputlog.generate("individual ranking pages created")
    
# 2) create ranking index page
def gen_ranking_index(rawrankings, player_dict, ranking_dict, ranking_cat_dict):
    classification_list = ['Fingers', 'Cues']
    discipline_list = ['Overall', 'Singles', 'Doubles']
    
    # make lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_subtitles = ['']*6
    list_of_tables_titles_href = ['']*6
    list_of_tables_subtitles_href = ['']*6
    
    for this_class in classification_list:
        for this_disc in discipline_list:
            summary_table = pandas.DataFrame(columns = ('Date', "#1", "#2", "#3", "#4", "#5"))
            summary_table_href = pandas.DataFrame(columns = ('Date', "#1", "#2", "#3", "#4", "#5"))
            display_top_x = 5
            if this_disc == 'Doubles':
                display_top_x = 3
                del summary_table['#4']
                del summary_table['#5']
                del summary_table_href['#4']
                del summary_table_href['#5']
            this_rank = rawrankings[(rawrankings['Classification']==this_class)
                                    & (rawrankings['Discipline']==this_disc)]
            # get list of dates
            date_list = list(set(this_rank['Structured Date']))
            date_list.sort(reverse=True) #most recent first
            for struc_date in date_list:
                rank_date = this_rank[this_rank['Structured Date']==struc_date]
                new_row = {} # passing new row as dictionary
                new_row_href = {}
                q1=list(rawrankings.columns)
                q2=q1.index('Date')
                formatted_date = rank_date.iloc[0,q2]
                new_row['Date'] = formatted_date
                rank_cat_id = formatted_date + ' ' + this_class + ' ' + this_disc
                new_row_href['Date'] = ranking_cat_dict[rank_cat_id]
                for r in range(1,display_top_x+1):
                    if len(rank_date[rank_date['Rank']==r])>0:
                        z=rank_date[rank_date['Rank']==r].index.values.astype(int)[0]
                        new_row['#'+str(r)] = rank_date.loc[z,'Player']
                        if rank_date.loc[z,'Player'] in player_dict:
                            new_row_href['#'+str(r)] = player_dict[rank_date.loc[z,'Player']]
                            #new_row_href['#'+str(r)] = ''
                        else:
                            new_row_href['#'+str(r)] = ''

                summary_table = summary_table.append(new_row, ignore_index=True)
                summary_table = summary_table.fillna('')
                summary_table_href = summary_table_href.append(new_row_href, ignore_index=True)
            
            list_of_tables_values += [summary_table]
            list_of_tables_href += [summary_table_href]
            list_of_tables_titles += [this_class + ': ' + this_disc]

    ## remaining list
    list_of_tables_titles_id = list_of_tables_titles
    
    ## page-nav items
    page_nav_dict = {'Fingers: Overall': 'Overall', 'Fingers: Singles': 'Singles', 'Fingers: Doubles': 'Doubles', 'Cues: Overall': 'Overall', 'Cues: Singles': 'Singles', 'Cues: Doubles': 'Doubles'}
    page_nav_table_layout = {'Fingers':['Fingers: Overall','Fingers: Singles','Fingers: Doubles'], 'Cues':['Cues: Overall','Cues: Singles','Cues: Doubles']}
    page_nav_table_layout = pandas.DataFrame(page_nav_table_layout, columns = ['Fingers','Cues'])
    page_nav_header_display = [1,1]
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - Ranking Index",
        'header-sub': 0,
        'page-heading': "Ranking Index",
        'sub-header': ['Included below are the CrokinoleCentre calculated player rankings across various categories.'],
        'description': ['A detailed explanation of the rankings formula is being developed.'],
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

# 3) create individual date ranking pages
def gen_indiv_date_rank(rawrankings, player_dict, this_date, rank_helper_table, ranking_cat_dict):
    categories_for_page = rank_helper_table[rank_helper_table['Date']==this_date]
    
    # initialize lists
    list_of_tables_values = []
    list_of_tables_href = []
    list_of_tables_titles = []
    list_of_tables_titles_id = []
    page_nav_dict = {}
    fingers_nav_display = 0
    cues_nav_display = 0
    fingers_nav_list = []
    cues_nav_list = []
    
    # loop through categories/disciplines
    for i in categories_for_page.index:
        this_cat = categories_for_page.loc[i, 'Category']
        this_disc = categories_for_page.loc[i, 'Discipline']
        x = rawrankings[(rawrankings['Date']==this_date)
                        & (rawrankings['Classification']==this_cat)
                        & (rawrankings['Discipline']==this_disc)]
        # sort by rank, then by rating for those unranked
        x = x.sort_values(by=['Rank', 'Rating'], ascending = [True, False])
        rank_table = x[['Rank', 'Player', 'Rating', 'Number Events', 'Number Games', 'Adj Number Games', 'Pts For','Pts Against','Pts %','Avg Opponent Rating','Avg Teammate Rating']]
        rank_table=rank_table.fillna('')
        # formatting the table for rounding
        rank_table['Rating'] = round(rank_table['Rating'],3)
        rank_table['Adj Number Games'] = round(rank_table['Adj Number Games'],1)
        rank_table['Pts For'] = round(rank_table['Pts For'],1)
        rank_table['Pts Against'] = round(rank_table['Pts Against'],1)
        rank_table['Pts %'] = round(rank_table['Pts %'],3)
        rank_table['Avg Opponent Rating'] = round(rank_table['Avg Opponent Rating'],0)
        rank_table['Avg Teammate Rating'] = round(rank_table['Avg Teammate Rating'],0)
        # make href table
        dict_href_columns = {'Player': 'Player Link'}
        rank_table_href = events.make_href_table(rank_table, x, dict_href_columns, 1)
        # make pag nav dict
        cat_id_long = this_cat+'-'+this_disc
        page_nav_dict[cat_id_long]=this_disc
        if this_cat == 'Fingers':
            fingers_nav_display = 1
            fingers_nav_list += [this_cat.lower()+'-'+this_disc.lower()]
        else:
            cues_nav_display = 1
            cues_nav_list += [this_cat.lower()+'-'+this_disc.lower()]
        
        ## update tables
        list_of_tables_values += [rank_table]
        list_of_tables_href += [rank_table_href]
        list_of_tables_titles += [this_cat+': '+this_disc]
        list_of_tables_titles_id += [this_cat.lower()+'-'+this_disc.lower()]
        
    # make lists
    n = len(list_of_tables_values)
    list_of_tables_subtitles = ['']*n
    list_of_tables_titles_href = ['']*n
    list_of_tables_subtitles_href = ['']*n
    
    n = max(len(cues_nav_list), len(fingers_nav_list))
    fingers_nav_list_extend = fingers_nav_list + ['']*(n-len(fingers_nav_list))
    cues_nav_list_extend = cues_nav_list + ['']*(n-len(cues_nav_list))
    
    ## page-nav items
    page_nav_dict = {'fingers-overall': 'Overall', 'fingers-singles': 'Singles', 'fingers-doubles': 'Doubles', 'cues-overall': 'Overall', 'cues-singles': 'Singles', 'cues-doubles': 'Doubles'}
    page_nav_table_layout = {'Fingers':fingers_nav_list_extend, 'Cues':cues_nav_list_extend}
    page_nav_table_layout = pandas.DataFrame(page_nav_table_layout, columns = ['Fingers','Cues'])
    page_nav_header_display = [fingers_nav_display,cues_nav_display]
    
    html_dict_event_index = {
        'meta-title': "Crokinole Reference - Rankings",
        'header-sub': 1,
        'page-heading': "CrokinoleCentre Ranking as of "+this_date,
        'sub-header': ['Included below are the CrokinoleCentre calculated player rankings across various categories.'
                       ,'Rankings are generated at the end of any month following an event being played.'],
        'description': ['A detailed explanation of the rankings formula is being developed.'],
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

# helper function to turn ranking cat dictionary into a table
def make_editions_table(ranking_cat_dict):
    ## reference table for number of editions and last edition
    editions_table = pandas.DataFrame(columns = ('Full name', 'Link', 'Page name', "Date", "Category", 'Discipline'))
    editions_table['Full name'] = ranking_cat_dict.keys()
    for i in editions_table.index:
        this_key = editions_table.loc[i, 'Full name']
        split_key = this_key.split(' ')
        editions_table.loc[i, 'Discipline'] = split_key[4]
        editions_table.loc[i, 'Category'] = split_key[3]
        editions_table.loc[i, 'Link'] = ranking_cat_dict[this_key]
        editions_table.loc[i, 'Date'] = split_key[0]+' '+split_key[1]+' '+split_key[2]
        editions_table.loc[i, 'Page name'] = 'rankings/'+split_key[0].lower()+'-'+split_key[1][:-1]+'-'+split_key[2]+'.html'

    return editions_table