from heuristos.parser.html import HTMLPolicyParser

import json
import httpx

_TEST_AGREEMENTS = [
    # "https://store.steampowered.com/privacy_agreement/",  # fixme: bs4 text nodes are not considered!
    "https://www.autodesk.com/company/terms-of-use/en/general-terms",
    # "https://simpletex.cn/terms/terms_en.html",
    # "https://ondemand.manageengine.com/terms.html?pos=MEhome&loc=mefooter",
    # "https://discord.com/terms",
    # "https://policies.google.com/terms",
    # "https://www.lastpass.com/legal-center/terms-of-service/business",
    # "https://www.salesforce.com/company/legal/sfdc-website-terms-of-service/"
    # "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service"
    # "https://privacy.fireworks.com/privacy-policy",
    # "https://www.acer.com/us-en/privacy",
    # "https://www.oneidentity.com/legal/license-agreements.aspx",
    # "https://www.okta.com/privacy-policy/",
    # "https://www.iubenda.com/privacy-policy/379226/full-legal",
]


def test_html_policy_parser():
    for url in _TEST_AGREEMENTS:
        html = httpx.get(url, follow_redirects=True).text
        parser = HTMLPolicyParser(html)

        d = parser.stdrep().to_dict()
        print(json.dumps(d, indent=2))

def test_autodesk():
    with open('./autodesk.html', 'r') as f:
        html = f.read()
        parser = HTMLPolicyParser(html)
        d = parser.stdrep().to_dict()
        print(json.dumps(d, indent=2))


if __name__ == "__main__":
    test_autodesk()
    # test_html_policy_parser()
