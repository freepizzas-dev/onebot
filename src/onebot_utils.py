import json
import os
from string import Formatter


# gets a random word from the WordsAPI hosted at RapidAPI.
# note: 2,500 lookups per day.
async def get_random_word(bot):
    endpoint = 'https://wordsapiv1.p.rapidapi.com/words/'
    rapidhost = 'wordsapiv1.p.rapidapi.com'
    XRAPIDKEY = os.environ.get("XRAPIDKEY")
    headers = {'x-rapidapi-key': XRAPIDKEY, 'x-rapidapi-host': rapidhost, 'useQueryString': 'true'}
    params = {'random': 'true'}
    word_data = ''
    async with bot.aiohttp_session.get(endpoint, headers=headers, params=params) as resp:
        if resp.status != 200:
            bot.logger.error("RANDOMWORD | Failed.")
            bot.logger.error("RANDOMWORD | Response code: " + str(resp.status))
            return ''
        else:
            word_data = json.loads(await resp.text())
    bot.logger.info("RANDOMWORD | " + word_data['word'])
    return word_data['word']


# format TimeDelta object to String
# from https://stackoverflow.com/a/17847006
def strfdelta(tdelta, fmt):
    f = Formatter()
    d = {}
    lookup = {'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    k = map(lambda x: x[1], list(f.parse(fmt)))
    rem = int(tdelta.total_seconds())

    for i in ('D', 'H', 'M', 'S'):
        if i in k and i in lookup.keys():
            d[i], rem = divmod(rem, lookup[i])

    return f.format(fmt, **d)
