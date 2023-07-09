import requests


def fetch(session: requests.Session, url):
    with session.get(url) as response:
        return response.text


def main():
    with requests.session() as session:
        html = fetch(session, 'https://python.org')
        print(html)


main()
