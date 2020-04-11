from bs4.element import Tag, Comment


class Rule:
    def __init__(self, content):
        self.content = content

    def get_elements(self):
        area = self.get_area()
        elements = self.select(area)
        filtered_elements = self.filter(elements)

        return filtered_elements

    def get_area(self):
        return self.content

    def select(self, area):
        return area

    def filter(self, elements):
        return [element for element in elements if self.select_element(element)]

    def select_element(self, element):
        return True

    def process(self):
        self.get_elements()


class TagRule(Rule):
    tag = ''

    def create_tag(self, tag=None):
        tag = tag or self.tag
        return self.content.new_tag(tag)

    def select(self, area):
        return area.findAll(self.tag)

    def process(self):
        tags = self.get_elements()
        for tag in tags:
            self.process_tag(tag)

    def process_tag(self, tag):
        attributes = tag.attrs
        new_tag = self.get_new_tag(attributes, contents=tag.contents)
        if new_tag:
            tag.replaceWith(new_tag)
        elif self.is_extract(attributes, contents=tag.contents):
            tag.extract()

    def get_new_tag(self, attributes, contents=None):
        return None

    def is_extract(self, attributes, contents=None):
        return False


class TextRule(Rule):
    def select(self, area):
        return area.findAll(text=True)

    def select_element(self, element):
        return not isinstance(element, Comment)

    def process(self):
        html_strings = self.get_elements()
        for html_string in html_strings:
            self.process_string(html_string)

    def process_string(self, html_string):
        string = str(html_string)
        new_string = self.get_new_string(string)
        if new_string != string:
            html_string.replace_with(new_string)
        elif self.is_extract(string):
            self._extract_node(html_string)

    def _extract_node(self, html_string):
        html_string.parent.decompose()

    def get_new_string(self, string):
        return string

    def is_extract(self, string):
        return False
