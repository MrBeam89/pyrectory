#    Pyrectory (csv_func.py)
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

import csv
from gi.repository import Gtk

def get_content_csv(filename:str)->list:
    content = []
    csv_file = open(filename, 'rt', encoding="utf-8")
    csv_reader = csv.reader(csv_file, delimiter=';', dialect='excel', lineterminator='\n')
    for row in csv_reader:
        content.append(row)
    csv_file.close()
    return content

def write_content_csv(filename:str, entry_list)->None:
    csv_file = open(filename, 'w', encoding="utf-8")
    csv_writer = csv.writer(csv_file, delimiter=';', dialect='excel', lineterminator='\n')
    for entry in entry_list:
        entry_content = entry[:]
        csv_writer.writerow(entry_content)
    csv_file.close()