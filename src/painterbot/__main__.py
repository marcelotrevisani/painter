import asyncio
import os
import sys
import traceback

import aiohttp
from aiohttp import web
import cachetools
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from config import GH_AUTH, GH_SECRET, GH_USERNAME, PORT

router = routing.Router()
cache = cachetools.LRUCache(maxsize=500)


async def main(request):
    try:
        body = await request.read()
        event = sansio.Event.from_http(request.headers, body, secret=GH_SECRET)
        print("GH delivery ID", event.delivery_id, file=sys.stderr)
        if event.event == "ping":
            return web.Response(status=200)
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(
                session,
                GH_USERNAME,
                oauth_token=GH_AUTH,
                cache=cache,
            )
            # Give GitHub some time to reach internal consistency.
            await asyncio.sleep(1)
            await router.dispatch(event, gh)
        try:
            print("GH requests remaining:", gh.rate_limit.remaining)
        except AttributeError:
            pass
        return web.Response(status=200)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


def init_webapp():
    app = web.Application()
    app.router.add_post("/", main)
    print(f"Running on PORT: {PORT}")
    web.run_app(app, port=PORT)


if __name__ == "__main__":
    init_webapp()
