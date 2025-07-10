import os

from scripts.agent_markdown import run as markdown_run
from scripts.agent_notion import run as notion_run


def main():
    notion_token = os.getenv("NOTION_TOKEN")
    notion_db = os.getenv("NOTION_DB_ID")

    if not notion_token or not notion_db:
        print("❌ Erreur : NOTION_TOKEN ou NOTION_DB_ID non défini.e.s.")
        exit(1)

    notion_run()
    markdown_run()


if __name__ == "__main__":
    main()
