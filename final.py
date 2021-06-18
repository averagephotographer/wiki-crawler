import json, requests, random, time
random.seed(26)
DEBUG = False

# make links become children as soon as they're made?
# make sure that self.views is not None


class Article():
    def __init__(self, article_name):
        if article_name.startswith("https://") or article_name.startswith("en.wikipedia.org"):
            self.name = article_name.rsplit('/', 1)[-1]
        else:
            self.name = article_name

        # list of links
        self.links = self._get_links(self.name)

        self.views = None
        # gets # of views for self and children article in same call
        self.random_links = random.sample(self.links, 48)
        self.random_links.append(self.name)
        self._get_views(self.random_links)

    #? may need an uplink function?
    # links the parent to the child
    def __call__(self, child):
        self.child = child
        child.parent = self
        # links on page
        # best link

    def _wiki_format(self, article_title):
        return article_title.replace(" ", "_")

    def _get_links(self, article_name):
        sub_links = []
        page_object = self._get_request(article_name)
        for page_id in page_object:
                for title in (page_object[page_id]['links']):
                    sub_article = title['title']
                    sub_links.append(sub_article)
        return sub_links

    
    def _get_views(self, article_list):
        page_object = self._get_request(article_list)
        # print(page_object)
        for page_id in page_object:
            title = (page_object[page_id]['title'])
            if DEBUG == True: 
                print(title)
            sum = 0
            try:
                for date in (page_object[page_id]['pageviews']):
                    try:
                        daily_viewcount = page_object[page_id]['pageviews'][date]
                        # in case there are no views
                        if daily_viewcount == None:
                            sum += 0
                        else:
                            sum += daily_viewcount
                    except KeyError:
                        if DEBUG == True:
                            print("view error")
                        sum += 0
                if self._wiki_format(title) == self.name:
                    self.views = sum
            except KeyError:
                if DEBUG == True:
                    print("pageview error")
            if DEBUG == True:
                print(sum)
                                


    
    # article_list can be a list of one
    # returns page_object to be looped over
    def _get_request(self, article_list):

        # if it's a list it's from _get_views
        if type(article_list) == list:
            titles = "|".join(article_list)
            # api call to get pageviews
            api = "https://en.wikipedia.org/w/api.php?action=query&prop=pageviews&format=json&pvipcontinue&titles=" + titles

        # if it's not a list, it's from _get_links, assume single string
        else:
            title = article_list
            # api to get page links
            api="https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=max&format=json&titles=" + title
        
        headers = {
            'User-Agent': 'wikipedia game solver',
            'From' : 'cdtv1473@gmail.com'
        }
        response = requests.get(api, headers=headers)
        # for header in response.headers:
            # print(header + ' : ' + response.headers[header])
        print('.')
        content = response.text

        json_object = json.loads(content)

        # this checks to see if json_object has a 'continue' when getting the number of views 
        # print(json_object['continue'])
        # try:
        
                
        if type(article_list) == list:
            while 'continue' in json_object:
                new_response = requests.get(api, headers=headers)
                # for header in response.headers:
                #     print(header + ' : ' + response.headers[header])
        
                # print(new_response.headers)
                new_content = new_response.text
                json_object = json.loads(new_content)
                # print(json_object)
                time.sleep(.5)
                print('.')
        
        # while "pvipcontinue" in json_object['continue']:
        #     self._get_request(article_list)
            # print(json_object['continue'])
        # except KeyError:
            # pass

        query_object = json_object['query']
        page_object = query_object['pages']
    
        return page_object



if __name__ == "__main__":
    name = "Avengers_(comics)"
    name2 = 'Harry_Potter'
    a = Article(name2)

    print(a.name)
    # print(a.links)
    print(a.views)
