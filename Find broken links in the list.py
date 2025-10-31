import re
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from aiofiles import open as aio_open

BROKEN_PHRASES = [
    "this channel is not available",
    "this account has been terminated",
    "channel does not exist",
    "404 not found",
    "video unavailable",
    "page not found",
]

def extract_links_from_readme(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return re.findall(r"https?://(?:www\.)?youtube\.com/[^\s)]+", f.read())

async def check_link(session: aiohttp.ClientSession, link: str) -> bool:
    try:
        async with session.get(link, allow_redirects=True, timeout=ClientTimeout(total=8)) as r:
            if r.status != 200:
                return False
            text = await r.text()
            return not any(p in text.lower() for p in BROKEN_PHRASES)
    except:
        return False

async def check_all(links: list[str], concurrency: int = 40):
    broken = []
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(concurrency)

        async def worker(link):
            async with sem:
                ok = await check_link(session, link)
                print(f"{'✅' if ok else '❌'} {link}")
                if not ok:
                    broken.append(link)

        await asyncio.gather(*(worker(l) for l in links))
    return broken

async def main():
    links = extract_links_from_readme("README.md")
    print(f"Found {len(links)} links\n")
    if not links:
        return
    broken = await check_all(links)
    if broken:
        async with aio_open("broken_links2.txt", "w", encoding="utf-8") as f:
            await f.writelines(l + "\n" for l in broken)
        print(f"\n{len(broken)} broken links saved to broken_links2.txt")
    else:
        print("\nNo broken links found")

if __name__ == "__main__":
    asyncio.run(main())
