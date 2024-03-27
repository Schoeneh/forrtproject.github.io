import pandas as pd

# Getting the whole database as a DataFrame-object
data = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgYcUP3ybhe4x05Xp4-GTf-Cn2snBCW8WOP_N7X-9r80AeCpFAGTfWn6ITtBk-haBkDqXAYXh9a_x4/pub?gid=1924034107&single=true&output=csv"
df = pd.read_csv(data)

# Keeping only the columns needed for the post
columns = [col for col in df.columns]
columns_needed = ["title", "type", "user tags", "language", "education level", "subject areas", "url", "clusters"]
columns_to_keep = []

## Future-proofing: names and ordering might change; casefold() for case-insensitive matching of substring in string
for element in columns_needed:
    for col in columns:
        if element.casefold() in col.casefold():
            columns_to_keep.append(col)

df = df[columns_to_keep]
## Renaming the columns to the ones defined above (columns_needed)
df.columns = columns_needed

## Replacing all NaN (float) with an empty string
df.fillna("", inplace=True)

# Generating the post
for i in range(1):

    str_title = df["title"][i]

    str_type = df["type"][i]
    str_type = ",".join(str_type.split(","))


    str_userTags = df["user tags"][i]
    str_language = df["language"][i]
    str_educationLevel = df["education level"][i]
    str_subjectAreas = df["subject areas"][i]
    str_url = df["url"][i]
    str_clusters = df["clusters"][i]

    char_count = {
        "static text": 151,
        "title": len(df["title"][i]),
        "type": len(df["type"][i]),
        "user tags": len(df["user tags"][i]),
        "language": len(df["language"][i]),
        "education level": len(df["education level"][i]),
        "subject areas": len(df["subject areas"][i]),
        "url": 23, #See https://github.com/mastodon/mastodon/pull/4427
        "clusters": len(df["clusters"][i])}

    parts = [
        "Suggestion No. "+ str(i)+": "+str_title,
        "This "+str_type+" will teach you about "+str_userTags+" and is available in "+str_language+".",
        "It's aimed at the "+str_educationLevel+" level in the field of "+str_subjectAreas+".",
        "You can find it here: "+str_url,
        str_clusters+" #OpenScience #OER"
    ]

post = "\n".join(parts)
print(post)
print("---")
print(sum(char_count.values()))
print(char_count)


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