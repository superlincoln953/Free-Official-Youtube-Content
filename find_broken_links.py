import re
import requests

def extract_links_from_readme(readme_path):
    """Extract all YouTube links from README.md"""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match all YouTube links (channel, playlist, etc.)
    return re.findall(r'https?://(?:www\.)?youtube\.com/[^\s)]+', content)

def check_link_status(link):
    """
    Returns:
      True if valid
      False if broken, unavailable, or invalid
    """
    try:
        response = requests.get(link, allow_redirects=True, timeout=8)
        text = response.text.lower()
        status_code = response.status_code

        # Common broken signs
        broken_phrases = [
            "this channel is not available",
            "this account has been terminated",
            "channel does not exist",
            "404 not found",
            "video unavailable",
            "page not found"
        ]

        if status_code != 200:
            return False
        for phrase in broken_phrases:
            if phrase in text:
                return False
        return True
    except requests.RequestException:
        return False

def main():
    readme_path = "README.md"
    links = extract_links_from_readme(readme_path)
    print(f"🔍 Found {len(links)} YouTube links in {readme_path}\n")

    broken_links = []

    for i, link in enumerate(links, start=1):
        print(f"[{i}/{len(links)}] Checking: {link}")
        if not check_link_status(link):
            print("❌ Broken / Unavailable")
            broken_links.append(link)
        else:
            print("✅ Valid")

    # Save broken links
    if broken_links:
        with open("broken_links2.txt", "w", encoding="utf-8") as f:
            for link in broken_links:
                f.write(link + "\n")
        print(f"\n⚠️ {len(broken_links)} broken links found. Saved to broken_links2.txt")
    else:
        print("\n🎉 No broken links found!")

if __name__ == "__main__":
    main()