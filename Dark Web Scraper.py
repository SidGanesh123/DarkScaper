import requests
import json
from bs4 import BeautifulSoup

#Should work for any blog with the same type of meta data
blog_link = "https://reycdxyc24gf7jrnwutzdn3smmweizedy7uojsa7ols6sflwu25ijoyd.onion/2024/02/09/tls-cert-for-onion/"


# Must have Tor running (either browser or through the terminal
def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session


if __name__ == '__main__':
    session = get_tor_session()

    # Use our Tor Session for requests
    r = session.get(blog_link)
    status_code = r.status_code
    # If OK, format response in a soup that's easy to handle
    if status_code == 200:
        soup = BeautifulSoup(r.content.decode(), 'html.parser')
    posts = []
    for post_item in soup.find_all("head"):
        title = post_item.find('meta', attrs= {"property": "og:title"}).get("content")
        date = post_item.find('meta', property = "article:published_time").get("content")
        content_divs = soup.find_all('div', class_="content e-content")
        paragraphs = [p_tag.get_text() for div in content_divs for p_tag in div.find_all("p")]
        #Makes content more readable
        post_content = '\n\n'.join([p.strip() for p in paragraphs]).replace("/**/*", "").replace("/2019", "'")
#Puts everything in a dictionary for the post
        post = {
            "Title": title,
            "Date and Time": date[:10] + " " + date[10:], 
            "Blog URL": blog_link,
            "Content": post_content
        }
        posts.append(post)

#Can be used to display information in terminal - Makes the content readable
    # for post in posts:
    #     print("Title: ", post["Title"])
    #     print("Date: ", post["Date"][:10] + " " + post["Date"][10:])
    #     print("Blog URL: ", post["Blog URL"])
    #     print("Content:\n", post["Content"])
    #     print()
        
#Dumps information into a JSON 
    with open("scraper.json", "w") as outfile:
        ##Could be used in case of automation
        #json.dump([{k: v if isinstance(v, str) else {"text": v[0], "lines": v[1:]} for k, v in post.items()} for post in posts], outfile, indent=2)
        #Makes its so that the content also has a line count (for manual reading)
        json.dump([{k: v if '\n\n' not in v else {"article": v.replace('\n\n', '\n'), "lines": v.count('\n')} for k, v in post.items()} for post in posts], outfile, indent=2)
