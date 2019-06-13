import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib import parse

def titles(url):

    # urlからhtmlを取得
    html = requests.get(url).content

    # htmlからスープを取得
    soup = BeautifulSoup(html,'html.parser')

    # setBlock nopscrのdivを取得
    div = soup.find('div', attrs={'class':'setBlock nopscr'})
    
    # タイトルのリストを取得
    titles_ = []
    for ttl in div.find_all('div', attrs={'class':'ttl'}):
        if ttl.find('span') is None:
            titles_.append( ttl.string )
        else:
            titles_.append( ttl.a.string + ttl.find('span').string )

    return titles_

def schBoxToDicts(schBox, serach_url):
    dicts = []
    for midBox in schBox.find_all('div', {'class':'midBox'}):
        dict_ = {}
        dict_['url'] = parse.urljoin( serach_url, midBox.h3.a.get('href') )
        dict_['address'] = midBox.find('span', {'class':'address'}).string
        dict_['artistName'] = midBox.find('h3', {'class':'artistName'}).string
        dict_['guestArtists'] = ','.join( [ ga.string for ga in midBox.find_all('p', {'class': 'guestArtist'}) ] )
        tmp = midBox.find('p', {'class':'date'})
        tmp.find("span", {"class":"address"}).extract()
        dict_['date'] = tmp.string
        dicts.append(dict_)
    return dicts

if __name__ == '__main__':

    serach_url = 'https://www.livefans.jp/search/artist/6209?year=before'

    html = requests.get(serach_url)
    soup = BeautifulSoup(html.text, 'html5lib')

    # schBoxを取得
    schBox =  soup.find('div', {'id':'schBox'})

    # schBoxから最大ページ数を取得
    pageNate = schBox.find('p', {'class':'pageNate'})
    maxPage = max( [ int(page.string) for page in pageNate.find_all('span') if page.string.isdecimal() ] )

    # schBox内のmidBoxからイベントページのURLと開催場所、ゲストアーティストを辞書で取得
    dicts = []
    dicts.extend( schBoxToDicts(schBox, serach_url) )

    # 2ページ目以降を取得
    for page in range(2, maxPage):

        print('get url', page, '/', maxPage)

        splited_url = serach_url.split('?')
        url_ = splited_url[0] + '/page:' + str(page) + '?&year=before&sort=e1'

        html = requests.get(url_)
        soup = BeautifulSoup(html.text, 'html5lib')
        # schBoxを取得
        schBox =  soup.find('div', {'id':'schBox'})
        # schBox内のmidBoxからイベントページのURLと開催場所、ゲストアーティストを辞書で取得
        dicts.extend( schBoxToDicts(schBox, serach_url) )

    output_list = []
    for n, dict_ in enumerate(dicts):

        print('get titles', n, '/', len(dicts))

        titles_ = titles( dict_['url'] )

        for num, title in enumerate(titles_):
            dict2 = dict_.copy()
            dict2['num'] = num
            dict2['title'] = title
            output_list.append(dict2)

    with open('set_list.csv', 'w', encoding='utf-8', newline='\n') as f:

        # 要素順を指定
        fieldnames = ['artistName', 'date', 'address', 'num', 'title', 'guestArtists', 'url']

        # writerオブジェクトを作成
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')

        # writeheaderでヘッダーを出力
        writer.writeheader()

        for n, dict_ in enumerate(output_list):
            # writerowで1行分を出力
            writer.writerow( dict_ )
