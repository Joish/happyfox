import datetime
import json
import logging
import os

from sqlalchemy import or_, and_
from sqlalchemy.sql import operators

from db.engine import Session
from db.models import Email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RuleProcessor:
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self.available_labels = self.get_labels()
        # Field
        self.string_fields = ["From", "To", "Subject"]
        self.date_fields = ["Received"]

        self.field_to_db_mapping = {
            "From": "from_address",
            "To": "to_address",
            "Subject": "subject",
            "Received": "date_received"
        }

        # Predicate - string
        self.string_comparison_operator = {
            "Contains": operators.contains_op,
            "Does not Contain": operators.notcontains_op,
            "Equals": operators.eq,
            "Does not equal": operators.ne
        }

        # Predicate - date
        self.date_comparison_operator = {
            "Less than": operators.lt,
            "Greater than": operators.gt
        }

    @staticmethod
    def read_rule_json(filename="rules.json"):
        """
        Reads the rule JSON file
        :param filename:
        :return:
        """
        try:
            # Construct the full path to the file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, filename)

            # Read and parse the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                rules = data.get('rules')
                if rules is not None:
                    return rules
                else:
                    logging.error(f"No 'rules' key found in JSON file: {filename}")
                    return None
        except FileNotFoundError:
            logging.error(f"File not found: {filename}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON file: {filename} - {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error reading file: {filename} - {e}")
            return None

    def get_string_comparison_operator(self, predicate):
        try:
            return self.string_comparison_operator.get(predicate)
        except Exception as e:
            logging.error(f'Error in get_string_comparison_operator: {e}')
            return None

    def get_date_comparison_operator(self, predicate):
        try:
            return self.date_comparison_operator.get(predicate)
        except Exception as e:
            logging.error(f'Error in get_date_comparison_operator: {e}')
            return None

    def get_comparison_operator(self, field, predicate):
        try:
            if field in self.string_fields:
                return self.get_string_comparison_operator(predicate)
            elif field in self.date_fields:
                return self.get_date_comparison_operator(predicate)
            else:
                logging.warning(f'Unknown field: {field}')
                return None
        except Exception as e:
            logging.error(f'Error in get_comparison_operator: {e}')
            return None

    @staticmethod
    def parse_date(value):
        """
        Parses a relative date string and returns a datetime object.
        :param
            value:A string representing the relative time period.
        :return:
            datetime.datetime: A datetime object representing the calculated past date.
        """
        try:
            # Assuming the value format is '30 days', '2 months', etc.
            num, period = value.split()
            num = int(num)
            if period == 'days':
                comparison_date = datetime.datetime.now() - datetime.timedelta(days=num)
            elif period == 'months':
                comparison_date = datetime.datetime.now() - datetime.timedelta(days=30 * num)  # Approximation
            else:
                raise ValueError("Unsupported time period")

            return comparison_date
        except Exception as e:
            logging.error(f'Error in date comparison: {e}')
            return None

    def apply_action(self, email, action):
        try:
            if action['action'] == 'Mark as read':
                self.mark_email_read_status(email, True)
            elif action['action'] == 'Mark as unread':
                self.mark_email_read_status(email, False)
            elif action['action'] == 'Move Message':
                self.move_message(email, action.get('folder'))
            else:
                logging.warning(f'Unknown action: {action}')
        except Exception as e:
            logging.error(f'Error applying action {action} to email {email}: {e}')

    def mark_email_read_status(self, email, mark_as_read):
        """
        Marks an email as read or unread in the email service.
        :param
            email: The email object representing the email to be modified.
            mark_as_read: If True, mark the email as read; if False, mark as unread.
        :return:
        """
        try:
            label_action = 'removeLabelIds' if mark_as_read else 'addLabelIds'
            label_ids = ['UNREAD']

            self.gmail_service.users().messages().modify(
                userId='me',
                id=email.id,
                body={label_action: label_ids}
            ).execute()

            action = 'read' if mark_as_read else 'unread'
            logging.info(f"Email marked as {action}: {email.id}, {email.from_address}, {email.subject}")
        except Exception as e:
            action = 'read' if mark_as_read else 'unread'
            logging.error(f"Error marking email as {action}: {email.id} - {e}")

    def move_message(self, email, folder):
        """
        Moves an email to a specified folder in the email service.
        :param
            email: The email object representing the email to be moved.
            folder: The name of the folder (label in Gmail) to move the email to.
        :return:
        """
        try:
            # Retrieve the label ID corresponding to the folder name
            label_id = self.get_label_id(folder)
            if label_id:
                # Apply the label to the email
                self.gmail_service.users().messages().modify(
                    userId='me',
                    id=email.id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                logging.info(
                    f"Email moved to folder: {folder} - Email ID: {email.id} {email.from_address}, {email.subject}")
            else:
                logging.warning(f"Label not found for folder: {folder}")
        except Exception as e:
            logging.error(f"Error moving email to folder: {folder} - Email ID: {email.id} - {e}")

    def get_labels(self):
        try:
            # List all labels
            response = self.gmail_service.users().labels().list(userId='me').execute()
            return response.get('labels', [])
        except Exception as e:
            logging.error(f"Error retrieving label: {e}")
            return None

    def get_label_id(self, folder_name):
        """
        Retrieves the label ID corresponding to a folder name.
        :param folder_name: The name of the folder (label in Gmail).
        :return:
        """
        try:
            # Find the label that matches the folder name
            for label in self.available_labels:
                if label['name'].lower() == folder_name.lower():
                    return label['id']

            logging.warning(f"No label found for folder name: {folder_name}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving label ID for folder: {folder_name} - {e}")
            return None

    def process_rules(self, rules):
        """
         Processes a list of rules against emails in the database and applies specified actions.
        :param
            rules: A list of rule dictionaries.
        :return:

        """
        with Session() as session:
            for rule in rules:
                logging.info(f"Processing Rule {rule.get('id')}::{rule.get('description')}")
                query = self.build_query(session.query(Email), rule)
                emails = query.all()
                logging.debug(f"Query: {query}, Email List: {len(emails)}")
                for email in emails:
                    for action in rule.get('actions', []):
                        self.apply_action(email, action)

    def build_query(self, query, rule):
        """
        Build a query based on the given rule.
        :param
            query: The base SQLAlchemy query object.
            rule: A dictionary representing a rule with conditions and overall predicate.
        :return:
            query: The modified query object with applied conditions.
        """
        try:
            conditions = rule.get('conditions', [])
            overall_predicate = rule.get('overall_predicate', 'All')
            condition_expressions = []

            for condition in conditions:

                # Validate condition structure
                if not all(key in condition for key in ['field', 'predicate', 'value']):
                    logging.warning(f'Skipping malformed condition: {condition}')
                    continue

                field = condition['field']
                db_field = self.field_to_db_mapping.get(field)
                if db_field:
                    comparison_operator = self.get_comparison_operator(field, condition['predicate'])
                    value = condition['value']

                    if field in self.date_fields:
                        value = self.parse_date(value)
                        logging.debug(f"Parsed Datetime {value}")

                    if comparison_operator:
                        condition_expr = comparison_operator(getattr(Email, db_field), value)
                        condition_expressions.append(condition_expr)
                    else:
                        logging.warning(f'Unknown comparison operator for predicate: {condition["predicate"]}')
                else:
                    logging.warning(f'Unknown DB Field operator: {field}')

            # Apply overall predicate logic
            if overall_predicate == 'All':
                query = query.filter(and_(*condition_expressions))
            elif overall_predicate == 'Any':
                query = query.filter(or_(*condition_expressions))

            return query
        except Exception as e:
            logging.error(f'Error building query: {e}')
            raise
