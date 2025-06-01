# scripts/zsync_scheduler.py

from scripts.agent_notion import run as notion_run
from scripts.agent_markdown import run as markdown_run

def main():
    notion_run()
    markdown_run()

if __name__ == "__main__":
    main()
