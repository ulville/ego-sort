#!/usr/bin/env python3

# ego-sort : Sort extensions on EGO by download numbers and get the ranking of eepresetselector
# Copyright (C) 2022  Ulvican Kahya aka ulville

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import pandas as pd
from datetime import datetime
from tabulate import tabulate
url = "https://extensions.gnome.org/extension-query"
payload = ""
headers = {
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Accept-Language': "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
    'Accept-Encoding': "gzip, deflate, br",
    'Referer': "https://extensions.gnome.org/",
    'X-Requested-With': "XMLHttpRequest",
    'Connection': "keep-alive",
    'Sec-Fetch-Dest': "empty",
    'Sec-Fetch-Mode': "cors",
    'Sec-Fetch-Site': "same-origin"
}
querystring = {"sort": "downloads", "page": "1", "shell_version": "all"}
extension_names = []
order = 0

with requests.Session() as s:
    r = s.request("GET", url, data=payload,
                  headers=headers, params=querystring)
    total_page = int(r.json()['numpages'])

    for page in range(1, total_page+1):

        print('Requesting page:', str(page), 'of', str(total_page), 'pages')
        querystring = {"sort": "downloads",
                       "page": "{}".format(page), "shell_version": "all"}
        r = s.request("GET", url, data=payload,
                      headers=headers, params=querystring)
        j = r.json()

        for i, extension in enumerate(j['extensions']):
            extension_names.append(extension['name'])
            if extension['name'] == 'EasyEffects Preset Selector':
                order = ((page - 1) * 10) + i + 1

        print('Done.')
print('Sırlama:', str(order), 'th most downloaded in',
      str(len(extension_names)), 'extensions')

new_entry = {'date': datetime.now().date(), 'order': order,
             'total': len(extension_names)}
data_from_csv = pd.read_csv('~/.local/share/ego/logs.csv').to_dict('list')
data_from_csv.pop('Unnamed: 0')
data_from_csv['date'].append(new_entry['date'])
data_from_csv['order'].append(new_entry['order'])
data_from_csv['total'].append(new_entry['total'])
pd.DataFrame.from_dict(data_from_csv).to_csv(('~/.local/share/ego/logs.csv'))
print(tabulate(data_from_csv))
