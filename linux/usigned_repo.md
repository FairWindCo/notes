# Force update from unsigned repository

Можна поставити в файлі `sources.list` (що розташовано в `/etc/apt/sources.list`):

`deb [trusted=yes] http://www.deb-multimedia.org jessie main`


Також можна вказати опції, що відключать перевірку:

`--allow-unauthenticated`
From the man pages for apt-get:

`--allow-unauthenticated`
    Ignore if packages can't be authenticated and don't prompt about
    it. This can be useful while working with local repositories, but
    is a huge security risk if data authenticity isn't ensured in
    another way by the user itself. The usage of the Trusted option for
    sources.list(5) entries should usually be preferred over this
    global override. Configuration Item: APT::Get::AllowUnauthenticated.

But be a little cautious about using this option more widely, the safeguards are in place to protect your computer not limit your freedom...

В нових версіях Ubuntu, замість  `--allow-unauthenticated`, використовують `--allow-insecure-repositories`.

Таким чином команда оновлення буде мати вигляд:
`sudo apt-get update --allow-insecure-repositories`
