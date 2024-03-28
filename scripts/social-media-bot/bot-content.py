import pandas as pd

# Getting the whole database as a DataFrame-object
data = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgYcUP3ybhe4x05Xp4-GTf-Cn2snBCW8WOP_N7X-9r80AeCpFAGTfWn6ITtBk-haBkDqXAYXh9a_x4/pub?gid=1924034107&single=true&output=csv"
df = pd.read_csv(data)


#Standardize column names; code reused from content/resources/resource.py
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

#Splitting cells; code reused from content/resources/resource.py
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
        out_str = "\'"+in_lst[0]+"\'"
    elif len(in_lst) > 1:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + "\'" + in_lst[x] + "\', "
        out_str = out_str + "and \'" + in_lst[len(in_lst)-1] + "\'"
    
    return(out_str)

def pretty_clusters(in_lst):
    for i in range(len(in_lst)):
        if in_lst[i] == "Open Data and Materials":
            in_lst[i] = "Open Data"

    if len(in_lst) == 0:
        out_str = "$NULL"
    else:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + "#" + in_lst[x].replace(" ", "") + " "
        out_str = out_str + "#" + in_lst[len(in_lst)-1].replace(" ", "")

    return(out_str)

def pretty_levels(in_lst):
    for i in range(len(in_lst)):
        if in_lst[i].casefold().contains("undergrad"):
            in_lst[i] = "Undergraduate"
        if in_lst[i].casefold().contains(undergraduates):
            in_lst[i] = "Undergraduate"
    
    if len(in_lst) == 1:
        out_str = in_lst[0]
    elif len(in_lst) > 1:
        out_str = ""
        for x in range(len(in_lst)-1):
            out_str = out_str + in_lst[x] + ", "
        out_str = out_str + "and " + in_lst[len(in_lst)-1]
    else:
        out_str = "$NULL"
    
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
    
    return(out_str)


# Generating the post
for i in range(1):

    str_title = df["title"][i]
    lst_type = df["material_type"][i]
    lst_tags = df["tags"][i]
    lst_language = df["language"][i]
    lst_educationLevel = df["education_level"][i]
    lst_subjectAreas = df["subject_areas"][i]
    str_url = df["link_to_resource"][i]
    lst_clusters = df["FORRT_clusters"][i]

    
    char_count = {
        "static text": 126,
        "title": len(str_title),
        "type": len(pretty_types(lst_type)),
        "user tags": len(pretty_tags(lst_tags)),
        "language": len(pretty_plurals(lst_language)),
        "education level": len(pretty_plurals(lst_educationLevel)),
        "subject areas": len(pretty_plurals(lst_subjectAreas)),
        "url": 23, #See https://github.com/mastodon/mastodon/pull/4427
        "clusters": len(pretty_clusters(lst_clusters))}

    parts = [
        "#FOERRT: " + str_title,
        "This " + pretty_types(lst_type) + " has been tagged with " + pretty_tags(lst_tags) + " and is available in " + pretty_plurals(lst_language) + ".",
        "It's aimed at the " + pretty_plurals(lst_educationLevel) + " level in " + pretty_plurals(lst_subjectAreas) + ".",
        "You can find it here: " + str_url,
        pretty_clusters(lst_clusters) + " #OpenScience #OER"
    ]

    post = "\n".join(parts)
    print(post)
    #print(sum(char_count.values()))
    #print(char_count)
    #print("---")

'''
char_count_avg = {}
title_len = []
type_len = []
userTags_len = []
language_len = []
educationLevel_len = []
subjectAreas_len = []
url_len = [23] #See https://github.com/mastodon/mastodon/pull/4427
clusters_len = []

for i in range(len(df)):
    title_len.append(len(df["title"][i]))
    type_len.append(len(df["type"][i]))
    userTags_len.append(len(df["user tags"][i]))
    language_len.append(len(df["language"][i]))
    educationLevel_len.append(len(df["education level"][i]))
    subjectAreas_len.append(len(df["subject areas"][i]))
    clusters_len.append(len(df["clusters"][i]))

char_count_avg = {
    "static text": 151,
    "title": sum(title_len) / len(title_len),
    "type": sum(type_len) / len(type_len),
    "userTags": sum(userTags_len) / len(userTags_len),
    "language": sum(language_len) / len(language_len),
    "educationLevel": sum(educationLevel_len) / len(educationLevel_len),
    "subjectAreas": sum(subjectAreas_len) / len(subjectAreas_len),
    "url": 23,
    "clusters": sum(clusters_len) / len(clusters_len)
}

print("---")
print("---")
print(sum(char_count_avg.values()))
print(char_count_avg)
'''