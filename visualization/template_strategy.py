from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
import os

class TemplateStrategy(ABC):
    """
    Abstract base class for all report template rendering strategies.
    """

    def __init__(self, template_folder: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_folder))

    @abstractmethod
    def render(self, data: dict, template_name: str) -> str:
        pass


class HtmlTemplateStrategy(TemplateStrategy):
    """
    Renders the report using an HTML Jinja2 template.
    """

    def render(self, data: dict, template_name: str = "report.j2") -> str:
        template = self.env.get_template(template_name)
        return template.render(data)


class MarkdownTemplateStrategy(TemplateStrategy):
    """
    Renders the report using a Markdown Jinja2 template.
    """

    def render(self, data: dict, template_name: str = "report.md.j2") -> str:
        template = self.env.get_template(template_name)
        return template.render(data)
