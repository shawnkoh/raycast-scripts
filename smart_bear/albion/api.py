import aiohttp

API_URL = "https://east.albion-online-data.com/api/v2/stats"
MAX_URL_LENGTH = 4096


class ApiClient:
    client: aiohttp.ClientSession

    def __init__(self, client: aiohttp.ClientSession) -> None:
        self.client = client

    async def get_prices(self, name_list: list[str], format: str = "json"):
        assert len(name_list) > 0

        result = list()

        url = f"{API_URL}/Prices/"
        format_suffix = f".{format}"
        max_url_length = MAX_URL_LENGTH - len(url) - len(format_suffix)

        url_chunks = list[str]()
        url_chunk = ""

        for index, name in enumerate(name_list):
            new_url_chunk = f"{url_chunk}{'' if url_chunk == '' else ','}{name}"

            if len(new_url_chunk) > max_url_length:
                url_chunks.append(f"{url}{url_chunk}{format_suffix}")
                url_chunk = name
            else:
                url_chunk = new_url_chunk

            if len(name_list) == index + 1:
                url_chunks.append(f"{url}{url_chunk}{format_suffix}")

        for url_chunk in url_chunks:
            async with self.client.get(url_chunk) as response:
                result_chunk = await response.json()
                result += result_chunk

        return result
