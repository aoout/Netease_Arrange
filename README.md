# Netease_Arrange

---

**Netease_Arrange** helps you organize your music files from netease.

```python
>>> from netease_arrange import Netease, Depository

>>> depository = Depository(path='the positon you want to store musics in.')
>>> depository.diff()

>>> netease = Netease(download_path='neteas_path', account='account', password='password')
>>> netease.sync(depository=depository)
```

Netease_Arrange allows you to copy your downloaded music files from netease to a hierarchical, clean path.

This process is a bit like synchronization.
If a new song be added to netease playlists, then it will be copy to the path when you run the program next time.
If a song be deleted, also similar results.

# Installation

---

get the package from the release page, and install it with the pip.

As the program is still too unstable, it cannot be published to pypi.org.

# RoadMap

---

- [ ] Automatically complete the transfer of membership format.
- [ ] Using the meta information and name of the playlist, create a rule to determine if it should be considered.
- [ ] Using the meta information and name of the playlist, create a rule to add hierarchy beyond playlists



