#    Pyrectory (misc.py)
#    Copyright (C) 2024 MrBeam89_
#
#    This file is part of Pyrectory
#
#    Pyrectory is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pyrectory is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Pyrectory. If not, see <https://www.gnu.org/licenses/>.

import re

SEARCH_BY_NAME = 0
SEARCH_BY_PHONE = 1
SEARCH_BY_EMAIL = 2
SEARCH_BY_FAVORITE = 3

def is_entry_info_valid(entry_list:list, original_name:str, name:str, phone:str, email:str, is_add:bool)->dict:
    """
    Check if the given entry information is valid.

    Args:
        entry_list (list): The list of existing entries.
        name (str): The name of the entry to check.
        phone (str): The phone number of the entry to check.
        email (str): The email address of the entry to check.
        is_add (bool): Indicates whether the entry is being added (True) or edited (False).

    Returns:
        dict: A dictionary with two keys: 'is_valid' (bool) and 'message_info' (str).
               'is_valid' is True if the entry information is valid, False otherwise.
               'message_info' is a message indicating the reason for the validation failure,
               if any.
    """
    # Check if name is empty
    if not name:
        return {"is_valid": False,
                "message_info": ("Empty name!")}

    # Check if name already exists in the list and if it is being added or if it is being edited and the name has changed
    elif (is_add and entry_already_exists(name, entry_list)) or (not is_add and (name != original_name and entry_already_exists(name, entry_list))):
        return {"is_valid": False,
                "message_info": ("Entry with this name already exists!")}

    # Check if at least one of phone or email is provided
    elif not(phone or email):
        return {"is_valid": False,
                "message_info": ("No phone number or e-mail address provided!")}

    # Check if phone number is valid
    elif phone and not phone.isdigit():
        return {"is_valid": False,
                "message_info": ("Invalid phone number!")}

    # Check if email address is valid
    elif email and not is_valid_email(email):
        return {"is_valid": False,
                "message_info": ("Invalid e-mail address!")}

    # If all checks pass, return valid result
    else:
        return {"is_valid": True,
                "message_info": ("")}


def is_valid_email(email:str)->bool:
    """
    Check if the given email address is valid.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(pattern, email) is not None # Renvoie True ou False pour une adresse valide/non-valide

def entry_already_exists(name, list_store)->bool:
    """
    Check if an entry with the given name already exists in the list store.

    Parameters:
        name (str): The name of the entry to check.
        list_store (Gtk.ListStore): The list store containing the entries.

    Returns:
        bool: True if an entry with the given name exists in the list store, False otherwise.
    """
    name_list = [entry[:][0] for entry in list_store]
    return name in name_list


def search(search_criteria: str, search_by: int, entry_list, search_results) -> None:
    """
    Search for entries in the given list store that match the search criteria.

    Args:
        search_criteria (str): The criteria to search for.
        search_by (int): The index of the list to search by.
        entry_list (List[List[str]]): The list of entries to search in.
        search_results (Gtk.ListStore): The list store to store the search results.

    Returns:
        None
    """
    # Clear the search results list store
    search_results.clear()

    # Iterate through each entry in the list store
    for entry in entry_list:
        entry_content = entry[:]

        # Check if the search criteria is in the search_by index or if the search criteria is equal to the search_by index
        if (search_by != SEARCH_BY_FAVORITE and search_criteria in entry_content[search_by]) or (search_criteria == entry_content[search_by]):
            # If the criteria is found, add the entry to the search results list store
            search_results.append(entry_content)
