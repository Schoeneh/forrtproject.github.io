import os
import re
import random
import pandas as pd
from mastodon import Mastodon

## Function definitions; wrangle_data reused from content/resources/resource.py
def wrangle_data(df, rand_row):
    df = df.loc[[rand_row]]
    
    #Standardize column names
    df.columns = df.columns.str.lower()
    df.rename(columns = {df.columns[df.columns.str.contains(pat = 'title')][0]: "title",
                            df.columns[df.columns.str.contains(pat = 'material type')][0]: 'material_type',
                            df.columns[df.columns.str.contains(pat = 'user tags')][0]: 'tags',
                            df.columns[df.columns.str.contains(pat = 'lang')][0]: 'language',
                            df.columns[df.columns.str.contains(pat = 'education level')][0]: 'education_level',
                            df.columns[df.columns.str.contains(pat = 'subject areas')][0]: 'subject_areas',
                            df.columns[df.columns.str.contains(pat = 'url')][0]: 'link_to_resource',                           
                            df.columns[df.columns.str.contains(pat = 'clusters')][0]: 'FORRT_clusters'},
                inplace = True)
    df.fillna('', inplace=True)    

    #Splitting cells
    df['material_type'] = [[y.strip() for y in x.split(',')] for x in df['material_type'].values]
    df['education_level'] = [[y.strip() for y in x.split(',')] for x in df['education_level'].values]
    df['subject_areas'] = [[y.strip() for y in x.split(',')] for x in df['subject_areas'].values]
    df['FORRT_clusters'] = [[y.strip() for y in x.split(',')] for x in df['FORRT_clusters'].values]
    df['tags'] = [[y.strip() for y in x.split(',')] for x in df['tags'].values]
    df['language'] = [[y.strip() for y in x.split(',')] for x in df['language'].values]

    data = {
        'title': df['title'][rand_row],
        'material_type': df['material_type'][rand_row],
        'tags': df['tags'][rand_row],
        'language': df['language'][rand_row],
        'education_level': df['education_level'][rand_row],
        'subject_areas': df['subject_areas'][rand_row],
        'link_to_resource': df['link_to_resource'][rand_row],
        'FORRT_clusters': df['FORRT_clusters'][rand_row]
        }
    return data

def gen_link(data, rand_row):
    filename = re.sub('[\W_]+', '-', data['title'].lower())
    filename = re.sub('^-', '', filename)
    filename = re.sub('-$', '', filename[:40])

    link = "https://forrt.org/curated_resources/" + str(rand_row) + "_" + filename

    return(link)

def prettify(data):
    #Removing empty values
    for value in data.values():
        for item in range(len(value)):
            if value[item] == '':
                value.remove('')

    #Removing certain material types
    remove_types = ["Reading", "Primary Source", "R Code", "Interactive"]
    data['material_type'] = [i for i in data['material_type'] if i not in remove_types]
    if len(data['material_type']) == 0:
        data['material_type'].append("Resource")
    
    #Removing certain user tags
    remove_tags = ["Open Science"] #redundant, see static text in main
    data['tags'] = [i for i in data['tags'] if i not in remove_tags]

    #Changing certain FORRT clusters, for better readability
    for item in range(len(data['FORRT_clusters'])):
        if data['FORRT_clusters'][item] == "Open Data and Materials":
            data['FORRT_clusters'][item] = "Open Data"
        elif data['FORRT_clusters'][item] == "Reproducibility and Replicability Knowledge":
            data['FORRT_clusters'][item] = "Reproducibility"
            data['FORRT_clusters'][item].append("Replicability")

    #Changing certain education levels, for better readability
    for item in range(len(data['education_level'])):
        if data['education_level'][item].casefold().find("undergrad") != -1:
            data['education_level'][item] = "Undergraduate"
        elif data['education_level'][item].casefold().find("professional") != -1:
            data['education_level'][item] = "Graduate/Professional"
        elif data['education_level'][item].casefold().find("career") != -1:
            data['education_level'][item] = "Career/Technical"
        elif data['education_level'][item].casefold().find("adult") != -1:
            data['education_level'][item] = "Adult-Education"
    
    return data

def pretty_types(in_lst):
    if len(in_lst) == 1:
        out_str = in_lst[0]
    elif len(in_lst) > 1:
        out_str = " / ".join(in_lst)
    else:
        out_str = ""
    
    return(out_str)

def pretty_tags(in_lst):
    if len(in_lst) == 0:
        out_str = ""
    elif len(in_lst) == 1:
        out_str = '\''+in_lst[0]+'\''
    elif len(in_lst) > 1:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + '\'' + in_lst[x] + '\', '
        out_str = out_str + 'and \'' + in_lst[len(in_lst)-1] + '\''
    
    out_str = out_str.replace(", and", " and")
    return(out_str)

def pretty_clusters(in_lst):
    if len(in_lst) == 0:
        out_str = ""
    else:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + "#" + in_lst[x].replace(" ", "") + " "
        out_str = out_str + "#" + in_lst[len(in_lst)-1].replace(" ", "") + " "

    return(out_str)

def pretty_plurals(in_lst):
    #print(in_lst)
    if len(in_lst) == 1:
        out_str = in_lst[0]
    elif len(in_lst) > 1:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + in_lst[x] + ", "
        out_str = out_str + "and " + in_lst[len(in_lst)-1]
    else:
        out_str = ""
    
    out_str = out_str.replace(", and", " and")
    return(out_str)

def char_count(data):

    char_count = [
        125, #characters in static text
        len(data['title']),
        len(pretty_types(data['material_type'])),
        len(pretty_tags(data['tags'])),
        len(pretty_plurals(data['language'])),
        len(pretty_plurals(data['education_level'])),
        len(pretty_plurals(data['subject_areas'])),
        23, #characters in url, see https://github.com/mastodon/mastodon/pull/4427
        len(pretty_clusters(data['FORRT_clusters']))
    ]
    if sum(char_count) > 500:
        if len(data['tags']) > 3: #more than 3 tags
            data['tags'] = [data['tags'][0], data['tags'][1], data['tags'][2], "..."]
            char_count[3] = len(pretty_tags(data['tags']))
    
    if sum(char_count) > 500:
        if len(data['title']) > 100: #title with more than 100 characters
            data['title'] = data['title'][:100] + "[...]"
            char_count[1] = 100

    print(char_count)
    print(sum(char_count))
    return data

def main():

    FORRT_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgYcUP3ybhe4x05Xp4-GTf-Cn2snBCW8WOP_N7X-9r80AeCpFAGTfWn6ITtBk-haBkDqXAYXh9a_x4/pub?gid=1924034107&single=true&output=csv"
    FORRT_DF = pd.read_csv(FORRT_DB_URL)

    rand_row = random.randint(0, len(FORRT_DF))
    #rand_row = 12 #+2 to get row in table

    data = wrangle_data(FORRT_DF, rand_row)
    data = prettify(data)


    # Generating the post
    data = char_count(data)

    #Dealing with multiple elements in a field
    str_type = pretty_types(data['material_type'])
    str_tags = pretty_tags(data['tags'])
    str_lang = pretty_plurals(data['language'])
    str_educ = pretty_plurals(data['education_level'])
    str_subj = pretty_plurals(data['subject_areas'])
    str_clus = pretty_clusters(data['FORRT_clusters'])

    #line 1 (title)
    line1 = "#FOERRT: " + data["title"]

    #line 2 (type, tags, language)
    line2 = [
        "This " + str_type,
        "",
        " is available in " + str_lang + "."
    ]
    if len(data['tags']) >= 1:
        line2[1] = " has been tagged with " + str_tags + " and"
    line2 = "".join(line2)

    #line 3 (education level, subject area)
    line3 = [
        "",
    	" in " + str_subj + "."
    ]
    if len(data['education_level']) == 1:
        line3[0] = "It's aimed at the " + str_educ + " level"
    else:
        line3[0] = "It's aimed at the " + str_educ + " levels"
    line3 = "".join(line3)

    #line 4 (link)
    line4 = "You can find it here: " + gen_link(data, rand_row)

    #line 5 (FORRT clusters as hashtags)
    line5 = str_clus + "#OpenScience #OER"

    #Joining lines to whole status
    lines = [line1, line2, line3, line4, line5]
    status = '\n\n'.join(lines)

    print("---")
    print(status)
    print(len(status))
    mastodon = Mastodon(access_token = os.environ["TOKEN"], api_base_url = os.environ["URL"])
    mastodon.status_post(status)

if __name__ == "__main__":
    main()