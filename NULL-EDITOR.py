# null – Small pseudo-editor created as a final project for a university course

########################## LICENSE ###########################
# Copyright (c) 2021 Matias Ikkala
#
# This file is part of 'null.'
#
# 'null.' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'null.' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'null.'  If not, see <https://www.gnu.org/licenses/>.


from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.scrolledtext as tkst


def validation(default_entry):
    """Make the command line start with a default lambda symbol.

    The command line starts with a lambda symbol that cannot be erased. This is
    used together with the default_entry function to make the symbol.

    :return: null

    """
    return default_entry.startswith("ᴧ ")


class Interface:
    """The main interface object used for creating the GUI.

    All the functions in the program are executed within the class.

    """
    def __init__(self):
        """The constructor used to create the interface.

        The constructor defines the widgets in the interface and other most
        important attributes of the program

        :param self.__main_default_trigger: bool: Trigger used to make the
        default text in the main frame disappear after clicking it.
        :param self.__item_container: dict: A dictionary that holds parts of
        the text stored in the item list.
        :param self.__command_list: dict: Dictionary of the commands and the
        functions they call when they are executed.

        """
        # Create the root that contains other widgets. Make the window non-
        # resizable, and make a popup appear if the window is closed.

        self.__root = Tk()
        self.__root.title("пull.")
        self.__root.protocol("WM_DELETE_WINDOW", self.quit_popup)
        command_validate = self.__root.register(validation)
        self.__root.resizable(width=False, height=False)

        # Bind the commands that are not widget specific, so they can be used
        # anywhere in the program, not just when focus is on the widget.

        self.__root.bind("<Control-l>", self.move_item_bind)
        self.__root.bind("<Alt-l>", self.next_item_bind)
        self.__root.bind("<Control-m>", self.tabulate)
        self.__root.bind("<Control-q>", self.delete_bind)
        self.__root.bind("<Control-r>", self.detach)

        # The style module is used to create the style for the Treeview widget
        # because it could not be styled with the configure method directly.

        self.__style = ttk.Style()
        ttk.Style().configure("Treeview", background="#282828",
                              foreground="#FFB000", fieldbackground="#282828")

        # Create a text widget with a scroll bar. Used to edit text.

        self.__main_frame = tkst.ScrolledText(self.__root, wrap=WORD)
        self.__main_frame.configure(foreground="#FFB000", background="#282828",
                                    insertbackground="#FFB000", insertwidth=3,
                                    selectbackground="#FFBE33",
                                    inactiveselectbackground="#FFCF66")

        # Default text is displayed in the main frame on startup, and clears
        # when the text widget is clicked. The trigger determines when the text
        # is displayed and should be destroyed.

        self.__main_default_trigger = False
        self.main_frame_default()

        # Define bindings for the main frame widget and the grid placement.

        self.__main_frame.bind("<FocusIn>", self.main_default_destroy)
        self.__main_frame.bind("<Control-j>", self.paste_bind)
        self.__main_frame.grid(row=0, column=1)

        # A Treeview widget is used to show the items that have been saved.
        # Holds only two levels: parents and childs.

        self.__tree = ttk.Treeview(self.__root, height=19)
        self.__tree.heading("#0", text="ITEM LIST", anchor=CENTER)

        # Define bindings and the grid placement for the treeview.

        self.__tree.bind("<Control-j>", self.paste_bind)
        self.__tree.bind("<<TreeviewSelect>>", self.show_selection)
        self.__tree.grid(row=0, column=0)

        # Create two buttons, for clearing the text in the main and side frame.

        self.__button = Button(self.__root, text="CLEAR MAIN TEXT", width=21,
                               command=self.clear_main_button)
        self.__button.grid(row=6, column=0)

        self.__button = Button(self.__root, text="CLEAR SIDE TEXT", width=29,
                               command=self.clear_side_button)
        self.__button.grid(row=6, column=5)

        # Create an Entry widget for inputting commands. Set the style, the
        # default symbol, and set the focus to this widget when starting.

        self.__command_box = Entry(self.__root, width=80, validate="key",
                                   validatecommand=(command_validate, "%P"))
        self.__command_box.configure(foreground="#FFB000",
                                     background="#282828",
                                     insertbackground="#FFB000", insertwidth=3,
                                     selectbackground="#FFBE33")
        self.__command_box.insert(1, "ᴧ ")
        self.__command_box.bind("<Return>", self.command_call)
        self.__command_box.focus_set()
        self.__command_box.grid(row=6, column=1)

        # Create a dictionary to hold the saved texts and an other to hold the
        # commands and functions they are used to call.

        self.__item_container = {}
        self.__command_list = {"-s": self.save_item, "-j": self.paste,
                               "-cs": self.save_child, "-q": self.delete_item,
                               "-l": self.move_item, "-quit": self.quit,
                               "-ex": self.save_main, "-im": self.open_main,
                               "-gg": self.clear_main_frame,
                               "-help": self.help}

        # Create another Text widget with a scrollbar to the side, this is used
        # to display the saved items, selected from the Treeview.

        self.__side_frame = tkst.ScrolledText(self.__root, width=30, wrap=WORD)
        self.__side_frame.configure(foreground="#FFB000", background="#282828",
                                    insertbackground="#FFB000", insertwidth=3,
                                    selectbackground="#FFBE33",
                                    inactiveselectbackground="#FFCF66")

        # Bind clicking on the widget to transfer focus on the command box to
        # make it read only, but to allow pasting the selected items in it.
        # Then set the insert cursor width to zero to hide it.

        self.__side_frame.bind("<FocusIn>",
                               lambda e: self.__command_box.focus())
        self.__side_frame.config(insertwidth=0)
        self.__side_frame.grid(row=0, column=5)

        # Enclose the structure in the mainloop.

        self.__root.mainloop()

    def command_print(self, text):
        """Used to print information in the command box.

        First delete from the second character onward, because the default
        symbol takes 2 characters. Then print the text in the widget, and after
        waiting for a while, remove the text.

        """

        self.__command_box.delete(2, END)
        self.__command_box.insert(2, text)
        self.__command_box.after(1500,
                                 lambda: self.__command_box.delete(2, END))

    def tabulate(self, event):
        """Tabulate between the main frame and the command box.

           Binded to the keyboard shortcut Control + m. Because items are saved
           by first selecting text in the main frame, tabulating easily makes
           saving more convenient.

        """

        # Check which widget currently has the focus. If the focus is on the
        # command box, set focus to the main frame, and vice versa. If focus
        # is anywhere else, set the focus on the command box.

        current = self.__root.focus_get()

        if current == self.__command_box:
            self.__main_frame.focus()
        elif current == self.__main_frame:
            self.__command_box.focus()
        else:
            self.__command_box.focus()

    def save_item(self):
        """Save item to the Treeview item list.

        Works by first selecting text in the main frame, then typing "-s
        *filename*". You can only use the same item name once.

        """

        # Get the line input by the user, to check the command was valid and
        # to get the item name used for saving.

        line = self.__command_box.get()

        try:
            line_list = line.split()

            # If the line contains too many words, the syntax is incorrect, so
            # an error will be raised.

            if len(line_list) != 3:
                raise IndexError

            # Get the selected text and check the lenght. If nothing is
            # selected, raise an error.

            selection = self.__main_frame.selection_get()
            if len(selection) == 0:
                raise TclError

            # Check the Treeview does not already contain another item with
            # the same name. If needed, print an error notification and return.

            if self.__tree.exists(line_list[2]):
                self.command_print("Can't save same name twice.")
                return

            # Insert an entry in the Treeview with the selected name as the
            # text and the item id. Then save the selected text to the
            # dictionary, with the name as key. Finally clear the command box.

            self.__tree.insert("", END, iid=line_list[2], text=line_list[2])
            self.__item_container[line_list[2]] = selection
            self.__command_box.delete(2, END)

        # Excepts used to catch errors and print error notifications.

        except TclError:
            self.command_print("No selection. Select text in main frame.")
        except IndexError:
            self.command_print("Incorrect syntax. Use form '-s"
                               " /item_name/'")

    def save_child(self):
        """Save selected text a an child item in the Treeview.

            The command to save a child is: "-cs -*parent* *filename*". Again,
            you cannot save multiple items with the same name.

        """

        # Get the line input by the user to check it is valid.

        line = self.__command_box.get()
        try:
            line_list = line.split()
            parent = line_list[2][1:]

            # If line does not have 4 words (including the default symbol), the
            # syntax is wrong, and a error will be raised. Also check that the
            # parent exists in the Treeview, and that there is not another item
            # with the same name. Raise errors if necessary.

            if len(line_list) != 4:
                raise IndexError
            if not self.__tree.exists(parent):
                raise TypeError
            if self.__tree.exists(line_list[3]):
                self.command_print("Cannot use same name twice.")
                return

            # Get the selected text. Insert the item to the Treeview and save
            # the text to the container. Finally clear the command box.

            selection = self.__main_frame.selection_get()
            self.__tree.insert(parent, 1, iid=line_list[3], text=line_list[3])
            self.__item_container[line_list[3]] = selection
            self.__command_box.delete(2, END)

        # Excepts used to catch errors and print error notifications.

        except ValueError:
            self.command_print("Too many arguments. Try '-cs -/parent/ "
                               "/item_name/'.")
        except TclError:
            self.command_print("No selection. Select text in main frame.")
        except IndexError:
            self.command_print("Incorrect syntax. Use form '-cs -/parent/ "
                               "/item_name/'")
        except TypeError:
            self.command_print("Parent not found. Try again.")

    def delete_item(self):
        """Delete an item from the Treeview item list.

        Uses the command "-q *item_name*". Deletes the item from the list and
        the text from the item_container dictionary.

        """

        # Get the line and split to a list to perform necessary inspections.

        line = self.__command_box.get()
        try:
            line_list = line.split()
            item_id = line_list[2]

            # If the line does not contain 3 words, the syntax is wrong.

            if len(line_list) != 3:
                raise IndexError

            # Delete the saved text from the item_container and from the
            # Treeview,

            del self.__item_container[item_id]
            self.__tree.delete(item_id)
            self.__command_box.delete(2, END)

        # Except used to catch the errors.

        except IndexError:
            self.command_print("Incorrect syntax. Use form '-q "
                               "/item_name/'")
        except TclError:
            self.command_print("Item not found. Try again.")

    def delete_bind(self, event):
        """Keyboard shortcut for the delete command.

        You can delete items from the Treeview with the Control + q shortcut.
        First select items from the item list, then press the keys.

        """

        # Get a list of all the selected items in the Treeview widget. Create
        # two new lists for the items that are parents, and for children.

        current = self.__tree.selection()
        children = []
        parents = []

        # Iterate over the selected items and save all children and parent
        # items in their respective lists.

        for item in current:
            if self.__tree.parent(item) != "":
                children.append(item)
            else:
                parents.append(item)

        # Iterate over the children list, delete them from the Treeview and
        # from the item container.

        for child in children:
            self.__tree.delete(child)
            del self.__item_container[child]

        # Now delete the parents. Children are deleted first, because otherwise
        # if both parent and child are selected, it would cause errors.

        for parent in parents:
            self.__tree.delete(parent)
            del self.__item_container[parent]

        self.__command_box.delete(2, END)

        # Clear text from the side frame if the list is empty after deleting
        # selected items.

        if len(self.__tree.get_children()) == 0:
            self.__side_frame.delete(1.0, END)

    def command_call(self, event):
        """The function used to read the command line and start a function.

        """

        # Get the line, split to a list, compile a list of all commands in the
        # command list.

        line = self.__command_box.get()
        commands = [key for key in self.__command_list]
        linelist = line.split()
        prompt = linelist[1]

        # Check the syntax and that the command is in the command list. If
        # nothing is wrong, call the function.

        if len(linelist) < 2:
            self.command_print("Unknown command. Type '-help' for a list of "
                               "commands.")
            return

        if prompt not in commands:
            self.command_print("Unknown command. Type '-help' for a list of "
                               "commands.")
        else:
            self.__command_list[prompt]()

    def paste(self):
        """"Paste items selected in the Treeview to the main frame.

        Use the command "-j /item_name/". You can paste multiple items by
        typing ":" between the items you want to paste. For example:
        "-j item1:item2".

        NOTE: If you paste multiple items. The contents will be separated by a
        newline character.

        """

        # Get the line and split into list to check the syntax.

        line = self.__command_box.get()

        try:
            line_list = line.split()

            # If the line does not have three words, syntax is wrong.

            if len(line_list) != 3:
                raise IndexError

            # Check if there is multiple items to paste by checking if the
            # string contains ":". If it does, split by ":", and iterate over
            # the list, getting the contents out of the item container and
            # inserting to the main frame.

            if ":" in line_list[2]:
                add_items = line_list[2].split(":")
                for item in add_items:
                    paste_text = self.__item_container[item]
                    self.__main_frame.insert(INSERT, paste_text + "\n")

            # If there was only one item to paste, do the same for that item.

            else:
                paste_text = self.__item_container[line_list[2]]
                self.__main_frame.insert(INSERT, paste_text)
            self.__command_box.delete(2, END)

        # Excepts used to catch any errors.

        except KeyError:
            self.command_print("Undefined function. See side frame for a list"
                               " of saved functions.")
        except IndexError:
            self.command_print("Incorrect syntax. Use form '-j "
                               "/function_name/'")

    def paste_bind(self, event):
        """Keyboard shortcut for the paste function.

        Use Control + j to paste after selecting items from the Treeview. NOTE:
        When pasting multiple things, a newline will be added between items.

        """

        # Get a list of items selected in the Treeview item list. Then iterate
        # over the list and fetch the text from the item container, and paste
        # in the insert cursors place.

        current = self.__tree.selection()
        for item in current:
            paste_text = self.__item_container[item]
            self.__main_frame.insert(INSERT, paste_text + "\n")

    def move_item(self):
        """Move selected item one step up in the Treeview widget.

        Note: Cannot move multiple items at the same time.

        """

        # Get the line and split it to check the syntax of the input and the
        # name of the file to be moved.

        line = self.__command_box.get()
        try:
            line_list = line.split()
            item = line_list[2][1:]

            # Raise error if length of the line is not 3 words.

            if len(line_list) != 3:
                raise IndexError

            # Check that the item length is not zero and that the item exists.

            if len(item) < 1:
                raise IndexError
            if not self.__tree.exists(item):
                self.command_print("Item not found. See list for saved items.")
                return

            # Get the index and the parent of the item.

            index = self.__tree.index(item)
            parent = self.__tree.parent(item)

            # If the item is on top of the list, move it to the bottom.
            # Otherwise move it one step up. Finally clear the command box.

            if index == 0:
                self.__tree.move(item, parent, END)
            else:
                self.__tree.move(item, parent, index - 1)

            self.__command_box.delete(2, END)

        # Except used to catch any errors.

        except IndexError:
            self.command_print("Incorrect syntax. Use form '-l "
                               "-/function_name/'")

    def move_item_bind(self, event):
        """Keyboard shortcut to move items in the Treeview item list.

        Use Control + l to move a selected item one step upwards.

        """

        # Get a list of the selected items. and its index and parent item.

        try:
            current = self.__tree.selection()
            index = self.__tree.index(current)
            parent = self.__tree.parent(current)

            # If item is on top of the list, move it to the end. Othetwise
            # move the item one step upwards.

            if index == 0:
                self.__tree.move(current, parent, END)
            else:
                self.__tree.move(current, parent, index - 1)

        # Except used to catch any errors.

        except TclError:
            return

    def next_item_bind(self, event):
        """Keyboard shortcut to select the next item in the Treeview widget.

        Use Alt + l to toggle the selected item in the item list.

        """

        # If the Treeview is empty, return. If nothing is selected, select the
        # first item in the list.

        if self.__tree.get_children() == "":
            return
        elif self.__tree.selection() == "":
            self.__tree.selection_set(self.__tree.get_children()[0])

        else:
            try:

                # Get the current selected item, and its next sibling, parent,
                # and the parents next sibling.

                current = self.__tree.selection()
                next_sibling = self.__tree.next(current)
                parent = self.__tree.parent(current)
                parent_sibling = self.__tree.next(parent)
                tree_list = self.__tree.get_children()

                # If the item has no parent, check if it has any children. If
                # there is children, select the first child. Otherwise, if item
                # has a next sibling, select it. Otherwise, if the item is last
                # on the list, select the first item in the list.

                if parent == "":
                    if len(self.__tree.get_children(current)) > 0:
                        children = self.__tree.get_children(current)
                        self.__tree.selection_set(children[0])
                    elif next_sibling != "":
                        self.__tree.selection_set(next_sibling)
                    elif next_sibling == "":
                        self.__tree.selection_set(tree_list[0])

                # If the item has a parent, check if there is a next sibling.
                # If there is, select it. Or if the item is last, select the
                # parent's next sibling. If the parent has no next sibling,
                # select the first item of the list.

                elif parent != "":
                    if next_sibling != "":
                        self.__tree.selection_set(next_sibling)
                    if next_sibling == "":
                        if self.__tree.next(parent) == "":
                            self.__tree.selection_set(tree_list[0])
                        else:
                            self.__tree.selection_set(parent_sibling)

            # Excepts used to catch errors.

            except TclError:
                return
            except IndexError:
                return

    def detach(self, event):
        """Keyboard shortcut to detach/attach items to others.

        Use Control + r to detach/attach. If the item is a child, it will be
        moved to the upper level. If the item is on the upper level and has
        a next sibling, it will be made a child of the sibling.

        """

        # Get a list of selected items, the parent and the next sibling.

        current = self.__tree.selection()
        parent = self.__tree.parent(current)
        next_item = self.__tree.next(current)

        # If item has a parent, get the index of the parent and move the item
        # one below the parent. If there is no parent and the item has a next
        # sibling, make the item the last child of the sibling.

        if parent != "":
            index = self.__tree.index(parent)
            self.__tree.move(current, "", index + 1)
        elif next_item != "":
            if len(self.__tree.get_children(current)) < 1:
                self.__tree.move(current, next_item, END)

    def show_selection(self, event):
        """Show the contents of the selected items on the side frame.

        The side frame can be used to check the contents of the saved items
        before pasting them or deleting them.

        """

        # Get the selected items and make a new list for the contents.

        selection = self.__tree.selection()
        text_list = []

        # Fetch the text for the selected items from the item container, and
        # append to the list. Join the contents into one string separated by
        # one empty line, and insert into the side frame.

        for item in selection:
            text_list.append(self.__item_container[item])
        text = "\n\n".join(text_list)

        self.__side_frame.delete(1.0, END)
        self.__side_frame.insert(END, text)

    def quit(self):
        """Quit the program, without saving or by first saving the text.

        Use the command "-quit n" if you want to quit without saving the text
        in the main frame. If you want to save, use "-quit y *item_name.txt".
        You do not have to select the text to save it, the program will save
        everything in the main frame automatically.

        NOTE: File will be saved in the same folder where the program is run
        from. Only saving .txt files supported.

        """

        # Get the line and split for checking the command.

        line = self.__command_box.get()
        try:
            line_list = line.split()

            # If the user does not want to save, quit the program directly.

            if line[2:] == "-quit n":
                self.__root.destroy()

            # If the user wants to save, first check the filename is correct.

            elif (line_list[2] == "y") and (len(line_list) == 4):

                # If the filename contains "/" (the user wants to save to
                # another directory), print an error notification.

                if "/" in line_list[3]:
                    self.command_print("Only saving in the run folder "
                                       "allowed.")

                # If the filename does not contain ".txt", show error message.

                elif ".txt" not in line_list[3]:
                    self.command_print("Incorrect syntax. Try '-quit y "
                                       "/filename.txt/' or '-quit n' to "
                                       "exit.")

                # Check that there is no extra dots in the filename. If not,
                # save the file by calling the save_file function.

                elif len(line_list[3].split(".")) != 2:
                    self.command_print("Incorrect syntax. Try '-quit y "
                                       "/filename.txt/' or '-quit n' to exit.")

                # Finally check that the "txt" does not have extra characters
                # and save the file by calling save_file function.

                else:
                    split_line = line_list[3].split(".")
                    if split_line[1] != "txt":
                        self.command_print("Incorrect syntax. Use form '-im "
                                           "/filename.txt/")
                        return

                    self.save_file(line_list[3])

            # Error if the "-quit y *filename*" command has too many words.

            else:
                self.command_print("Incorrect syntax. Try '-quit y "
                                   "/filename.txt/' or '-quit n' to exit.")

        # Except to catch any unnoticed errors.

        except IndexError:
            self.command_print("Incorrect syntax. Type '-quit y "
                               "/filename.txt/' or '-quit n' to exit.")

    def quit_popup(self):
        """Make a pop up notification appear when closing from the window.

        A simple popup to prevent closing by mistake.

        """

        # Show a pop up message, quit if the user says ok.

        popup = messagebox.askokcancel("Quit Application",
                                       "Sure you want to quit?",
                                       icon="warning")
        if popup:
            self.__root.destroy()

    def save_main(self):
        """Save without quitting.

        Use the "-ex *filename.txt*" command. The saving is done in a similar
        manner than in the save and quit function before.

        """

        # Get the line, check the syntax for errors.

        line = self.__command_box.get()
        try:
            line_list = line.split()
            if len(line_list) != 3:
                raise IndexError

            # If "/" in filename, show an error notification.

            if "/" in line_list[2]:
                self.command_print("Only saving in the run folder allowed.")

            # If ".txt" is not defined in the filename, show error message.

            elif ".txt" not in line_list[2]:
                self.command_print("Incorrect syntax. Use form '-ex "
                                   "/filename.txt/")

            # Split the filename for dots to see if the filename contains too
            # many dots and that the "txt" does not have extra characters.

            else:
                split_line = line_list[2].split(".")

                if len(split_line) != 2:
                    self.command_print("Incorrect syntax. Use form '-ex "
                                       "/filename.txt/")
                elif split_line[1] != "txt":
                    self.command_print("Incorrect syntax. Use form '-im "
                                       "/filename.txt/")

                # Finally, save the file by calling the save_file function.

                else:
                    self.save_file(line_list[2])

        # Except to catch any errors.

        except IndexError:
            self.command_print("Incorrect syntax. Use form '-ex "
                               "/filename.txt/'")

    def save_file(self, filename):
        """The save file method used above.

        """

        # Open the file with the given filename, get the whole text from the
        # main frame, and write.

        file = open(filename, "w")
        file.write(self.__main_frame.get(1.0, END))
        file.close()

        # Show a notification that the file was saved.

        notification = "File saved as: {:s}".format(filename)
        self.command_print(notification)

    def open_main(self):
        """Open a ".txt" file and import to the main frame.

        Use the command "-im *filename.txt*. Only opening files from the same
        folder the program is run from allowed. If the main frame contains
        text, a pop up will first ask whether to open, because the frame will
        be cleared from previous text.

        """

        # Get line, check the current text in the main frame.

        line = self.__command_box.get()
        current_text = self.__main_frame.get(1.0, END)

        # Check the syntax and show error notification if necessary.

        try:
            line_list = line.split()
            split_line = line_list[2].split(".")
            if len(line_list) != 3:
                raise IndexError

            # Show error if the filename contains "/" or ".txt".

            if "/" in line_list[2]:
                self.command_print("Only opening from the run folder allowed.")
            if ".txt" not in line_list[2]:
                self.command_print("Incorrect syntax. Use form '-im "
                                   "/filename.txt/")

            # Show error if the filename contains too many dots or the "txt"
            # contains extra characters.

            elif len(split_line) != 2:
                self.command_print("Incorrect syntax. Use form '-im "
                                   "/filename.txt/")
            elif split_line[1] != "txt":
                self.command_print("Incorrect syntax. Use form '-im "
                                   "/filename.txt/")

            # Check main frame contains current text, and show a warning if it
            # does, because the text will be cleared when importing the file.

            elif len(current_text) > 1:
                popup = messagebox.askokcancel("Open Warning",
                                               "Text field not empty. All text"
                                               " will be cleared. Continue?",
                                               icon="warning")

                # If user said ok, clear the main frame, open the file, read
                # the text, insert to main frame, and show notification in
                # the command box.

                if popup:
                    self.__main_frame.delete(1.0, END)
                    self.open_file(line_list[2])

            # If there was no text in main frame, import the file directly.

            else:
                self.open_file(line_list[2])

        # Excepts to catch unwanted errors.

        except IndexError:
            self.command_print("Incorrect syntax. Use form '-im "
                               "/filename.txt/'")
        except OSError:
            self.command_print("Error in opening file. Check '-help' for more"
                               " information.")

    def open_file(self, filename):
        """Used to open the file in when importing text.

        """

        # Open the file, read the text, paste, and show notification.

        file = open(filename, "r")
        text = file.read()
        self.__main_frame.insert(1.0, text)
        file.close()
        self.__command_box.delete(2, END)

    def help(self):
        """Show the help file in the main frame.

        Use the command "-help" to show the help file. It lists the commands
        and the basic info about the program. The help file is contained in the
        program folder and must not be moved.

        """

        # See if the main frame contains text. Open the help file and save
        # the help text, then close file.

        current_text = self.__main_frame.get(1.0, END)
        help_file = open("help.txt", "r")
        help_text = help_file.read()
        help_file.close()

        # Get the default text from the default file. It is used to see if the
        # current text in the main frame is only the default text, then a pop
        # up will not ask whether you want to import.

        default_file = open("default_main.txt", "r")
        default_text = default_file.read() + "\n"
        default_file.close()

        self.__command_box.delete(2, END)

        # If the main frame is empty, paste the help text. If it only contains
        # the default text, clear it and paste the help text.

        if len(current_text) <= 1:
            self.__main_frame.insert(1.0, help_text)
        elif current_text == default_text:
            self.__main_frame.delete(1.0, END)
            self.__main_frame.insert(1.0, help_text)

        # If there was other text in the main frame, first show a pop up
        # asking if the user really wants to open the file. If the answer is
        # ok, clear the main frame and paste the help text.

        else:
            popup = messagebox.askokcancel("Open Warning",
                                           "Text field not empty. All text "
                                           "will be cleared. Continue?",
                                           icon="warning")
            if popup:
                self.__main_frame.delete(1.0, END)
                self.__main_frame.insert(1.0, help_text)

    def main_frame_default(self):
        """Show the default text when the program is started.

        The default text shows a logo and a text telling to type "-help" for
        more information. It will disappear when focus moves to the main frame.

        """

        # Get the default text and insert it to the main frame.

        default_file = open("default_main.txt", "r")
        default_text = default_file.read()
        self.__main_frame.insert(1.0, default_text)
        default_file.close()

        # This trigger is used to record if the user has focused on the main
        # frame. If it has, the trigger will be set False, and the default
        # text will not be showed again.

        self.__main_default_trigger = True

    def main_default_destroy(self, event):
        """When the user focuses on the main frame, destroy the default text.

        """

        # If the default text trigger is True and the focus shifts to the
        # main frame, clear all text from it and set the trigger to False, so
        # that all text will not be cleared every time the user shifts focus
        # to the main frame.

        if self.__main_default_trigger:
            self.__main_frame.delete(1.0, END)
        self.__main_default_trigger = False

    def clear_main_frame(self):
        """Clear the main frame from text.

        Use the command "-gg" to clear the main frame from all text.

        """

        # Get the line, check the syntax for errors.

        line = self.__command_box.get()
        line_list = line.split()

        # If syntax is ok, clear the text and show notification in command box.

        if len(line_list) == 2:
            self.__main_frame.delete(1.0, END)
            self.command_print("Main frame cleared successfully.")

        # Show error message if syntax was wrong.

        else:
            self.command_print("Incorrect syntax. Try '-gg' to clear the "
                               "main frame.")

    def clear_main_button(self):
        """The button that clears the text in the main frame.

        """

        self.__main_frame.delete(1.0, END)

    def clear_side_button(self):
        """The button that clears text from the side frame.

        """
        self.__side_frame.delete(1.0, END)


def main():
    interface = Interface()


main()
