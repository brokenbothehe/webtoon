from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return (render_template('index.html'))


@app.route('/<comic>/<chapter>')
def load_page(comic, chapter):
    next = f"/{comic}/{int(chapter)+1}"
    prev = f"/{comic}/{int(chapter)-1}"
    images = get_page(comic, f"chapter-{chapter}")
    return (render_template('comic.html', images=images, next=next, prev=prev))


def get_page(comic, chapter):
    url = f"https://manga18h.xyz/manga/{comic}/{chapter}/"
    r = requests.get(url)
    data = r.text
    tags = parser(data, "<img", '">')
    images = []
    for tag in tags:
        if "wp-manga-chapter-img" in tag:
            link = parser(tag, 'http', 'g"')[0]
            images.append(link)
    return (images)


def parser(text, start, end):
    count = 0
    items = []
    for letter in text:
        if text[count:count+4] == start:
            pointer = count
            while True:
                if text[pointer:pointer+2] == end:
                    break
                if pointer - count > 500:
                    break
                pointer += 1
            items.append(text[count:pointer+1])
        count += 1
    return (items)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
