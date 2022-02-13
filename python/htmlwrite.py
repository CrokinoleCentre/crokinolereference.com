# Crokinole Reference - Script to Generate webpages

## html writer
### create html page with the following inputs:
    ## filename: 'players.html'
    ## location: webpage_output_location + 'players/'
    ## info is a dictionary of the form:
        ## 'meta-title': "Crokinole Reference - Player Index"
        ## 'header-sub': 0, number indicates how many subfolders we are in for header info to back out of for navigation links
            # number
        ## 'page-heading': "Player Index",
            # short string
        ## 'sub-header': "",
            # list of strings, each new item is a line break, item 1 is <h1>
            # appending strings to list will be variable
            # this can be an empty list
        ## 'description': "",
            # similar to sub-header format
            # this can be an empty list
        ## 'page-nav-dict': ,
            # dictionary to map href id to name visible in page_nav table
            # keys are the href id, values are the display
            # this can be empty
        ## 'page-nav-table-layout: ,
            # table layout of page_nav by id
            # values in table correspond to keys of dictionary
            # this can be empty
        ## 'page-nav-header-display': ,
            # list of binary results, 1 indicates to display header in page_nav table
            # this can be empty
        ## 'detail-values': list_of_tables
        ## 'detail-href
            # both are lists
            # values is the formatted values tables
            # href is same format with applicable href links
        ## 'detail-titles'
            # list, table titles
        ## 'detail-subtitles'
            # list, table subtitles
            # if empty string, then html code should be nothing
        ## 'detail-titles-href': 
        ## 'detail-titles-id': 
        ## 'detail-subtitles-href':
            # all are lists for href or id tags of titles/subtitles
        ## 'detail-column-number': number
            # number of tables side by side (css is setup to use any number from 1 to 4)
        ## table-sort: if set =1 then sorting is added to each table of the page
        ## to_top_remove: if set =1 then "to top" links are excluded from the page

# crokinole reference scripts
import excelimport
# python scripts
import numpy

### import the layout file once so it isn't called numerous times
def layout_dict():
    ### input the common layout file
    layout_file = 'layout.xlsx'
    ##### input common layout
    footer_layout = excelimport.import_excel(layout_file, "footer")
    meta_layout = excelimport.import_excel(layout_file, "meta")
    header_layout = excelimport.import_excel(layout_file, "header")
    header_sub1_layout = excelimport.import_excel(layout_file, "header-sub1")
    table_sort_layout = excelimport.import_excel(layout_file, "table-sort")
    
    layout_dict = {}
    layout_dict['footer_layout'] = footer_layout
    layout_dict['meta_layout'] = meta_layout
    layout_dict['header_layout'] = header_layout
    layout_dict['header_sub1_layout'] = header_sub1_layout
    layout_dict['table-sort'] = table_sort_layout
    
    return layout_dict
    

### main function
def generate(filename, location, info, layout_dict):
    ##### input common layout
    footer_layout = layout_dict['footer_layout']
    meta_layout = layout_dict['meta_layout']
    header_layout = layout_dict['header_layout']
    header_sub1_layout = layout_dict['header_sub1_layout']
    table_sort_layout = layout_dict['table-sort']
    
    ## meta text
    meta_str=meta_layout.to_string(index = False)
    table_sort_str=table_sort_layout.to_string(index = False)
    if 'table-sort' in info:
        if info['table-sort'] == 1:
            meta = meta_str +"\n"+ '<title>' + info['meta-title'] + '</title>' +"\n"+ table_sort_str
    else:
        meta = meta_str +"\n"+ '<title>' + info['meta-title'] + '</title>'
    
    ## header html text
        # read in from excel - IF statement
    if info['header-sub'] == 0:
        header = header_layout
    elif info["header-sub"] == 1:
        header = header_sub1_layout
    else:
        header = header_layout
    header=header.to_string(index = False)
    
    ## page header
    x = info['page-heading']
    page_heading = '<div id="top" class="page-heading">' + x + '</div>'
    
    ## sub header
    x = info['sub-header']
    if len(x) == 0:
        sub_header = ''
    else:
        sub_header = ''
        for i in range(len(x)):
            if i==0:
                sub_header = sub_header + '<div class="sub-heading"> <h1>' + x[0] + '</h1>'
            else:
                sub_header = sub_header + x[i] + '</br>'
        sub_header = sub_header + '</div>'
    
    ## description
    x = info['description']
    if len(x) == 0:
        description = ''
    else:
        description = ''
        for i in range(len(x)):
            if i==0:
                description = description + '<div class="description"> <p>' + x[0]
            else:
                description = description + '</br>' + x[i]
        description = description + '</p></div>'
    
    ## page nav
    page_nav = page_nav_href(info['page-nav-dict'], info['page-nav-table-layout'], info['page-nav-header-display'])
    
    ## detail
    # inputs
    list_of_tables_values = info['detail-values']
    list_of_tables_href = info['detail-href']
    list_of_tables_titles = info['detail-titles']
    list_of_tables_subtitles = info['detail-subtitles']
    list_of_tables_titles_href = info['detail-titles-href']
    list_of_tables_titles_id = info['detail-titles-id']
    list_of_tables_subtitles_href = info['detail-subtitles-href']
    column_number = info['detail-column-number']
    to_top_remove = 0
    if 'to_top_remove' in info:
        to_top_remove = info['to_top_remove']
    table_sort_indicator = 0
    if 'table-sort' in info:
        table_sort_indicator = info['table-sort']
    # detail code
    detail_start = '<div class="detail">'
    detail_end = '</div>'
    detail_middle = ''
    # loop through lists to populate the middle section
    detail_middle = detail_all_tables(list_of_tables_values, list_of_tables_href, list_of_tables_titles, column_number, list_of_tables_subtitles, list_of_tables_titles_href, list_of_tables_titles_id, list_of_tables_subtitles_href, to_top_remove, table_sort_indicator)
    
    detail = detail_start +"\n" + detail_middle +"\n" + detail_end
    
    ## footer
        # read in from excel
    footer = footer_layout
    footer=footer.to_string(index = False)
    
    html_code = meta +"\n" + header +"\n" + page_heading +"\n" + sub_header +"\n" + description +"\n" + page_nav +"\n" + detail +"\n" + footer
    
    #final part
    write_html(filename, location, html_code)



### Helper Functions

## loop through detail lists of tables to form the html code of the detail section
def detail_all_tables(list_of_tables_values, list_of_tables_href, list_of_tables_titles, column_number, list_of_tables_subtitles, list_of_tables_titles_href, list_of_tables_titles_id, list_of_tables_subtitles_href, to_top_remove, table_sort_indicator):
    detail_all_tables = ''
    # column class name
    column_class_name = 'column'+str(column_number)
    for i in range(len(list_of_tables_values)):
        this_table_start = ''
        this_table_end = ''
        top_link_ind = 0
        # add row class if new row of tables and to_top_remove is 0
        if ((i % column_number) == 0):
            this_table_start = '<div class="row">'
            top_link_ind = 1*(1 - to_top_remove) #add to top button if table is first of new row
        if ((i+1) % column_number) == 0: #add the ending div tag for the row class if it's the last table in the row
            this_table_end = '</div>'
        # add the column class
        this_table_start = this_table_start +"\n"+ '<div class="'+column_class_name+'">'
        this_table_end = '</div>' +"\n"+ this_table_end
        
        # helper function to get middle table section
        values = list_of_tables_values[i]
        href = list_of_tables_href[i]
        title = list_of_tables_titles[i]
        subtitle = list_of_tables_subtitles[i]
        title_href = list_of_tables_titles_href[i]
        title_id = list_of_tables_titles_id[i]
        subtitle_href = list_of_tables_subtitles_href[i]
        this_table_mid = code_this_table(values, href, title, subtitle, title_href, title_id, subtitle_href, top_link_ind, table_sort_indicator)
        
        detail_this_table = this_table_start +"\n"+ this_table_mid +"\n"+ this_table_end
        
        #save results to outer variable
        detail_all_tables = detail_all_tables + detail_this_table
        
    return detail_all_tables

## output the html code for one table
def code_this_table(values, href, title, subtitle, title_href, title_id, subtitle_href, top_link_ind, table_sort_indicator):
    # 1) table title
    c_title_id = ' '
    c_title_href = ''
    c_atag_open1 = ''
    c_atag_open2 = ''
    c_atag_close = ''
    top_link = ''
    if title_href != '':
        c_atag_open1 = '<a '
        c_title_href = 'href="' + title_href + '"'
        c_atag_open2 = '>'
        c_atag_close = '</a>'
    if title_id != '':
        c_title_id = ' id="' + title_id + '"'
    if top_link_ind == 1:
        top_link = '<a href="#top" class="toplink">to top</a>'
    c_title = '<h2' + c_title_id + '>' + c_atag_open1 + c_title_href + c_atag_open2 + title + c_atag_close + top_link + '</h2>'
    
    # 2) subtitle and table sort box
    ## should be blank if not being used
    c_subtitle_href = ''
    c_atag_open1 = ''
    c_atag_open2 = ''
    c_atag_close = ''
    if subtitle_href != '':
        c_atag_open1 = '<a '
        c_subtitle_href = 'href="' + subtitle_href + '"'
        c_atag_open2 = '>'
        c_atag_close = '</a>'
    c_table_sort_input = ''
    if table_sort_indicator == 1:
        c_table_sort_input = "\n"+ 'Use input box to search<br/>' +"\n"+ '<input id="InputBox" type="text" placeholder="Search..">'
    c_subtitle = '<h3>' + c_atag_open1 + c_subtitle_href + c_atag_open2 + subtitle + c_atag_close + '</h3>' + c_table_sort_input
    
    # 3) table code
    ## 3a) header row - no href values
    header_row = table_code_one_row('th', values.columns, 0, '')
    ## 3b) table sort rows - add tbody tag
    sort_start = ''
    sort_end = ''
    if table_sort_indicator == 1:
        sort_start = '<tbody id="TableToSort">'
        sort_end = '</tbody>'
    ## 3c) body rows
    body_rows = ''
    for i in range(len(values)):
        this_row = table_code_one_row('td', values.iloc[i], 1, href.iloc[i])
        body_rows = body_rows +"\n"+ this_row
    
    
    c_table = '<table>' +"\n"+ header_row +"\n"+sort_start+"\n"+ body_rows +"\n"+ sort_end+"\n"+ '</table>'
    
    this_table_mid = c_title +"\n"+ c_subtitle +"\n"+ c_table
    return this_table_mid

## input cell tag, one row of values, one row of href
## output the html code for that one row
## href indicator (0 no, 1 yes) says if href should be looked at
def table_code_one_row(celltag, row_values, href_indicator, row_href):
    start = '<tr>'
    end = '</tr>'
    mid = ''
    if not isinstance(row_values[0], (int, float, numpy.int64)):
        if (len(row_values[0])>8) & (row_values[0][0:8] == 'Colspan!'): #colspan row
            if row_values[0][8] == '*': #modified colspan
                num_cells_to_span = int(row_values[0][9:11])
                section_name = row_values[0][11:]
                mid = '<' + celltag + ' class="sectionbreak" colspan="' + str(num_cells_to_span) + '">' + section_name + '</' + celltag + '>'
                ## now add remaining cells to fill out table
                for i in range(num_cells_to_span,len(row_values)):
                    cell_value = row_values[i]
                    if href_indicator==1:
                        if row_href[i]=='':
                            value_and_href = cell_value
                        else: 
                            value_and_href = '<a href="'+ str(row_href[i])+'">' + str(cell_value) + '</a>'
                    else:
                        value_and_href = row_values[i]
                    cell = '<' + celltag + ' class="sectionbreak"' + '>' + str(value_and_href) +'</' + celltag + '>'
                    mid = mid + cell
            else: # standard colspan
                num_cells_to_span = len(row_values)
                section_name = row_values[0][8:] 
                mid = '<' + celltag + ' class="sectionbreak" colspan="' + str(num_cells_to_span) + '">' + section_name + '</' + celltag + '>'
        else: #not a colspan row
            for i in range(len(row_values)):
                if '.0' in str(row_values[i]): #remove if whole number
                    cell_value = str(row_values[i])[:-2]
                else:
                    cell_value = row_values[i]
                if href_indicator==1:
                    if row_href[i]=='':
                        value_and_href = cell_value
                    else: 
                        value_and_href = '<a href="'+ str(row_href[i])+'">' + str(cell_value) + '</a>'
                else:
                    value_and_href = row_values[i]
                cell = '<' + celltag + '>' + str(value_and_href) +'</' + celltag + '>'
                mid = mid + cell
    else: #not a colspan row
        for i in range(len(row_values)):
            if '.0' in str(row_values[i]): #remove if whole number
                cell_value = str(row_values[i])[:-2]
            else:
                cell_value = row_values[i]
            if href_indicator==1:
                if row_href[i]=='':
                    value_and_href = cell_value
                else: 
                    value_and_href = '<a href="'+ str(row_href[i])+'">' + str(cell_value) + '</a>'
            else:
                value_and_href = row_values[i]
            cell = '<' + celltag + '>' + str(value_and_href) +'</' + celltag + '>'
            mid = mid + cell
    
    this_row = start + mid + end
    return this_row

## generate page_nav html in string format
### input: dictionary of page nav, table layout, header display indicators
### output: table of desired grid layout of <a> tags with href links
##### if dict is empty, return empty string
def page_nav_href(page_nav_dict, page_nav_table_layout, page_nav_header_display):
    if bool(page_nav_dict):
        # initial code
        page_nav = '<div class="page-navigation">Jump to:<ul class="grid">' +'\n'
        # loop through columns of table
        for i in range(len(page_nav_table_layout.columns)):
            colname = page_nav_table_layout.columns[i]
            vector = page_nav_table_layout[colname].values
            #column header
            row_li = '<li>'
            if page_nav_header_display[i] == 1:
                #add column name
                row_li = row_li + colname + '<ul>'
            else:
                #don't add column name, add break to take up row space
                row_li = row_li + '</br><ul>'
            #row by row code
            for j in range(len(vector)):
                id_tag = vector[j]
                if len(id_tag) > 0:
                    display_tag = page_nav_dict[id_tag]
                    sub_row_li = '<li><a href="#' + id_tag + '">' + display_tag + '</a></li>'
                else:
                    sub_row_li = '<li></li>'
                
                row_li = row_li +'\n' + sub_row_li
            
            #ending tags for row
            row_li = row_li + '</ul></li>' +'\n'
            
            page_nav = page_nav + row_li
            
        
        # ending code
        page_nav = page_nav + '</ul></div>'
    
    else: #dictionary is empty, so return empty string so page_nav is not populated
        page_nav = ''
     
    return page_nav

#### write [text] to html file called [filename] and saved in [subfolder]
    ## blank subfolder if it appears in main folder (not working)
    ## NOTE - location has to exist
def write_html(filename, subfolder, html):
    filepath = subfolder + filename
    html_file = open(filepath, 'w')
    html_file.write(html)
    html_file.close

###### example data
## new line in text so can read html file easier in debugging
#filename = 'test.html'
#line1 = "<html>"
#line2 = "\n" + "<h1>Yo this is the title</h1>"
#line3 = "\n" + "</html>"
#text = line1 + line2 + line3
#subfolder = "testsubfolder/"
#write_html(filename, subfolder, text)
## end of example data