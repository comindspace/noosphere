from typing import Generator, Any

def redirected_links(links: list[str]) -> Generator[str, Any, None]:
    for link_string in links:
        if link_string.strip() == "https://en.wikipedia.org/wiki/Pok%C3%A9mon (NOT REQUIRED, BUT HELPFUL)":
            yield "https://en.wikipedia.org/wiki/Pok%C3%A9mon"
            continue
        for pre_link in link_string.split(", "):
            link = (pre_link.strip()
                    .split("#")[0]
                    .replace("https://en.m.wikipedia.org/", "https://en.wikipedia.org/")
                    .replace("https://simple.wikipedia.org/", "https://en.wikipedia.org/"))
            match link:
                case "https://en.wikipedia.org/w/index.php?search=Polytrichum+piliferum&title=Special:Search&profile=advanced&fulltext=1&ns0=1":
                    yield "https://en.wikipedia.org/wiki/Polytrichum_piliferum"
                case "https://en.wikipedia.org/w/index.php?title=Bronco&redirect=no":
                    yield "https://en.wikipedia.org/wiki/Bucking_horse"
                case "https://w.wiki/ASFv":
                    yield "https://en.wikipedia.org/wiki/Harry_C._Bradley_(actor)"
                case "https://en.wikipedia.org/wiki/2021_French_Open_%E2%80%93_Men%2527s_singles":
                    yield "https://en.wikipedia.org/wiki/2021_French_Open_%E2%80%93_Men's_singles"
                case _:
                    yield link
