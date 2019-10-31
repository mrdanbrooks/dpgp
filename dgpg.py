#!/usr/bin/env python3
#   Copyright 2019 Dan Brooks
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" dgpg v0.1 """

import argparse
import getpass
import sys, tempfile, os
import pydoc
import shlex
from subprocess import call, Popen, run, PIPE

EDITOR = os.environ.get('EDITOR','vim')

class DGPG:
    def __init__(self):
        self.__buffer = None  # holds decrypted content
        self.__passwd = None  # holds password
        self.__buffer_updated = False  # Flag to determine if buffer has changed

    def read_passwd(self, confirm=False):
        """ Reads in a password.
        if confirm=True, ask twice to check if it is the same.
        If confirm=True and not the same, ask to try again until success
        """
        while True:
            passwd = getpass.getpass("Enter passphrase: ")
            # If not confirming, jump to bottom and save password
            if not confirm:
                break
            repeat_passwd = getpass.getpass("Please re-enter this passphrase: ")
            if passwd == repeat_passwd:
                break

        self.__passwd = passwd

    def write_gpg_file(self, filepath):
        # tempfile idea - https://stackoverflow.com/a/6309753
        # passing input from command line - https://stackoverflow.com/a/165662
        if not self.__buffer_updated:
            print("No change to write.")
            return
        with tempfile.NamedTemporaryFile(prefix="myfile", suffix=".tmp") as tf:
            tf.write(self.__buffer)
            tf.flush()
            cmd = "gpg --batch --yes --symmetric --armor --passphrase-fd 0 --output %s %s" % (filepath, tf.name)
#             p = Popen(shlex.split(cmd), stdout=PIPE, stdin=PIPE, stderr=PIPE)
#             p.communicate(self.__passwd)
            run(shlex.split(cmd), input=self.__passwd, encoding='ascii')

    def read_gpg_file(self, filepath):
        """ Attempts to read an input file.
        Saves contents inside buffer made by class
        returns True if successful, Flase if decryption failed
        """
        # https://stackoverflow.com/a/165662
        cmd = "gpg --no-mdc-warning --ignore-mdc-error --batch --decrypt --passphrase-fd 0 %s" % (filepath)
        p = run(shlex.split(cmd), stdout=PIPE, input=self.__passwd, encoding='ascii')
        # Detect decryption error
        if p.returncode != 0:
            return False
        # Copy decrypted content to buffer
        self.__buffer = p.stdout
        return True

    def editor(self):
        """ Opens editor.
        If there is content stored in buffer, display it.
        Final editor content (once closed) is put into buffer. 
        """
        # Save a copy of the current buffer so we can tell if it changed later
        orig_buffer = self.__buffer
        if not orig_buffer is None and not isinstance(orig_buffer, bytes):
            orig_buffer = orig_buffer.encode('ascii')

        with tempfile.NamedTemporaryFile(prefix="myfile", suffix=".tmp") as tf:
            if self.__buffer:
                tf.write(self.__buffer.encode('ascii'))
                tf.flush()
            call([EDITOR, "+set backupcopy=yes", tf.name])
            tf.seek(0)
            self.__buffer = tf.read()

        # Set updated flag if buffer changed.
        # This will indicate to write_gpg_file() if we need to actually write a new file
        if not orig_buffer == self.__buffer:
            self.__buffer_updated = True

    def display(self):
        """ Show buffer contents using pager (less) """
        pydoc.pager(self.__buffer)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--edit", action="store_true")
    args = parser.parse_args()

    filepath = os.path.abspath(os.path.expanduser(args.file))
    if not os.path.isdir(os.path.dirname(filepath)):
        print("Directory not found: %s" % os.path.dirname(filepath)) 
        return -1

    dgpg = DGPG()

    # Create a new file if it does not exist
    if not os.path.isfile(filepath):
        dgpg.editor()
        dgpg.read_passwd(confirm=True)
        dgpg.write_gpg_file(filepath)
        return

    # if file exists and user wants to edit, open with editor and write changes
    elif args.edit:
        dgpg.read_passwd()
        success = dgpg.read_gpg_file(filepath)
        if success:
            dgpg.editor()
            dgpg.write_gpg_file(filepath)
        else:
            print("Bad passphrase")
        return 

    # Otherwise, just display the file contents
    else:
        dgpg.read_passwd()
        success = dgpg.read_gpg_file(filepath)
        if success:
            dgpg.display()
        else:
            print("Bad passphrase")
        return
        


if __name__ == "__main__":
    main()
