import pandas as pd
import json

# packages for scraping data from internet
import requests
from lxml import html


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


udland = 'https://www.dr.dk/nyheder/udland'
response = requests.get(udland, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    tree = html.fromstring(response.content)
    
    # Use XPath to find all <div class="dre-article-teaser"> and extract <a> href attributes
    links = tree.xpath('//div[contains(@class, "dre-article-teaser")]/a/@href')
    
    # Print the extracted links
    print("Extracted Links:")
    for link in links:
        print(link)
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

# we select only links that starts with '/nyheder/udland/'
filtered_links = [link for link in links if link.startswith('/nyheder/udland/')]

base_url = "https://www.dr.dk"
full_links = [base_url + link for link in filtered_links]

print("Full Filtered Links:")
for full_link in full_links:
    print(full_link)


# List to store all extracted data
all_data = []

# Iterate over each link in the list
for link in full_links:
    response = requests.get(link, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    })

    if response.status_code == 200:
        # Parse the HTML content
        tree = html.fromstring(response.content)

        # Extract title
        title = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/header/div/div/div/div[2]/h1//text()')
        title_text = "\n".join([text.strip() for text in title if text.strip()])
        title_text = title_text.replace("\n", " ").strip()

        # Extract label
        label = tree.xpath('//*[@id="dre-main"]/div/div[2]/div/main/article/div/div[3]/div[1]/div[1]/div/div/header/div/div[1]/div[2]/div/span/span//text()')
        label_text = "\n".join([text.strip() for text in label if text.strip()])

        # Extract theme
        theme = tree.xpath('//div[contains(@class, "dre-theme-header-band")]//text()')
        theme_text = "\n".join([t.strip() for t in theme if t.strip()])
        theme_text = theme_text.replace("\nSe tema", "").strip()

        # Extract badge (type)
        badge = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/header/div/div/div/div[1]/div/div/div/div/div[1]/span/span//text()')
        badge_text = "\n".join([text.strip() for text in badge if text.strip()])

        # Extract text from all <div class="dre-speech">
        speech_sections = tree.xpath('//div[contains(@class, "dre-speech")]//text()')
        full_text = "\n".join([text.strip() for text in speech_sections if text.strip()])

        # Extract the datetime attribute
        datetime = tree.xpath('//div[contains(@class, "dre-byline__dates")]//time/@datetime')
        datetime_value = datetime[0] if datetime else "No datetime found"

        # Extract the author
        author = tree.xpath('//*[@id="dre-main"]/div/div/div/main/article/div/div[3]/div[3]/div/div/div/div[1]/div[2]/div/a/span//text()')
        author_text = "\n".join([text.strip() for text in author if text.strip()])

        # Add the extracted data to the list
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

        print(f"Successfully scraped: {link}")
    else:
        print(f"Failed to retrieve the page: {link}. Status code: {response.status_code}")

# Convert the list of data to a Pandas DataFrame
df = pd.DataFrame(all_data)

# Save to JSON
with open('scraped_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

# Save to CSV
df.to_csv('scraped_data.csv', index=False, encoding='utf-8')

print("Scraping completed. Data saved to 'scraped_data.json' and 'scraped_data.csv'.")


