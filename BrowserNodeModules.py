# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import sublime
from sublime_plugin import (WindowCommand)

PKG_JSONS = {}
MTIMES = {}

def load_package_json(package_json_path):
    global PKG_JSONS, MTIMES
    try:
        mtime = os.path.getmtime(package_json_path)
    except OSError:
        return
    else:
        if mtime > MTIMES.get(package_json_path, 0) or package_json_path not in PKG_JSONS:
            with open(package_json_path) as f:
                PKG_JSONS[package_json_path] = json.load(f)
    return PKG_JSONS[package_json_path]

class BrowseNodeModulesCommand(WindowCommand):
    def get_dependencies(self, package_json_path):
        package_json = load_package_json(package_json_path)

        all_dependencies = {}
        all_dependencies.update(package_json.get('dependencies', {}))
        all_dependencies.update(package_json.get('peerDependencies', {}))
        all_dependencies.update(package_json.get('devDependencies', {}))

        items = [[name, version] for name, version in all_dependencies.items()]
        return sorted(items, key=lambda item: item[0])

    def run(self):
        first_folder = self.window.folders()[0]
        package_json_path = os.path.join(first_folder, 'package.json')
        node_modules_path = os.path.join(first_folder, 'node_modules')

        if not os.path.exists(package_json_path) or not os.path.exists(node_modules_path):
           return

        items = self.get_dependencies(package_json_path)
        if not items:
           return

        def on_done(index):
            if index == -1:
               return

            module_package_json = os.path.join(node_modules_path, items[index][0], 'package.json')

            if os.path.exists(module_package_json):
                self.window.open_file(module_package_json)
                sublime.set_timeout(lambda: self.window.run_command('reveal_in_side_bar'), 100)

        self.window.show_quick_panel(items, on_done)
