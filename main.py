from parsel import Selector
import requests
import pandas as pd


def scrape_page_link(html):

    url = "https://www.uniuneanotarilor.ro"
    links = []
    table = html.xpath('//div[@class="content"]/table/tr[2]/td')

    trs = table.xpath('//a/@href')
    for tr in trs:
        if tr.get().startswith('./?start='):
            link_text = tr.get()
            full_link = f'{url}{link_text[1:]}'
            links.append(full_link)

    return links


def load_content(html):
    # Select the div using the given XPath
    table = html.xpath('/html/body/div[5]/div[@class="content"]/table/tr[2]/td/table')
    keys = table.xpath(".//tr/td[1]")
    values = table.xpath(".//tr/td[2]")

    # #make a dictionary that stores this information in key value pairs
    info = {}

    for key in keys:
        key_name = key.xpath('.//text()').get()
        info[key_name] = None

    for i, val in enumerate(values):
        value_text = val.xpath('.//text()').get()
        # Get the corresponding key from the `keys` list using the index `i`
        key_name = keys[i].xpath('.//text()').get()
        # Assign the value to the corresponding key in the dictionary
        info[key_name] = value_text

    return info

def scrape_info_link(html):

    table = html.xpath('//div[@class="content"]/table/tr[2]/td/table')

    trs = table.xpath('//tr')

    links = []

    for tr in trs[1:]:

        #Getting the link to the page containing further info
        if tr.xpath('./td/a[@href]'):
            links.append(tr.xpath('./td/a/@href').get())

    return links


            #------------------------------------main program-----------------------------------#

url = "https://www.uniuneanotarilor.ro/?p=2.2.3"

headers = {
    "content-type" : "application/x-www-form-urlencoded",
    "origin" : "https://www.uniuneanotarilor.ro"
}

body = "birouri=1&lang=ro&camera=&judet=&circumscriptie=&localitate=&nume=&adresa=&limba1=&limba2="

response = requests.post(url, data=body ,headers=headers)
html = response.text

selector = Selector(text=html)
df = pd.DataFrame()
data = []
links = scrape_info_link(selector)
for link in links[1:]:
        in_url = f'https://www.uniuneanotarilor.ro/?p=2.2.3/{link}'
        in_response = requests.get(f'{in_url}')
        in_html = in_response.text
        in_selector = Selector(text=in_html)
        #data.append(load_content(in_selector))
        record = load_content(in_selector)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_excel("output.xlsx", index=False)


page_links = scrape_page_link(selector)
i = 0
for page_link in page_links:
    page_response = requests.get(f'{page_link}')
    page_html = page_response.text
    page_selector = Selector(text=page_html)
    print(f'Scrapped page: {i}')
    i += 1
    links = scrape_info_link(page_selector)
    print("Scrapped page Links")
    for link in links[1:]:
        in_url = f'https://www.uniuneanotarilor.ro{link}'
        in_response = requests.get(f'{in_url}')
        in_html = in_response.text
        in_selector = Selector(text=in_html)
        print("Scrapped Links Data")
        record = load_content(in_selector)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_excel("output.xlsx", index=False)

