import asyncio
import os
import re
import subprocess
import sys
import traceback
from tempfile import TemporaryDirectory
from typing import List

import aiohttp
from aiohttp import web
import cachetools
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio
import git

from config import GH_AUTH, GH_AUTH_BOT, GH_SECRET, GH_USERNAME, PORT


router = routing.Router()
cache = cachetools.LRUCache(maxsize=500)


async def send_comment(msg: str, event):
    try:
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(
                session, GH_USERNAME, oauth_token=GH_AUTH_BOT
            )
            await gh.post(
                event.data["issue"]["comments_url"],
                data={"body": msg}
            )
    except asyncio.exceptions.CancelledError:
        pass


@router.register("issue_comment", action="edited")
@router.register("issue_comment", action="created")
@router.register("pull_request_review_comment")
async def received_issue_comment(event, gh, *args, **kwargs):
    comment = event.data["comment"]["body"]
    if event.data["comment"]["user"]["login"] == GH_USERNAME:
        return
    comment_trigger = re.search(
        r"@painter-bot[,]*\s+paint\s+it\s+all", comment,
        re.IGNORECASE | re.MULTILINE
    )

    if comment_trigger is None:
        comment_trigger = re.search(
            r"@painter-bot[,]*\s+fix",
            comment,
            re.IGNORECASE | re.MULTILINE
        )
        if comment_trigger is None:
            return

    await run_pre_commit_and_push(event, gh)


async def get_clone_url_branch(event, gh):
    data = await gh.getitem(
        f"/repos/{event.data['repository']['full_name']}/pulls/{event.data['issue']['number']}"
    )
    return (data["head"]["repo"]["clone_url"], data["head"]["ref"])


async def run_pre_commit_and_push(event, gh):
    clone_url, branch_ref = await get_clone_url_branch(event, gh)
    old_folder = os.getcwd()
    try:
        with TemporaryDirectory() as clone_dir:
            os.chdir(str(clone_dir))

            repo = git.Repo.clone_from(clone_url, str(clone_dir))
            repo.config_writer().set_value(
                "user", "name", "painter-bot"
            ).release()
            repo.config_writer().set_value(
                "user", "email", "contact@marcelotrevisani.info"
            ).release()
            repo.remotes.origin.pull()
            repo.git.checkout(branch_ref)

            await run_pre_commit(event, gh)

            if repo.is_dirty():
                repo.git.add(update=True)
                repo.index.commit("Fix linter problems.")
                repo.remote(name="origin").push(branch_ref)
                msg = "@painter-bot tried to fix as much as possible."
            else:
                msg = "@painter-bot has nothing to change on this PR."
            await send_comment(msg, event)
    except BaseException as exc:
        await send_comment(
            "It was not possible to fix the problems.\n"
            "Please try again or be sure that your code can be"
            " executed.",
            event
        )
        raise exc
    finally:
        os.chdir(old_folder)


async def run_pre_commit(event, gh):
    modified_files = await gh.getitem(
        f"/repos/{event.data['repository']['full_name']}/pulls/"
        f"{event.data['issue']['number']}/files"
    )
    modified_files = [f["filename"] for f in modified_files]
    cmds = [sys.executable, "-m", "pre_commit", "run", "--files"]
    cmds.extend(modified_files)
    subprocess.run(cmds)


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
            await router.dispatch(event, gh)
        try:
            print("GH requests remaining:", gh.rate_limit.remaining)
        except AttributeError:
            pass
        return web.Response(status=200)
    except BaseException as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


def init_webapp():
    app = web.Application()
    app.router.add_post("/", main)
    print(f"Running on PORT: {PORT}")
    web.run_app(app, port=PORT)


if __name__ == "__main__":
    init_webapp()
