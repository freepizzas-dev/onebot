# This library was originally created by Hardik Vasa.
# It is included with onebot with many modifications.
# https://github.com/hardikvasa/google-images-download/
# Below is the original License included with the software
#
#
# The MIT License (MIT)

# Copyright (c) 2015-2019 Hardik Vasa

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#!/usr/bin/env python
###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import sys
version = (3, 0)
cur_version = sys.version_info
import urllib.request
from urllib.parse import quote
import http.client
http.client._MAXHEADERS = 1000
import time
import json

args_list = ["keywords", "keywords_from_file", "online_chip", "prefix_keywords", "suffix_keywords",
             "limit", "format", "color", "color_type", "usage_rights", "size",
             "exact_size", "aspect_ratio", "type", "time", "time_range", "delay", "url", "single_image",
             "output_directory", "image_directory", "no_directory", "proxy", "similar_images", "specific_site",
             "print_urls", "print_size", "print_paths", "metadata", "extract_metadata", "coco_metadata", "socket_timeout",
             "thumbnail", "thumbnail_only", "language", "prefix", "chromedriver", "related_images", "safe_search",
             "no_numbering",
             "offset", "no_download", "save_source", "silent_mode", "ignore_urls"]

class googleimagesdownload:
    def __init__(self):
        pass

    def _extract_data_pack(self, page):
        start_line = page.find("AF_initDataCallback({key: \\'ds:1\\'") - 10
        start_object = page.find('[', start_line + 1)
        end_object = page.rfind(']',0,page.find('</script>', start_object + 1))+1
        object_raw = str(page[start_object:end_object])
        return bytes(object_raw, "utf-8").decode("unicode_escape")

    def _image_objects_from_pack(self, data):
        image_objects = json.loads(data)[56][-1][0][0][1][0]
        url_list = []
        for image in image_objects:
            try:
                dictionary = image[0][0]
                dictionary = next(iter(dictionary.values()))
                url = dictionary[1][3][0]
                url_list.append(url)
            except:
                continue
        return url_list

    # Downloading entire Web Document (Raw Page Content)
    def download_page(self, url):
        headers = {}
        headers[
            'User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req)
            respData = str(resp.read())
        except:
            print("Could not open URL. Please check your internet connection and/or ssl settings \n"
                    "If you are using proxy, make sure your proxy settings is configured correctly")
        try:
            return self._image_objects_from_pack(self._extract_data_pack(respData)), self.get_all_tabs(respData)
        except Exception as e:
            print(e)
            print('Image objects data unpacking failed. Please leave a comment with the above error at https://github.com/hardikvasa/google-images-download/pull/298')

    # Finding 'Next Image' from the given raw page
    def get_next_tab(self, s):
        start_line = s.find('class="dtviD"')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_tabs"
            return link, '', end_quote
        else:
            start_line = s.find('class="dtviD"')
            start_content = s.find('href="', start_line + 1)
            end_content = s.find('">', start_content + 1)
            url_item = "https://www.google.com" + str(s[start_content + 6:end_content])
            url_item = url_item.replace('&amp;', '&')

            start_line_2 = s.find('class="dtviD"')
            s = s.replace('&amp;', '&')
            start_content_2 = s.find(':', start_line_2 + 1)
            end_content_2 = s.find('&usg=', start_content_2 + 1)
            url_item_name = str(s[start_content_2 + 1:end_content_2])

            chars = url_item_name.find(',g_1:')
            chars_end = url_item_name.find(":", chars + 6)
            if chars_end == -1:
                updated_item_name = (url_item_name[chars + 5:]).replace("+", " ")
            else:
                updated_item_name = (url_item_name[chars + 5:chars_end]).replace("+", " ")

            return url_item, updated_item_name, end_content

    # Getting all links with the help of '_images_get_next_image'
    def get_all_tabs(self, page):
        tabs = {}
        while True:
            item, item_name, end_content = self.get_next_tab(page)
            if item == "no_tabs":
                break
            else:
                if len(item_name) > 100 or item_name == "background-color":
                    break
                else:
                    tabs[item_name] = item  # Append all the links in the list named 'Links'
                    time.sleep(0.1)  # Timer could be used to slow down the request for image downloads
                    page = page[end_content:]
        return tabs

    # Building URL parameters
    def build_url_parameters(self, arguments):
        if arguments['language']:
            lang = "&lr="
            lang_param = {"Arabic": "lang_ar", "Chinese (Simplified)": "lang_zh-CN",
                          "Chinese (Traditional)": "lang_zh-TW", "Czech": "lang_cs", "Danish": "lang_da",
                          "Dutch": "lang_nl", "English": "lang_en", "Estonian": "lang_et", "Finnish": "lang_fi",
                          "French": "lang_fr", "German": "lang_de", "Greek": "lang_el", "Hebrew": "lang_iw ",
                          "Hungarian": "lang_hu", "Icelandic": "lang_is", "Italian": "lang_it", "Japanese": "lang_ja",
                          "Korean": "lang_ko", "Latvian": "lang_lv", "Lithuanian": "lang_lt", "Norwegian": "lang_no",
                          "Portuguese": "lang_pt", "Polish": "lang_pl", "Romanian": "lang_ro", "Russian": "lang_ru",
                          "Spanish": "lang_es", "Swedish": "lang_sv", "Turkish": "lang_tr"}
            lang_url = lang + lang_param[arguments['language']]
        else:
            lang_url = ''

        if arguments['exact_size']:
            size_array = [x.strip() for x in arguments['exact_size'].split(',')]
            exact_size = ",isz:ex,iszw:" + str(size_array[0]) + ",iszh:" + str(size_array[1])
        else:
            exact_size = ''
        
        if arguments['online_chip']:
            online_chip = "&chips=online_chip:" + ",online_chip:".join([t.strip().replace(" ", "+") for t in arguments['online_chip'].split(',')]) 
        else:
            online_chip = ''

        built_url = "&tbs="
        counter = 0
        params = {'color': [arguments['color'], {'red': 'ic:specific,isc:red', 'orange': 'ic:specific,isc:orange',
                                                 'yellow': 'ic:specific,isc:yellow', 'green': 'ic:specific,isc:green',
                                                 'teal': 'ic:specific,isc:teel', 'blue': 'ic:specific,isc:blue',
                                                 'purple': 'ic:specific,isc:purple', 'pink': 'ic:specific,isc:pink',
                                                 'white': 'ic:specific,isc:white', 'gray': 'ic:specific,isc:gray',
                                                 'black': 'ic:specific,isc:black', 'brown': 'ic:specific,isc:brown'}],
                  'color_type': [arguments['color_type'],
                                 {'full-color': 'ic:color', 'black-and-white': 'ic:gray', 'transparent': 'ic:trans'}],
                  'usage_rights': [arguments['usage_rights'],
                                   {'labeled-for-reuse-with-modifications': 'sur:fmc', 'labeled-for-reuse': 'sur:fc',
                                    'labeled-for-noncommercial-reuse-with-modification': 'sur:fm',
                                    'labeled-for-nocommercial-reuse': 'sur:f'}],
                  'size': [arguments['size'],
                           {'large': 'isz:l', 'medium': 'isz:m', 'icon': 'isz:i', '>400*300': 'isz:lt,islt:qsvga',
                            '>640*480': 'isz:lt,islt:vga', '>800*600': 'isz:lt,islt:svga',
                            '>1024*768': 'visz:lt,islt:xga', '>2MP': 'isz:lt,islt:2mp', '>4MP': 'isz:lt,islt:4mp',
                            '>6MP': 'isz:lt,islt:6mp', '>8MP': 'isz:lt,islt:8mp', '>10MP': 'isz:lt,islt:10mp',
                            '>12MP': 'isz:lt,islt:12mp', '>15MP': 'isz:lt,islt:15mp', '>20MP': 'isz:lt,islt:20mp',
                            '>40MP': 'isz:lt,islt:40mp', '>70MP': 'isz:lt,islt:70mp'}],
                  'type': [arguments['type'], {'face': 'itp:face', 'photo': 'itp:photo', 'clipart': 'itp:clipart',
                                               'line-drawing': 'itp:lineart', 'animated': 'itp:animated'}],
                  'time': [arguments['time'], {'past-24-hours': 'qdr:d', 'past-7-days': 'qdr:w', 'past-month': 'qdr:m',
                                               'past-year': 'qdr:y'}],
                  'aspect_ratio': [arguments['aspect_ratio'],
                                   {'tall': 'iar:t', 'square': 'iar:s', 'wide': 'iar:w', 'panoramic': 'iar:xw'}],
                  'format': [arguments['format'],
                             {'jpg': 'ift:jpg', 'gif': 'ift:gif', 'png': 'ift:png', 'bmp': 'ift:bmp', 'svg': 'ift:svg',
                              'webp': 'webp', 'ico': 'ift:ico', 'raw': 'ift:craw'}]}
        for key, value in params.items():
            if value[0] is not None:
                ext_param = value[1][value[0]]
                # counter will tell if it is first param added or not
                if counter == 0:
                    # add it to the built url
                    built_url = built_url + ext_param
                    counter += 1
                else:
                    built_url = built_url + ',' + ext_param
                    counter += 1
        built_url = lang_url + online_chip + built_url + exact_size

        return built_url

    # building main search URL
    def build_search_url(self, search_term, params, url, similar_images, specific_site, safe_search):
        # check safe_search
        safe_search_string = "&safe=active"
        # check the args and choose the URL
        if url:
            url = url
        elif specific_site:
            url = 'https://www.google.com/search?q=' + quote(
                search_term.encode(
                    'utf-8')) + '&as_sitesearch=' + specific_site + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
        else:
            url = 'https://www.google.com/search?q=' + quote(
                search_term.encode(
                    'utf-8')) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

        # safe search check
        if safe_search:
            url = url + safe_search_string

        return url

    # Bulk Download
    def download(self, arguments):
        for arg in args_list:
            if arg not in arguments:
                arguments[arg] = None
        ######Initialization and Validation of user arguments
        if arguments['keywords']:
            search_keyword = [str(item) for item in arguments['keywords'].split(',')]

        limit = 100
        i = 0
        while i < len(search_keyword):  # 3.for every main keyword
            iteration = "\n" + "Item no.: " + str(i + 1) + " -->" + " Item name = " + (
            search_keyword[i])
            if not arguments["silent_mode"]:
                print(iteration.encode('raw_unicode_escape').decode('utf-8'))
                print("Evaluating...")
            #true silent mode
            #else:
            #    print("Downloading images for: " + (pky) + (search_keyword[i]) + (sky) + " ...")
            search_term = search_keyword[i]

            params = self.build_url_parameters(arguments)  # building URL with params

            url = self.build_search_url(search_term, params, arguments['url'], arguments['similar_images'],
                                        arguments['specific_site'],
                                        arguments['safe_search'])  # building main search url

            if limit < 101:
                images, tabs = self.download_page(url)  # download page
            else:
                images, tabs = self.download_extended_page(url, arguments['chromedriver'])

            return images