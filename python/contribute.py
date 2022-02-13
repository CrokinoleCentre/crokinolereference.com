# Crokinole Reference - Script to Generate webpages

## Generate contribution page
    
# other crokinole reference scripts
import outputlog
import htmlwrite

# Main)
def generate(webpage_output_location, layout_dict):
    html_dict_index = gen_contrib_dict()
    link = 'contribute.html'
    htmlwrite.generate(link, webpage_output_location, html_dict_index, layout_dict)
    outputlog.generate("contribute page created")
    
# generate html index dictionary
def gen_contrib_dict():
    
    html_dict_index = {
        'meta-title': "Crokinole Reference - Contribute Results",
        'header-sub': 0,
        'page-heading': 'Contribute Results to Crokinole Reference',
        'sub-header': [],
        'description': ['This website was designed to include results from competitive crokinole events from all over the world, and from any decade.'
                        ,"At this website's inception the majority of results are those from NCA events and other events in Ontario, Canada. Even for the tournament results included on this site, numerous currently have incomplete results." 
                        ,''
                        ,"It is desired to both expand the breadth of results available by adding info from more tournaments, and expand the depth of info by improving the quality of results for existing tournaments. "
                        ,'Scan the available <b><a href="events.html">events</a></b> to see what results currently exist.'
                        ,''
                        ,'<b>How to Contribute to Crokinole Reference</b>'
                        ,'1. Download the example <b><a href="Database Input.xlsx">database input</a></b> file.'
                        ,'2. Follow the format of the input to submit full or partial data. This may include individual match results, round-by-round tournament scores, or simply the final ranking of the event.'
                        ,'Note that the data in the example corresponds to what you can see for the <b><a href="events/owen-sound-nov-23-2013-competitive-fingers-singles.html">2013 Owen Sound event</a></b> and the <b><a href="events/wcc-jun-07-2014-competitive-fingers-doubles.html">2014 WCC Doubles H2H Matches</a></b>, so feel free to review what the inputted data will transform to when listed on this site.'
                        ,'3. Finally submit the completed file via email to <b>crokinolecentre@gmail.com.</b>'
                        ,''
                        ,'Note that all data is subject to review and secondary validation before being included in the database.'],
        'page-nav-dict': {},
        'page-nav-table-layout': '',
        'page-nav-header-display': '',
        'detail-values': [],
        'detail-href': [],
        'detail-titles': [],
        'detail-subtitles': [],
        'detail-titles-href': [],
        'detail-titles-id': [],
        'detail-subtitles-href': [],
        'detail-column-number': 1,
        'to_top_remove': 1 #only add when needed, 1 to not list "to top" link on page
        }
    
    return html_dict_index
