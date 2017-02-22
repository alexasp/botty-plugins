import asyncio, aiohttp
import plugins
import logging
import time, random, json, re
from urllib import parse

logger = logging.getLogger(__name__)

urls_posted = []

def _initialise(bot):
	plugins.register_handler(on_message, type="message", priority=5)
	
def ext_content(url):
	logger.info(url)

	data = None
	try:
		r = yield from aiohttp.request("post", "https://www.jamapi.xyz", data={
			"url": url,
			"json_data": json.dumps({
				"title": "h1",
				"content": ["p"]
			})
		})
		data = yield from r.json()
	except:
		return False, "", ""
	
	if data is None:
		return False, "", ""
	
	if "content" not in data or len(data["content"]) == 0:
		return False, "", ""
		
	title = '<b>' + data["title"] + '</b>\n' if "title" in data and len(data["title"]) != 0 else ''
	return True, title, " ".join(data["content"])
	
	
def summarize(text): 
	headers = {
		"X-Mashape-Key": "CZrByDIfctmshUZlKmwtVsg64yNSp14UJ6jjsnCSwRfXEPI0If",
	}
	data = {
		"Percent": 5,
		"Language": "en",
		"Text": text
	}
	j_data = json.dumps(data)

	r = yield from aiohttp.request("post", "https://cotomax-summarizer-text-v1.p.mashape.com/summarizer", headers=headers, data=data)
	ret = yield from r.text()
	return ret[1:-1].replace("\\n", "") #strip quotes
	
def on_message(bot, event, command):
	global urls_posted
	
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', event.text)
	if len(urls) != 0:
		urls_posted = urls

	if "#tldr" in event.text.lower():
		for url in urls_posted:
			success, title, content = yield from ext_content(url)
			if success:
				summary = yield from summarize(content)
				yield from bot.coro_send_message(event.conv_id, "<b>TL;DR </b>" + url + "\n\n" + title + summary)
			else:
				yield from bot.coro_send_message(event.conv_id, "Failed to <b>TL;DR </b>" + url)
			