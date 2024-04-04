import os
import random
import pandas as pd
from mastodon import Mastodon

## Function definitions; wrangle_data reused from content/resources/resource.py
def wrangle_data(df):
    rand_row = random.randint(0, len(df))
    #rand_row = 9 #+2 to get row in table

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

def prettify(data):
    #Removing empty values
    for value in data.values():
        for item in range(len(value)):
            if value[item] == '':
                value.remove('')

    #Removing certain material types
    remove_types = ["Reading", "Primary Source", "R Code"]
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
        out_str = "/".join(in_lst)
    else:
        out_str = "$NULL"
    
    return(out_str)

def pretty_tags(in_lst):
    #print(in_lst)

    if len(in_lst) == 0:
        out_str = "$NULL"
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

def pretty_levels(in_lst):    
    if len(in_lst) == 1:
        out_str = in_lst[0]
    elif len(in_lst) > 1:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + in_lst[x] + ", "
        out_str = out_str + "and " + in_lst[len(in_lst)-1]
    else:
        out_str = "$NULL"
    
    out_str = out_str.replace(", and", " and")
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
        out_str = "$NULL"
    
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
    sum(char_count)

    print(char_count)
    print(sum(char_count))
    return char_count

def main():

    FORRT_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgYcUP3ybhe4x05Xp4-GTf-Cn2snBCW8WOP_N7X-9r80AeCpFAGTfWn6ITtBk-haBkDqXAYXh9a_x4/pub?gid=1924034107&single=true&output=csv"
    FORRT_DF = pd.read_csv(FORRT_DB_URL)

    data = wrangle_data(FORRT_DF)
    data = prettify(data)

    # Generating the post
    char_count(data)

    lines = [
        "#FOERRT: " + data["title"],
        "This " + pretty_types(data["material_type"]) + " has been tagged with " + pretty_tags(data["tags"]) + " and is available in " + pretty_plurals(data["language"]) + ".",
        "It's aimed at the " + pretty_levels(data["education_level"]) + " level in " + pretty_plurals(data["subject_areas"]) + ".",
        "You can find it here: " + data["link_to_resource"],
        pretty_clusters(data["FORRT_clusters"]) + "#OpenScience #OER"
    ]

    status = '\n\n'.join(lines)

    print("---")
    print(status)
    #mastodon = Mastodon(access_token = os.environ["TOKEN"], api_base_url = os.environ["URL"])
    #mastodon.status_post(status)

if __name__ == "__main__":
    main()