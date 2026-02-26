"""
Diary analysis project - Classification System Builder
This creates the classification system that defines how your diary entries are structured.
"""

import json
import os
import difflib 
from typing import List, Dict, Optional, Tuple

from shared_utils import *
from shared_tag_parser import *
from category_config import *

class ClassSysBuilder:
    """
    Configures user's classification system
    """

    def __init__(self):
        """
        Constructor, initializes a new classification system builder
        """
        self.config = {
            'config_version': '1.0'
        }
        # Specifies version of classification system builder
        self.sections_complete = {
            'section_1': False,
            'section_2': False
        } # States that all sections are incomplete

        self.tag_parser = None
        self.category_configs = {}

    def run(self):
        """Main entry point, runs the code"""
        self.welcome_message()

        # Ask user about loading existing config
        if self.load_or_start():
            return # User loaded config and is done
        
        # Build new config (if applicable)
        self.section_1()
        self.section_2()
        self.final_review()
    
    def welcome_message(self):
        """Display welcome message"""
        fancy_title("CLASSIFICATION SYSTEM BUILDER")
        print("Hello! Welcome to the Classification System Builder for the Diary Analysis System!")
        print("This tool will help you create a configuration file that defines " \
        "how your diary entries are structured and tagged.\n")
        print("If you have completed this process already, you may skip this step "
        "and upload your file.")
        print("If this is your first time completing this process, you'll only have to do this once. ")
        print("Once you complete this process, you can import the file that will be generated " \
        "at the end.")

    def load_or_start(self) -> bool:
        """
        Ask if user wants to load an existing config file
        Returns True if user loaded file, meaning that user is done
        Returns False if user is starting fresh
         
        :param self: current instance
        :return: whether user loaded existing config
        :rtype: bool
        """

        if not yes_or_no("\nWould you like to load an existing config?"):
            print("\nStarting fresh configuration...")
            input("Press Enter to continue.")
            return False
    
        # User wants to load a config
        while True:
            filename = input("Enter config filename (default: diary_config.json): ").strip()
            if not filename:
                filename = "diary_config.json"
            
            load_result = self.load_config(filename)
            
            if load_result:
                print("\nConfiguration loaded successfully!")
                input("\nPress Enter to review and edit...")
                self.final_review()
                return True
            else:
                # Loading failed
                print("\nWhat would you like to do?")
                print("  (1) Try another file")
                print("  (2) Start fresh configuration")
                
                choice = input("Choice: ").strip()
                
                if choice == '1':
                    continue  # Loop back to ask for filename
                elif choice == '2':
                    print("\nStarting fresh configuration...")
                    input("Press Enter to continue.")
                    return False
                else:
                    print("Invalid choice. Please try again.")
                    continue
        
    def load_config(self, filename: str) -> bool:
        """
        Load configuration from JSON file
        
        :param filename: Path to config file
        :type filename: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            with open(filename, 'r') as f:
                loaded_config = json.load(f)
            
            # Validate version
            if loaded_config.get('config_version') != '1.0':
                print(f"Warning: Config version mismatch")
            
            self.config = loaded_config
            
            # Reconstruct tag parser
            if 'tag_format' in self.config:
                tf = self.config['tag_format']
                self.tag_parser = TagFormatParser(
                    tf['format_string'],
                    tf['case_sensitive'],
                    tf['normalize_to']
                )
            
            # Reconstruct category configs
            if 'tag_categories' in self.config:
                self.category_configs = {
                    name: CategoryConfig.from_dict(name, data)
                    for name, data in self.config['tag_categories'].items()
                }
            
            self.sections_complete = {
                'section_1': True,
                'section_2': True
            }
            
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return False
        except json.JSONDecodeError:
            print(f"Error: '{filename}' is not valid JSON")
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def section_1a(self):
        """
        Section 1A: Header configuration
        Only applicable if user is using a header instead of entry separator character(s)
        """
        # Question A: Date
        fancy_title("SECTION 1A: Header configuration")
        initiate_question("A", "Date")

        date_field_name = None
        date_format = None
        has_date = yes_or_no("Would you like a date field in your header?")

        if has_date:
            print("What would you like to name your date field?")
            date_field_name = input("Date field name: ")
            if not date_field_name:
                date_field_name = "Date"

            # Question Aa: 
            initiate_question("Aa", "Date format")
            while True:
                print("Select your date format:")
                print("  (1) YYYY-MM-DD (e.g., 2001-03-24)")
                print("  (2) MM-DD-YYYY (e.g., 03-24-2001)")
                print("  (3) DD-MM-YYYY (e.g., 24-03-2001)")
                print("  (4) Month DD, YYYY (e.g., March 24, 2001)")
                print("  (5) DD Month YYYY (e.g., 24 March 2001)")
                print("  (6) YYYY/MM/DD (e.g., 2001/03/24)")
                print("  (7) MM/DD/YYYY (e.g., 03/24/2001)")
                print("  (8) DD/MM/YYYY (e.g., 24/03/2001)")
                print("  (9) Custom format")

                format_map = {
                    '1': 'YYYY-MM-DD',
                    '2': 'MM-DD-YYYY',
                    '3': 'DD-MM-YYYY',
                    '4': 'Month DD, YYYY',
                    '5': 'DD Month YYYY',
                    '6': 'YYYY/MM/DD',
                    '7': 'MM/DD/YYYY',
                    '8': 'DD/MM/YYYY'                
                }

                while True:  # Changed from checking choice
                    choice = input("\nChoice: ").lower().strip()
                    if choice in format_map:
                        date_format = format_map[choice]
                        break
                    elif choice == '9':
                        date_format = input("Enter custom format (use YYYY, MM, DD, Month): ").strip()
                        break
                    else:
                        print("Invalid choice. Please select 1-9.")

                if yes_or_no(f"Date format: {date_format}. Is this correct?"):
                    break
                else:
                    continue

        # Question B: Header fields
        initiate_question("B", "Header fields")
        print("Example header fields: Diary volume, Entry number, Page numbers, Languages") 
        print("Please enter any header field names you would like (comma-separated)")
        if has_date:
            print(f"Note: {date_field_name} will be included automatically")

        fields_input = input("Fields: ").strip()
        header_fields = [f.strip() for f in fields_input.split(',') if f.strip()]

        # Remove duplicates while preserving order
        seen = set()
        unique_fields = []
        for field in header_fields:
            if field.lower() not in seen:  # Case-insensitive duplicate check
                seen.add(field.lower())
                unique_fields.append(field)
        header_fields = unique_fields

        if has_date and date_field_name not in header_fields:
            header_fields.insert(0, date_field_name)

        print(f"\nYou entered {len(header_fields)} fields:")
        for field in header_fields:
            print(f"  - {field}")

        if not yes_or_no("Is this correct?"): 
            # Define warning callback for date field
            def warn_date_deletion(items_to_delete):
                date_field = self.config.get('date_field', {}).get('field_name')
                if date_field and date_field in items_to_delete:
                    print(f"\nWARNING: You're about to delete the date field '{date_field}'!")
                    print("This will remove temporal analysis capabilities.")
                    return yes_or_no("Are you sure you want to delete the date field?")
                return True
            
            header_fields = ListManager.manage_list(header_fields, "header field", warn_date_deletion)

        self.config['header_fields'] = header_fields

        # Question C: Required fields
        initiate_question("C", "Required fields")
        print("\nRequired fields will cause errors if missing during parsing.")
        print("Optional fields won't stop parsing.\n")

        for i, field in enumerate(header_fields, 1):
            print(f"  ({i}) {field}")

        print("\nWhich fields would you like to be REQUIRED for every entry?")
        print("Enter comma-separated numbers, 'ALL', or 'NONE'")
        if has_date:
            print(f"(Recommendation: include {date_field_name} for temporal analysis.)")

        required_input = input("\nRequired fields: ").strip().upper()

        if required_input == 'ALL':
            required_fields = header_fields.copy()
        elif required_input == 'NONE':
            required_fields = []
        else:
            try:
                # FIX: Remove the generator, make it a proper list comprehension
                indices = [int(n.strip()) - 1 for n in required_input.split(',') if n.strip()]
                # Validate indices
                required_fields = [header_fields[i] for i in indices if 0 <= i < len(header_fields)]
                
                # Show what was selected
                if required_fields:
                    print(f"\nSelected {len(required_fields)} required field(s):")
                    for field in required_fields:
                        print(f"  - {field}")
                else:
                    print("\nNo valid fields selected. No fields set as required.")
                    
            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}. No fields set as required.")
                required_fields = []

        self.config['required_fields'] = required_fields

        # Question Ca: Warnings for optional fields
        optional_fields = [f for f in header_fields if f not in required_fields]

        if optional_fields:
            initiate_question("Ca", "Warnings for optional fields")

            print("Show warnings when optional fields are missing?")
            if yes_or_no("You can specify which fields later if you don't want warnings for all."):
                print("\nWhich optional fields should trigger warnings?")
                for i, field in enumerate(optional_fields, 1):
                    print(f"  ({i}) {field}")

                print("\nEnter comma-separated numbers, 'ALL', or 'NONE'")
                warn_input = input("Warn for: ").strip().upper()

                if warn_input == 'ALL':
                    warning_fields = optional_fields.copy()
                elif warn_input == 'NONE':
                    warning_fields = []
                else:
                    try:
                        # FIX: Same issue here
                        indices = [int(n.strip()) - 1 for n in warn_input.split(',') if n.strip()]
                        warning_fields = [optional_fields[i] for i in indices if 0 <= i < len(optional_fields)]
                        
                        if warning_fields:
                            print(f"\nWarnings enabled for {len(warning_fields)} field(s):")
                            for field in warning_fields:
                                print(f"  - {field}")
                                
                    except (ValueError, IndexError):
                        print("Invalid input. No warning fields set.")
                        warning_fields = []
            else:
                warning_fields = []
        else:
            warning_fields = []
            
        self.config['warning_fields'] = warning_fields

    def section_1(self):
        """
        Section 1: Basic format & Entry separators
        Sets up the tag format, entry separators, and header
        """
        fancy_title("SECTION 1: Basic Format")
        
        # Question 1: Tag Format
        initiate_question("1", "Tag Format")
        print("Examples: {{{TAGNAME_}}}, [[TAGNAME]], <TAGNAME_>")
        print("\nEnter your tag format using TAGNAME as the placeholder.")

        while True:
            tag_format_input = input("Tag format: ").strip()

            # Validate
            if 'tagname' not in tag_format_input.lower():
                print("Error: Your tag format must contain 'TAGNAME' as a placeholder. Please try again.")
                continue

            if 'tagname' == tag_format_input.lower():
                print("Error: Your tag format needs something before and/or after TAGNAME. Please try again.")
                continue

            # Confirm response
            tag_parts = tag_format_input.split("tagname", maxsplit=1)  # Case-insensitive split
            # Find actual position of TAGNAME
            tagname_pos = tag_format_input.lower().find('tagname')
            prefix = tag_format_input[:tagname_pos]
            suffix = tag_format_input[tagname_pos + 7:]  # 7 = len('tagname')
            
            print("\nConfirmation:")
            print(f"Prefix: '{prefix}'")
            print(f"Suffix: '{suffix}'")
            if not yes_or_no(f"Are you sure that you want your tag format to be: '{prefix}TAGNAME{suffix}'?"):
                continue

            break

        # Question 2: Case Sensitivity
        initiate_question("2", "Case Sensitivity")
        case_sensitive = yes_or_no("Do you want your tags to be case-sensitive?")

        normalize_to = 'keep'  # ← Add default value here

        if not case_sensitive:
            # Question 2a: Normalizing tag format
            initiate_question("2a", "Normalizing tag format")
            print("\nWhen extracting tags, convert to:")
            print("  (1) UPPERCASE")
            print("  (2) lowercase")
            print("  (3) Capitalize the first letter")
            print("  (4) Keep first occurrence's casing")

            while True:
                choice = input("Choice: ").lower().strip()
                if choice == '1':
                    normalize_to = 'upper'
                    break
                elif choice == '2':
                    normalize_to = 'lower'
                    break
                elif choice == '3':
                    normalize_to = 'first'
                    break
                elif choice == '4':
                    normalize_to = 'keep'
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")

        # Now this line works regardless of case_sensitive value
        self.tag_parser = TagFormatParser(tag_format_input, case_sensitive, normalize_to)
        self.config['tag_format'] = self.tag_parser.to_dict()

        # Question 3: Entry separators
        initiate_question("3", "Entry separators")
        
        while True:
            print("How do you separate entries in your diary?")
            print("  (1) Header section with fields (DATE, PAGE_NUMBERS, etc.)")
            print("  (2) Simple separator characters only")

            choice = input("Choice: ").lower().strip()
            
            if choice == '1':
                # Question 3a: Header separators
                initiate_question("3a", "Header separators")
                
                # Get header start
                while True:
                    header_start = input("Enter characters to mark the BEGINNING of your header: ").strip()
                    if not header_start:
                        print("You must enter at least one character. Please try again.")
                        continue
                    
                    print(f"\nYou entered: '{header_start}'")
                    if yes_or_no(f"Header will begin with '{header_start}'. Correct?"):
                        break

                # Get header end
                while True:
                    header_end = input("Enter characters to mark the END of your header: ").strip()
                    if not header_end:
                        print("You must enter at least one character. Please try again.")
                        continue
                    
                    print(f"\nYou entered: '{header_end}'")
                    if yes_or_no(f"Header will end with '{header_end}'. Correct?"):
                        break

                self.config['entry_separators'] = {
                    'type': 'header',
                    'header_start': header_start,
                    'header_end': header_end
                }
                
                # Go to Section 1A for header configuration
                self.section_1a()
                break
                
            elif choice == '2':
                # Question 3b: Simple separators
                initiate_question("3b", "Entry separators")
                
                while True:
                    entry_separator = input("Enter your entry separator character(s): ").strip()
                    if not entry_separator:
                        print("You must enter at least one character. Please try again.")
                        continue
                    
                    print(f"\nYou entered: '{entry_separator}'")
                    if yes_or_no(f"Entry separator will be '{entry_separator}'. Correct?"):
                        break

                self.config['entry_separators'] = {
                    'type': 'simple',
                    'separator': entry_separator
                }
                break
                
            else:
                print("Invalid choice. Please enter 1 or 2.")
                continue

        self.sections_complete['section_1'] = True
        self.section_review(1)

    def add_relationships(self, category_name: str, 
                          relationship_type: str,
                          is_parent_side: bool) -> list[str]:
        """Add new relationships with automatic bidirectional updates"""

        print(f"\nAvailable categories:")
        # FIX THIS, does this account for relationships that are already added?
        for cat in self.category_configs.keys():
            if cat != category_name:
                print(f"  - {cat}")

        input_text = input(f"\nEnter {relationship_type} categories (comma-separated): ").strip()
        new_relations = [r.strip() for r in input_text.split(',') if r.strip()]

        # Validate
        valid_relations = []
        for rel in new_relations:
            if rel not in self.category_configs:
                print(f"Warning: '{rel}' is not a valid category. Skipping.")
            elif rel == category_name:
                print(f"Warning: Category cannot be its own {relationship_type}. Skipping.")
            else:
                valid_relations.append(rel)
        
        # Bidirectional sync
        if valid_relations:
            self.sync_bidirectional_relationships(
                category_name,
                valid_relations,
                relationship_type,
                is_parent_side,
                adding=True
            )

        return valid_relations
    
    def sync_bidirectional_relationships(self, category_name: str,
                                         related_categories: list[str],
                                         relationship_type: str,
                                         is_parent_side: bool,
                                         adding: bool):
        """
        Maintain bidirectional consistency between parent/child relationships

        Example:
            If CHARACTERS adds BOOKS as parent:
            - CHARACTERS.parent_types += [BOOKS]
            - BOOKS.child_types += [CHARACTERS]

        :param category_name: The category being modified
        :type category_name: str
        :param related_categories: Categories to link/unlink
        :type related_categories: list[str]
        :param relationship_type: "parent" or "child"
        :type relationship_type: str
        :param is_parent_side: True if category_name is parent, False if category_name is child
        :type is_parent_side: bool
        :param adding: True to add relationships, False to remove
        :type adding: bool
        """

        for related_cat in related_categories:
            if related_cat not in self.category_configs:
                continue

            related_config = self.category_configs[related_cat]

            # Determine which list to modify on the related category
            if relationship_type == "parent":
                # category_name is adding related_cat as PARENT
                # so related_cat should add category_name as CHILD
                target_list = related_config.child_types
                related_config.can_have_parents = True

            # Add or remove
            if adding:
                if category_name not in target_list:
                    target_list.append(category_name)
                    print(f"Auto-added {category_name} to {related_cat}'s {relationship_type}s")
                else:
                    if category_name in target_list:
                        target_list.remove(category_name)
                        print(f"Auto-removed {category_name} from {related_cat}'s {relationship_type}s")

            # Update the list reference
            if relationship_type == "parent":
                related_config.child_types = target_list
            else:
                related_config.parent_types = target_list
    
    def delete_relationships(self, current_list: list[str],
                             category_name: str,
                             relationship_type: str,
                             is_parent_side: bool) -> list[str]:
        """Delete relationships with warnings and bidirectional updates"""

        print(f"\nCurrent {relationship_type}s:")
        for i, rel in enumerate(current_list, 1):
            print(f"  ({i}) {rel}")

        input_text = input("\nEnter numbers to delete (comma-separated): ").strip()

        try:
            indices = [int(n.strip()) - 1 for n in input_text.split(',')]
            to_delete = [current_list[i] for i in indices if 0 <= i < len(current_list)]
        except ValueError:
            print("Invalid input. No changes made.")
            return current_list
        
        if not to_delete:
            return current_list
        
        # Show warning
        print(f"\nWARNING: Removing {len(to_delete)} {relationship_type}(s):")
        for rel in to_delete:
            print(f"  - {rel}")

        # Explain bidirectional impact
        opposite = "child" if relationship_type == "parent" else "parent"
        print(f"\nThis will also remove {category_name} as a {opposite} from:")
        for rel in to_delete:
            print(f"  - {rel}")

        if not yes_or_no("\nProceed with deletion?"):
            print("Deletion canceled.")
            # FIX THIS, well ideally this should go through for each individual thing from the list instead of canceling everything
            return current_list
        
        # Remove from current list
        updated_list = [r for r in current_list if r not in to_delete]

        # Bidirectional sync
        self.sync_bidirectional_relationships(
            category_name,
            to_delete,
            relationship_type,
            is_parent_side,
            adding=False
        )

        print(f"Removed {len(to_delete)} {relationship_type}(s)")
        return updated_list
    
    def modify_relationship_list(self, current_list: list[str],
                                 category_name: str,
                                 relationship_type: str, # "parent" or "child"
                                 is_parent_side: bool) -> list[str]:
        """
        Modify a relationship list with bidirectional updates

        :param current_list: Current parent_types or child_types
        :type current_list: list[str]
        :param category_name: The category being configured
        :type category_name: str
        :param relationship_type: "parent" or "child"
        :type relationship_type: str
        :param is_parent_side: True if category_name is the parent, False if child
        :type is_parent_side: bool
        :return: Modified parent_types or child_types
        :rtype: list[str]
        """
        print(f"\nModify {relationship_type} list:")
        print("  (1) Add more")
        print("  (2) Delete some")
        print("  (3) Keep as is")

        choice = input("Choice: ").lower().strip()

        if choice == '3':
            return current_list
        
        elif choice == '1':
            new_relationships = self.add_relationships(
                category_name,
                relationship_type,
                is_parent_side
            )
            # Merge with existing
            return list(set(current_list + new_relationships))
        
        elif choice == '2':
            return self.delete_relationships(
                current_list,
                category_name,
                relationship_type,
                is_parent_side
            )
        
        else:
            # FIX THIS MAYBE CHANGE THIS SO NOT AUTOMATICALLY END
            print("Invalid choice. Keeping current list.")
            return current_list
    
    def configure_category(self, category_name: str, num: int, total: int,
                       use_relationships: bool, use_time_based: bool, 
                       use_custom_attrs: bool):
        """
        Configure a single category with global feature flags
        """
        print(f"\n[{num}/{total}] Configuring: {category_name}")
        print("=" * 70)
        
        config = self.category_configs[category_name]

        # Q5: Parent Entities (only if relationships enabled)
        if use_relationships:
            initiate_question("5", "Parent Entities")
            print("Example: A CHARACTER belongs to a BOOK (BOOK would be the parent)")

            if config.parent_types:
                print(f"Current parents for {category_name}:")
                for parent in config.parent_types:
                    print(f"  - {parent}")
                
                if yes_or_no("Would you like to modify this list?"):
                    config.parent_types = self.modify_relationship_list(
                        config.parent_types,
                        category_name,
                        "parent",
                        is_parent_side=False
                    )
                    # Update can_have_parents based on result
                    config.can_have_parents = len(config.parent_types) > 0
            else:
                if yes_or_no(f"Can {category_name} tags have parent entities?"):
                    config.can_have_parents = True
                    config.parent_types = self.add_relationships(
                        category_name,
                        "parent",
                        is_parent_side=False
                    )

            # Q6: Child entities
            initiate_question("6", "Child Entities")
            print("Example: A BOOK contains CHARACTERS (CHARACTER would be the child)")

            if config.child_types:
                print(f"Current children for {category_name}:")
                for child in config.child_types:
                    print(f"  - {child}")
                
                if yes_or_no("Would you like to modify this list?"):
                    config.child_types = self.modify_relationship_list(
                        config.child_types,
                        category_name,
                        "child",
                        is_parent_side=True
                    )
                    # Update can_have_children based on result
                    config.can_have_children = len(config.child_types) > 0
            else:
                if yes_or_no(f"Can {category_name} tags have child entities?"):
                    config.can_have_children = True
                    config.child_types = self.add_relationships(
                        category_name,
                        "child",
                        is_parent_side=True
                    )

        # Q7: Time-based relationships (only if globally enabled)
        if use_time_based:
            initiate_question("7", "Time-based relationships")
            print("Example: 'roommate from 2019-2020'")
            config.time_based = yes_or_no(f"Can {category_name} have time-based relationships?")

        # Q8: Custom attributes (only if globally enabled)
        if use_custom_attrs:
            initiate_question("8", "Custom attributes")
            print("Examples: nicknames, relationship_categories")
            
            if yes_or_no(f"Does {category_name} have custom attributes?"):
                attrs_input = input("Enter attributes (comma-separated): ").strip()
                config.custom_attributes = [a.strip() for a in attrs_input.split(',') if a.strip()]

        # Show summary for this category
        print(f"\n{'=' * 70}")
        print(f"SUMMARY: {category_name}")
        print('=' * 70)
        print(config)

        if not yes_or_no("\nDoes this look good?"):
            print("Let's reconfigure this category")
            input("Press Enter to continue")
            self.configure_category(category_name, num, total, 
                                use_relationships, use_time_based, use_custom_attrs)
        else:
            print(f"{category_name} configured!")
            
            # Different message for last category vs others
            if num < total:
                input("\nPress Enter for next category...")
            else:
                print(f"\nAll {total} categories configured!")
                input("\nPress Enter to continue to Section Review...")

    def section_2(self):
        """
        Section 2: Configure tag categories
        """
        fancy_title("SECTION 2: Tag Categories")

        # Question 4: Category names
        initiate_question("4", "Category names")
        
        print("Examples: People, Places, Activities, Moods, etc.")
        print("\nEnter your tag category names (comma-separated)")
        print("If you would not like any tag categories, please enter 'NO CATEGORIES'")
        categories_input = input("Categories: ").strip()

        if categories_input.upper() == 'NO CATEGORIES':
            self.category_configs = {}
            print("\nNo categories configured.")
            self.sections_complete['section_2'] = True
            self.section_review(2)
            return
        
        categories_names = [c.strip() for c in categories_input.split(',') if c.strip()]
        
        if not categories_names:
            self.category_configs = {}
            print("\nNo categories configured.")
            self.sections_complete['section_2'] = True
            self.section_review(2)
            return
        
        # Confirm categories
        print(f"\nYou entered {len(categories_names)} categories:")
        for cat in categories_names:
            print(f"  - {cat}")

        if not yes_or_no("Is this correct?"):
            categories_names = ListManager.manage_list(categories_names, "category")

        # Initialize category configs
        self.category_configs = {name: CategoryConfig(name) for name in categories_names}

        # === GLOBAL QUESTIONS (asked once for all categories) ===
        print("\n" + "=" * 70)
        print("CONFIGURATION PREFERENCES")
        print("=" * 70)
        print("The following questions determine which features you'll configure")
        print("for your categories. Answer 'no' to skip entire sections.\n")

        # Global flags
        use_relationships = yes_or_no("Do you want ANY categories to have parent/child relationships?\n" +
                                    "(e.g., CHARACTER belongs to BOOK, BOOK contains CHARACTERS)")
        use_time_based = yes_or_no("Do you want ANY categories to have time-based relationships?\n" +
                                    "(e.g., 'roommate from 2019-2020')")
        use_custom_attrs = yes_or_no("Do you want ANY categories to have custom attributes?\n" +
                                    "(e.g., nicknames, relationship_categories)")

        print("\n" + "=" * 70)
        print("Now let's configure each category...")
        input("Press Enter to continue")

        # Configure each category with global flags
        for i, name in enumerate(categories_names, 1):
            self.configure_category(
                name, i, len(categories_names),
                use_relationships, use_time_based, use_custom_attrs
            )

        self.sections_complete['section_2'] = True
        self.section_review(2)

    def section_review(self, section_num: int):
        """
        Review a completed section

        :param section_num: number for the section just completed
        :type section_num: int
        """
        while True:
            print("\n")
            fancy_title(f"SECTION {section_num} REVIEW")

            # Show all completed sections up to this one
            for i in range(1, section_num + 1):
                self.show_section_summary(i)

            print("Options:")
            if section_num < 2:  # Changed from < 3
                print(f"  (c) Continue to Section {section_num + 1}")
            else:
                print("  (c) Continue to Final Review")
            print(f"  ({section_num}) Edit Section {section_num}")
            if section_num > 1:
                for i in range(section_num - 1, 0, -1):
                    print(f"  ({i}) Edit Section {i}")
            print("  (s) Start over")

            choice = input("\nChoice: ").lower().strip()

            if choice == 'c':
                return  # Continue to next section
            elif choice == str(section_num):  # Convert to string for comparison
                self.edit_section(section_num)
            elif choice.isdigit() and 1 <= int(choice) < section_num:
                self.edit_section(int(choice))
            elif choice == 's':
                if yes_or_no("Are you sure you want to start over? All progress will be lost."):
                    self.run()
                    return
            else:
                print("Invalid choice. Please try again.")

    def show_section_summary(self, section_num: int):
        """
        Display summary of a section
        :param section_num: section number
        :type section_num: int
        """
        if section_num == 1:
            fancy_title("SECTION 1 Summary")
            
            # Tag format info
            if 'tag_format' in self.config:
                tf = self.config['tag_format']
                print(f"  Tag format: {tf['format_string']}")
                print(f"  Prefix: '{tf['prefix']}'")
                print(f"  Suffix: '{tf['suffix']}'")
                print(f"  Case-sensitive: {tf['case_sensitive']}")
                if not tf['case_sensitive']:
                    normalize_map = {
                        'upper': 'UPPERCASE',
                        'lower': 'lowercase',
                        'first': 'Capitalize first letter',
                        'keep': 'Keep original casing'
                    }
                    print(f"  Normalization: {normalize_map.get(tf['normalize_to'], tf['normalize_to'])}")
            
            # Entry separator info
            if 'entry_separators' in self.config:
                e_sep = self.config['entry_separators']
                print()  # Blank line for readability
                if e_sep['type'] == 'header':
                    print(f"  Entry format: Headers")
                    print(f"  Header start: '{e_sep['header_start']}'")
                    print(f"  Header end: '{e_sep['header_end']}'")
                    
                    # Show header configuration if it exists
                    if 'date_field' in self.config:
                        df = self.config['date_field']
                        if df['enabled']:
                            print(f"  Date field: '{df['field_name']}' (format: {df['format']})")
                    
                    if 'header_fields' in self.config:
                        print(f"  Header fields ({len(self.config['header_fields'])}): {', '.join(self.config['header_fields'])}")
                    
                    if 'required_fields' in self.config:
                        req = self.config['required_fields']
                        if req:
                            print(f"  Required fields: {', '.join(req)}")
                        else:
                            print(f"  Required fields: none")
                    
                    # Show warning fields
                    if 'warning_fields' in self.config:
                        warn = self.config['warning_fields']
                        optional_count = len(self.config.get('header_fields', [])) - len(self.config.get('required_fields', []))
                        if optional_count == 0:
                            print(f"  Optional field warnings: N/A (all fields required)")
                        elif warn:
                            print(f"  Optional field warnings: {', '.join(warn)}")
                        else:
                            print(f"  Optional field warnings: none")
                else:
                    print(f"  Entry format: Simple separators")
                    print(f"  Entry separator: '{e_sep['separator']}'")
            print()

        elif section_num == 2:
            fancy_title("SECTION 2 Summary")
            
            if not self.category_configs:
                print("  No categories configured")
            else:
                print(f"  Categories ({len(self.category_configs)}):")
                for name, config in self.category_configs.items():
                    print(f"    {config}")
            print()

    def edit_section_granular(self, section_num: int):
        """Granular editing interface for sections"""
        
        if section_num == 1:
            self._edit_section_1_granular()
        elif section_num == 2:
            self._edit_section_2_granular()

    def _edit_section_1_granular(self):
        """Granular editor for Section 1"""
        while True:
            print("\n" + "=" * 70)
            print("EDIT SECTION 1")
            print("=" * 70)
            
            # Show current config
            self.show_section_summary(1)
            
            print("\nWhat would you like to edit?")
            print("  (1) Tag format & case sensitivity (Q1-Q2)")
            print("  (2) Entry separators (Q3)")
            
            if self.config.get('entry_separators', {}).get('type') == 'header':
                print("  (3) Header configuration (Q3a, Date, Fields, etc.)")
            
            print("  (r) Redo entire section from scratch")
            print("  (d) Done editing")
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == '1':
                self._edit_tag_format()
            elif choice == '2':
                self._edit_entry_separators()
            elif choice == '3' and self.config.get('entry_separators', {}).get('type') == 'header':
                self._edit_header_config()
            elif choice == 'r':
                if yes_or_no("Redo entire Section 1? This will clear all Section 1 data."):
                    self.section_1()
                    return
            elif choice == 'd':
                return
            else:
                print("Invalid choice.")

    def _edit_tag_format(self):
        """Edit just tag format and case sensitivity"""
        print("\n" + "=" * 70)
        print("EDITING: Tag Format & Case Sensitivity")
        print("=" * 70)
        
        # Show current
        if 'tag_format' in self.config:
            tf = self.config['tag_format']
            print(f"\nCurrent tag format: {tf['format_string']}")
            print(f"Case-sensitive: {tf['case_sensitive']}")
            if not tf['case_sensitive']:
                print(f"Normalization: {tf['normalize_to']}")
        
        if not yes_or_no("\nChange tag format settings?"):
            return
        
        # Re-run Q1 and Q2
        # (Copy the Q1 and Q2 code from section_1 here)
        initiate_question("1", "Tag Format")
        print("Examples: {{{TAGNAME_}}}, [[TAGNAME]], <TAGNAME_>")
        print("\nEnter your tag format using TAGNAME as the placeholder.")

        while True:
            tag_format_input = input("Tag format: ").strip()

            if 'tagname' not in tag_format_input.lower():
                print("Error: Must contain 'TAGNAME'. Please try again.")
                continue

            if 'tagname' == tag_format_input.lower():
                print("Error: Need something before/after TAGNAME. Please try again.")
                continue

            tagname_pos = tag_format_input.lower().find('tagname')
            prefix = tag_format_input[:tagname_pos]
            suffix = tag_format_input[tagname_pos + 7:]
            
            print(f"\nPrefix: '{prefix}', Suffix: '{suffix}'")
            if yes_or_no(f"Confirm tag format: '{prefix}TAGNAME{suffix}'?"):
                break

        # Q2: Case sensitivity
        initiate_question("2", "Case Sensitivity")
        case_sensitive = yes_or_no("Case-sensitive tags?")
        
        normalize_to = 'keep'
        if not case_sensitive:
            initiate_question("2a", "Normalization")
            print("  (1) UPPERCASE")
            print("  (2) lowercase")
            print("  (3) Capitalize first")
            print("  (4) Keep original")
            
            while True:
                choice = input("Choice: ").strip()
                if choice == '1':
                    normalize_to = 'upper'
                    break
                elif choice == '2':
                    normalize_to = 'lower'
                    break
                elif choice == '3':
                    normalize_to = 'first'
                    break
                elif choice == '4':
                    normalize_to = 'keep'
                    break
                else:
                    print("Invalid. Enter 1-4.")
        
        self.tag_parser = TagFormatParser(tag_format_input, case_sensitive, normalize_to)
        self.config['tag_format'] = self.tag_parser.to_dict()
        
        print("\n✓ Tag format updated!")
        input("Press Enter to continue...")

    def _edit_entry_separators(self):
        """Edit entry separator type"""
        print("\n" + "=" * 70)
        print("EDITING: Entry Separators")
        print("=" * 70)
        
        current = self.config.get('entry_separators', {})
        if current.get('type') == 'header':
            print(f"\nCurrent: Header format")
            print(f"  Start: '{current.get('header_start')}'")
            print(f"  End: '{current.get('header_end')}'")
        else:
            print(f"\nCurrent: Simple separator")
            print(f"  Separator: '{current.get('separator')}'")
        
        print("\nWARNING: Changing separator type will reset header configuration!")
        if not yes_or_no("Change entry separator settings?"):
            return
        
        # Re-run Q3 logic (copy from section_1)
        initiate_question("3", "Entry separators")
        
        while True:
            print("How do you separate entries?")
            print("  (1) Header section")
            print("  (2) Simple separators")
            
            choice = input("Choice: ").strip()
            
            if choice == '1':
                # Get header markers
                while True:
                    header_start = input("Header start characters: ").strip()
                    if header_start and yes_or_no(f"Use '{header_start}'?"):
                        break
                
                while True:
                    header_end = input("Header end characters: ").strip()
                    if header_end and yes_or_no(f"Use '{header_end}'?"):
                        break
                
                self.config['entry_separators'] = {
                    'type': 'header',
                    'header_start': header_start,
                    'header_end': header_end
                }
                
                # Offer to configure header
                if yes_or_no("Configure header fields now?"):
                    self.section_1a()
                
                break
                
            elif choice == '2':
                while True:
                    separator = input("Entry separator: ").strip()
                    if separator and yes_or_no(f"Use '{separator}'?"):
                        break
                
                self.config['entry_separators'] = {
                    'type': 'simple',
                    'separator': separator
                }
                
                # Clear header config if exists
                self.config.pop('date_field', None)
                self.config.pop('header_fields', None)
                self.config.pop('required_fields', None)
                self.config.pop('warning_fields', None)
                
                break
            else:
                print("Invalid. Enter 1 or 2.")
        
        print("\n✓ Entry separators updated!")
        input("Press Enter to continue...")

    def _edit_header_config(self):
        """Edit header fields configuration"""
        print("\n" + "=" * 70)
        print("EDITING: Header Configuration")
        print("=" * 70)
        
        # Show current header config
        if 'date_field' in self.config:
            df = self.config['date_field']
            if df['enabled']:
                print(f"\nDate field: '{df['field_name']}' ({df['format']})")
        
        if 'header_fields' in self.config:
            print(f"Header fields: {', '.join(self.config['header_fields'])}")
        
        if 'required_fields' in self.config:
            req = self.config['required_fields']
            print(f"Required: {', '.join(req) if req else 'none'}")
        
        print("\nWhat would you like to edit?")
        print("  (1) Date field settings")
        print("  (2) Header field list")
        print("  (3) Required fields")
        print("  (4) Warning fields")
        print("  (5) Redo entire header config")
        print("  (b) Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            self._edit_date_field()
        elif choice == '2':
            self._edit_header_field_list()
        elif choice == '3':
            self._edit_required_fields()
        elif choice == '4':
            self._edit_warning_fields()
        elif choice == '5':
            if yes_or_no("Redo entire header config?"):
                self.section_1a()
        elif choice == 'b':
            return
        else:
            print("Invalid choice.")

    def _edit_date_field(self):
        """Edit date field settings"""
        print("\n" + "-" * 50)
        current = self.config.get('date_field', {})
        
        if current.get('enabled'):
            print(f"Current date field: '{current['field_name']}' ({current['format']})")
            print("\n  (1) Change name")
            print("  (2) Change format")
            print("  (3) Disable date field")
            print("  (b) Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                new_name = input(f"New name (current: '{current['field_name']}'): ").strip()
                if new_name:
                    old_name = current['field_name']
                    current['field_name'] = new_name
                    
                    # Update in header_fields list
                    if 'header_fields' in self.config and old_name in self.config['header_fields']:
                        idx = self.config['header_fields'].index(old_name)
                        self.config['header_fields'][idx] = new_name
                    
                    print(f"✓ Renamed to '{new_name}'")
            
            elif choice == '2':
                # Show format options (copy from section_1a)
                # ... (implement format selection)
                pass
            
            elif choice == '3':
                if yes_or_no("Disable date field? You'll lose temporal analysis."):
                    current['enabled'] = False
                    if 'header_fields' in self.config and current['field_name'] in self.config['header_fields']:
                        self.config['header_fields'].remove(current['field_name'])
                    print("✓ Date field disabled")
        else:
            if yes_or_no("Enable date field?"):
                # Run date field setup
                pass

    def _edit_header_field_list(self):
        """Edit the list of header fields"""
        print("\n" + "-" * 50)
        
        if 'header_fields' not in self.config:
            print("No header fields configured.")
            return
        
        # Use ListManager with date field protection
        def warn_date_deletion(items_to_delete):
            date_field = self.config.get('date_field', {}).get('field_name')
            if date_field and date_field in items_to_delete:
                print(f"\nWARNING: Deleting date field '{date_field}'!")
                return yes_or_no("Are you sure?")
            return True
        
        self.config['header_fields'] = ListManager.manage_list(
            self.config['header_fields'],
            "header field",
            warn_date_deletion
        )
        
        print("✓ Header fields updated")

    def _edit_required_fields(self):
        """Edit required fields list"""
        # Similar to _edit_header_field_list but for required_fields
        pass

    def _edit_warning_fields(self):
        """Edit warning fields list"""
        # Similar implementation
        pass

    def _edit_section_2_granular(self):
        """Granular editor for Section 2 (Categories)"""
        while True:
            print("\n" + "=" * 70)
            print("EDIT SECTION 2")
            print("=" * 70)
            
            self.show_section_summary(2)
            
            print("\nWhat would you like to edit?")
            print("  (1) Add new category")
            print("  (2) Delete category")
            print("  (3) Reconfigure existing category")
            print("  (4) Rename category")
            print("  (r) Redo entire section")
            print("  (d) Done editing")
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == '1':
                self._add_category()
            elif choice == '2':
                self._delete_category()
            elif choice == '3':
                self._reconfigure_category()
            elif choice == '4':
                self._rename_category()
            elif choice == 'r':
                if yes_or_no("Redo entire Section 2?"):
                    self.section_2()
                    return
            elif choice == 'd':
                return
            else:
                print("Invalid choice.")

    def _add_category(self):
        """Add a new category"""
        # Implementation
        pass

    def _delete_category(self):
        """Delete a category with dependency warnings"""
        # Implementation
        pass

    def _reconfigure_category(self):
        """Reconfigure an existing category"""
        # Implementation with selection menu
        pass

    def _rename_category(self):
        """Rename a category and update all references"""
        # Implementation
        pass

    def edit_section(self, section_num: int):
        """Edit a specific section"""
        self.edit_section_granular(section_num)

    def final_review(self):
        """Final review before saving"""
        while True:
            fancy_title("FINAL REVIEW")
        
            # show all sections
            self.show_section_summary(1)
            self.show_section_summary(2)

            print("\nOptions:")
            print("  (s) Save configuration")
            print("  (1) Edit Section 1")
            print("  (2) Edit Section 2")
            print("  (r) Start over")
            print("  (q) Quit without saving")

            choice = input("\nChoice: ").lower().strip()
                
            if choice == 's':
                self.save_configuration()
                return
            elif choice in ['1', '2']:
                self.edit_section(int(choice))
            elif choice == 'r':
                if yes_or_no("Are you sure you want to start over? All progress will be lost."):
                    self.run()
                    return
            elif choice == 'q':
                if yes_or_no("Are you sure you want to quit without saving? All progress will be lost?"):
                    print("\nConfiguration not saved. Exiting")
                    return
            else:
                print("Invalid choice.")
                input("Press Enter to continue")

    def save_configuration(self):
        """Save configuration to JSON file"""
        # Compile category configs into the main config
        self.config['tag_categories'] = {
            name: config.to_dict()
            for name, config in self.category_configs.items()
        }

        # Ask for filename
        default_filename = "diary_config.json"
        filename = input(f"\nSave as (default: {default_filename}): ").strip()
        if not filename:
            filename = default_filename
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Check if file exists
        if os.path.exists(filename):
            if not yes_or_no(f"File '{filename}' exists. Overwrite?"):
                print("Save cancelled.")
                input("Press Enter to continue")
                return
        
        # Save to file
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print("\n" + "=" * 70)
            print("✓ CONFIGURATION SAVED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\nFile: {filename}")
            print(f"Location: {os.path.abspath(filename)}")
            
            self.show_next_steps()
            
        except Exception as e:
            print(f"\n✗ Error saving configuration: {e}")
            input("Press Enter to continue...")
    
    def show_next_steps(self):
        """Display next steps after saving"""
        print("\n" + "-" * 70)
        print("NEXT STEPS:")
        print("-" * 70)
        print("1. Run the Tag Classifier to extract and classify tags from your diary")
        print("2. Use the Analysis Engine to analyze your entries")
        print("\nYou can always re-run this Configuration Builder to modify settings.")
        print("-" * 70)
        print("\nThank you for using the Diary Analysis System!")
        print("=" * 70 + "\n")


# ===================================
# MAIN ENTRY POINT
# ===================================
    
if __name__ == "__main__":
        builder = ClassSysBuilder()
        builder.run()