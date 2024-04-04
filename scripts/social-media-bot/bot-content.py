import os
import random
import pandas as pd
from mastodon import Mastodon

## Function definitions; wrangle_data reused from content/resources/resource.py
def wrangle_data(df):
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

def pretty_types(in_lst):
    #print(in_lst)
    remove = ["Reading", "Primary Source"]
    in_lst = [i for i in in_lst if i not in remove]

    if len(in_lst) == 0:
        out_str = "Resource"
    elif len(in_lst) == 1:
        out_str = in_lst[0]
    elif len(in_lst) > 1:
        out_str = "/".join(in_lst)
    else:
        out_str = "$NULL"
    
    return(out_str)

def pretty_tags(in_lst):
    #print(in_lst)
    remove = ["Open Science"]
    in_lst = [i for i in in_lst if i not in remove]

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
    for i in range(len(in_lst)):
        if in_lst[i] == '':
            in_lst.remove('')
        elif in_lst[i] == "Open Data and Materials":
            in_lst[i] = "Open Data"
        elif in_lst[i] == "Reproducibility and Replicability Knowledge":
            in_lst[i] = "Reproducibility"
            in_lst.append("Replicability")

    if len(in_lst) == 0:
        out_str = ""
    else:
        out_str = " "
        for x in range(len(in_lst)-1):
            out_str = out_str + "#" + in_lst[x].replace(" ", "") + " "
        out_str = out_str + "#" + in_lst[len(in_lst)-1].replace(" ", "")

    
    return(out_str)

def pretty_levels(in_lst):
    for i in range(len(in_lst)):
        if in_lst[i].casefold().find("undergrad") != -1:
            in_lst[i] = "Undergraduate"
        #if in_lst[i].casefold().find("undergraduates"):
        #    in_lst[i] = "Undergraduate"
    
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

def main():

    FORRT_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgYcUP3ybhe4x05Xp4-GTf-Cn2snBCW8WOP_N7X-9r80AeCpFAGTfWn6ITtBk-haBkDqXAYXh9a_x4/pub?gid=1924034107&single=true&output=csv"
    FORRT_DF = pd.read_csv(FORRT_DB_URL)

    wrangle_data(FORRT_DF)

    # Generating the post
    i = random.randint(0, len(FORRT_DF))
    i = 794
    print(i)

    fields = [
        FORRT_DF["title"][i],
        FORRT_DF["material_type"][i],
        FORRT_DF["tags"][i],
        FORRT_DF["language"][i],
        FORRT_DF["education_level"][i],
        FORRT_DF["subject_areas"][i],
        FORRT_DF["link_to_resource"][i],
        FORRT_DF["FORRT_clusters"][i]
        ]

    #char_count(fields)


    lines = [
        "#FOERRT: " + fields[0],
        "This " + pretty_types(fields[1]) + " has been tagged with " + pretty_tags(fields[2]) + " and is available in " + pretty_plurals(fields[3]) + ".",
        "It's aimed at the " + pretty_levels(fields[4]) + " level in " + pretty_plurals(fields[5]) + ".",
        "You can find it here: " + fields[6],
        pretty_clusters(fields[7]) + "#OpenScience #OER"
    ]

    status = '\n\n'.join(lines)

    print(status)
    #mastodon = Mastodon(access_token = os.environ["TOKEN"], api_base_url = os.environ["URL"])
    #mastodon.status_post(status)

if __name__ == "__main__":
    main()