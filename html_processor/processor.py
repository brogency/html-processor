from urllib.parse import unquote
from bs4 import BeautifulSoup


class HtmlProcessor:
    rules = []
    processed_content = None

    def __init__(self, content, rules=None):
        self.raw_content = content
        if rules:
            self.rules.extend(rules)

    @staticmethod
    def get_simplyfy_content(content):
        return unquote(
            content.replace('\n', ''),
        )

    def process(self):
        content = BeautifulSoup(
            self.get_simplyfy_content(self.raw_content),
            'html.parser',
        )
        for create_rule in self.rules:
            rule = create_rule(content)
            rule.process()
        return content

    def __repr__(self):
        return self.process().prettify()

    def __str__(self):
        return str(self.process())
