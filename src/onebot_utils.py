import json
import os


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
        else:
            word_data = json.loads(await resp.text())
    bot.logger.info("RANDOMWORD | " + word_data['word'])
    return word_data['word']
