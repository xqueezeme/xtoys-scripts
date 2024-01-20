def getUrl(site, id):
    if (site == 'pornhub'):
        return 'https://nl.pornhub.com/view_video.php?viewkey=' + id
    elif (site == 'spankbang'):
        return 'https://nl.spankbang.com/' + id + '/video/test'
    elif (site == 'xvideos'):
        return 'https://www.xvideos.com/video' + id + '/xxx'
    elif (site == 'xhamster'):
        return 'https://nl.xhamster.com/videos/xxx-' + id
    elif (site == 'eporner'):
        return 'https://www.eporner.com/video-' + id + '/'

    return None
