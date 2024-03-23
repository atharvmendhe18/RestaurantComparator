from autoscraper import AutoScraper

url = 'https://www.amazon.in/s?k=iphone+13'

# We can add one or multiple candidates here.
# You can also put urls here to retrieve urls.
wanted_list = ['href']

scraper = AutoScraper()
result = scraper.build(url, wanted_list)
print(result)