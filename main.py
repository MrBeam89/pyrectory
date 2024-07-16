#!/usr/bin/env python3
#    Pyrectory (main.py)
#    Copyright (C) 2024 MrBeam89_
#
#    This file is part of Pyrectory
#
#    Pyrectory is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pyrectory is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Pyrectory. If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os

import csv_func
import misc

# Allows for the program to be ran from any working directory
APP_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
GLADE_DIRECTORY = "res"
GLADE_FILENAME = "ui.glade"
GLADE_FILEPATH = os.path.join(APP_DIRECTORY, GLADE_DIRECTORY, GLADE_FILENAME)
directory_filepath = ""

# Constants for the help window message
NEW_BUTTON_HELP_EXPLANATION = "Create a new entry directory (CSV file)"
OPEN_BUTTON_HELP_EXPLANATION = "Open an existing entry directory (CSV file)"
SAVE_BUTTON_HELP_EXPLANATION = "Save modifications made to the directory"
ADD_BUTTON_HELP_EXPLANATION = "Add a new entry to the directory"
REMOVE_BUTTON_HELP_EXPLANATION = "Remove an entry from the directory"
EDIT_BUTTON_HELP_EXPLANATION = "Edit an entry in the directory"
SEARCH_BUTTON_HELP_EXPLANATION = "Search for an entry in the directory"
HELP_BUTTON_HELP_EXPLANATION = "Show this help window"
ABOUT_BUTTON_HELP_EXPLANATION = "Show information about the program"

global is_file_open, is_unsaved, is_search_result
is_file_open = False
is_unsaved = False
is_search_result = False

search_results = Gtk.ListStore(str, str, str, str)

def summon_message_win(**kwargs):
    """
    Summon a message popup window.

    Args:
        **kwargs:
            - title (str): Title of the window.
            - message (str): Message to display.
            - set_transient_for (Gtk.Window, optional): Only optional for main window, to fix window not appearing on the front.
    """
    
    # Create a builder and load the Glade file.
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_FILEPATH)

    # Connect the signals
    builder.connect_signals(handlers)

    # Get the message window object from the builder.
    message_win = builder.get_object("message_win")

    # Set the transient window if provided.
    set_transient_for = kwargs.get("set_transient_for", None)
    if set_transient_for:
        message_win.set_transient_for(set_transient_for)

    # Set the title and message of the window.
    message_win.set_title(kwargs["title"])
    label_message_win = builder.get_object("label_message_win")
    label_message_win.set_text(kwargs["message"])

    # Show the window and make it appear on top of other windows.
    message_win.show_all()
    message_win.present()


def on_main_win_delete_event(widget, event):
    """
    Handle the delete event of the main window.

    If the file has not been saved, show a confirmation dialog with options to either cancel or save before closing.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.
        event (Gtk.DeleteEvent): The delete event.

    Returns:
        bool: True if the event was handled, False otherwise.
    """

    # Check if the file has been saved
    if not is_unsaved:
        return False

    # Load the confirmation dialog from the Glade file
    builder.add_from_file(GLADE_FILEPATH)
    global confirm_close_win
    confirm_close_win = builder.get_object("confirm_close_win")

    # Connect the signals
    builder.connect_signals(handlers)

    # Show the confirmation dialog
    confirm_close_win.show_all()
    return True


def on_no_button_confirm_close_win_clicked(widget):
    """
    This function is called when the "No" button is clicked in the confirmation dialog. It destroys the confirmation dialog.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.
    """

    # Destroy the confirmation dialog
    confirm_close_win.destroy()


def on_yes_button_confirm_close_win_clicked(widget):
    """
    This function is called when the "Yes" button is clicked in the confirmation dialog. It destroys the main window and quits the application.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.
    """

    # Destroy the main window
    main_win.destroy()

    # Quit the application
    Gtk.main_quit()


def on_new_button_main_win_clicked(widget, entry_list):
    """
    This function is called when the "New" button is clicked. It checks if there are unsaved changes and if so, it shows an error message. If there are no unsaved changes, it opens a filechooser window to save a new file.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.
        entry_list (Gtk.ListStore): The list store containing the entries.

    Returns:
        None
    """

    # Check if there are unsaved changes
    if is_unsaved:
        # If there are unsaved changes, show an error message
        summon_message_win(title="Error", message="You have unsaved changes!", set_transient_for=main_win)
        return

    # Initiate the window
    builder.add_from_file(GLADE_FILEPATH)
    save_filechooser_win = builder.get_object("save_filechooser_win")
    builder.connect_signals(handlers)

    # Set the filechooser action to save the file and show the dialog
    save_filechooser_win.set_action(Gtk.FileChooserAction.SAVE)

    # Run the dialog
    response = save_filechooser_win.run()

    # If OK button clicked and overwrite confirmed
    if response == Gtk.ResponseType.OK:
        global directory_filepath, is_file_open

        # Get the filename from the filechooser window
        directory_filepath = save_filechooser_win.get_filename()

        # Write the content of the entry list to the file
        csv_func.write_content_csv(directory_filepath, entry_list)

        # Set is_file_open to True to indicate that a file has been opened
        is_file_open = True

        # Close the filechooser window
        save_filechooser_win.destroy()

    # If Cancel button clicked or closed the window
    elif response == Gtk.ResponseType.CANCEL:
        # Close the filechooser window
        save_filechooser_win.destroy()


def on_open_button_main_win_clicked(widget):
    """
    This function is called when the "Open" button is clicked. It checks if a file is open, and if so, it opens the file and populates the entry list with its contents.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.

    Returns:
        None
    """

    # Check if a file has unsaved changes
    if is_unsaved:
        summon_message_win(title="Error", message="You have unsaved changes!", set_transient_for=main_win)
        return
    
    # Initiate the window
    builder.add_from_file(GLADE_FILEPATH)
    open_filechooser_win = builder.get_object("open_filechooser_win")
    builder.connect_signals(handlers)
    
    # Set the filechooser action to open the file and show the dialog
    open_filechooser_win.set_action(Gtk.FileChooserAction.OPEN)

    # Run the dialog
    response = open_filechooser_win.run()

    # If OK button clicked and overwrite confirmed
    if response == Gtk.ResponseType.OK:
        global directory_filepath, is_file_open
        directory_filepath = open_filechooser_win.get_filename()
        content_csv = csv_func.get_content_csv(directory_filepath)
    
        # Clear the entry list and populate it with the contents of the file
        open_filechooser_win.destroy()
        entry_list.clear()
        try:
            for entry in content_csv:
                entry_list.append(entry)
        except ValueError:
            # If the file is invalid, show an error message
            summon_message_win(title="Error", message="Invalid CSV file!", set_transient_for=main_win)
            return

        is_file_open = True
        main_win.set_title(f"Pyrectory - {directory_filepath}")

    # If Cancel button clicked or closed the window
    elif response == Gtk.ResponseType.CANCEL:
        open_filechooser_win.destroy()


def on_save_button_main_win_clicked(widget, entry_list):
    """
    This function is called when the "Save" button is clicked. It checks if a file is open, and if so, it saves the contents of the entry list to the file.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.
        entry_list (Gtk.ListStore): The list store containing the entries.

    Returns:
        None
    """

    # Check if a file is open
    if not is_file_open:
        # If no file is open, show an error message
        summon_message_win(title="Error", message="No file is open!", set_transient_for=main_win)
        return

    # Save the contents of the entry list to the file
    global directory_filepath, is_unsaved
    csv_func.write_content_csv(directory_filepath, entry_list)

    # Set is_unsaved to False to indicate that the file has been saved
    is_unsaved = False

def on_add_button_main_win_clicked(widget):
    """
    This function is called when the "Add" button is clicked. It creates a new window using a Glade file and connects it to the main window. The new window allows the user to add a new entry to the contact list.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.

    Returns:
        None
    """
    if not is_file_open:
        summon_message_win(title="Error", message="No file is open!", set_transient_for=main_win)
        return

    builder.add_from_file(GLADE_FILEPATH)

    global add_entry_win, name_entry_add_entry_win, phone_entry_add_entry_win, email_entry_add_entry_win, favorite_checkbutton_add_entry_win
    add_entry_win = builder.get_object("add_entry_win")
    name_entry_add_entry_win = builder.get_object("name_entry_add_entry_win")
    phone_entry_add_entry_win = builder.get_object("phone_entry_add_entry_win")
    email_entry_add_entry_win = builder.get_object("email_entry_add_entry_win")
    favorite_checkbutton_add_entry_win = builder.get_object("favorite_checkbutton_add_entry_win")

    builder.connect_signals(handlers)
    add_entry_win.show_all()


def on_add_button_add_entry_win_clicked(widget, entry_list):
    """
    This function is called when the "Add" button in the add entry window is clicked. It retrieves the values from the name, phone, email, and favorite checkbutton entries, and performs validation checks on the inputs. If the inputs are valid, it creates a new entry list item and appends it to the existing entries list.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.
        entry_list (Gtk.ListStore): The list of existing entries.

    Returns:
        None
    """
    name = name_entry_add_entry_win.get_text().strip()
    phone = phone_entry_add_entry_win.get_text().strip()
    email = email_entry_add_entry_win.get_text().strip()
    is_favorite = favorite_checkbutton_add_entry_win.get_active()

    entry_info_validity = misc.is_entry_info_valid(entry_list, None, name, phone, email, True)
    if entry_info_validity["is_valid"]:
        new_entry = [name, phone, email, "☆" if is_favorite else ""]
        entry_list.append(new_entry)

        global is_unsaved
        is_unsaved = True
    else:
        summon_message_win(title="Error", message=entry_info_validity["message_info"], set_transient_for=add_entry_win)


def on_remove_button_main_win_clicked(widget, entry_treeview):
    """
    Remove the selected entry from the entry_treeview when the remove button is clicked.

    Args:
        widget (Gtk.Button): The remove button widget.
        entry_treeview (Gtk.TreeView): The tree view widget displaying the entries.

    Returns:
        None
    """
    selection = entry_treeview.get_selection()
    model, treeiter = selection.get_selected()
    if treeiter:
        model.remove(treeiter)
        global is_unsaved
        is_unsaved = True


def on_edit_button_main_win_clicked(widget, entry_treeview):
    """
    Edit the selected entry in the entry_treeview when the edit button is clicked.

    Args:
        widget (Gtk.Button): The edit button widget.
        entry_treeview (Gtk.TreeView): The tree view widget displaying the entries.

    Returns:
        None
    """

    # Get data of entry to edit
    selection = entry_treeview.get_selection()
    model, treeiter = selection.get_selected()
    if not treeiter:
        return
    entry = model[treeiter]
    entry_data = entry[:]  # Create a copy of the entry data

    # Create a new window for editing the entry
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_FILEPATH)

    global edit_entry_win, name_entry_edit_entry_win, phone_entry_edit_entry_win, email_entry_edit_entry_win, favorite_checkbutton_edit_entry_win
    edit_entry_win = builder.get_object("edit_entry_win")
    name_entry_edit_entry_win = builder.get_object("name_entry_edit_entry_win")
    phone_entry_edit_entry_win = builder.get_object("phone_entry_edit_entry_win")
    email_entry_edit_entry_win = builder.get_object("email_entry_edit_entry_win")
    favorite_checkbutton_edit_entry_win = builder.get_object("favorite_checkbutton_edit_entry_win")

    builder.connect_signals(handlers)
    edit_entry_win.show_all()

    # Set the initial values of the entry fields
    name_entry_edit_entry_win.set_text(entry_data[0])
    phone_entry_edit_entry_win.set_text(entry_data[1])
    email_entry_edit_entry_win.set_text(entry_data[2])
    if entry_data[3]:
        favorite_checkbutton_edit_entry_win.set_active(True)


def on_edit_button_edit_entry_win_clicked(widget, entry_list, entry_treeview):
    """
    Updates the selected entry in the entry_treeview when the edit button is clicked.

    Args:
        widget (Gtk.Button): The edit button widget.
        entry_list (Gtk.ListStore): The list store containing the entries.
        entry_treeview (Gtk.TreeView): The tree view widget displaying the entries.

    Returns:
        None
    """
    selection = entry_treeview.get_selection()
    model, treeiter = selection.get_selected()
    if not treeiter:
        return
    
    original_name = model[treeiter][0]
    name = name_entry_edit_entry_win.get_text().strip()
    phone = phone_entry_edit_entry_win.get_text().strip()
    email = email_entry_edit_entry_win.get_text().strip()
    is_favorite = favorite_checkbutton_edit_entry_win.get_active()

    entry_info_validity = misc.is_entry_info_valid(entry_list, original_name, name, phone, email, False)
    if entry_info_validity["is_valid"]:
        entry = model[treeiter]
        entry[0] = name_entry_edit_entry_win.get_text().strip()
        entry[1] = phone_entry_edit_entry_win.get_text().strip()
        entry[2] = email_entry_edit_entry_win.get_text().strip()
        entry[3] = f"{'☆' if favorite_checkbutton_edit_entry_win.get_active() else ''}"
    
        global is_unsaved
        is_unsaved = True
    else:
        summon_message_win(title="Error", message=entry_info_validity["message_info"], set_transient_for=edit_entry_win)


def on_search_button_main_win_clicked(widget):
    """
    This function is called when the "Search" button is clicked in the main window.
    It creates a new window for searching entries and connects it to the main window.

    Parameters:
        widget (Gtk.Widget): The widget that triggered the event.

    Returns:
        None
    """

    # Check if a file is open
    if not is_file_open:
        summon_message_win(title="Error", message="No file is open!", set_transient_for=main_win)
        return
    
    # Create a new window using a Glade file
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_FILEPATH)
    search_win = builder.get_object("search_win")

    # Get the radio buttons and entry fields for search criteria
    global name_radiobutton_search_win, phone_radiobutton_search_win, email_radiobutton_search_win, \
        favorite_radiobutton_search_win, name_entry_search_win, phone_entry_search_win, \
        email_entry_search_win, favorite_checkbutton_search_win

    name_radiobutton_search_win = builder.get_object("name_radiobutton_search_win")
    phone_radiobutton_search_win = builder.get_object("phone_radiobutton_search_win")
    email_radiobutton_search_win = builder.get_object("email_radiobutton_search_win")
    favorite_radiobutton_search_win = builder.get_object("favorite_radiobutton_search_win")

    name_entry_search_win = builder.get_object("name_entry_search_win")
    phone_entry_search_win = builder.get_object("phone_entry_search_win")
    email_entry_search_win = builder.get_object("email_entry_search_win")
    favorite_checkbutton_search_win = builder.get_object("favorite_checkbutton_search_win")

    # Get the reset button and search button
    reset_button_search_win = builder.get_object("reset_button_search_win")
    search_button_search_win = builder.get_object("search_button_search_win")

    # Connect the signals
    builder.connect_signals(handlers)

    # Show the search window
    search_win.show_all()


def on_reset_button_search_win_clicked(widget, entry_list, entry_treeview):
    """
    Reset the tree view to show the full list of entries when the reset button in the search window is clicked.

    Args:
        widget (Gtk.Button): The reset button widget.
        entry_list (Gtk.ListStore): The list store containing the entries.
        entry_treeview (Gtk.TreeView): The tree view widget displaying the entries.

    Returns:
        None
    """

    # Reset the tree view to show the full list of entries
    entry_treeview.set_model(entry_list)

    global is_search_result
    is_search_result = False


def on_search_button_search_win_clicked(widget, entry_list, search_results, entry_treeview):
    """
    Handles the "clicked" event of the search button in the search window.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.
        entry_list (Gtk.ListStore): The list store containing the entries.
        search_results (Gtk.ListStore): The list store to store the search results.
        entry_treeview (Gtk.TreeView): The tree view widget displaying the entries.

    Returns:
        None
    """
    
    # Get data of entry to search and criteria
    if name_radiobutton_search_win.get_active():
        # Search by name
        search_criteria = name_entry_search_win.get_text().strip()
        search_by = 0
    elif phone_radiobutton_search_win.get_active():
        # Search by phone
        search_criteria = phone_entry_search_win.get_text().strip()
        search_by = 1
    elif email_radiobutton_search_win.get_active():
        # Search by email
        search_criteria = email_entry_search_win.get_text().strip()
        search_by = 2
    elif favorite_radiobutton_search_win.get_active():
        # Search by favorite
        search_criteria = f"{'☆' if favorite_checkbutton_search_win.get_active() else ''}"
        search_by = 3

    # Search from the entry list
    misc.search(search_criteria, search_by, entry_list, search_results)

    # Update the entry treeview to show the search results
    entry_treeview.set_model(search_results)

    global is_search_result
    is_search_result = True


def on_help_button_main_win_clicked(widget):
    """
    Handles the "clicked" event of the help button in the main window.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.

    Returns:
        None

    This function creates a new Gtk.Builder object and adds a Glade file to it. It then retrieves the "help_win" object from the builder and assigns it to the "help_win" variable. It also retrieves the "description_label_help_win" object from the builder and assigns it to the "description_label_help_win" variable.

    After that, it connects the signals of the builder to the "handlers" dictionary. Finally, it shows the "help_win" window.

    Note: The "handlers" dictionary is not defined in this function and must be defined elsewhere in the codebase.
    """

    # Initiate the builder and load Glade file
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_FILEPATH)
    help_win = builder.get_object("help_win")

    # Retrieve the explanation label object from the builder
    global description_label_help_win
    description_label_help_win = builder.get_object("description_label_help_win")

    # Connect the signals and show the help window
    builder.connect_signals(handlers)
    help_win.show_all()


def on_about_button_main_win_clicked(widget):
    """
    Handles the "clicked" event of the about button in the main window.

    Args:
        widget (Gtk.Widget): The widget that triggered the event.

    Returns:
        None
    """

    # Initiate the builder and load Glade file
    builder = Gtk.Builder()
    builder.add_from_file(GLADE_FILEPATH)

    # Show the about window
    about_win = builder.get_object("about_win")
    about_win.connect("response", lambda d, r: d.destroy()) # Destroy the window when the user clicks on the "Close" button
    about_win.run()


# Initiate the builder and load Glade file
builder = Gtk.Builder()
builder.add_from_file(GLADE_FILEPATH)

# Main window
main_win = builder.get_object("main_win")
main_win.connect("destroy", Gtk.main_quit)

# Entry table
entry_list = builder.get_object("entry_list")
entry_treeview = builder.get_object("entry_treeview")

# Signals
handlers = {
    # Signals for the main window
    "on_main_win_delete_event": lambda widget, event: on_main_win_delete_event(widget, event),
    "on_no_button_confirm_close_win_clicked": lambda widget: on_no_button_confirm_close_win_clicked(widget),
    "on_yes_button_confirm_close_win_clicked": lambda widget: on_yes_button_confirm_close_win_clicked(widget),

    "on_new_button_main_win_clicked": lambda widget: on_new_button_main_win_clicked(widget, entry_list),
    "on_open_button_main_win_clicked": lambda widget: on_open_button_main_win_clicked(widget),
    "on_save_button_main_win_clicked": lambda widget: on_save_button_main_win_clicked(widget, entry_list),
    "on_add_button_main_win_clicked": lambda widget: on_add_button_main_win_clicked(widget),
    "on_remove_button_main_win_clicked": lambda widget: on_remove_button_main_win_clicked(widget, entry_treeview),
    "on_edit_button_main_win_clicked": lambda widget: on_edit_button_main_win_clicked(widget, entry_treeview),
    "on_search_button_main_win_clicked": lambda widget: on_search_button_main_win_clicked(widget),
    "on_help_button_main_win_clicked": lambda widget: on_help_button_main_win_clicked(widget),
    "on_about_button_main_win_clicked": lambda widget: on_about_button_main_win_clicked(widget),

    # Signals for the add, edit and search windows
    "on_add_button_add_entry_win_clicked": lambda widget: on_add_button_add_entry_win_clicked(widget, entry_list),
    "on_edit_button_edit_entry_win_clicked": lambda widget: on_edit_button_edit_entry_win_clicked(widget, entry_list, entry_treeview),
    "on_reset_button_search_win_clicked": lambda widget: on_reset_button_search_win_clicked(widget, entry_list, entry_treeview),
    "on_search_button_search_win_clicked": lambda widget: on_search_button_search_win_clicked(widget, entry_list, search_results, entry_treeview),

    # Signals for the help window
    "on_new_button_help_win_clicked": lambda *args: description_label_help_win.set_text(NEW_BUTTON_HELP_EXPLANATION),
    "on_open_button_help_win_clicked": lambda *args: description_label_help_win.set_text(OPEN_BUTTON_HELP_EXPLANATION),
    "on_save_button_help_win_clicked": lambda *args: description_label_help_win.set_text(SAVE_BUTTON_HELP_EXPLANATION),
    "on_add_button_help_win_clicked": lambda *args: description_label_help_win.set_text(ADD_BUTTON_HELP_EXPLANATION),
    "on_remove_button_help_win_clicked": lambda *args: description_label_help_win.set_text(REMOVE_BUTTON_HELP_EXPLANATION),
    "on_edit_button_help_win_clicked": lambda *args: description_label_help_win.set_text(EDIT_BUTTON_HELP_EXPLANATION),
    "on_search_button_help_win_clicked": lambda *args: description_label_help_win.set_text(SEARCH_BUTTON_HELP_EXPLANATION),
    "on_help_button_help_win_clicked": lambda *args: description_label_help_win.set_text(HELP_BUTTON_HELP_EXPLANATION),
    "on_about_button_help_win_clicked": lambda *args: description_label_help_win.set_text(ABOUT_BUTTON_HELP_EXPLANATION),
}
builder.connect_signals(handlers)

# Show main window
main_win.show_all()
Gtk.main()
