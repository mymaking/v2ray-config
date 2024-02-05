import base64
import json
import requests
import re
import concurrent.futures
from data import workers, proxies

def get_response(url):
    try:
        response = requests.get(url, timeout=3, headers={"User-Agent": "v2rayNG/1.8.12"})
        if response.status_code != 200:
            raise
        response = response.text
    except Exception as e:
        print(e)
        response = requests.get(url, timeout=3, headers={"User-Agent": "v2rayNG/1.8.12"}, proxies=proxies)
    links = []
    if any(proto in response for proto in ["vmess:", "trojan:", "vless:"]):
      for link in response.splitlines():
        if any(proto in link for proto in ["vmess:", "trojan:", "vless:"]):
          links.append(link)
    elif any(proto in response for proto in ["http:", "https:"]):
      url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
      sub_urls = re.findall(url_pattern, response)
      links = get_responses(sub_urls)
    else:
        decoded_line = base64.b64decode(response).decode('utf-8')
        for link in decoded_line.splitlines():
          if any(proto in link for proto in ["vmess:", "trojan:", "vless:"]):
            links.append(link)
    return links
    
def get_responses(urls):
  links = []
  def process(url):
    try:
      sub_response = requests.get(url, timeout=3, headers={"User-Agent": "v2rayNG/1.8.12"})
      if sub_response.status_code != 200:
        raise
      sub_response = sub_response.text
    except Exception as e:
        print(e)
        sub_response = requests.get(url, timeout=3, headers={"User-Agent": "v2rayNG/1.8.12"}, proxies=proxies)
    if any(proto in sub_response for proto in ["vmess:", "trojan:", "vless:"]):
      links.extend(sub_response.splitlines())
    else:
      try:
        decoded_line = base64.b64decode(sub_response).decode('utf-8')
        if any(proto in decoded_line for proto in ["vmess:", "trojan:", "vless:"]):
          links.extend(decoded_line.splitlines())
      except Exception as e:
        print(e)
  with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(process, urls)
  return links

# async def async_process(session, url, proxy, workers, links):
#     try:
#         async with session.get(url, timeout=3, headers={"User-Agent": "v2rayNG/1.8.12"}) as sub_response:
#             if sub_response.status != 200:
#                 raise Exception("Request failed")
#             sub_response = await sub_response.text()
#     except Exception as e:
#         print(e)
#         try:
#             sub_response = await session.get(proxy, params={"url": url}, timeout=3)
#             sub_response = await sub_response.text()
#         except Exception as e:
#             sub_response = await session.get(workers, params={"url": url}, timeout=3)
#             sub_response = await sub_response.text()
# 
#     if any(proto in sub_response for proto in ["vmess:", "trojan:", "vless:"]):
#         links.extend(sub_response.splitlines())
#     else:
#         try:
#             decoded_line = base64.b64decode(sub_response).decode('utf-8')
#             if any(proto in decoded_line for proto in ["vmess:", "trojan:", "vless:"]):
#                 links.extend(decoded_line.splitlines())
#         except Exception as e:
#             print(e)
# 
# async def get_responses_async(urls):
#     links = []
#     async with aiohttp.ClientSession() as session:
#         tasks = [async_process(session, url, proxy, workers, links) for url in urls]
#         await asyncio.gather(*tasks)
#     return links