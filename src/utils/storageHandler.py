# This is a handler that gives functions to manipulate files.
#
# FUNCTION:
#  - shortset: manipulate shortcuts creation, renaming, destuction, etc.
#  - addressof: get the adress of a file by passing its shortcut, name(with extension) or the default file.
#
#  - file_read: read a file (json, txt) and return its content.
#  - file_create: create a new file (json, txt) and return True if the operation has been done.
#  - file_delete: delete a file (json, txt) and return True if the operation has been done.
#  - file_rename: rename a file (json, txt) and return True if the operation has been done.
#
#  - param_get: get a parameter from a json file and return its value.
#  - param_getlist: get multiple parameters from a json file and yield their values.
#  - param_set: set multiple parameters in a json file and return True if the operation has been done.
#  - param_del: delete multiple parameters in a json file and return True if the operation has been done.
#  - param_reset: reset/patternate a json file and return True if the operation has been done.
import json
import os
from utils.consoleSystem import error, warn, trace, info

# Fast functions (function that use the storage class to be used elsewere)
def file_read(file_name:str=None, type=None): return storage.file_read(file_name, type)
def file_create(file_name:str, type=None, content=None, short:str=None): return storage.file_create(file_name, type, content, short)
def file_delete(file_name:str, type=None): return storage.file_delete(file_name, type)
def file_rename(file_name:str, new_name:str, type=None): return storage.file_rename(file_name, new_name, type)
def param_get(param_name:str, file_name:str=None): return storage.parameter_get(param_name, file_name)
def param_getlist(param_name:list, file_name=None):
    """Get  a list of parameters"""
    if type(param_name) != list:
        warn("param_getlist take param_name as a list. Type "+type(param_name)+" not allowed")
        yield None
    if type(file_name) == str:
        file_name = [file_name]*len(param_name)
    elif file_name == None:
        file_name = [None]*len(param_name)
    elif type(file_name) != list:
        warn("param_getlist take file_name as a list or str. Type "+type(param_name)+" not allowed")
        yield None
    for k in range(len(param_name)):
        yield storage.parameter_get(param_name[k], file_name[k])
def param_set(param_name:str, param_value:str, file_name:str=None): return storage.parameter_set(param_name, param_value, file_name)
def param_del(param_name:str, file_name:str=None): return storage.parameter_delete(param_name, file_name)
def param_reset(file_name:str=None, reset:dict={}): return storage.parameter_reset(file_name, reset)
    

class storageHandler():

    def __init__(self):
        # Setting up the storage handler
        self.storage_folder_path = "assets/storage/"
        try:
            self.shortcuts = self.file_read("shortcuts.json")
        except:
            error("Shortcuts file not found. Make sure it exists and that the path is correct.")
        info("Storage handler initialized.")

    def quit(self):
        """Save the shortcuts and quit"""
        self.parameter_reset("shortcuts", self.shortcuts)
        info("Storage handler has quit.")

    def set_shortcut(self, new_file_name:str=None, old_file_name:str=None, new_file_short:str=None, old_file_short:str=None):
        """
        Set a shortcut.

        Args:
            new_file_name (str): name of the new file.
            old_file_name (str): name of the old file.
            new_file_short (str): shortcut of the new file.
            old_file_short (str): shortcut of the old file.


        Returns:
            True if the shortcut has been set. False otherwise.
        """
        # Set new file name if not set.
        if new_file_name != None and new_file_short == None:
            new_file_short, type = new_file_name.split(".", 1)
            type = "."+type
        elif new_file_name != None:
            type = new_file_name.split(".", 1)[-1]
            type = "."+type

        # Set old file name if not set.
        if old_file_name != None and old_file_short == None:
            old_file_short, old_type = old_file_name.split(".", 1)
            old_type = "."+old_type
        elif old_file_name != None:
            old_type = old_file_name.split(".", 1)[-1]
            old_type = "."+old_type

        # Rename a shortcut.
        if old_file_name != None and new_file_name != None:
            if old_file_name in self.shortcuts.values():
                for key in self.shortcuts.keys():
                    if self.shortcuts[key] == old_file_name:
                        break
                del self.shortcuts[key]
            if not new_file_short in self.shortcuts.keys():
                self.shortcuts[new_file_short] = new_file_name
            else:
                warn("Shortcut already exists. Can't apply new shortcut '"+str(new_file_short)+"'.")
                return False
        # Set a new shortcut.
        elif new_file_name != None and old_file_name == None:
            if not new_file_short in self.shortcuts.keys():
                self.shortcuts[new_file_short] = new_file_name
            else:
                warn("Shortcut already exists. Can't apply new shortcut '"+str(new_file_short)+"'.")
                return False
        # Delete a shortcut.
        elif new_file_name == None and old_file_name != None:
            if old_file_name in self.shortcuts.values():
                for key in self.shortcuts.keys():
                    if self.shortcuts[key] == old_file_name:
                        break
                del self.shortcuts[key]
        # No input.
        else :
            warn("Wrong set_shortcut() input command. Please check your parameters input.")
            return False
        return True

    def get_address_of(self, file_name:str):
        """
        Get the adress of a file by passing its shortcut, name(with extension) or the default file is not set.

        Args:
            file_name (str): name of the file.

        Returns:
            The adress of the file (str). None if the file doesn't exist.
        """
        if file_name is None or file_name == "":
            file_name = self.shortcuts["default"]
        elif file_name.count(".json") + file_name.count(".txt") == 0:
            try:
                file_name = self.shortcuts[file_name]
            except:
                warn("Unknown file name '"+str(file_name)+"'.")
                return None
        if os.path.exists(self.storage_folder_path + file_name):
            return file_name
        else:
            warn("Unknown file "+str(file_name)+". Make sure the file exists.")
            return None


    ##################
    # FILE FUNCTIONS #
    ##################
    def file_read(self, file_name:str=None, type=None):
        """
        Read a file and return its content.

        Args:
            file_name (str): name of the file.

        Returns:
            The content of the file (str).
        """
        file_name = self.get_address_of(file_name)
        if type is None:
            file_name, temp = file_name.split(".", 1)
            type = "."+temp
        try:
            with open(self.storage_folder_path+file_name+type) as file:
                if type == ".json":
                    return json.load(file)
                elif type == ".txt":
                    return file.read()
                else:
                    warn("Unknown file extension '"+type+"'.")
                    return None
        except:
            warn("No files named '"+str(file_name+type)+"' were found.")
            return None
            
    def file_create(self, file_name:str, type=None, content=None, short:str=None):
        """
        Create a new file.

        Args:
            file_name (str): name of the file.
            type (str): type of the file.
            content: content of the file.
            short (str): shortcut of the file.

        Returns:
            None
        """
        if type is None:
            file_name, temp = file_name.split(".", 1)
            type = "."+temp
        if os.path.exists(self.storage_folder_path+file_name+type):
            self.file_delete(file_name, type)
        with open(self.storage_folder_path+file_name+type, "a") as file:
            if type == ".json":
                if content != None:
                    json.dump(content, file, indent=4)
                else:
                    file.write("{\n\n}")
                self.set_shortcut(file_name+type, None, short)
                return True
            elif type == ".txt":
                if content != None:
                    file.write(content)
                self.set_shortcut(file_name+type, None, short)
                return True
            else:
                warn("Unknown file extension '"+str(type)+"'.")
                return False
            
    def file_delete(self, file_name:str, type:str=None):
        """
        Delete a file.

        Args:
            file_name (str): name of the file.

        Returns:
            None
        """
        if type is None:
            file_name = self.get_address_of(file_name)
            file_name, temp = file_name.split(".", 1)
            type = "."+temp
        try:
            os.remove(self.storage_folder_path+file_name+type)
            self.set_shortcut(None, file_name+type)
            return True
        except:
            warn("Unknown file named '"+str(file_name+type)+"'.")
            return False
        
    def file_rename(self, old_name:str, new_name:str, short:str=None):
        """
        Get a file and rename it and also his shortcut

        Args:
            old_name (str): old name of the file or shortcut.
            new_name (str): new name of the file.
            short (str): new name of the shortcut.

        Return:

        """
        old_name = self.get_address_of(old_name)
        old_name, type = old_name.split(".", 1)
        new_name = new_name.split(".", 1)[0]
        type = "."+type
        if short == None:
            short = new_name
        
        if os.path.exists(self.storage_folder_path+new_name+type) == True:
            trace("Rename has replaced the name "+str(new_name+type)+".")
            self.file_delete(new_name, type)
        try:
            os.rename(self.storage_folder_path+old_name+type, self.storage_folder_path+new_name+type)
            self.set_shortcut(new_name+type, old_name+type, short)
            return True
        except:
            warn("File can't be rename.")
            return False


    ###################
    # PARAM FUNCTIONS #
    ###################
    def parameter_get(self, param_name:str, file_name:str=None):
        """
        Get a parameter from a file.

        Args:
            param_name (str): name of the parameter.
            file_name (str): name of the file.

        Returns:
            The value of the parameter (str).
        """
        # Verify if the file exists in all the shortcuts files.
        if file_name == None:
            for file in self.shortcuts:
                if param_name in self.file_read(self.shortcuts[file]):
                    file_name = self.shortcuts[file]
                    break

        # Set the file address
        file_name = self.get_address_of(file_name)
        try:
            return self.file_read(file_name)[param_name]
        except:
            warn("Can't find parameter named '"+str(param_name)+"' in the file '"+str(file_name)+"'.")
            return None
        
    def parameter_set(self, param_name, param_value, file_name=None):
        """
        Set multiple parameters in a file.

        Args:
            param_name (list): name of the parameter.
            param_value (list): value of the parameter.
            file_name (list): name of the file.

        Returns:
            True if all the parameters have been set. False otherwise.
        """
        if type(param_name) == str:
            param_name = [param_name]
            param_value = [param_value]
        if file_name == None:
            file_name = [""]*len(param_name)
        elif type(file_name) == str:
            file_name = [file_name]*len(param_name)
        for k in range(len(param_name)):
            file_name[k] = self.get_address_of(file_name[k])

            try:
                modified = self.file_read(file_name[k])
                modified[param_name[k]] = param_value[k]
                json.dump(modified, open(self.storage_folder_path+file_name[k], "w"), indent=4)
                return True
            except:
                warn("Can't set the parameter named '"+str(param_name[k])+"' in the file '"+str(file_name[k])+"'.")

    def parameter_delete(self, param_name, file_name=None):
        """
        Delete multiple parameters in a file.

        Args:
            param_name (list): name of the parameter.
            file_name (str): name of the file.

        Returns:
            True if all the parameters have been deleted. False otherwise.
        """
        if type(param_name) == str:
            param_name = [param_name]
        if type(file_name) == str:
            file_name = [file_name]*len(param_name)
        
        for k in range(len(param_name)):
            file_name[k] = self.get_address_of(file_name[k])
        
            try:
                modified = self.file_read(file_name[k])
                del modified[param_name[k]]
                json.dump(modified, open(self.storage_folder_path+file_name[k], "w"), indent=4)
                return True
            except:
                warn("Can't delete the parameter named '"+str(param_name[k])+"' in the file '"+str(file_name[k])+"'.")
                return False

    def parameter_reset(self, file_name:str=None, reset:dict={}):
        """
        Reset a parameter in a file.

        Args:
            file_name (str): name of the file.

        Returns:
            True if the file has been reset. False otherwise.
        """
        file_name = self.get_address_of(file_name)
        
        try:
            json.dump(reset, open(self.storage_folder_path+file_name, "w"), indent=4)
            return True
        except:
            warn("Can't reset the file '"+str(file_name)+"'")
            return False

# Set the storage object
storage = storageHandler()