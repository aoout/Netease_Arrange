# Netease_Arrange

**Netease_Arrange** helps you organize your music files from netease.

```python
from netease_arrange import Sync

Sync(
    account='account',
    password='password',
    depository='the positon you want to store musics in',
    netease_download_path='...'
)
```

Netease_Arrange allows you to copy your downloaded music files from netease to a hierarchical, clean path.

This process is a bit like synchronization.
If a new song be added to netease playlists, then it will be copy to the path when you run the program next time.
If a song be deleted, also similar results.

For additional information, be sure to look at the roadmap.

# Installation

get the package from the release page, and install it with the pip.

As the program is still too unstable, it cannot be published to pypi.org.

# RoadMap

- [x] Automatically complete the transfer of membership format.

Put the exe file with transcoding function into `.netease_arrange` folder under the user folder, and rename it to `converter.exe`.
This project does not directly provide transcoding function.

- [ ] Become able to recognize different song title formats.

Now, You must follow the default song title format of NetEase Cloud Music Download.
- [ ] Using the meta information and name of the playlist, create a rule to determine if it should be considered.
- [ ] Using the meta information and name of the playlist, create a rule to add hierarchy beyond playlists.



