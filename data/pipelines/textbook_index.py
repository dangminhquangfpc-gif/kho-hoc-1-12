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


class StructuredMathToc(HTMLParser):
    """Secondary Math 6–12 TOC layout. Confined to the main contents box."""

    def __init__(self):
        super().__init__()
        self.divs = []
        self.anchor = None
        self.chapter = ""
        self.semester = None
        self.entries = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            self.divs.append(attrs.get("id", ""))
        if tag == "a" and "event_1_columns" in self.divs:
            self.anchor = [attrs.get("href", ""), ""]

    def handle_data(self, text):
        if self.anchor is not None:
            self.anchor[1] += text

    def handle_endtag(self, tag):
        import re

        if tag == "a" and self.anchor is not None:
            url, title = self.anchor
            title = " ".join(title.split())
            lower = title.casefold()
            if lower.startswith(("toán ", "giải toán ")):
                match = re.search(r"tập\s*([12])", lower)
                if match:
                    self.semester = int(match.group(1))
                self.chapter = ""
            elif lower.startswith(("chương ", "hoạt động thực hành trải nghiệm")):
                self.chapter = title
            elif (
                title
                and not lower.startswith("ôn tập ôn tập")
                and re.search(r"-[ace]\d+\.html$", url)
            ):
                self.entries.append(
                    dict(
                        url=urljoin("https://loigiaihay.com/", url),
                        title=title,
                        chapter=self.chapter,
                        semester=self.semester,
                    )
                )
            self.anchor = None
        if tag == "div" and self.divs:
            self.divs.pop()
