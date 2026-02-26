class ListManager:
    """Reusable interface for managing lists"""

    @staticmethod
    def show_list(items: list[str], title: str = "Current items"):
        """Display a numbered list"""
        print(f"\n{title}:")
        if not items:
            print("  (empty)")
            return
        for i, item in enumerate(items, 1):
            print(f"  ({i}) {item}")

    @staticmethod
    def manage_list(items: list[str], item_type: str = "item", on_delete_callback=None) -> list[str]:
        """
        Interactive list management
        Returns modified list
        """
        items = items.copy()

        while True:
            ListManager.show_list(items, f"Current {item_type}s")

            print(f"\nOptions:")
            print(f"  (1) Add {item_type}")
            print(f"  (2) Delete {item_type}")
            print(f"  (3) Modify {item_type}")
            print(f"  (4) Continue (looks good)")

            choice = input("\nChoice: ").lower().strip()

            if choice == '1':
                items = ListManager._add_item(items, item_type)
                continue
            elif choice == '2':
                items = ListManager._delete_item(items, item_type, on_delete_callback)
                continue
            elif choice == '3':
                items = ListManager._modify_item(items, item_type)
                continue
            elif choice == '4':
                return items
            else:
                print("Invalid choice. Please try again.")
                continue

    @staticmethod
    def _add_item(items: list[str], item_type: str) -> list[str]:
        """Add new item to list"""
        new_items_input = input(f"Enter new {item_type}(s) (comma-separated): ").strip()

        if not new_items_input: 
            print("Empty input. Nothing added.")
            return items

        new_items = [n.strip() for n in new_items_input.split(',') if n.strip()]

        for n in new_items:
            # Case-insensitive duplicate check
            if any(n.lower() == existing.lower() for existing in items):
                print(f"'{n}' already exists in the list of {item_type}s and was not added.")
            else:
                items.append(n)
                print(f"Successfully added '{n}'!")
        
        return items
    
    @staticmethod
    def _delete_item(items: list[str], item_type: str, on_delete_callback=None) -> list[str]:
        """Delete item from list with optional pre-delete warnings"""
        if not items:
            print(f"The list of {item_type}s is empty, so items cannot be deleted!")
            return items
        
        try:
            del_items_input = input(f"Enter number(s) to delete (comma-separated): ").strip()
            del_indices = [int(d.strip()) for d in del_items_input.split(',') if d.strip()]
            
            # Validate ALL indices BEFORE deleting anything
            valid_indices = []
            for d in del_indices:
                if d < 1 or d > len(items):
                    print(f"Number {d} is out of range (valid: 1-{len(items)}) and will be skipped.")
                else:
                    valid_indices.append(d)
            
            if not valid_indices:
                print("No valid items to delete.")
                return items
            
            # Check for warnings via callback
            if on_delete_callback:
                items_to_delete = [items[i - 1] for i in valid_indices]
                if not on_delete_callback(items_to_delete):
                    print("Deletion cancelled.")
                    return items
            
            # Sort in reverse order so we delete from end to beginning
            for d in sorted(valid_indices, reverse=True):
                removed = items.pop(d - 1)
                print(f"Removed '{removed}'!")

            return items

        except ValueError:
            print("Invalid input. Use numbers separated by commas.")
            return items
    
    @staticmethod
    def _modify_item(items: list[str], item_type: str) -> list[str]:
        """Modify existing item"""
        if not items:
            print(f"The list of {item_type}s is empty, so items cannot be modified!")
            return items
        
        try:
            mod_items_input = input(f"Enter number(s) to modify (comma-separated): ").strip()
            mod_indices = [int(m.strip()) for m in mod_items_input.split(',') if m.strip()]
            
            # Validate ALL indices first
            valid_indices = []
            for m in mod_indices:
                if m < 1 or m > len(items):
                    print(f"Number {m} is out of range (valid: 1-{len(items)}) and will be skipped.")
                else:
                    valid_indices.append(m)
            
            if not valid_indices:
                print("No valid items to modify.")
                return items
            
            # Modify each valid item
            for i, m in enumerate(valid_indices, 1):
                print(f"\nModifying item {i} of {len(valid_indices)}")
                old_name = items[m - 1]  # Convert to 0-indexed
                
                while True:
                    new_name = input(f"Current name: '{old_name}'\nNew name: ").strip()

                    if not new_name:
                        print("Empty input, please try again.")
                        continue

                    if new_name in items:
                        print(f"'{new_name}' already exists! Please try again.")
                        continue

                    items[m - 1] = new_name  # Convert to 0-indexed
                    print(f"✓ Renamed: '{old_name}' → '{new_name}'")
                    break

            return items

        except ValueError:
            print("Invalid input. Use numbers separated by commas.")
            return items

def fancy_title(title : str):
    """
    Generates an aesthetically pleasing title with the inputted text
    
    :param title: inputted text for the title
    :type title: str
    """
    print("=" * 15 + title + "=" * 15)

def yes_or_no(prompt : str) -> bool:
    """
    Asks a yes/no question

    :param prompt: the question being asked
    :type prompt: str
    :return: whether user responded yes or no
    :rtype: bool
    """
    yn_req = " Please answer Y or N.\n"
    while True:
        response = input(prompt + yn_req).lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print(yn_req)

def initiate_question(q_num : str, q_topic : str):
    """
    Marks the beginning of a question
    
    :param q_num: Question number
    :type q_num: str
    :param q_topic: the topic of the question
    :type q_topic: str
    """
    print(f"\nQ{q_num}: {q_topic}")
    print("-" * 35)