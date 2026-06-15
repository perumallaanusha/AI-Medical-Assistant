from icrawler.builtin import BingImageCrawler

keywords = [
    "healthy human skin close up",
    "normal skin close up",
    "healthy skin texture",
    "clear skin",
    "healthy arm skin",
    "healthy hand skin",
    "healthy leg skin",
    "healthy face skin",
    "normal human skin texture",
    "healthy body skin"
]

for keyword in keywords:
    print(f"Downloading: {keyword}")

    crawler = BingImageCrawler(
        storage={"root_dir": "dataset/healthy"}
    )

    crawler.crawl(
        keyword=keyword,
        max_num=200
    )

print("Healthy images downloaded!")