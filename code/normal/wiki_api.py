import json

import requests

# wiki-api likes their headers
headers = {
'User-Agent': 'wikipedia game solver',
'From' : 'cdtv1473@gmail.com'
}


def skippable(title):
    skip_list_start = [ 'Wikipedia:', 'Category:', 'Help:', 'User:', 'User talk:', 'Talk:', 'Template:', 'Wikipedia talk:', ]
    skip_list_end = ['(disambiguation)']
    
    for item in skip_list_start:
        if title.startswith(item):
            return True

    for item in skip_list_end:
        if title.endswith(item):
            return True
    
    return False


def api_forwardlinks(article_title):
    """Gets the forwardlinks for an article, for use on left nodes

    Args:
        article_title (text): wiki article title

    Returns:
        list: wiki links from the title page
    """
    links = []
    api="https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=max&format=json&titles=" + article_title
    json_object = _request_json(api)
    page = _page_obj(json_object)

    if list(page.keys())[0] != "-1":
        for page_id in page:
            for article in page[page_id]['links']:
                title = article['title']
                # skips wiki, category, help, and user articles
                if skippable(title):
                    continue
                links.append(title)
    # early error
    else:
        exit(f"\n{article_title} does not have any forwardlinks")
    
    # later error 
    if len(links) == 0:
        exit(f"\n'{article_title}' has no valid forwardlinks, try a different set of links")

    return links

def api_backlinks(article_title):
    """Gets the backlinks for an article, for use on right nodes

    Args:
        article_title (text): wiki article title

    Returns:
        list: wiki links that link to the title page
    """
    links = []
    api="https://en.wikipedia.org/w/api.php?action=query&prop=linkshere&lhlimit=max&format=json&titles=" + article_title
    json_object = _request_json(api)
    page = _page_obj(json_object)
    for page_id in page:
        if 'linkshere' in page[page_id].keys():
            for article in page[page_id]['linkshere']:
                title = article['title']
                # skips wiki, category, help, and user articles
                if not (title.startswith("Wikipedia:") or title.startswith("Category:") or title.startswith("Help:") or title.startswith("User:") or title.startswith("User talk:") or title.startswith("Talk:") or title.startswith("Template:") or title.endswith("(disambiguation)")):
                    links.append(title)
        # early error
        else:
            exit(f"\n{article_title} does not have any backlinks")
            
    # later error
    if len(links) == 0:
        exit(f"\n'{article_title}' has no valid backlinks, try a different set of links")

    return links

def api_views(article_list):
    """Gets pageviews from the last 60 days for a list of 50 articles or fewer

    Args:
        article_list (list): a list of article titles

    Returns:
        dict: {title : viewcount} for each article in the list
    """
    titles = "|".join(article_list)
    api = "https://en.wikipedia.org/w/api.php?action=query&prop=pageviews&format=json&pvipcontinue&titles=" + titles
    json_object = _request_json(api)
    views_dict = {}

    # api tag that lets us know if we need to make the request again (seems like api caches the result for us?)
    while 'continue' in json_object:
        json_object = _request_json(api)
    
    page = _page_obj(json_object)
    
    for page_id in page:
        title = page[page_id]['title']
        pageviews = page[page_id]['pageviews']
        total_views = 0
        # pageviews are separated by day, summed here
        for date in pageviews:
            daily_views = pageviews[date]
            
            if daily_views is None:
                total_views += 0
            else:
                total_views += daily_views

        views_dict[title] = total_views
            
    return views_dict

def _request_json(api_call):
    """makes request to the wiki api and returns a json object with article information

    Args:
        api_call (text): link to the wiki api

    Returns:
        dict: json content from wiki api
    """
    response = requests.get(api_call, headers=headers)
    content = response.text
    print(".", flush = True, end = "")
    return json.loads(content)


# also here for cleaner code
def _page_obj(json_object):
    """takes json input and returns a page object

    Args:
        json_object (dict): json data from api

    Returns:
        dict: json object for the 'pages' of an article
    """
    query_object = json_object['query']
    return query_object['pages']
