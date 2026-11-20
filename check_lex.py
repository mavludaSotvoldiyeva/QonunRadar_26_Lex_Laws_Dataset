
import requests
from urllib.robotparser import RobotFileParser

robots_url = "https://lex.uz/robots.txt"
law_url = "https://lex.uz/docs/-2006789"

try:
    response = requests.get(
        robots_url,
        timeout=20,
        headers={"User-Agent": "QonunRadarResearchBot/0.1"}
    )

    print("HTTP status:", response.status_code)
    print("Final URL:", response.url)
    print("Response preview:", response.text[:500])

    if response.status_code == 200:
        parser = RobotFileParser()
        parser.parse(response.text.splitlines())

        print(
            "Crawler allowed:",
            parser.can_fetch(
                "QonunRadarResearchBot/0.1",
                law_url
            )
        )
    else:
        print("Permission could not be confirmed.")

except requests.RequestException as error:
    print("Connection error:", error)
