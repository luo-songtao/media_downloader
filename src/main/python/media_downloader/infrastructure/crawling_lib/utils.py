from urllib.parse import *


def url_constructor(scheme='https', netloc='', path='/', params='', query='', fragment=''):
    '''

    :param scheme: <str>
    :param netloc: <str>
    :param path: <str>
    :param params: <str>
    :param query: <str/dict/list>
    :param fragment: <str>
    :return:
    '''
    if isinstance(query, dict) or isinstance(query, list):
        query = unquote(urlencode(query))
    return urlunparse((scheme, netloc, path, params, query, fragment))

if __name__ == '__main__':
    url = "http://baobab.kaiyanapp.com/api/v5/index/tab/feed?udid=fb9e95c45e4e4b239de80bdadf3cc34dd711b00e&vc=481&vn=5.3&size=1080X2265&deviceModel=ELE-AL00&first_channel=eyepetizer_googleplay_market&last_channel=eyepetizer_googleplay_market&system_version_code=28"
    ret = urlparse(url)
    print(ret)
