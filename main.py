from flask import Flask, render_template
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

app = Flask(__name__)
# Create a session object for reusing connections
session = requests.Session()
# Thread-local storage for the session
thread_local = threading.local()

def get_session():
    """Get a thread-local session"""
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/<comic>/<chapter>')
def load_page(comic, chapter):
    next = f"/{comic}/{int(chapter)+1}"
    prev = f"/{comic}/{int(chapter)-1}"
    images = get_valid_urls(comic, f"{chapter}")
    return render_template('comic.html', images=images, next=next, prev=prev)

def check_url(args):
    """Function to check individual URL"""
    comic, chapter, number = args
    session = get_session()
    url = f"https://cdn4.webtoonscan.com/site-1/{comic}/{chapter}/{number}.jpg"
    try:
        response = session.get(url, timeout=5)
        if response.status_code == 200:
            return url
        return None
    except requests.RequestException:
        return None

def get_valid_urls(comic, chapter):
    valid_urls = []
    # Create a list of numbers to check (limiting to reasonable maximum, e.g., 100)
    numbers_to_check = range(1, 101)

    # Create arguments for thread pool
    args = [(comic, chapter, num) for num in numbers_to_check]

    # Use ThreadPoolExecutor to check URLs concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks and get futures
        future_to_url = {executor.submit(check_url, arg): arg for arg in args}

        # Process completed futures
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                valid_urls.append(result)
            # If we get a None result, this might indicate we've reached the end
            # but we'll continue checking other ongoing requests

    # Sort the valid URLs to maintain order
    valid_urls.sort(key=lambda x: int(x.split('/')[-1].split('.')[0]))
    print(valid_urls)
    return valid_urls

def get_images(comic, chapter):
    session = get_session()
    url = f"https://webtoonscan.com/manhwa/{comic}/{chapter}/"
    print(url)
    try:
        r = session.get(url)
        data = r.text
        print(data)
        tags = parser(data, "<img", '/>')
        images = []
        print(images)
        for tag in tags:
            if "chapter" in tag:
                link = parser(tag, 'http', 'g"')[0]
                images.append(link)
        return images
    except requests.RequestException as e:
        print(f"Error fetching images: {e}")
        return []

def parser(text, start, end):
    items = []
    count = 0
    text_length = len(text)

    while count < text_length:
        if text[count:count+len(start)] == start:
            pointer = count
            while pointer < text_length and pointer - count <= 500:
                if text[pointer:pointer+len(end)] == end:
                    items.append(text[count:pointer+len(end)])
                    break
                pointer += 1
        count += 1

    return items

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
