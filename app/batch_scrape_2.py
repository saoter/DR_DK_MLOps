import requests
import json
from lxml import html

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

udland = 'https://www.dr.dk/nyheder/udland'
response = requests.get(udland, headers=headers)

if response.status_code == 200:
    tree = html.fromstring(response.content)
    links = tree.xpath('//div[contains(@class, "dre-article-teaser")]/a/@href')
    filtered_links = [link for link in links if link.startswith('/nyheder/udland/')]
    base_url = "https://www.dr.dk"
    full_links = [base_url + link for link in filtered_links]
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
    exit()

# List to store all extracted data
all_data = []

for link in full_links:
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        tree = html.fromstring(response.content)

        title = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/header/div/div/div/div[2]/h1//text()')
        title_text = "\n".join([text.strip() for text in title if text.strip()])

        label = tree.xpath('//*[@id="dre-main"]/div/div[2]/div/main/article/div/div[3]/div[1]/div[1]/div/div/header/div/div[1]/div[2]/div/span/span//text()')
        label_text = "\n".join([text.strip() for text in label if text.strip()])

        theme = tree.xpath('//div[contains(@class, "dre-theme-header-band")]//text()')
        theme_text = "\n".join([t.strip() for t in theme if t.strip()])
        theme_text = theme_text.replace("\nSe tema", "").strip()

        badge = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/header/div/div/div/div[1]/div/div/div/div/div[1]/span/span//text()')
        badge_text = "\n".join([text.strip() for text in badge if text.strip()])

        speech_sections = tree.xpath('//div[contains(@class, "dre-speech")]//text()')
        full_text = "\n".join([text.strip() for text in speech_sections if text.strip()])

        datetime = tree.xpath('//div[contains(@class, "dre-byline__dates")]//time/@datetime')
        datetime_value = datetime[0] if datetime else "No datetime found"

        author = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/div[3]/div/div/div/div[1]/div[2]/div/a/span//text()')
        author_text = "\n".join([text.strip() for text in author if text.strip()])

        extracted_data = {
            "url": link,
            "title": title_text,
            "label": label_text,
            "theme": theme_text,
            "badge": badge_text,
            "datetime": datetime_value,
            "author": author_text,
            "text": full_text
        }
        all_data.append(extracted_data)
        print(f"Scraped: {link}")
    else:
        print(f"Failed to retrieve: {link}")

# ✅ Send the data to FastAPI server using POST request
API_URL = "http://130.225.39.127:8000/articles/"
response = requests.post(API_URL, json=all_data)

if response.status_code == 200:
    print("✅ Data successfully sent to FastAPI server.")
else:
    print(f"❌ Failed to send data. Status code: {response.status_code}, Response: {response.text}")
