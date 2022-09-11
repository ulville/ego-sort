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

from time import time
import httpx
import asyncio
import pandas as pd
from datetime import datetime
from tabulate import tabulate

LOG_PATH = "~/.local/share/ego/logs.csv"
# LOG_PATH = "logs.csv"

url = "https://extensions.gnome.org/extension-query/"
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
querystring = {"shell_version": "all", "sort": "downloads", "page": "1"}
extension_names = []
order_list = []


def get_total_page():
    r = httpx.request("GET", url, data=payload,
                      headers=headers, params=querystring)
    return int(r.json()['numpages'])


async def log_request(request):
    print('Requesting page:',  request.url.params.get(
        'page'), 'of', str(total_page), 'pages')


async def log_response(response):
    request = response.request
    print('Got response of page:', request.url.params.get('page'))


async def get_extensions(page):
    querystring = {"sort": "downloads",
                   "page": "{}".format(page), "shell_version": "all"}
    async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}) as client:
        r = await client.request("GET", url, data=payload, headers=headers, params=querystring, timeout=10)
        j = r.json()

        for i, extension in enumerate(j['extensions']):
            extension_names.append(extension['name'])
            if extension['name'] == 'EasyEffects Preset Selector':
                order = ((page - 1) * 10) + i + 1
                order_list.append(order)
        return


async def main():
    tasks = []
    for page in range(1, total_page+1):
        tasks.append(get_extensions(page))
    await asyncio.gather(*tasks)

ts = time()

total_page = get_total_page()
asyncio.run(main())

print('Sırlama:', str(order_list[0]), 'th most downloaded in',
      str(len(extension_names)), 'extensions')

new_entry = {'date': datetime.now().date(), 'order': order_list[0],
             'total': len(extension_names)}
data_from_csv = pd.read_csv(LOG_PATH).to_dict('list')
data_from_csv.pop('Unnamed: 0')
data_from_csv['date'].append(new_entry['date'])
data_from_csv['order'].append(new_entry['order'])
data_from_csv['total'].append(new_entry['total'])
pd.DataFrame.from_dict(data_from_csv).to_csv((LOG_PATH))
print(tabulate(data_from_csv))

te = time()
print('Took: %.4f sec' % (te-ts))
