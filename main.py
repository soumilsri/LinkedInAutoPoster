"""
Main entry point for LinkedIn Auto-Posting Agent
"""
from cli import LinkedInAutoPosterCLI

if __name__ == "__main__":
    app = LinkedInAutoPosterCLI()
    app.run()

