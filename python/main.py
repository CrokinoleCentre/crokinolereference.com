# Crokinole Reference - Script to Generate webpages
### Note CSS pages are not involved

## Main script
### 1) Lists all inputs and outputs 
### 2) imports all necessary functions and data
### 3) creates global dictionaries
### 4) Runs code to generate webpages

# Perform input check before running

## 1) a) inputs
import os
path = os.getcwd()
parent_path = os.path.abspath(os.path.join(path, os.pardir))
input_location = parent_path + '/inputs/'
results_name = input_location + 'All Crokinole Results.xlsx'
matches_name = input_location + 'Crokinole Match Detail.xlsx'
rankings_name = input_location + 'Rankings BT Python.xlsx'
shell_html = parent_path + '/shell/'

## 1) b) output (script creates this folder)
webpage_output_location = parent_path + '/crokinolereference.com/'

## 2) a) import scripts
import excelimport 
import players
import outputlog
import events
import htmlwrite
import rankings
import leagues
import records
import index
import contribute
import shutil

## 2) b) import excel files and transform to aid later work
outputlog.generate("script started")

rawleagues = excelimport.import_excel(results_name, "Leagues")
rawmapping = excelimport.import_excel(results_name, "Mapping")

rawresults = excelimport.generate_results(results_name, "Results")
rawmatches = excelimport.generate_matches(matches_name, "Matches")
rawrankings = excelimport.generate_rankings(rankings_name, "Rankings")

outputlog.generate("import of excel files complete")

## 3) Global dictionaries - contain data that will be used in other scripts
layout_dict = htmlwrite.layout_dict() #header and meta info for html pages
player_dict = players.gen_player_dict(rawresults) #full name, page link
events_dict = events.gen_event_dict(rawresults)
events_dict_div_format = events.gen_event_dict_div_format(rawresults)
events_mapping_dict = events.gen_event_mapping_dict(rawmapping)
ranking_dict = rankings.gen_ranking_dict(rawrankings) # key is date, link to that page
ranking_cat_dict = rankings.gen_ranking_cat_dict(rawrankings) # key is date+category, link to that page and #href to id
league_dict = leagues.gen_league_dict(rawleagues)
league_year_cat_dict = leagues.gen_league_dict_cat_year(rawleagues)

outputlog.generate("creation of dictionaries complete")

## 4) Run code - all functions are generating their own webpages
### 4a) copy contents of shell into output folder
shutil.copytree(shell_html, webpage_output_location)
### 4b) scripts to generate pages
players.generate(rawresults, rawmatches, rawrankings, player_dict, events_dict_div_format, ranking_cat_dict, league_year_cat_dict, webpage_output_location, layout_dict)
events.generate(rawresults, rawmatches, player_dict, events_dict, events_dict_div_format, events_mapping_dict, webpage_output_location, layout_dict)
rankings.generate(rawrankings, player_dict, ranking_dict, ranking_cat_dict, webpage_output_location, layout_dict)
leagues.generate(rawresults, rawleagues, player_dict, events_dict_div_format, league_dict, league_year_cat_dict, webpage_output_location, layout_dict)
records.generate(rawresults, rawmatches, rawleagues, events_dict, events_dict_div_format, league_dict, player_dict, webpage_output_location, layout_dict)
index.generate(rawresults, rawrankings, rawleagues, player_dict, events_dict, league_dict, league_year_cat_dict, events_dict_div_format, ranking_cat_dict, webpage_output_location, layout_dict)
contribute.generate(webpage_output_location, layout_dict)
outputlog.generate("crokinole reference script complete")