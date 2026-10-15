"""Extract primary contents-list metadata, excluding sidebars and article bodies."""

from html.parser import HTMLParser
from urllib.parse import urljoin


class Toc(HTMLParser):
    def __init__(self):
        super().__init__()
        self.divs = []
        self.anchor = None
        self.heading = None
        self.chapter = ""
        self.entries = []

    def handle_starttag(self, t, a):
        attr = dict(a)
        if t == "div":
            self.divs.append(attr.get("class", ""))
        if t == "h2":
            self.heading = ""
        if t == "a" and any("event-articles-wrap" in c for c in self.divs):
            self.anchor = [attr.get("href", ""), "", attr.get("title", "")]

    def handle_data(self, d):
        if self.anchor:
            self.anchor[1] += d
        if self.heading is not None:
            self.heading += d

    def handle_endtag(self, t):
        if t == "div" and self.divs:
            self.divs.pop()
        if t == "h2" and self.heading is not None:
            self.chapter = " ".join(self.heading.split())
            self.heading = None
        if t == "a" and self.anchor:
            u, label, title = self.anchor
            self.entries.append(
                dict(
                    url=urljoin("https://loigiaihay.com/", u),
                    title=" ".join(label.split()),
                    source_title=title,
                    chapter=self.chapter,
                )
            )
            self.anchor = None
