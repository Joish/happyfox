import logging

from fetch_email import GmailClient
from rule_processor.rule_processor import RuleProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """
    Main function to fetch and process emails based on defined rules.
    """
    try:
        # Initialize the Gmail client
        client = GmailClient()

        # Initialize the RuleProcessor with the Gmail client's service
        processor = RuleProcessor(client.service)

        # Read rules from the JSON file
        rules = processor.read_rule_json()
        if not rules:
            logging.error("No rules found or failed to read rules.")
            return

        # Process rules
        processor.process_rules(rules)
        logging.info("Finished processing rules.")

    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}")


if __name__ == "__main__":
    # Run the main function
    main()
